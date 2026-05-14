# 🚀 DermaVision AI - Lokal Kurulum Rehberi

## ✅ Tamamlanan Adımlar

1. ✅ MongoDB başlatıldı (port 27017)
2. ✅ Backend .env dosyası oluşturuldu
3. ✅ Python virtual environment oluşturuldu
4. ✅ Backend bağımlılıkları kuruluyor

## 📋 Kalan Adımlar

### Backend Çalıştırma

```bash
cd /Users/furkansevinc/dermvision/backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000

### Frontend Kurulumu ve Çalıştırma

```bash
cd /Users/furkansevinc/dermvision/frontend
npm install
# veya
yarn install

# Çalıştırma
npm start
# veya
yarn start
```

Frontend: http://localhost:3000

### MongoDB Kontrol

```bash
# MongoDB durumu
ps aux | grep mongod

# MongoDB durdurma (gerekirse)
mongod --dbpath ~/.mongodb/data --shutdown
```

## 🔧 Yapılandırma

### Backend (.env)
- MongoDB URL: `mongodb://localhost:27017`
- Database: `dermvision_local`
- Backend Port: `8000`

### Frontend
- Backend URL: `http://localhost:8000`
- Port: `3000`

## 📱 Mobil Erişim (Telefon)

Bilgisayar ve telefon aynı WiFi'de olduğunda:

1. Bilgisayarın IP adresini öğren:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. Telefondan eriş:
```
http://[BILGISAYAR_IP]:3000
```

## ⚠️ Sorun Giderme

### MongoDB başlamıyor
```bash
mkdir -p ~/.mongodb/data ~/.mongodb/logs
mongod --dbpath ~/.mongodb/data --logpath ~/.mongodb/logs/mongod.log --fork
```

### Backend hatası
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend hatası
```bash
cd frontend
rm -rf node_modules
npm install
```




