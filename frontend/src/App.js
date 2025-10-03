import React, { useState, useRef } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
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
        },
        timeout: 30000
      });

      setAnalysisResult(response.data);
      toast.success('Cilt analizi tamamlandı!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Analiz sırasında bir hata oluştu.');
    } finally {
      setIsAnalyzing(false);
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              DermaVision AI
            </h1>
          </div>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Yapay zeka destekli profesyonel cilt analizi ve kişiselleştirilmiş bakım önerileri
          </p>
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
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
                onDragOver={handleDragOver}
                onDrop={handleDrop}
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

        {/* Info Section */}
        <div className="max-w-4xl mx-auto mt-16">
          <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-sm">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl text-slate-800">DermaVision AI Hakkında</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div className="p-6">
                  <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">AI Teknolojisi</h3>
                  <p className="text-sm text-slate-600">
                    Vision Transformer modeli ile %95 doğruluk oranında cilt tipi analizi
                  </p>
                </div>
                
                <div className="p-6">
                  <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">Kişisel Bakım</h3>
                  <p className="text-sm text-slate-600">
                    Cilt tipinize özel ürün önerileri ve profesyonel bakım tavsiyeleri
                  </p>
                </div>
                
                <div className="p-6">
                  <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">Güvenli & Hızlı</h3>
                  <p className="text-sm text-slate-600">
                    Fotoğraflarınız işlendikten sonra silinir, saniyeler içinde sonuç alın
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SkinAnalyzer />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;