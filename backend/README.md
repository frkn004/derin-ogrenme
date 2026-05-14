# DermaVision — Backend

FastAPI tabanlı REST API. ViT-B/16 derin öğrenme modeli ile cilt tipi sınıflandırması, kişiselleştirilmiş ürün önerisi ve ödeme entegrasyonu içerir.

---

## Kurulum

### Gereksinimler
- Python 3.10+
- MongoDB (yerel veya Atlas)

### Adımlar

```bash
# 1. Sanal ortam oluştur
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını kendi değerlerinizle doldurun

# 4. Model dosyasını yerleştir
# vit_b16_skin_state_dict.pth → backend/models/ klasörüne koyun

# 5. Sunucuyu başlat
uvicorn server:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

---

## Klasör Yapısı

```
backend/
├── server.py                  # Ana FastAPI uygulaması (tüm endpoint'ler)
├── recommendation_engine.py   # Ürün öneri ve puanlama motoru
├── admin_service.py           # Admin işlemleri (kullanıcı yönetimi vb.)
├── iyzico_service.py          # İyzico ödeme entegrasyonu
├── requirements.txt           # Python bağımlılıkları
├── .env.example               # Ortam değişkeni şablonu
├── fonts/                     # PDF oluşturma için fontlar
└── models/
    ├── vit_b16_skin_meta.json  # Model metadata (sınıf isimleri, normalize değerleri)
    └── vit_b16_skin_state_dict.pth  # ← Git'e dahil değil, ayrıca temin edin
```

---

## Ortam Değişkenleri

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `MONGO_URL` | MongoDB bağlantı adresi | `mongodb://localhost:27017` |
| `DB_NAME` | Veritabanı adı | `dermvision` |
| `JWT_SECRET` | JWT imzalama anahtarı | `gizli-anahtar-123` |
| `CORS_ORIGINS` | İzin verilen origin'ler | `http://localhost:3000` |
| `IYZICO_API_KEY` | İyzico API anahtarı | _(boş bırakılabilir)_ |
| `IYZICO_SECRET_KEY` | İyzico gizli anahtar | _(boş bırakılabilir)_ |
| `IYZICO_BASE_URL` | İyzico API URL'i | `https://sandbox-api.iyzipay.com` |

---

## Temel Endpoint'ler

### Kimlik Doğrulama
- `POST /api/register` — Kullanıcı kaydı
- `POST /api/login` — JWT token alımı
- `GET  /api/me` — Profil bilgisi

### Cilt Analizi
- `POST /api/analyze-skin` — Görüntü yükle → cilt tipi + öneriler
- `GET  /api/analysis-history` — Geçmiş analizler
- `GET  /api/analysis/{id}/pdf` — PDF raporu indir

### Ürün Önerileri
- `GET  /api/recommendations/{skin_type}` — Cilt tipine göre ürünler
- `POST /api/recommendations/{id}/interact` — Etkileşim kaydı

### Ödeme
- `POST /api/payment/initialize` — İyzico ödeme başlat
- `POST /api/upgrade-package/{type}` — Paket yükselt (demo/standard/premium)

### Admin
- `GET  /api/admin/dashboard` — Sistem istatistikleri
- `GET  /api/admin/users` — Kullanıcı listesi
- `POST /api/admin/recommendations` — Ürün ekle

---

## Model Detayları

```json
{
  "model_name": "vit_b_16",
  "img_size": 224,
  "classes": { "0": "dry", "1": "normal", "2": "oily" },
  "normalize_mean": [0.485, 0.456, 0.406],
  "normalize_std":  [0.229, 0.224, 0.225]
}
```

Classification head: `Linear(in_features=768, out_features=3)`
