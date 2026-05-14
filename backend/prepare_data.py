"""
DermaVision — Veri Hazırlama Pipeline'ı
=========================================
Video / ham görüntü  →  frame çıkarma  →  yüz tespiti  →
kalite kontrolü  →  AI otomatik etiketleme (CLIP)  →  data/

Kullanım:
    # Video klasöründen otomatik pipeline:
    python prepare_data.py --input videos/ --mode video

    # Ham görüntü klasörü (etiket yok, AI etiketlesin):
    python prepare_data.py --input raw_images/ --mode images

    # Zaten etiketli klasör, sadece kalite filtrele:
    python prepare_data.py --input data/ --mode quality_only

    # AI güven eşiğini düşür (daha fazla görüntü kabul):
    python prepare_data.py --input raw_images/ --mode images --clip_threshold 0.5

Çıktı klasörü yapısı:
    data/
    ├── kuru/
    ├── normal/
    └── yagli/
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

# ─── İsteğe bağlı bağımlılıklar ──────────────────────────────────────────────
try:
    import torch
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    print("[UYARI] transformers/torch yüklü değil → AI etiketleme devre dışı")

try:
    import mediapipe as mp
    MP_AVAILABLE = True
    mp_face = mp.solutions.face_detection
except ImportError:
    MP_AVAILABLE = False
    print("[UYARI] mediapipe yüklü değil → OpenCV yüz tespitine geçiliyor")


# ─── Sabitler ────────────────────────────────────────────────────────────────
CLASS_NAMES = ["kuru", "normal", "yagli"]

# CLIP prompt'ları — İngilizce daha iyi sonuç verir
CLIP_PROMPTS = {
    "kuru":   "a close-up photo of a human face with dry and flaky skin",
    "normal": "a close-up photo of a human face with normal balanced skin",
    "yagli":  "a close-up photo of a human face with oily and shiny skin",
}

# Kalite kontrol eşikleri
QUALITY_CONFIG = {
    "min_blur_score":     80.0,    # Laplacian varyansı (düşük = bulanık)
    "min_brightness":     40,      # 0-255 arası minimum parlaklık
    "max_brightness":     220,     # 0-255 arası maksimum parlaklık
    "min_face_ratio":     0.10,    # Görüntüde yüzün minimum alanı (%)
    "min_img_size":       150,     # Minimum kenar boyutu (piksel)
    "clip_threshold":     0.55,    # CLIP güven skoru eşiği
}


# ─── Argümanlar ───────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="DermaVision veri hazırlama pipeline'ı")
    p.add_argument("--input",           type=str, required=True,       help="Kaynak klasör (video veya görüntü)")
    p.add_argument("--output",          type=str, default="data",       help="Çıktı klasörü")
    p.add_argument("--mode",            type=str, default="images",
                   choices=["video", "images", "quality_only"],         help="Çalışma modu")
    p.add_argument("--frame_interval",  type=int, default=15,           help="Video'dan kaç frame'de bir çıkar")
    p.add_argument("--clip_threshold",  type=float,
                   default=QUALITY_CONFIG["clip_threshold"],            help="CLIP güven eşiği (0-1)")
    p.add_argument("--no_ai_label",     action="store_true",            help="AI etiketlemeyi devre dışı bırak")
    p.add_argument("--no_face_check",   action="store_true",            help="Yüz tespitini atla")
    p.add_argument("--dry_run",         action="store_true",            help="Sadece raporla, dosya kopyalama")
    return p.parse_args()


# ════════════════════════════════════════════════════════════════════════════════
# 1. VIDEO FRAME ÇIKARMA
# ════════════════════════════════════════════════════════════════════════════════
def extract_frames(video_path: str, output_dir: str, interval: int = 15) -> list[str]:
    """
    Video dosyasından her `interval` frame'de bir görüntü çıkarır.
    Çıkarılan frame'leri output_dir/frames/ klasörüne kaydeder.
    """
    os.makedirs(output_dir, exist_ok=True)
    cap    = cv2.VideoCapture(video_path)
    frames = []
    idx    = 0

    video_name = Path(video_path).stem
    pbar = tqdm(desc=f"  Frame çıkarılıyor: {Path(video_path).name}", unit="frame")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            fname = os.path.join(output_dir, f"{video_name}_f{idx:06d}.jpg")
            cv2.imwrite(fname, frame)
            frames.append(fname)
        idx += 1
        pbar.update(1)

    pbar.close()
    cap.release()
    print(f"    → {len(frames)} frame kaydedildi (toplam: {idx})")
    return frames


def extract_all_videos(input_dir: str, output_dir: str, interval: int) -> list[str]:
    """Klasördeki tüm video dosyalarından frame çıkarır."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v"}
    video_files = [
        p for p in Path(input_dir).rglob("*")
        if p.suffix.lower() in video_exts
    ]
    print(f"\n[1/4] Video frame çıkarma — {len(video_files)} video bulundu")

    frames_dir = os.path.join(output_dir, "_frames")
    all_frames = []
    for vf in video_files:
        frames = extract_frames(str(vf), frames_dir, interval)
        all_frames.extend(frames)

    print(f"  Toplam {len(all_frames)} frame çıkarıldı\n")
    return all_frames


