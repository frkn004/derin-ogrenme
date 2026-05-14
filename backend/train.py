"""
DermaVision — ViT-B/16 Eğitim Scripti
=======================================
Cilt tipi sınıflandırması: kuru / normal / yağlı

Kullanım:
    python train.py --data_dir data/ --epochs 30 --batch_size 32

Veri klasörü yapısı:
    data/
    ├── kuru/      (kuru cilt fotoğrafları)
    ├── normal/    (normal cilt fotoğrafları)
    └── yagli/     (yağlı cilt fotoğrafları)
"""

import argparse
import json
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
from torchvision.models import vit_b_16, ViT_B_16_Weights
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
import seaborn as sns


# ─── Sabitler ────────────────────────────────────────────────────────────────
IMG_SIZE   = 224
MEAN       = [0.485, 0.456, 0.406]
STD        = [0.229, 0.224, 0.225]
NUM_CLASSES = 3
CLASS_NAMES = ["kuru", "normal", "yagli"]   # klasör isimleriyle aynı olmalı
DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─── Argümanlar ───────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="DermaVision ViT-B/16 eğitim scripti")
    p.add_argument("--data_dir",   type=str, default="data",        help="Veri klasörü yolu")
    p.add_argument("--output_dir", type=str, default="models",      help="Model çıktı klasörü")
    p.add_argument("--epochs",     type=int, default=30,            help="Epoch sayısı")
    p.add_argument("--batch_size", type=int, default=32,            help="Batch boyutu")
    p.add_argument("--lr",         type=float, default=1e-4,        help="Öğrenme oranı")
    p.add_argument("--test_ratio", type=float, default=0.2,         help="Test oranı (0-1)")
    p.add_argument("--seed",       type=int, default=42,            help="Rastgelelik tohumu")
    p.add_argument("--freeze_backbone", action="store_true",        help="Backbone'u dondur (sadece head eğit)")
    return p.parse_args()


# ─── Veri Dönüşümleri ─────────────────────────────────────────────────────────
def get_transforms(is_train: bool):
    if is_train:
        return transforms.Compose([
            transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
            transforms.RandomCrop(IMG_SIZE),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
            transforms.RandomRotation(degrees=10),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ])


# ─── Model ────────────────────────────────────────────────────────────────────
def build_model(num_classes: int, freeze_backbone: bool = False) -> nn.Module:
    """ImageNet ön eğitimli ViT-B/16 yükle, classification head'i değiştir."""
    model = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Orijinal head'i 3 sınıflı Linear ile değiştir
    in_features = model.heads.head.in_features
    model.heads.head = nn.Linear(in_features, num_classes)

    return model.to(DEVICE)


# ─── Eğitim / Doğrulama Döngüsü ──────────────────────────────────────────────
def run_epoch(model, loader, criterion, optimizer, is_train: bool):
    model.train() if is_train else model.eval()
    total_loss, correct, total = 0.0, 0, 0

    with torch.set_grad_enabled(is_train):
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            outputs = model(images)
            loss    = criterion(outputs, labels)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            preds      = outputs.argmax(dim=1)
            correct   += (preds == labels).sum().item()
            total     += images.size(0)

    return total_loss / total, correct / total


# ─── Grafik: Eğitim Eğrileri ─────────────────────────────────────────────────
def plot_training_curves(history: dict, output_dir: str):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    epochs = range(1, len(history["train_loss"]) + 1)

    ax1.plot(epochs, history["train_loss"], label="Eğitim", color="#1565C0")
    ax1.plot(epochs, history["val_loss"],   label="Doğrulama", color="#E65100")
    ax1.set_title("Kayıp (Loss)"); ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss")
    ax1.legend(); ax1.grid(alpha=0.3)

    ax2.plot(epochs, history["train_acc"], label="Eğitim", color="#1565C0")
    ax2.plot(epochs, history["val_acc"],   label="Doğrulama", color="#E65100")
    ax2.set_title("Doğruluk (Accuracy)"); ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy")
    ax2.legend(); ax2.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "egitim_egrileri.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → Eğitim eğrileri kaydedildi: {path}")


# ─── Grafik: Karışıklık Matrisi ───────────────────────────────────────────────
def plot_confusion_matrix(y_true, y_pred, class_names, output_dir: str):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names,
                linewidths=0.5, annot_kws={"size": 13, "weight": "bold"}, ax=ax)
    ax.set_xlabel("Tahmin Edilen", fontsize=11)
    ax.set_ylabel("Gerçek", fontsize=11)
    ax.set_title(f"Karışıklık Matrisi (n={len(y_true)})", fontsize=11)
    plt.tight_layout()
    path = os.path.join(output_dir, "karisiklik_matrisi.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → Karışıklık matrisi kaydedildi: {path}")


