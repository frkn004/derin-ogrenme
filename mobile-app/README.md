# DermaVision — Mobil Uygulama

React Native + Expo ile geliştirilmiş iOS & Android uygulaması.
Kullanıcı yüz fotoğrafı çeker veya yükler; cilt tipini ve kişiselleştirilmiş ürün önerilerini görür.

---

## Kurulum

### Gereksinimler
- Node.js 18+
- npm veya yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS: Xcode 15+ (macOS) veya Expo Go uygulaması
- Android: Android Studio veya Expo Go uygulaması

### Adımlar

```bash
# 1. Bağımlılıkları yükle
cd mobile-app
npm install

# 2. API adresini ayarla
# src/config/api.ts dosyasını aç
# TEST_API_URL → bilgisayarının IP adresini yaz
# Örnek: 'http://192.168.1.XXX:8000/api'

# 3. Uygulamayı başlat
npx expo start

# iOS simülatör için:
npx expo run:ios

# Android emülatör için:
npx expo run:android
```

---

## Klasör Yapısı

```
mobile-app/
├── App.tsx                    # Ana uygulama bileşeni
├── index.ts                   # Giriş noktası
├── app.json                   # Expo konfigürasyonu
├── package.json
├── tsconfig.json
├── assets/                    # İkon, splash screen
├── config/
│   └── api.ts                 # API URL ve endpoint tanımları
└── src/
    ├── config/                # Uygulama ayarları
    ├── services/              # API servis katmanı
    │   ├── AuthService.ts     # Kimlik doğrulama
    │   ├── AnalysisService.ts # Cilt analizi
    │   └── AdminService.ts    # Admin işlemleri
    └── types/                 # TypeScript tip tanımları
```

---

## Ana Ekranlar

| Ekran | Açıklama |
|-------|----------|
| **Kamera** | Yüz fotoğrafı çek veya galeriden yükle |
| **Sonuç** | Cilt tipi, güven skoru ve ürün önerileri |
| **Geçmiş** | Önceki analizler listesi |
| **PDF Raporu** | Kişiselleştirilmiş raporu indir |
| **Paket** | Demo / Standart / Premium kredi satın al |

---

## API Konfigürasyonu

`src/config/api.ts` dosyasında:

```typescript
// Geliştirme: Aynı WiFi'deki bilgisayarın IP'si
const TEST_API_URL = 'http://192.168.1.XXX:8000/api';

// Üretim: Deploy edilmiş backend URL'i
const PROD_API_URL = 'https://your-backend.onrender.com/api';
```

---

## Teknoloji

| Paket | Versiyon | Kullanım |
|-------|----------|----------|
| React Native | 0.81.5 | Temel framework |
| Expo | ~54.0.22 | Geliştirme ortamı |
| TypeScript | ~5.9.2 | Tip güvenliği |
| Axios | — | HTTP istekleri |
| expo-image-picker | — | Kamera / galeri |
| react-native-paper | — | UI bileşenleri |
| @react-navigation | — | Ekran yönetimi |
