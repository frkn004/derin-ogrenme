# DermaVision — Web Yönetim Paneli

DermaVision admin dashboard — firma yönetimi, ürün kataloğu, kullanıcı istatistikleri.

React + Tailwind CSS ile geliştirilmiştir.

---

## Kurulum

```bash
cd frontend
npm install
npm start
```

Uygulama: http://localhost:3000

Backend'in `http://localhost:8000` adresinde çalışıyor olması gerekir.

---

## Klasör Yapısı

```
frontend/src/
├── App.js              # Ana uygulama bileşeni
├── components/         # Yeniden kullanılabilir UI bileşenleri
├── hooks/              # Custom React hook'ları
└── lib/                # Yardımcı fonksiyonlar
```

---

## Build

```bash
npm run build   # Production build → frontend/build/
```

---

## Ortam Değişkenleri

Kök dizinde `.env` dosyası oluşturun:

```env
REACT_APP_API_URL=http://localhost:8000/api
```
