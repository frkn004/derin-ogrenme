/**
 * DermaVision AI - TypeScript Type Definitions
 * Tüm uygulama için merkezi tip tanımları
 */

// ============================================
// USER TYPES
// ============================================

export type PackageType = 'demo' | 'standard' | 'premium';

export interface User {
  id: string;
  email: string;
  full_name: string;
  package_type: PackageType;
  credits_remaining: number;
  created_at: string;
  last_login?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ============================================
// ANALYSIS TYPES
// ============================================

export type SkinType = 'dry' | 'oily' | 'normal';

export interface SkinProbabilities {
  dry: number;
  oily: number;
  normal: number;
}

export interface ProductRecommendation {
  id: string;
  name: string;
  description: string;
  skin_types: string[];
  category: string;
  brand: string;
  price_range: string;
  ingredients: string[];
  benefits: string[];
  usage_instructions: string;
  personalization_score?: number;
  recommendation_reason?: string;
}

export interface Recommendations {
  description: string;
  products: string[];
  tips: string[];
  product_recommendations?: ProductRecommendation[];
}

export interface AnalysisResult {
  id: string;
  user_id: string;
  skin_type: SkinType;
  confidence: number;
  probabilities: SkinProbabilities;
  recommendations: Recommendations;
  timestamp: string;
  image_data?: string | null;
}

// ============================================
// DASHBOARD TYPES
// ============================================

export interface DashboardStats {
  total_analyses: number;
  credits_remaining: number;
  package_type: PackageType;
  recent_analyses: AnalysisResult[];
}

// ============================================
// API RESPONSE TYPES
// ============================================

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

// ============================================
// NAVIGATION TYPES
// ============================================

export type RootStackParamList = {
  Auth: undefined;
  Dashboard: undefined;
  Camera: undefined;
  Results: { analysis: AnalysisResult };
  History: undefined;
  Profile: undefined;
};

// ============================================
// FORM TYPES
// ============================================

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}