# ─── Grafik: ROC Eğrileri ─────────────────────────────────────────────────────
def plot_roc_curves(y_true, y_probs, class_names, output_dir: str):
    colors = ["#1565C0", "#2E7D32", "#E65100"]
    plt.figure(figsize=(6, 5))

    for i, (name, color) in enumerate(zip(class_names, colors)):
        y_bin  = (np.array(y_true) == i).astype(int)
        fpr, tpr, _ = roc_curve(y_bin, np.array(y_probs)[:, i])
        auc = roc_auc_score(y_bin, np.array(y_probs)[:, i])
        plt.plot(fpr, tpr, color=color, lw=2, label=f"{name.capitalize()} (AUC={auc:.3f})")

    plt.plot([0, 1], [0, 1], "k--", lw=1)
    plt.xlabel("Yanlış Pozitif Oranı"); plt.ylabel("Doğru Pozitif Oranı")
    plt.title("ROC Eğrileri"); plt.legend(loc="lower right"); plt.grid(alpha=0.3)
    plt.tight_layout()
    path = os.path.join(output_dir, "roc_egrileri.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → ROC eğrileri kaydedildi: {path}")


# ─── Değerlendirme ────────────────────────────────────────────────────────────
@torch.no_grad()
def evaluate(model, loader):
    """Test kümesi üzerinde tüm tahminleri ve olasılıkları topla."""
    model.eval()
    all_labels, all_preds, all_probs = [], [], []

    for images, labels in loader:
        images = images.to(DEVICE)
        outputs = model(images)
        probs   = torch.softmax(outputs, dim=1).cpu().numpy()
        preds   = outputs.argmax(dim=1).cpu().numpy()

        all_labels.extend(labels.numpy())
        all_preds.extend(preds)
        all_probs.extend(probs)

    return all_labels, all_preds, all_probs


# ─── Model Metadasını Kaydet ──────────────────────────────────────────────────
def save_meta(class_to_idx: dict, output_dir: str):
    meta = {
        "arch": "vit_b_16",
        "img_size": IMG_SIZE,
        "normalize_mean": MEAN,
        "normalize_std": STD,
        "class_to_idx": class_to_idx,
        "idx_to_class": {str(v): k for k, v in class_to_idx.items()},
    }
    path = os.path.join(output_dir, "vit_b16_skin_meta.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  → Meta dosyası kaydedildi: {path}")


# ─── Ana Fonksiyon ────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"\n{'='*55}")
    print(f"  DermaVision — ViT-B/16 Eğitim")
    print(f"  Cihaz  : {DEVICE}")
    print(f"  Veri   : {args.data_dir}")
    print(f"  Epoch  : {args.epochs}  |  Batch: {args.batch_size}  |  LR: {args.lr}")
    print(f"{'='*55}\n")

    # ── Veri kümesi ──────────────────────────────────────────────────────────
    full_dataset = datasets.ImageFolder(
        root=args.data_dir,
        transform=get_transforms(is_train=False),   # split sonrası transform atanacak
    )
    class_to_idx = full_dataset.class_to_idx
    print(f"Sınıflar: {class_to_idx}")
    print(f"Toplam görüntü: {len(full_dataset)}")

    test_size  = int(len(full_dataset) * args.test_ratio)
    train_size = len(full_dataset) - test_size
    train_ds, test_ds = random_split(
        full_dataset,
        [train_size, test_size],
        generator=torch.Generator().manual_seed(args.seed),
    )

    # Eğitim kümesine augmentation uygula
    train_ds.dataset = datasets.ImageFolder(
        root=args.data_dir,
        transform=get_transforms(is_train=True),
    )

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=2, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=args.batch_size, shuffle=False, num_workers=2, pin_memory=True)
    print(f"Eğitim: {train_size}  |  Test: {test_size}\n")

    # ── Model ────────────────────────────────────────────────────────────────
    model     = build_model(NUM_CLASSES, freeze_backbone=args.freeze_backbone)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr,
        weight_decay=1e-4,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # ── Eğitim döngüsü ───────────────────────────────────────────────────────
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_acc = 0.0

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()

        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, is_train=True)
        val_loss,   val_acc   = run_epoch(model, test_loader,  criterion, optimizer, is_train=False)
        scheduler.step()

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        elapsed = time.time() - t0
        print(
            f"Epoch {epoch:>2}/{args.epochs} | "
            f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f}  Acc: {val_acc:.4f} | "
            f"{elapsed:.1f}s"
        )

        # En iyi modeli kaydet
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_path = os.path.join(args.output_dir, "vit_b16_skin_state_dict.pth")
            torch.save(model.state_dict(), best_path)
            print(f"  ✓ En iyi model kaydedildi (val_acc={best_val_acc:.4f})")

    # ── Değerlendirme ─────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    print("Test kümesi değerlendirmesi...")
    y_true, y_pred, y_probs = evaluate(model, test_loader)

    print("\nSınıflandırma Raporu:")
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))

    # ── Grafikler ─────────────────────────────────────────────────────────────
    print("Grafikler üretiliyor...")
    plot_training_curves(history, args.output_dir)
    plot_confusion_matrix(y_true, y_pred, CLASS_NAMES, args.output_dir)
    plot_roc_curves(y_true, y_probs, CLASS_NAMES, args.output_dir)

    # ── Meta kaydet ───────────────────────────────────────────────────────────
    save_meta(class_to_idx, args.output_dir)

    print(f"\n{'='*55}")
    print(f"  Eğitim tamamlandı!")
    print(f"  En iyi doğrulama doğruluğu : {best_val_acc:.4f} ({best_val_acc*100:.1f}%)")
    print(f"  Model kaydedildi           : {args.output_dir}/vit_b16_skin_state_dict.pth")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
