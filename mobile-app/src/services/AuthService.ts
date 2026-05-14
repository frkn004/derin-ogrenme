import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { API_URL, API_TIMEOUT, ENDPOINTS } from '../config/api';
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types';

/**
 * DermaVision AI - Authentication Service
 * Modern, type-safe authentication yönetimi
 */

// AsyncStorage keys
const STORAGE_KEYS = {
  TOKEN: '@dermavision_token',
  USER: '@dermavision_user',
} as const;

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  /**
   * Initialize - Uygulama açılışında çağrılır
   */
  async initialize(): Promise<boolean> {
    try {
      const token = await this.getStoredToken();
      const user = await this.getStoredUser();
      
      if (token && user) {
        this.token = token;
        this.user = user;
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Auth initialization error:', error);
      return false;
    }
  }

  /**
   * Register - Yeni kullanıcı kaydı
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(
        `${API_URL}${ENDPOINTS.REGISTER}`,
        data,
        { timeout: API_TIMEOUT }
      );

      await this.saveAuth(response.data);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Login - Kullanıcı girişi
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(
        `${API_URL}${ENDPOINTS.LOGIN}`,
        data,
        { timeout: API_TIMEOUT }
      );

      await this.saveAuth(response.data);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Logout - Çıkış yap
   */
  async logout(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([STORAGE_KEYS.TOKEN, STORAGE_KEYS.USER]);
      this.token = null;
      this.user = null;
    } catch (error) {
      console.error('Logout error:', error);
      throw new Error('Çıkış yaparken hata oluştu');
    }
  }

  /**
   * Get Current Token
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Get Current User
   */
  getUser(): User | null {
    return this.user;
  }

  /**
   * Is Authenticated
   */
  isAuthenticated(): boolean {
    return !!this.token && !!this.user;
  }

  /**
   * Save Authentication Data
   */
  private async saveAuth(authResponse: AuthResponse): Promise<void> {
    try {
      this.token = authResponse.access_token;
      this.user = authResponse.user;

      await AsyncStorage.setItem(STORAGE_KEYS.TOKEN, authResponse.access_token);
      await AsyncStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(authResponse.user));
    } catch (error) {
      console.error('Save auth error:', error);
      throw new Error('Kimlik doğrulama verileri kaydedilemedi');
    }
  }

  /**
   * Get Stored Token
   */
  private async getStoredToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(STORAGE_KEYS.TOKEN);
    } catch (error) {
      console.error('Get token error:', error);
      return null;
    }
  }

  /**
   * Get Stored User
   */
  private async getStoredUser(): Promise<User | null> {
    try {
      const userJson = await AsyncStorage.getItem(STORAGE_KEYS.USER);
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      console.error('Get user error:', error);
      return null;
    }
  }

  /**
   * Handle API Errors
   */
  private handleError(error: any): Error {
    console.error('Auth API error:', error);

    if (error.code === 'ECONNABORTED') {
      return new Error('Bağlantı zaman aşımına uğradı. Lütfen tekrar deneyin.');
    }

    if (error.message === 'Network Error') {
      return new Error('Sunucuya bağlanılamıyor. İnternet bağlantınızı kontrol edin.');
    }

    const message = error.response?.data?.detail || 'Bir hata oluştu. Lütfen tekrar deneyin.';
    return new Error(message);
  }
}

// Singleton instance
export default new AuthService();


