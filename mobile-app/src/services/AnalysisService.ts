import axios from 'axios';
import AuthService from './AuthService';
import { API_URL, API_TIMEOUT, ENDPOINTS } from '../config/api';
import type { AnalysisResult, DashboardStats } from '../types';

/**
 * DermaVision AI - Analysis Service
 * Cilt analizi API işlemleri
 */

class AnalysisService {
  /**
   * Analyze Skin - Fotoğrafı analiz et
   */
  async analyzeSkin(imageUri: string): Promise<AnalysisResult> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      // FormData oluştur
      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      } as any);

      const response = await axios.post<AnalysisResult>(
        `${API_URL}${ENDPOINTS.ANALYZE_SKIN}`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          timeout: API_TIMEOUT,
        }
      );

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  /**
   * Get Analysis History
   */
  async getHistory(): Promise<AnalysisResult[]> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.get<AnalysisResult[]>(
        `${API_URL}${ENDPOINTS.ANALYSIS_HISTORY}`,
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
   * Get Dashboard Stats
   */
  async getDashboard(): Promise<DashboardStats> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error('Lütfen önce giriş yapın');
      }

      const response = await axios.get<DashboardStats>(
        `${API_URL}${ENDPOINTS.DASHBOARD}`,
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
   * Handle API Errors
   */
  private handleError(error: any): Error {
    console.error('Analysis API error:', error);

    if (error.code === 'ECONNABORTED') {
      return new Error('İşlem zaman aşımına uğradı');
    }

    if (error.message === 'Network Error') {
      return new Error('İnternet bağlantınızı kontrol edin');
    }

    if (error.response?.status === 401) {
      return new Error('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın');
    }

    const message = error.response?.data?.detail || 'Analiz hatası oluştu';
    return new Error(message);
  }
}

export default new AnalysisService();


