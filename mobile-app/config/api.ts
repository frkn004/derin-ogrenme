import { Platform } from 'react-native';

/**
 * API Configuration
 * 
 * Development: localhost/emulator
 * Production: Deploy edilen backend URL'i
 */

// Geliştirme ortamı için API URL'leri
const DEV_API_URL = Platform.select({
  ios: 'http://localhost:8000/api',        // iOS simülatör için
  android: 'http://10.0.2.2:8000/api',     // Android emulator için
  default: 'http://localhost:8000/api',
});

// Production ortamı için API URL
// Backend'i deploy ettikten sonra buraya gerçek URL'i yazın
const PROD_API_URL = 'https://your-backend-url.onrender.com/api';

// Gerçek cihazda test için (aynı WiFi'de)
// Bilgisayarınızın IP adresini öğrenin: ifconfig | grep "inet "
// Örnek: const TEST_API_URL = 'http://192.168.1.100:8000/api';
const TEST_API_URL = DEV_API_URL;

/**
 * Otomatik ortam seçimi
 * __DEV__ : Development modunda mı?
 */
// export const API_URL = __DEV__ ? DEV_API_URL : PROD_API_URL;

/**
 * GERÇEK CİHAZ TESTİ İÇİN:
 * Bilgisayarınızın IP'si ile test yapıyoruz
 * SON GÜNCELLEME: 192.168.1.212
 */
export const API_URL = 'http://192.168.1.212:8000/api';

// API timeout ayarları
export const API_TIMEOUT = 30000; // 30 saniye

// Diğer yapılandırmalar
export const API_CONFIG = {
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
};

console.log('🔗 API URL:', API_URL);