# ════════════════════════════════════════════════════════════════════════════════
# 2. YÜZ TESPİTİ VE KIRPMA
# ════════════════════════════════════════════════════════════════════════════════
class FaceDetector:
    def __init__(self):
        if MP_AVAILABLE:
            self._mp_detector = mp_face.FaceDetection(
                model_selection=0, min_detection_confidence=0.6
            )
            self._backend = "mediapipe"
        else:
            # OpenCV Haar Cascade fallback
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._cv_detector = cv2.CascadeClassifier(cascade_path)
            self._backend = "opencv"
        print(f"  Yüz tespiti: {self._backend}")

    def detect_and_crop(self, img_path: str, min_ratio: float = 0.10):
        """
        Görüntüde yüz tespit eder ve kırpılmış yüz bölgesini döner.
        Yüz bulunamazsa None döner.
        min_ratio: görüntünün en az %X'i kadar yüz alanı olmalı.
        """
        img = cv2.imread(img_path)
        if img is None:
            return None

        h, w = img.shape[:2]
        img_area = h * w

        if self._backend == "mediapipe":
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self._mp_detector.process(rgb)
            if not results.detections:
                return None
            det   = results.detections[0]  # En belirgin yüzü al
            bbox  = det.location_data.relative_bounding_box
            x1    = max(0, int(bbox.xmin * w) - 20)
            y1    = max(0, int(bbox.ymin * h) - 20)
            x2    = min(w, x1 + int(bbox.width  * w) + 40)
            y2    = min(h, y1 + int(bbox.height * h) + 40)
        else:
            gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._cv_detector.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
            if len(faces) == 0:
                return None
            # En büyük yüzü al
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            x, y, fw, fh = faces[0]
            pad = 20
            x1, y1 = max(0, x - pad), max(0, y - pad)
            x2, y2 = min(w, x + fw + pad), min(h, y + fh + pad)

        face_area = (x2 - x1) * (y2 - y1)
        if face_area / img_area < min_ratio:
            return None  # Yüz çok küçük

        cropped = img[y1:y2, x1:x2]
        return cropped


# ════════════════════════════════════════════════════════════════════════════════
# 3. KALİTE KONTROLÜ
# ════════════════════════════════════════════════════════════════════════════════
def compute_blur_score(img_bgr: np.ndarray) -> float:
    """Laplacian varyansı — yüksek = keskin, düşük = bulanık."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def compute_brightness(img_bgr: np.ndarray) -> float:
    """Ortalama parlaklık (HSV-V kanalı)."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    return hsv[:, :, 2].mean()


