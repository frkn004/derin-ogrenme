# 🧪 DermaVision Pro - Kapsamlı Test Planı

## 📱 UYGULAMA BİLGİLERİ
- **Uygulama Adı:** DermaVision Pro 💎
- **Versiyon:** 1.0.0
- **Platform:** iOS (Expo)
- **Backend:** http://172.20.10.3:8000

---

## ✅ TEST 1: BAŞLANGIÇ VE YÜ KLEME

### Kontroller:
- [ ] Uygulama simülatörde açıldı mı?
- [ ] Loading ekranı "DermaVision Pro" yazıyor mu?
- [ ] Splash screen göründü mü?
- [ ] Login ekranına geçiş yaptı mı?

### Beklenen Sonuç:
✅ Uygulama sorunsuz açılmalı ve login ekranı görünmeli

---

## ✅ TEST 2: LOGIN/REGISTER EKR ANI

### Test 2.1: Validasyon
- [ ] Boş form gönderilmeye çalışılınca hata veriyor mu?
- [ ] Email formatı kontrolü var mı?
- [ ] Şifre alanı gizli mi?

### Test 2.2: Kayıt Ol
**Adımlar:**
1. "Hesap Oluşturun" linkine tıkla
2. Ad Soyad: `Test User Pro`
3. Email: `testpro@dermvision.com`
4. Şifre: `123456`
5. "Kayıt Ol" butonuna bas

**Beklenen:**
- ✅ "Başarılı" mesajı
- ✅ Dashboard'a geçiş
- ✅ Backend'e kayıt edildi

### Test 2.3: Çıkış
1. "Çıkış" butonuna bas
2. Login ekranına dönüldü mü?

### Test 2.4: Tekrar Giriş
1. Email: `testpro@dermvision.com`
2. Şifre: `123456`
3. "Giriş Yap" butonuna bas

**Beklenen:**
- ✅ Başarılı giriş
- ✅ Dashboard görünmeli

---

## ✅ TEST 3: TOKEN PERSISTENCE (ÖNEMLİ!)

