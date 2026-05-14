import { Platform } from 'react-native';

/**
 * DermaVision AI - API Configuration
 * Modern, temiz ve type-safe API ayarları
 */

// Development - Lokal test için
const DEV_API_URL = Platform.select({
  ios: 'http://localhost:8000/api',
  android: 'http://10.0.2.2:8000/api',
  default: 'http://localhost:8000/api',
});

// Production - Deploy edilmiş backend
const PROD_API_URL = 'https://your-backend-url.onrender.com/api';

// Gerçek cihaz testi için (aynı WiFi'de)
// Bilgisayarın IP'sini buraya yazın
const TEST_API_URL = 'http://192.168.1.212:8000/api';

/**
 * Aktif API URL
 * __DEV__ = Development mode kontrolü
 */
export const API_URL = __DEV__ ? TEST_API_URL : PROD_API_URL;

/**
 * API Timeout ayarları (millisaniye)
 */
export const API_TIMEOUT = 30000; // 30 saniye

/**
 * Default API Headers
 */
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * API Endpoints
 */
export const ENDPOINTS = {
  // Auth
  REGISTER: '/register',
  LOGIN: '/login',
  ME: '/me',
  
  // Analysis
  ANALYZE_SKIN: '/analyze-skin',
  ANALYSIS_HISTORY: '/analysis-history',
  
  // Dashboard
  DASHBOARD: '/dashboard',
  
  // PDF
  ANALYSIS_PDF: (analysisId: string) => `/analysis/${analysisId}/pdf`,
} as const;

// Console'da hangi API kullanıldığını göster
console.log('🔗 API Configuration:', {
  mode: __DEV__ ? 'Development' : 'Production',
  url: API_URL,
  timeout: `${API_TIMEOUT}ms`,
});

export default {
  API_URL,
  API_TIMEOUT,
  DEFAULT_HEADERS,
  ENDPOINTS,
};

