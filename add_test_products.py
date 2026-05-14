#!/usr/bin/env python3
import requests
import json

API_URL = "http://192.168.1.212:8000/api"

# Admin credentials
EMAIL = "muratsimsek003@gmail.com"
PASSWORD = "123456"  # Değiştirin!

# Login
print("🔐 Admin girişi yapılıyor...")
login_response = requests.post(
    f"{API_URL}/login",
    json={"email": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login hatası: {login_response.json()}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print(f"✅ Giriş başarılı! Token alındı.")

# Test products
products = [
    {
        "name": "Hyaluronik Asit Serum",
        "description": "Derinlemesine nemlendirme sağlayan yoğun serum. Cildin nem tutma kapasitesini artırır.",
        "skin_types": ["dry", "normal"],
        "category": "serum",
        "brand": "DermaVision Pro",
        "price_range": "200-400 TL",
        "ingredients": ["Hyaluronic Acid", "Vitamin B5", "Glycerin"],
        "benefits": ["Yoğun nemlendirme", "Anti-aging", "Cilt barrier güçlendirme"]
    },
    {
        "name": "Niacinamide %10 Serum",
        "description": "Gözenek görünümünü azaltan ve sebum kontrolü sağlayan güçlü serum.",
        "skin_types": ["oily", "combination"],
        "category": "serum",
        "brand": "The Ordinary",
        "price_range": "150-300 TL",
        "ingredients": ["Niacinamide 10%", "Zinc 1%"],
        "benefits": ["Sebum kontrolü", "Gözenek bakımı", "Ton eşitliği", "Akne izleri"]
    },
    {
        "name": "Gentle Cleanser",
        "description": "Hassas ciltler için yatıştırıcı, köpüksüz temizleyici. Doğal yağları korur.",
        "skin_types": ["dry", "normal", "sensitive"],
        "category": "cleanser",
        "brand": "CeraVe",
        "price_range": "100-200 TL",
        "ingredients": ["Ceramides", "Hyaluronic Acid", "Glycerin"],
        "benefits": ["Nazik temizlik", "Yatıştırıcı", "Barrier koruma", "Hipoalerjenik"]
    },
    {
        "name": "SPF 50+ Sunscreen",
        "description": "Geniş spektrumlu güneş koruyucu krem. UVA ve UVB filtreli, su geçirmez formül.",
        "skin_types": ["dry", "oily", "normal", "combination"],
        "category": "sunscreen",
        "brand": "La Roche-Posay",
        "price_range": "250-350 TL",
        "ingredients": ["Mexoryl XL", "Titanium Dioxide", "Thermal Water"],
        "benefits": ["UV koruma", "Su geçirmez", "Mattifying", "Beyaz iz bırakmaz"]
    },
    {
        "name": "Ceramide Moisturizer",
        "description": "Cilt bariyerini güçlendiren zengin nemlendirici. 24 saat nem kilidi.",
        "skin_types": ["dry", "normal"],
        "category": "moisturizer",
        "brand": "CeraVe",
        "price_range": "180-280 TL",
        "ingredients": ["Ceramides 1,3,6", "Hyaluronic Acid", "MVE Technology"],
        "benefits": ["Barrier onarımı", "24 saat nemlendirme", "Hipoalerjenik", "Kokusuz"]
    },
    {
        "name": "Salicylic Acid Exfoliant",
        "description": "Gözenek içine nüfuz eden BHA exfoliant. Ölü deriyi nazikçe temizler.",
        "skin_types": ["oily", "combination"],
        "category": "treatment",
        "brand": "Paula's Choice",
        "price_range": "220-320 TL",
        "ingredients": ["Salicylic Acid 2%", "Green Tea Extract"],
        "benefits": ["Gözenek temizliği", "Akne önleme", "Pürüzsüz doku", "Mat görünüm"]
    }
]

# Add products
print(f"\n📦 {len(products)} ürün ekleniyor...\n")
for i, product in enumerate(products, 1):
    try:
        response = requests.post(
            f"{API_URL}/admin/recommendations",
            json=product,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {i}. {product['name']} eklendi (ID: {result.get('id')})")
        else:
            print(f"❌ {i}. {product['name']} eklenemedi: {response.json()}")
    except Exception as e:
        print(f"❌ {i}. {product['name']} hata: {str(e)}")

print(f"\n🎉 İşlem tamamlandı!")
print(f"📱 Mobile app'te Admin Panel'den ürünleri görebilirsiniz.")