### Adımlar:
1. Uygulamada giriş yapılmış durumda ol
2. iOS simülatörde **CMD+Shift+H** (Home'a dön)
3. Uygulamayı yukarı kaydırıp **KAPAT**
4. Simülatörden **DermaVision Pro**'yu tekrar aç

### Beklenen Sonuç:
✅ **OTOMATIK GİRİŞ YAPMALI!**
❌ Login ekranı göstermemeli!

**Bu test çok önemli!** Token persistence çalışıyor mu?

---

## ✅ TEST 4: DASHBOARD EKRANI

### Kontroller:
- [ ] "Merhaba 👋" mesajı görünüyor mu?
- [ ] "Cilt Analizi" başlığı var mı?
- [ ] "Çıkış" butonu çalışıyor mu?
- [ ] Card tasarımı şık görünüyor mu?

---

## ✅ TEST 5: FOTOĞRAF SEÇİMİ

### Test 5.1: Galeri İzni
1. "Galeri" butonuna bas
2. İzin popup'ı çıktı mı?
3. "Allow" seçeneğine bas

### Test 5.2: Fotoğraf Seçme
1. Simülatör fotoğraf galerisinden bir fotoğraf seç
2. Fotoğraf önizlemesi göründü mü?
3. Fotoğraf tam ekran gösteriliyor mu?

---

## ✅ TEST 6: CİLT ANALİZİ (EN ÖNEMLİ!)

### Adımlar:
1. Galeriden bir yüz fotoğrafı seç
2. "🔍 Analiz Et" butonuna bas
3. Loading indicator göründü mü?

### Backend Testi:
```bash
# Terminal'de kontrol:
tail -f /Users/furkansevinc/dermvision/backend/backend.log | grep "analyze-skin"
```

### Beklenen Sonuç:
✅ 2-5 saniye içinde sonuç gelmeli
✅ "Başarılı" alert'i görmeli
✅ Sonuç kartı görünmeli

### Kontroller:
- [ ] Cilt tipi gösterildi mi? (Kuru/Yağlı/Normal)
- [ ] Güven oranı (%) gösterildi mi?
- [ ] Açıklama metni var mı?
- [ ] Ürün önerileri listelendi mi? (3 adet)

---

## ✅ TEST 7: SONUÇ KARTI

### Görsel Kontroller:
- [ ] Başlık: "✨ Sonuçlar"
- [ ] Badge tasarımı şık mı?
- [ ] Güven oranı büyük ve net mi?
- [ ] Açıklama okunabilir mi?
- [ ] Ürün önerileri madde madde mi?

### İçerik Kontrolleri:
- [ ] Cilt tipi Türkçe mi? (İngilizce değil!)
- [ ] Öneriler mantıklı mı?
- [ ] Typography okunaklı mı?

---

## ✅ TEST 8: HATA YÖNETİMİ

### Test 8.1: Network Hatası
1. Backend'i durdur:
```bash
pkill -f "uvicorn server:app"
```
2. Analiz yapmayı dene

**Beklenen:**
❌ "İnternet bağlantınızı kontrol edin" mesajı

3. Backend'i tekrar başlat:
```bash
cd backend && source venv/bin/activate && uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
```

### Test 8.2: Geçersiz Token
1. 7 gün geç simülasyonu (manuel token silme)
2. Analiz yapmayı dene

**Beklenen:**
❌ "Oturum süreniz dolmuş" mesajı
✅ Otomatik logout

---

## ✅ TEST 9: UI/UX KALİTESİ

### Tasarım Kontrolleri:
- [ ] Gradient renkler güzel mi?
- [ ] Kartlar gölge efekti var mı?
- [ ] Buttonlar hover/press efekti var mı?
- [ ] Spacing ve padding düzgün mü?
- [ ] Typography hiyerarşisi net mi?
- [ ] Renkler uyumlu mu?

### Animasyon Kontrolleri:
- [ ] Loading animasyonları smooth mu?
- [ ] Ekran geçişleri akıcı mı?
- [ ] Button press feedback var mı?

---

## ✅ TEST 10: PERFORMANS

### Kontroller:
- [ ] Uygulama açılışı hızlı mı? (<3 saniye)
- [ ] Analiz süresi makul mü? (2-5 saniye)
- [ ] Scroll performansı iyi mi?
- [ ] Memory leak var mı? (uygulama uzun süre açık kalınca)

---

## ✅ TEST 11: ÇOKLU KULLANICI SENARYOsu

### Senaryo:
1. Kullanıcı A kayıt ol
2. Analiz yap
3. Çıkış yap
4. Kullanıcı B kayıt ol
5. Analiz yap
6. İki kullanıcının verileri karışmadı mı?

---

## ✅ TEST 12: EDGE CASES

### Test 12.1: Çok Büyük Fotoğraf
- [ ] 10MB+ fotoğraf seçince ne oluyor?
- [ ] Timeout hatası var mı?

### Test 12.2: Çok Küçük Fotoğraf
- [ ] 50x50px fotoğraf ile test
- [ ] Model hata veriyor mu?

### Test 12.3: Yüz Olmayan Fotoğraf
- [ ] Manzara fotoğrafı ile test
- [ ] Anlamlı hata mesajı var mı?

---

## 📊 TEST SONUÇ TABLOSU

| Test No | Test Adı | Durum | Notlar |
|---------|----------|-------|--------|
| 1 | Başlangıç | ⏳ | |
| 2 | Login/Register | ⏳ | |
| 3 | Token Persistence | ⏳ | EN ÖNEMLİ! |
| 4 | Dashboard | ⏳ | |
| 5 | Fotoğraf Seçimi | ⏳ | |
| 6 | Cilt Analizi | ⏳ | EN ÖNEMLİ! |
| 7 | Sonuç Kartı | ⏳ | |
| 8 | Hata Yönetimi | ⏳ | |
| 9 | UI/UX | ⏳ | |
| 10 | Performans | ⏳ | |
| 11 | Çoklu Kullanıcı | ⏳ | |
| 12 | Edge Cases | ⏳ | |

---

## 🎯 KRİTİK BAŞARI KRİTERLERİ

Uygulamanın MVP olarak kabul edilmesi için:

1. ✅ **Token Persistence:** Uygulama kapanıp açılınca otomatik giriş
2. ✅ **Cilt Analizi:** 2-5 saniyede başarılı sonuç
3. ✅ **Hata Yönetimi:** Tüm hata durumları handle edilmiş
4. ✅ **UI/UX:** Profesyonel ve şık görünüm
5. ✅ **Performans:** Smooth ve hızlı

---

## 📝 TEST NOTLARI

### Test Eden: 
### Tarih: 
### Cihaz: iOS Simülatör
### Backend: http://172.20.10.3:8000

### Genel Değerlendirme:
- [ ] Tüm testler passed
- [ ] Minor buglar var ama kullanılabilir
- [ ] Major buglar var, düzeltme gerekli

### Bulunan Buglar:
1. 
2. 
3. 

### Öneriler:
1. 
2. 
3. 

---

**Test tamamlandığında bu dosyayı güncelleyin!** ✅


