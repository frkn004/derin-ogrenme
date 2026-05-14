# DermaVision AI 🧴

**Yüz fotoğrafından cilt tipi tespiti ve kişiselleştirilmiş cilt bakım ürünü öneri sistemi.**

Kullanıcı yüzünün fotoğrafını yükler → ViT-B/16 modeli cilt tipini (kuru / normal / yağlı) %92,2 doğrulukla sınıflandırır → Kişiselleştirilmiş ürün önerileri sunulur.

---

## Proje Yapısı

```
dermvision/
├── backend/          # FastAPI REST API + ViT-B/16 modeli
├── mobile-app/       # React Native + Expo mobil uygulama (iOS & Android)
├── frontend/         # React web yönetim paneli (admin dashboard)
└── docs/             # Kurulum ve test dokümanları
```

---

## Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| AI Modeli | ViT-B/16 (Vision Transformer), PyTorch 2.8 |
| Backend | FastAPI, MongoDB (Motor async), JWT auth |
| Mobil | React Native 0.81, Expo 54, TypeScript |
| Web Panel | React, Tailwind CSS |
| Ödeme | İyzico (Demo / Standart / Premium) |
| Rapor | ReportLab (PDF oluşturma) |

---

## Hızlı Başlangıç

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle (MongoDB URL, JWT_SECRET vb.)

uvicorn server:app --reload --port 8000
```

API çalıştığında: [http://localhost:8000/docs](http://localhost:8000/docs)

> **Not:** `backend/models/vit_b16_skin_state_dict.pth` model ağırlık dosyası
> (~300 MB) Git'e dahil edilmemiştir. Model dosyasını ayrıca temin edip
> `backend/models/` klasörüne koyun.

### 2. Mobil Uygulama

```bash
cd mobile-app
npm install

# API adresini güncelle
# src/config/api.ts → TEST_API_URL = 'http://<bilgisayar-ip>:8000/api'

npx expo start
```

### 3. Web Yönetim Paneli

```bash
cd frontend
npm install
npm start
```

---

## API Endpoints (Özet)

| Yöntem | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/register` | Kullanıcı kaydı |
| POST | `/api/login` | JWT token alımı |
| POST | `/api/analyze-skin` | Cilt analizi (görüntü yükle) |
| GET | `/api/recommendations/{skin_type}` | Ürün önerileri |
| GET | `/api/analysis/{id}/pdf` | PDF raporu indir |
| POST | `/api/payment/initialize` | İyzico ödeme başlat |

Tüm endpoint'ler için: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Model Bilgisi

- **Mimari:** ViT-B/16 (Vision Transformer Base 16)
- **Sınıflar:** Kuru (0) · Normal (1) · Yağlı (2)
- **Giriş:** 224 × 224 px, ImageNet normalizasyonu
- **Doğruluk:** %92,2 (204 görüntülük test kümesi)
- **AUC:** Kuru 0.952 · Normal 0.945 · Yağlı 0.973

---

## Ürün Öneri Motoru

Sistem B2B mantığıyla çalışır:
- Platforma kayıtlı bir firma kendi ürün kataloğunu eklemişse → firma ürünleri öncelikli önerilir
- Firma kataloğu yoksa → genel marka ürünleri önerilir

Her ürün için kişiselleştirme skoru:

| Bileşen | Katkı |
|---------|-------|
| Cilt tipi uyumu | +30 |
| Model güven skoru | 0–10 |
| Ürün kategorisi önceliği | 5–25 |
| Anahtar kelime eşleşmesi | 0–15 |

---

## Lisans

Bu proje Ostim Teknik Üniversitesi Yapay Zeka Mühendisliği bölümü
Derin Öğrenme dersi kapsamında geliştirilmiştir.

**Geliştirici:** Furkan Sevinç
