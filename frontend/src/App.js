import React, { useState, useEffect, useRef } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast, Toaster } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = (tokenData) => {
    setToken(tokenData.access_token);
    setUser(tokenData.user);
    localStorage.setItem('token', tokenData.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => React.useContext(AuthContext);

// Auth Components
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: ''
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? '/login' : '/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      login(response.data);
      toast.success(isLogin ? 'Başarıyla giriş yapıldı!' : 'Kayıt başarılı!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12 lg:py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
          
          {/* Left Side - Information */}
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
                <h1 className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  DermaVision AI
                </h1>
              </div>
              
              <h2 className="text-2xl lg:text-3xl font-semibold text-slate-800 leading-tight">
                Yapay Zeka ile Profesyonel Cilt Analizi
              </h2>
              
              <p className="text-lg text-slate-600 leading-relaxed">
                Gelişmiş Vision Transformer teknolojisi ile cildinizi analiz edin. 
                Kişiselleştirilmiş bakım önerileri alın ve cilt sağlığınızı takip edin.
              </p>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start gap-3 p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-blue-100">
                <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">AI Teknolojisi</h3>
                  <p className="text-sm text-slate-600">%95 doğruluk oranında cilt tipi analizi</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-emerald-100">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Kişisel Bakım</h3>
                  <p className="text-sm text-slate-600">Size özel ürün önerileri</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-purple-100">
                <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">PDF Rapor</h3>
                  <p className="text-sm text-slate-600">Detaylı analiz raporları</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 rounded-xl bg-white/60 backdrop-blur-sm border border-orange-100">
                <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Güvenli & Hızlı</h3>
                  <p className="text-sm text-slate-600">Saniyeler içinde sonuç</p>
                </div>
              </div>
            </div>

            {/* Pricing Preview */}
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-200">
              <h3 className="font-semibold text-slate-800 mb-3">Paketlerimiz</h3>
              <div className="flex items-center justify-between">
                <div className="text-center">
                  <p className="text-2xl font-bold text-slate-800">Demo</p>
                  <p className="text-sm text-slate-600">5 Analiz</p>
                  <p className="text-lg font-semibold text-green-600">Ücretsiz</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-slate-800">Standart</p>
                  <p className="text-sm text-slate-600">300 Analiz</p>
                  <p className="text-lg font-semibold text-blue-600">₺300/ay</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-slate-800">Premium</p>
                  <p className="text-sm text-slate-600">1000 Analiz</p>
                  <p className="text-lg font-semibold text-purple-600">₺1000/ay</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Auth Form */}
          <div className="flex justify-center lg:justify-end">
            <Card className="w-full max-w-md border-0 shadow-2xl bg-white/80 backdrop-blur-lg">
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-2xl text-slate-800 mb-2">
                  {isLogin ? 'Giriş Yapın' : 'Ücretsiz Başlayın'}
                </CardTitle>
                <CardDescription className="text-slate-600">
                  {isLogin 
                    ? 'Hesabınıza giriş yaparak analizlerinize devam edin' 
                    : 'Hemen ücretsiz hesap oluşturun ve ilk analizinizi yapın'
                  }
                </CardDescription>
              </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div className="space-y-2">
                <Label htmlFor="full_name">Ad Soyad</Label>
                <Input
                  id="full_name"
                  type="text"
                  placeholder="Adınızı girin"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required={!isLogin}
                />
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">E-posta</Label>
              <Input
                id="email"
                type="email"
                placeholder="E-posta adresinizi girin"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Şifre</Label>
              <Input
                id="password"
                type="password"
                placeholder="Şifrenizi girin"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full h-12 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
              disabled={loading}
              data-testid={isLogin ? "login-button" : "register-button"}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  İşleniyor...
                </div>
              ) : (
                isLogin ? 'Giriş Yap' : 'Kayıt Ol'
              )}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              {isLogin 
                ? 'Hesabınız yok mu? Kayıt olun' 
                : 'Zaten hesabınız var mı? Giriş yapın'
              }
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/dashboard`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setStats(response.data);
      } catch (error) {
        toast.error('Dashboard verileri alınırken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const getPackageColor = (packageType) => {
    switch (packageType) {
      case 'demo': return 'bg-gray-100 text-gray-800';
      case 'standard': return 'bg-blue-100 text-blue-800';
      case 'premium': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPackageLabel = (packageType) => {
    switch (packageType) {
      case 'demo': return 'Demo Paket';
      case 'standard': return 'Standart Paket';
      case 'premium': return 'Premium Paket';
      default: return packageType;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white/70 backdrop-blur-sm border-b shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">DermaVision AI</h1>
              <p className="text-sm text-slate-600">Hoşgeldin, {user?.full_name}</p>
            </div>
          </div>
          <Button 
            variant="outline" 
            onClick={logout}
            data-testid="logout-button"
          >
            Çıkış Yap
          </Button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Kalan Kredi</p>
                  <p className="text-2xl font-bold text-slate-900" data-testid="credits-remaining">
                    {stats?.credits_remaining || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Aktif Paket</p>
                  <Badge className={`mt-1 ${getPackageColor(stats?.package_type)}`}>
                    {getPackageLabel(stats?.package_type)}
                  </Badge>
                </div>
                <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Toplam Analiz</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {stats?.total_analyses || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="analyze" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="analyze">Cilt Analizi</TabsTrigger>
            <TabsTrigger value="history">Analiz Geçmişi</TabsTrigger>
            <TabsTrigger value="packages">Paketler</TabsTrigger>
          </TabsList>
          
          <TabsContent value="analyze" className="mt-6">
            <SkinAnalyzer />
          </TabsContent>
          
          <TabsContent value="history" className="mt-6">
            <AnalysisHistory />
          </TabsContent>
          
          <TabsContent value="packages" className="mt-6">
            <PackageManager />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Skin Analyzer Component
const SkinAnalyzer = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
        
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
        
        setAnalysisResult(null);
      } else {
        toast.error('Lütfen sadece resim dosyaları yükleyin.');
      }
    }
  };

  const analyzeSkin = async () => {
    if (!selectedImage) {
      toast.error('Lütfen önce bir resim yükleyin.');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedImage);

      const response = await axios.post(`${API}/analyze-skin`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        timeout: 30000
      });

      setAnalysisResult(response.data);
      toast.success('Cilt analizi tamamlandı!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.response?.data?.detail || 'Analiz sırasında bir hata oluştu.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadPDF = async (analysisId) => {
    try {
      toast.info('PDF hazırlanıyor...');
      
      // Alternative method: Direct URL with authentication
      const token = localStorage.getItem('token');
      const pdfUrl = `${API}/analysis/${analysisId}/pdf`;
      
      const response = await fetch(pdfUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/pdf'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        
        if (blob && blob.size > 0) {
          // Create download link
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `dermavision_analiz_${analysisId.substring(0, 8)}.pdf`;
          link.style.display = 'none';
          
          // Trigger download
          document.body.appendChild(link);
          link.click();
          
          // Cleanup
          setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }, 100);
          
          toast.success(`PDF raporu indirildi! (${Math.round(blob.size/1024)} KB)`);
        } else {
          toast.error('PDF dosyası boş');
        }
      } else {
        const errorText = await response.text();
        console.error('PDF download failed:', response.status, errorText);
        
        if (response.status === 403) {
          toast.error('PDF raporu için Standart veya Premium paket gereklidir');
        } else {
          toast.error(`PDF indirilemedi: ${response.status}`);
        }
      }
    } catch (error) {
      console.error('PDF download error:', error);
      toast.error('PDF indirme hatası: ' + error.message);
    }
  };

  const getSkinTypeColor = (skinType) => {
    switch (skinType) {
      case 'dry': return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'oily': return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'normal': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSkinTypeLabel = (skinType) => {
    switch (skinType) {
      case 'dry': return 'Kuru Cilt';
      case 'oily': return 'Yağlı Cilt';
      case 'normal': return 'Normal Cilt';
      default: return skinType;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Upload Section */}
      <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-slate-800">Cilt Analizi</CardTitle>
          <CardDescription className="text-slate-600">
            Cilt tipinizi öğrenmek için net bir yüz fotoğrafı yükleyin
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Drag & Drop Area */}
          <div
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition-colors ${
              imagePreview 
                ? 'border-blue-300 bg-blue-50/50' 
                : 'border-slate-300 bg-slate-50/50 hover:border-blue-400 hover:bg-blue-50/50'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            {imagePreview ? (
              <div className="space-y-4">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded-xl shadow-lg"
                  data-testid="image-preview"
                />
                <p className="text-sm text-slate-600">Görsel yüklendi - analiz için hazır</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-lg font-medium text-slate-700 mb-2">
                    Fotoğrafınızı buraya sürükleyin
                  </p>
                  <p className="text-sm text-slate-500">
                    veya <span className="text-blue-600 font-medium">dosya seçmek için tıklayın</span>
                  </p>
                </div>
              </div>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            data-testid="file-input"
          />

          <Button
            onClick={analyzeSkin}
            disabled={!selectedImage || isAnalyzing}
            className="w-full h-12 text-lg bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 transition-all duration-300"
            data-testid="analyze-button"
          >
            {isAnalyzing ? (
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Analiz Ediliyor...
              </div>
            ) : (
              'Cilt Analizini Başlat'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-slate-800">Analiz Sonuçları</CardTitle>
          <CardDescription className="text-slate-600">
            AI destekli cilt analizi ve öneriler
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analysisResult ? (
            <div className="space-y-6" data-testid="analysis-results">
              {/* Skin Type Result */}
              <div className="text-center p-6 rounded-2xl bg-gradient-to-br from-slate-50 to-blue-50 border">
                <h3 className="text-lg font-medium text-slate-700 mb-3">Cilt Tipiniz</h3>
                <Badge className={`text-lg px-4 py-2 ${getSkinTypeColor(analysisResult.skin_type)}`}>
                  {getSkinTypeLabel(analysisResult.skin_type)}
                </Badge>
                <p className="text-sm text-slate-600 mt-2">
                  Güven Oranı: %{Math.round(analysisResult.confidence * 100)}
                </p>
              </div>

              {/* PDF Download Button */}
              <div className="flex justify-center gap-3">
                <Button
                  onClick={() => downloadPDF(analysisResult.id)}
                  variant="outline"
                  className="flex items-center gap-2"
                  data-testid="download-pdf-button"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  PDF Rapor İndir
                </Button>
                
                <Button
                  onClick={() => window.open(`${API}/analysis/${analysisResult.id}/pdf?token=${localStorage.getItem('token')}`, '_blank')}
                  variant="ghost"
                  size="sm"
                  className="text-xs"
                >
                  Tarayıcıda Aç
                </Button>
              </div>

              {/* Probability Distribution */}
              <div>
                <h4 className="font-medium text-slate-700 mb-4">Detaylı Analiz</h4>
                <div className="space-y-3">
                  {Object.entries(analysisResult.probabilities).map(([type, prob]) => (
                    <div key={type} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-600">{getSkinTypeLabel(type)}</span>
                        <span className="text-slate-700 font-medium">%{Math.round(prob * 100)}</span>
                      </div>
                      <Progress value={prob * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Recommendations */}
              {analysisResult.recommendations && (
                <div>
                  <h4 className="font-medium text-slate-700 mb-3">Profesyonel Değerlendirme</h4>
                  <div className="p-4 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
                    <p className="text-slate-700 mb-4">
                      {analysisResult.recommendations.description}
                    </p>
                  </div>

                  {/* Product Recommendations */}
                  {analysisResult.recommendations.products && (
                    <div className="mt-6">
                      <h5 className="font-medium text-slate-700 mb-3">Önerilen Ürünler</h5>
                      <div className="space-y-2">
                        {analysisResult.recommendations.products.map((product, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
                            <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0"></div>
                            <p className="text-sm text-slate-700">{product}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Care Tips */}
                  {analysisResult.recommendations.tips && (
                    <div className="mt-6">
                      <h5 className="font-medium text-slate-700 mb-3">Bakım Önerileri</h5>
                      <div className="space-y-2">
                        {analysisResult.recommendations.tips.map((tip, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-emerald-50">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 mt-2 flex-shrink-0"></div>
                            <p className="text-sm text-slate-700">{tip}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-slate-200 to-slate-300 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-slate-500">
                Analiz sonuçları burada gösterilecek
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Analysis History Component
const AnalysisHistory = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API}/analysis-history`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setHistory(response.data);
      } catch (error) {
        toast.error('Analiz geçmişi alınırken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const downloadPDF = async (analysisId) => {
    try {
      toast.info('PDF hazırlanıyor...');
      
      // Alternative method: Direct URL with authentication
      const token = localStorage.getItem('token');
      const pdfUrl = `${API}/analysis/${analysisId}/pdf`;
      
      const response = await fetch(pdfUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/pdf'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        
        if (blob && blob.size > 0) {
          // Create download link
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `dermavision_analiz_${analysisId.substring(0, 8)}.pdf`;
          link.style.display = 'none';
          
          // Trigger download
          document.body.appendChild(link);
          link.click();
          
          // Cleanup
          setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }, 100);
          
          toast.success(`PDF raporu indirildi! (${Math.round(blob.size/1024)} KB)`);
        } else {
          toast.error('PDF dosyası boş');
        }
      } else {
        const errorText = await response.text();
        console.error('PDF download failed:', response.status, errorText);
        
        if (response.status === 403) {
          toast.error('PDF raporu için Standart veya Premium paket gereklidir');
        } else {
          toast.error(`PDF indirilemedi: ${response.status}`);
        }
      }
    } catch (error) {
      console.error('PDF download error:', error);
      toast.error('PDF indirme hatası: ' + error.message);
    }
  };

  const getSkinTypeLabel = (skinType) => {
    switch (skinType) {
      case 'dry': return 'Kuru Cilt';
      case 'oily': return 'Yağlı Cilt';
      case 'normal': return 'Normal Cilt';
      default: return skinType;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-2xl text-slate-800">Analiz Geçmişi</CardTitle>
        <CardDescription>
          Geçmiş cilt analizi sonuçlarınız
        </CardDescription>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-500">Henüz analiz yapılmamış</p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((analysis, index) => (
              <div key={analysis.id} className="p-4 rounded-lg border bg-slate-50">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-medium">{getSkinTypeLabel(analysis.skin_type)}</h3>
                    <p className="text-sm text-slate-600">
                      Güven: %{Math.round(analysis.confidence * 100)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-slate-500">
                      {new Date(analysis.timestamp).toLocaleDateString('tr-TR')}
                    </p>
                    {(user?.package_type === 'standard' || user?.package_type === 'premium') && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadPDF(analysis.id)}
                        className="text-xs"
                      >
                        PDF
                      </Button>
                    )}
                  </div>
                </div>
                <p className="text-sm text-slate-700">
                  {analysis.recommendations.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Package Manager Component
const PackageManager = () => {
  const { user } = useAuth();
  
  const packages = [
    {
      type: 'demo',
      name: 'Demo Paket',
      credits: 5,
      price: 'Ücretsiz',
      features: ['5 analiz hakkı', 'Temel öneriler'],
      color: 'border-gray-300 bg-gray-50'
    },
    {
      type: 'standard',
      name: 'Standart Paket',
      credits: 300,
      price: '₺300/ay',
      features: ['300 analiz hakkı', 'Detaylı öneriler', 'Analiz geçmişi', 'PDF rapor'],
      color: 'border-blue-300 bg-blue-50'
    },
    {
      type: 'premium',
      name: 'Premium Paket',
      credits: 1000,
      price: '₺1000/ay',
      features: ['1000 analiz hakkı', 'Premium öneriler', 'PDF rapor', 'Öncelik desteği', '7/24 destek'],
      color: 'border-purple-300 bg-purple-50'
    }
  ];

  const handleUpgrade = async (packageType) => {
    try {
      await axios.post(`${API}/upgrade-package/${packageType}`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Paket başarıyla yükseltildi!');
      window.location.reload();
    } catch (error) {
      toast.error('Paket yükseltme hatası');
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {packages.map((pkg) => (
        <Card key={pkg.type} className={`border-2 ${pkg.color} ${user?.package_type === pkg.type ? 'ring-2 ring-blue-500' : ''}`}>
          <CardHeader>
            <CardTitle className="text-xl">{pkg.name}</CardTitle>
            <div className="text-2xl font-bold">{pkg.price}</div>
            <div className="text-sm text-slate-600">{pkg.credits} kredi</div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 mb-6">
              {pkg.features.map((feature, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
            
            {user?.package_type === pkg.type ? (
              <Button disabled className="w-full">
                Aktif Paket
              </Button>
            ) : pkg.type === 'demo' ? (
              <Button disabled className="w-full">
                Kullanılamaz
              </Button>
            ) : (
              <Button 
                onClick={() => handleUpgrade(pkg.type)}
                className="w-full"
                data-testid={`upgrade-${pkg.type}`}
              >
                Yükselt
              </Button>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<AppContent />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return user ? <Dashboard /> : <AuthPage />;
};

export default App;