# ⚡ DermaVision Pro - Hızlı Test Rehberi

## ✅ SİSTEM DURUMU

```
🟢 Backend API:        http://192.168.1.212:8000
🟢 MongoDB:            Çalışıyor
🟢 iOS Simülatör:      Açık
🟢 DermaVision Pro:    Yüklendi ve çalışıyor
🟢 Model:              ViT-B/16 Skin yüklü
```

---

## 🚀 HIZLI TEST ADIMLARI

### 1️⃣ KAYIT OL (1 dakika)

**iOS Simülatörde:**
1. Uygulamayı aç (zaten açık olmalı)
2. "Hesap Oluşturun" linkine tıkla
3. Bilgileri gir:
   - **Ad:** Test Kullanıcı  
   - **Email:** test001@dermvision.com
   - **Şifre:** test123
4. "Kayıt Ol" butonuna bas
5. ✅ "Başarılı" mesajı görmeli
6. ✅ Dashboard ekranı açılmalı

---

### 2️⃣ FOTOĞRAF SEÇ (30 saniye)

**Dashboard'da:**
1. "📷 Galeri" butonuna tıkla
2. Galeri izni iste (Allow)
3. Herhangi bir fotoğraf seç
4. ✅ Fotoğraf önizlemesi görünmeli

---

### 3️⃣ CİLT ANALİZİ YAP (5 saniye)

**Fotoğraf seçildikten sonra:**
1. "🔍 Analiz Et" butonuna bas
2. Loading göster
3. 2-5 saniye bekle
4. ✅ Sonuç kartı görünmeli:
   - Cilt tipi (Kuru/Yağlı/Normal)
   - Güven oranı (%)
   - Açıklama
   - 3 ürün önerisi

---

### 4️⃣ TOKEN PERSİSTENCE (30 saniye)

**KRİTİK TEST!**
1. iOS simülatörde **CMD+Shift+H** (Home)
2. Uygulamayı yukarı kaydır ve **KAPAT**
3. Simülatörden **DermaVision Pro**'yu tekrar aç
4. ✅ **OTOMATIK GİRİŞ YAPMALI**
5. ❌ Login ekranı göstermemeli

---

### 5️⃣ ÇIKIŞ VE TEKRsR GİRİŞ (1 dakika)

**Dashboard'da:**
1. "Çıkış" butonuna bas
2. Login ekranına dön
3. Giriş yap:
   - **Email:** test001@dermvision.com
   - **Şifre:** test123
4. "Giriş Yap" butonuna bas
5. ✅ Dashboard açılmalı

---

## 🔧 SORUN GİDERME

### Backend Çalışmıyor mu?
```bash
cd /Users/furkansevinc/dermvision/backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### IP Adresi Değişti mi?
```bash
# Yeni IP'yi bul:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Config'i güncelle:
# mobile-app/config/api.ts dosyasında:
export const API_URL = 'http://YENİ_IP:8000/api';

# Uygulamayı yeniden başlat
```

### Uygulama Crash Oluyor mu?
```bash
# Metro bundler'ı yeniden başlat:
cd /Users/furkansevinc/dermvision/mobile-app
npx expo start --clear
```

### Simülatör Dondu mu?
```bash
# Simülatörü resetle:
xcrun simctl erase all
# Uygulamayı yeniden yükle:
npx expo run:ios
```

---

## 📊 BAŞARI KRİTERLERİ

| Özellik | Durum | Beklenen Süre |
|---------|-------|---------------|
| Kayıt | ⏳ | <3 saniye |
| Giriş | ⏳ | <2 saniye |
| Analiz | ⏳ | 2-5 saniye |
| Token Persistence | ⏳ | Anında |
| Çıkış | ⏳ | Anında |

---

## 🎯 TEST SONUCU

### ✅ PASSED
- [ ] Kayıt başarılı
- [ ] Giriş başarılı
- [ ] Fotoğraf seçimi çalışıyor
- [ ] Analiz sonuç veriyor
- [ ] Token persistence çalışıyor
- [ ] UI şık ve kullanışlı

### ❌ FAILED
- [ ] 
- [ ] 
- [ ] 

### 📝 NOTLAR
- 
- 
- 

---

**Testi tamamladığında bu dosyayı güncelle!** 
**Detaylı test için: `KAPSAMLI_TEST_PLANI.md`**


