import axios from 'axios';
import AuthService from './AuthService';
import { API_URL, API_TIMEOUT } from '../config/api';

/**
 * DermaVision AI - Admin Service
 * Ürün yönetimi API işlemleri
 */

export interface ProductRecommendation {
  id?: string;
  name: string;
  description: string;
  skin_types: string[]; // ['dry', 'oily', 'normal', 'combination']
  category: string; // 'cleanser', 'moisturizer', 'serum', 'sunscreen', 'treatment'
  brand?: string;
  price_range?: string;
  ingredients?: string[];
  benefits?: string[];
  usage_instructions?: string;
  active?: boolean;
  created_at?: string;
}

class AdminService {
  /**
   * Get all product recommendations
   */
  async getProducts(): Promise<ProductRecommendation[]> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.get<ProductRecommendation[]>(
        `${API_URL}/admin/recommendations`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          timeout: API_TIMEOUT,
        }
      );

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Create new product
   */
  async createProduct(product: ProductRecommendation): Promise<{ message: string; id: string }> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.post<{ message: string; id: string }>(
        `${API_URL}/admin/recommendations`,
        product,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          timeout: API_TIMEOUT,
        }
      );

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Update product
   */
  async updateProduct(id: string, product: ProductRecommendation): Promise<{ message: string }> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.put<{ message: string }>(
        `${API_URL}/admin/recommendations/${id}`,
        product,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          timeout: API_TIMEOUT,
        }
      );

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Delete product
   */
  async deleteProduct(id: string): Promise<{ message: string }> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.delete<{ message: string }>(
        `${API_URL}/admin/recommendations/${id}`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          timeout: API_TIMEOUT,
        }
      );

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Check if user is admin
   */
  isAdmin(): boolean {
    const user = AuthService.getUser();
    const adminEmails = ['admin@dermavision.ai', 'muratsimsek003@gmail.com', 'frkn@gmail.com'];
    return user && adminEmails.includes(user.email);
  }

  /**
   * Handle API Errors
   */
  private handleError(error: any): Error {
    console.error('Admin API error:', error);

    if (error.response?.status === 403) {
      return new Error('Admin yetkisi gerekli');
    }

    if (error.code === 'ECONNABORTED') {
      return new Error('İşlem zaman aşımına uğradı');
    }

    if (error.message === 'Network Error') {
      return new Error('İnternet bağlantınızı kontrol edin');
    }

    if (error.response?.status === 401) {
      return new Error('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın');
    }

    const message = error.response?.data?.detail || 'İşlem hatası oluştu';
    return new Error(message);
  }
}

export default new AdminService();