def compute_image_hash(img_path: str) -> str:
    """MD5 hash ile tekrar görüntü tespiti."""
    with open(img_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


class QualityChecker:
    def __init__(self, config: dict):
        self.cfg     = config
        self._hashes = set()

    def check(self, img_bgr: np.ndarray, img_path: str) -> tuple[bool, str]:
        """
        (geçti_mi, red_sebebi) döner.
        """
        h, w = img_bgr.shape[:2]

        # Boyut kontrolü
        if min(h, w) < self.cfg["min_img_size"]:
            return False, f"küçük boyut ({min(h,w)}px)"

        # Bulanıklık kontrolü
        blur = compute_blur_score(img_bgr)
        if blur < self.cfg["min_blur_score"]:
            return False, f"bulanık (score={blur:.1f})"

        # Parlaklık kontrolü
        brightness = compute_brightness(img_bgr)
        if brightness < self.cfg["min_brightness"]:
            return False, f"çok karanlık (brightness={brightness:.1f})"
        if brightness > self.cfg["max_brightness"]:
            return False, f"çok parlak/aşırı poz (brightness={brightness:.1f})"

        # Tekrar görüntü kontrolü
        img_hash = compute_image_hash(img_path)
        if img_hash in self._hashes:
            return False, "duplicate"
        self._hashes.add(img_hash)

        return True, "ok"


# ════════════════════════════════════════════════════════════════════════════════
# 4. AI OTOMATİK ETİKETLEME (CLIP)
# ════════════════════════════════════════════════════════════════════════════════
class CLIPLabeler:
    def __init__(self, threshold: float = 0.55):
        if not CLIP_AVAILABLE:
            raise RuntimeError("transformers veya torch yüklü değil!")

        self.threshold  = threshold
        self.device     = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  CLIP modeli yükleniyor (cihaz: {self.device})...")

        self.model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.prompts   = list(CLIP_PROMPTS.values())
        self.labels    = list(CLIP_PROMPTS.keys())

        # Metin özelliklerini önceden hesapla (hız için)
        inputs      = self.processor(text=self.prompts, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            self.text_features = self.model.get_text_features(**inputs)
            self.text_features = self.text_features / self.text_features.norm(dim=-1, keepdim=True)

        print(f"  CLIP hazır. Eşik: {self.threshold}")

    @torch.no_grad()
    def predict(self, img_path: str) -> tuple[str | None, float]:
        """
        (tahmin_etiketi, güven_skoru) döner.
        Güven eşiğin altındaysa (None, skor) döner.
        """
        try:
            image  = Image.open(img_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            img_features = self.model.get_image_features(**inputs)
            img_features = img_features / img_features.norm(dim=-1, keepdim=True)

            sims    = (img_features @ self.text_features.T).squeeze(0)
            probs   = sims.softmax(dim=-1).cpu().numpy()
            top_idx = probs.argmax()
            score   = float(probs[top_idx])

            if score < self.threshold:
                return None, score
            return self.labels[top_idx], score

        except Exception as e:
            print(f"    [CLIP hata] {img_path}: {e}")
            return None, 0.0


# ════════════════════════════════════════════════════════════════════════════════
# 5. ANA PIPELINE
# ════════════════════════════════════════════════════════════════════════════════
def collect_images(input_dir: str) -> list[str]:
    """Klasördeki tüm görüntü dosyalarını toplar."""
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
    return [
        str(p) for p in Path(input_dir).rglob("*")
        if p.suffix.lower() in exts
    ]


def save_image(img_bgr: np.ndarray, label: str, output_dir: str,
               source_path: str, dry_run: bool) -> str:
    """Görüntüyü doğru etiket klasörüne kaydeder."""
    dest_dir = os.path.join(output_dir, label)
    os.makedirs(dest_dir, exist_ok=True)
    fname = Path(source_path).name
    dest  = os.path.join(dest_dir, fname)

    # Aynı isim varsa suffix ekle
    counter = 1
    while os.path.exists(dest):
        stem, ext = os.path.splitext(fname)
        dest = os.path.join(dest_dir, f"{stem}_{counter}{ext}")
        counter += 1

    if not dry_run:
        cv2.imwrite(dest, img_bgr)

    return dest


def run_pipeline(args):
    os.makedirs(args.output, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  DermaVision — Veri Hazırlama Pipeline'ı")
    print(f"  Mod    : {args.mode}")
    print(f"  Kaynak : {args.input}")
    print(f"  Çıktı  : {args.output}")
    if args.dry_run:
        print(f"  ⚠  DRY RUN — dosyalar kopyalanmayacak")
    print(f"{'='*60}\n")

    stats = {
        "toplam"      : 0,
        "kabul"       : 0,
        "ret_blur"    : 0,
        "ret_bright"  : 0,
        "ret_duplicate": 0,
        "ret_no_face" : 0,
        "ret_kucuk"   : 0,
        "ret_clip_dusuk": 0,
        "etiket"      : {c: 0 for c in CLASS_NAMES},
    }

    # ── Adım 1: Frame çıkarma (sadece video modunda) ─────────────────────────
    if args.mode == "video":
        frame_files = extract_all_videos(args.input, args.output, args.frame_interval)
        image_files = frame_files
    else:
        image_files = collect_images(args.input)
        print(f"[1/4] Görüntü tarama — {len(image_files)} görüntü bulundu\n")

    if not image_files:
        print("Hiç görüntü/video bulunamadı. Giriş klasörünü kontrol edin.")
        sys.exit(1)

    # ── Adım 2: Yüz dedektörü başlat ─────────────────────────────────────────
    print(f"[2/4] Yüz dedektörü başlatılıyor...")
    face_detector = None if args.no_face_check else FaceDetector()

    # ── Adım 3: Kalite denetçisi başlat ──────────────────────────────────────
    print(f"[3/4] Kalite denetçisi başlatılıyor...")
    QUALITY_CONFIG["clip_threshold"] = args.clip_threshold
    quality_checker = QualityChecker(QUALITY_CONFIG)

    # ── Adım 4: CLIP etiketleyici başlat ─────────────────────────────────────
    labeler = None
    if not args.no_ai_label and args.mode != "quality_only":
        print(f"[4/4] CLIP etiketleyici başlatılıyor...")
        if CLIP_AVAILABLE:
            labeler = CLIPLabeler(threshold=args.clip_threshold)
        else:
            print("  [UYARI] CLIP yok, AI etiketleme atlanıyor.")

    print(f"\n{'─'*60}")
    print(f"  Pipeline çalışıyor ({len(image_files)} görüntü)...\n")

    label_log = []   # (kaynak, etiket, skor, durum) log kaydı

    for img_path in tqdm(image_files, desc="İşleniyor", unit="img"):
        stats["toplam"] += 1

        # quality_only modunda etiket klasör adından gelir
        folder_label = None
        if args.mode == "quality_only":
            parent = Path(img_path).parent.name
            if parent in CLASS_NAMES:
                folder_label = parent

        # ── Görüntüyü oku ────────────────────────────────────────────────────
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            continue

        # ── Yüz tespiti ve kırpma ─────────────────────────────────────────
        if face_detector is not None:
            cropped = face_detector.detect_and_crop(
                img_path, min_ratio=QUALITY_CONFIG["min_face_ratio"]
            )
            if cropped is None:
                stats["ret_no_face"] += 1
                label_log.append((img_path, None, 0, "yüz bulunamadı"))
                continue
            img_bgr = cropped

        # ── Kalite kontrolü ───────────────────────────────────────────────
        passed, reason = quality_checker.check(img_bgr, img_path)
        if not passed:
            if "bulanık"   in reason: stats["ret_blur"]      += 1
            elif "karanlık" in reason or "parlak" in reason: stats["ret_bright"] += 1
            elif "duplicate" in reason: stats["ret_duplicate"] += 1
            elif "boyut"   in reason: stats["ret_kucuk"]     += 1
            label_log.append((img_path, None, 0, reason))
            continue

        # ── Etiket belirleme ──────────────────────────────────────────────
        if folder_label:
            label, score = folder_label, 1.0   # quality_only: var olan etiketi koru
        elif labeler:
            label, score = labeler.predict(img_path)
            if label is None:
                stats["ret_clip_dusuk"] += 1
                label_log.append((img_path, None, score, f"CLIP güven düşük ({score:.2f})"))
                continue
        else:
            label, score = "belirsiz", 0.0    # Etiketleme yoksa geç

        # ── Kaydet ───────────────────────────────────────────────────────
        dest = save_image(img_bgr, label, args.output, img_path, args.dry_run)
        stats["kabul"] += 1
        stats["etiket"][label] = stats["etiket"].get(label, 0) + 1
        label_log.append((img_path, label, score, "kabul edildi"))

    # ── Rapor ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  PIPELINE RAPORU")
    print(f"{'='*60}")
    print(f"  Toplam işlenen    : {stats['toplam']}")
    print(f"  Kabul edilen      : {stats['kabul']}  ({stats['kabul']/max(1,stats['toplam'])*100:.1f}%)")
    print(f"{'─'*60}")
    print(f"  Red — yüz yok     : {stats['ret_no_face']}")
    print(f"  Red — bulanık     : {stats['ret_blur']}")
    print(f"  Red — parlaklık   : {stats['ret_bright']}")
    print(f"  Red — duplicate   : {stats['ret_duplicate']}")
    print(f"  Red — küçük boyut : {stats['ret_kucuk']}")
    print(f"  Red — CLIP düşük  : {stats['ret_clip_dusuk']}")
    print(f"{'─'*60}")
    print(f"  Etiket dağılımı:")
    for cls, cnt in stats["etiket"].items():
        bar = "█" * (cnt // max(1, max(stats["etiket"].values()) // 20))
        print(f"    {cls:<8} : {cnt:>4}  {bar}")
    print(f"{'='*60}\n")

    # ── Log JSON olarak kaydet ─────────────────────────────────────────────────
    log_path = os.path.join(args.output, "pipeline_log.json")
    if not args.dry_run:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump({
                "stats"  : stats,
                "details": [
                    {"path": p, "label": l, "score": round(s, 3), "status": st}
                    for p, l, s, st in label_log
                ],
            }, f, ensure_ascii=False, indent=2)
        print(f"  Log kaydedildi: {log_path}")


# ─── Giriş ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args)
