# 🛠️ Test Ürünleri Ekleme Rehberi

## Admin Giriş Bilgileri
```
Email: muratsimsek003@gmail.com
Şifre: (mevcut şifreniz)
```

## Backend'e Test Ürünleri Ekleme

### Python Script ile Ürün Ekleme:

```python
import requests

API_URL = "http://192.168.1.212:8000/api"

# 1. Admin login
login_response = requests.post(
    f"{API_URL}/login",
    json={
        "email": "muratsimsek003@gmail.com",
        "password": "123456"  # Şifrenizi buraya yazın
    }
)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Örnek ürünler
products = [
    {
        "name": "Hyaluronik Asit Serum",
        "description": "Derinlemesine nemlendirme sağlayan yoğun serum",
        "skin_types": ["dry", "normal"],
        "category": "serum",
        "brand": "DermaVision",
        "price_range": "200-400 TL",
        "benefits": ["Nemlendirme", "Anti-aging", "Cilt barrier"]
    },
    {
        "name": "Niacinamide %10 Serum",
        "description": "Gözenek görünümünü azaltan ve sebum kontrolü sağlayan serum",
        "skin_types": ["oily", "combination"],
        "category": "serum",
        "brand": "DermaVision",
        "price_range": "150-300 TL",
        "benefits": ["Sebum kontrolü", "Gözenek bakımı", "Ton eşitliği"]
    },
    {
        "name": "Gentle Cleanser",
        "description": "Hassas ciltler için yatıştırıcı temizleyici",
        "skin_types": ["dry", "normal", "sensitive"],
        "category": "cleanser",
        "brand": "CeraVe",
        "price_range": "100-200 TL",
        "benefits": ["Nazik temizlik", "Yatıştırıcı", "Barrier koruma"]
    },
    {
        "name": "SPF 50+ Sunscreen",
        "description": "Geniş spektrumlu güneş koruyucu krem",
        "skin_types": ["dry", "oily", "normal", "combination"],
        "category": "sunscreen",
        "brand": "La Roche-Posay",
        "price_range": "250-350 TL",
        "benefits": ["UV koruma", "Su geçirmez", "Mattifying"]
    },
    {
        "name": "Ceramide Moisturizer",
        "description": "Cilt bariyerini güçlendiren nemlendirici",
        "skin_types": ["dry", "normal"],
        "category": "moisturizer",
        "brand": "CeraVe",
        "price_range": "180-280 TL",
        "benefits": ["Barrier onarımı", "24 saat nemlendirme", "Hipoalerjenik"]
    }
]

# 3. Ürünleri ekle
for product in products:
    response = requests.post(
        f"{API_URL}/admin/recommendations",
        json=product,
        headers=headers
    )
    print(f"✅ {product['name']} eklendi: {response.json()}")
```

## VEYA Terminal ile Curl:

### 1. Login
```bash
TOKEN=$(curl -s -X POST "http://192.168.1.212:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"muratsimsek003@gmail.com","password":"123456"}' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Ürün Ekle
```bash
curl -X POST "http://192.168.1.212:8000/api/admin/recommendations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hyaluronik Asit Serum",
    "description": "Derinlemesine nemlendirme sağlayan yoğun serum",
    "skin_types": ["dry", "normal"],
    "category": "serum",
    "brand": "DermaVision",
    "price_range": "200-400 TL"
  }'
```

---

## Mobile App'te Admin Panel Kullanımı

### 1. Admin Girişi
```
1. Uygulamayı aç
2. Email: muratsimsek003@gmail.com
3. Şifre: (şifreniz)
4. "Giriş Yap"
```

### 2. Admin Panel'e Erişim
```
Dashboard'da sağ üstte:
[⚙️] [📊 Geçmiş] [Çıkış]

⚙️ → Admin Panel
```

### 3. Admin Panel Özellikleri
- ✅ Tüm ürünleri listele
- ✅ Ürün detaylarını gör (isim, marka, açıklama)
- ✅ Cilt tipi tag'lerini gör
- ✅ Kategori görüntüle
- ✅ Fiyat aralığı
- ✅ Ürün silme (🗑️ butonu)

---

## Admin Panel Ekran Yapısı

```
┌─────────────────────────────────────┐
│ ← Geri    ⚙️ Ürün Yönetimi          │
├─────────────────────────────────────┤
│                                     │
│ ┌───────────────────────────────┐  │
│ │ Hyaluronik Asit Serum    🗑️   │  │
│ │ DermaVision                    │  │
│ │ Derinlemesine nemlendirme...   │  │
│ │ [dry] [normal] [serum]         │  │
│ │ 💰 200-400 TL                  │  │
│ └───────────────────────────────┘  │
│                                     │
│ ┌───────────────────────────────┐  │
│ │ Niacinamide %10 Serum     🗑️  │  │
│ │ DermaVision                    │  │
│ │ Gözenek görünümünü azaltan...  │  │
│ │ [oily] [combination] [serum]   │  │
│ │ 💰 150-300 TL                  │  │
│ └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 Sonraki Adımlar (Opsiyonel)

1. **Ürün Ekleme Formu:** Mobile app'te ürün ekleme ekranı
2. **Ürün Düzenleme:** Mevcut ürünleri düzenleme
3. **Toplu İşlemler:** Birden fazla ürünü seçip silme
4. **Arama/Filtreleme:** Cilt tipine göre filtreleme
5. **Stok Takibi:** Ürün stok durumu
6. **İstatistikler:** Hangi ürün ne kadar önerilmiş

---

**NOT:** Şu an için Admin Panel sadece **görüntüleme ve silme** yapabiliyor.
Ürün ekleme backend üzerinden (Python script veya Postman) yapılıyor.

Mobil app'te ürün ekleme formu istiyor musunuz? 🤔


