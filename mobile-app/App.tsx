import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AuthService from './src/services/AuthService';
import AnalysisService from './src/services/AnalysisService';
import AdminService, { ProductRecommendation } from './src/services/AdminService';
import type { AnalysisResult } from './src/types';

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  
  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  
  // Analysis states
  const [image, setImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  
  // History states
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Admin states
  const [showAdmin, setShowAdmin] = useState(false);
  const [products, setProducts] = useState<ProductRecommendation[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  
  // Add Product Form states
  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [productBrand, setProductBrand] = useState('');
  const [productPrice, setProductPrice] = useState('');
  const [productCategory, setProductCategory] = useState('serum');
  const [selectedSkinTypes, setSelectedSkinTypes] = useState<string[]>([]);

  // Initialize
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      const authenticated = await AuthService.initialize();
      setIsAuthenticated(authenticated);
      
      // Check if user is admin
      if (authenticated) {
        const adminStatus = AdminService.isAdmin();
        setIsAdmin(adminStatus);
        if (adminStatus) {
          console.log('👑 Admin yetkisi tespit edildi');
        }
      }
      
      console.log('✅ DermaVision Pro başlatıldı');
      console.log('🔗 Backend:', 'http://192.168.1.212:8000');
    } catch (error) {
      console.error('❌ Başlatma hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auth Handler
  const handleAuth = async () => {
    if (!email || !password) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurun');
      return;
    }

    setIsLoading(true);
    try {
      if (isLogin) {
        await AuthService.login({ email, password });
      } else {
        if (!fullName) {
          Alert.alert('Hata', 'Lütfen adınızı girin');
          setIsLoading(false);
          return;
        }
        await AuthService.register({ email, password, full_name: fullName });
      }
      
      setIsAuthenticated(true);
      Alert.alert('✅ Başarılı', isLogin ? 'Giriş yapıldı!' : 'Kayıt başarılı!');
    } catch (error: any) {
      Alert.alert('❌ Hata', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Pick Image
  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('İzin Gerekli', 'Galeriye erişim izni gerekli');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setResult(null);
    }
  };

  // Analyze
  const analyzeSkin = async () => {
    if (!image) {
      Alert.alert('Hata', 'Lütfen önce fotoğraf seçin');
      return;
    }

    setAnalyzing(true);
    try {
      const analysisResult = await AnalysisService.analyzeSkin(image);
      setResult(analysisResult);
      Alert.alert('✅ Başarılı', 'Analiz tamamlandı!');
    } catch (error: any) {
      Alert.alert('❌ Hata', error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  // Load History
  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const historyData = await AnalysisService.getHistory();
      console.log('📊 Geçmiş analiz sayısı:', historyData.length);
      if (historyData.length > 0) {
        console.log('📊 İlk analiz verisi:', JSON.stringify(historyData[0], null, 2));
      }
      setHistory(historyData);
      setShowHistory(true);
    } catch (error: any) {
      console.error('❌ Geçmiş yükleme hatası:', error);
      Alert.alert('❌ Hata', error.message);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Load Products (Admin)
  const loadProducts = async () => {
    setLoadingProducts(true);
    try {
      console.log('🔄 Ürünler yükleniyor...');
      console.log('👤 Mevcut kullanıcı:', AuthService.getUser());
      console.log('🔑 Token:', AuthService.getToken() ? 'Var' : 'Yok');
      console.log('👑 Admin mi?', AdminService.isAdmin());
      
      const productData = await AdminService.getProducts();
      console.log('✅ Ürün sayısı:', productData.length);
      setProducts(productData);
      setShowAdmin(true);
    } catch (error: any) {
      console.error('❌ Detaylı hata:', error);
      console.error('❌ Hata mesajı:', error.message);
      console.error('❌ Hata response:', error.response?.data);
      Alert.alert('❌ Hata', error.message || 'Bilinmeyen hata');
    } finally {
      setLoadingProducts(false);
    }
  };

  // Delete Product (Admin)
  const deleteProduct = async (id: string, name: string) => {
    Alert.alert(
      'Ürünü Sil',
      `"${name}" ürününü silmek istediğinizden emin misiniz?`,
      [
        { text: 'İptal', style: 'cancel' },
        {
          text: 'Sil',
          style: 'destructive',
          onPress: async () => {
            try {
              await AdminService.deleteProduct(id);
              Alert.alert('✅ Başarılı', 'Ürün silindi');
              loadProducts(); // Reload
            } catch (error: any) {
              Alert.alert('❌ Hata', error.message);
            }
          },
        },
      ]
    );
  };

  // Toggle Skin Type Selection
  const toggleSkinType = (type: string) => {
    if (selectedSkinTypes.includes(type)) {
      setSelectedSkinTypes(selectedSkinTypes.filter(t => t !== type));
    } else {
      setSelectedSkinTypes([...selectedSkinTypes, type]);
    }
  };

  // Reset Product Form
  const resetProductForm = () => {
    setProductName('');
    setProductDescription('');
    setProductBrand('');
    setProductPrice('');
    setProductCategory('serum');
    setSelectedSkinTypes([]);
  };

  // Add Product (Admin)
  const handleAddProduct = async () => {
    if (!productName || !productDescription || selectedSkinTypes.length === 0) {
      Alert.alert('⚠️ Eksik Bilgi', 'Ürün adı, açıklama ve en az 1 cilt tipi seçmelisiniz');
      return;
    }

    setLoadingProducts(true);
    try {
      const newProduct: ProductRecommendation = {
        name: productName,
        description: productDescription,
        skin_types: selectedSkinTypes,
        category: productCategory,
        brand: productBrand || undefined,
        price_range: productPrice || undefined,
      };

      await AdminService.createProduct(newProduct);
      Alert.alert('✅ Başarılı', 'Ürün eklendi!');
      
      resetProductForm();
      setShowAddProduct(false);
      loadProducts(); // Reload product list
    } catch (error: any) {
      Alert.alert('❌ Hata', error.message);
    } finally {
      setLoadingProducts(false);
    }
  };

  // Logout
  const handleLogout = async () => {
    await AuthService.logout();
    setIsAuthenticated(false);
    setImage(null);
    setResult(null);
    setShowHistory(false);
    setHistory([]);
    setShowAdmin(false);
    setProducts([]);
    setIsAdmin(false);
  };

  // Loading Screen
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>DermaVision AI</Text>
      </View>
    );
  }

  // Login Screen
  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView contentContainerStyle={styles.scrollView}>
            <View style={styles.header}>
              <Text style={styles.logo}>🔬</Text>
              <Text style={styles.title}>DermaVision AI</Text>
              <Text style={styles.subtitle}>Yapay Zeka ile Cilt Analizi</Text>
            </View>

            <View style={styles.formCard}>
              <Text style={styles.formTitle}>
                {isLogin ? 'Hoş Geldiniz' : 'Hesap Oluşturun'}
              </Text>
              
              {!isLogin && (
                  <TextInput
                    style={styles.input}
                  placeholder="Ad Soyad"
                    value={fullName}
                    onChangeText={setFullName}
                  placeholderTextColor="#999"
                  />
              )}
              
                <TextInput
                  style={styles.input}
                placeholder="E-posta"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                placeholderTextColor="#999"
                />
              
                <TextInput
                  style={styles.input}
                placeholder="Şifre"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                placeholderTextColor="#999"
                />
              
              <TouchableOpacity
                style={styles.primaryButton}
                onPress={handleAuth}
                disabled={isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.primaryButtonText}>
                    {isLogin ? 'Giriş Yap' : 'Kayıt Ol'}
                  </Text>
                )}
              </TouchableOpacity>
              
              <TouchableOpacity onPress={() => setIsLogin(!isLogin)}>
                <Text style={styles.switchText}>
                  {isLogin ? 'Hesabınız yok mu? ' : 'Zaten hesabınız var mı? '}
                  <Text style={styles.switchLink}>
                    {isLogin ? 'Kayıt olun' : 'Giriş yapın'}
                  </Text>
                </Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    );
  }

  // Main App Screen - History View
  if (showHistory) {
  return (
      <SafeAreaView style={styles.container}>
        <View style={styles.historyHeader}>
          <TouchableOpacity onPress={() => setShowHistory(false)}>
            <Text style={styles.backButton}>← Geri</Text>
          </TouchableOpacity>
          <Text style={styles.historyTitle}>Geçmiş Analizler</Text>
          <View style={{ width: 60 }} />
        </View>

        <ScrollView contentContainerStyle={styles.historyScrollView}>
          {loadingHistory ? (
            <ActivityIndicator size="large" color="#667eea" style={{ marginTop: 50 }} />
          ) : history.length === 0 ? (
            <View style={styles.emptyHistory}>
              <Text style={styles.emptyHistoryEmoji}>📊</Text>
              <Text style={styles.emptyHistoryText}>Henüz analiz geçmişiniz yok</Text>
              <Text style={styles.emptyHistorySubtext}>İlk analizinizi yapmak için geri dönün</Text>
            </View>
          ) : (
            history.map((item, index) => {
              // Tarih formatı düzeltme - backend'den timestamp geliyor
              const dateField = (item as any).timestamp || item.created_at;
              const date = dateField ? new Date(dateField) : new Date();
              const isValidDate = !isNaN(date.getTime());
              const dateString = isValidDate 
                ? date.toLocaleDateString('tr-TR', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : 'Tarih bilinmiyor';

              return (
                <View key={item.id || index} style={styles.historyCard}>
                  <View style={styles.historyCardHeader}>
                    <Text style={styles.historyCardDate}>
                      {dateString}
                    </Text>
                    <View style={[styles.historyBadge, { backgroundColor: '#667eea' }]}>
                      <Text style={styles.historyBadgeText}>
                        {item.skin_type || 'Bilinmiyor'}
                      </Text>
                    </View>
                  </View>
                  
                  <Text style={styles.historyCardConfidence}>
                    Güven: {((item.confidence || 0) * 100).toFixed(1)}%
                  </Text>
                  
                  {item.description && (
                    <Text style={styles.historyCardDescription} numberOfLines={3}>
                      {item.description}
                    </Text>
                  )}
                  
                  {(() => {
                    // recommendations bir Dict - product_recommendations array'ini al
                    const recs = (item.recommendations as any)?.product_recommendations || [];
                    if (recs.length === 0) return null;
                    
                    return (
                      <View style={styles.recommendationsContainer}>
                        <Text style={styles.recommendationsTitle}>💡 Ürün Önerileri:</Text>
                        {recs.slice(0, 3).map((rec: any, idx: number) => (
                          <Text key={idx} style={styles.recommendationItem}>
                            • {rec.product_name || rec.name || 'Ürün'}
                          </Text>
                        ))}
                      </View>
                    );
                  })()}
                </View>
              );
            })
          )}
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Add Product Form Screen
  if (showAddProduct) {
    const skinTypes = [
      { key: 'dry', label: 'Kuru' },
      { key: 'oily', label: 'Yağlı' },
      { key: 'normal', label: 'Normal' },
      { key: 'combination', label: 'Karma' },
    ];

    const categories = [
      { key: 'serum', label: 'Serum' },
      { key: 'moisturizer', label: 'Nemlendirici' },
      { key: 'cleanser', label: 'Temizleyici' },
      { key: 'sunscreen', label: 'Güneş Kremi' },
      { key: 'treatment', label: 'Tedavi' },
    ];

    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.historyHeader}>
          <TouchableOpacity onPress={() => { setShowAddProduct(false); resetProductForm(); }}>
            <Text style={styles.backButton}>← Geri</Text>
          </TouchableOpacity>
          <Text style={styles.historyTitle}>➕ Ürün Ekle</Text>
          <View style={{ width: 60 }} />
        </View>

        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={{ flex: 1 }}
        >
          <ScrollView contentContainerStyle={styles.formScrollView}>
            {/* Ürün Adı */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Ürün Adı *</Text>
              <TextInput
                style={styles.formInput}
                placeholder="Örn: Hyaluronik Asit Serum"
                value={productName}
                onChangeText={setProductName}
              />
            </View>

            {/* Marka */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Marka</Text>
              <TextInput
                style={styles.formInput}
                placeholder="Örn: DermaVision Pro"
                value={productBrand}
                onChangeText={setProductBrand}
              />
            </View>

            {/* Açıklama */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Açıklama *</Text>
              <TextInput
                style={[styles.formInput, styles.formTextArea]}
                placeholder="Ürün açıklamasını yazın..."
                value={productDescription}
                onChangeText={setProductDescription}
                multiline
                numberOfLines={4}
              />
            </View>

            {/* Cilt Tipleri */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Cilt Tipleri * (En az 1 seçin)</Text>
              <View style={styles.checkboxGroup}>
                {skinTypes.map(type => (
                  <TouchableOpacity
                    key={type.key}
                    style={[
                      styles.checkbox,
                      selectedSkinTypes.includes(type.key) && styles.checkboxSelected
                    ]}
                    onPress={() => toggleSkinType(type.key)}
                  >
                    <Text style={[
                      styles.checkboxText,
                      selectedSkinTypes.includes(type.key) && styles.checkboxTextSelected
                    ]}>
                      {selectedSkinTypes.includes(type.key) ? '✓ ' : ''}{type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Kategori */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Kategori *</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.radioGroup}>
                  {categories.map(cat => (
                    <TouchableOpacity
                      key={cat.key}
                      style={[
                        styles.radioButton,
                        productCategory === cat.key && styles.radioButtonSelected
                      ]}
                      onPress={() => setProductCategory(cat.key)}
                    >
                      <Text style={[
                        styles.radioText,
                        productCategory === cat.key && styles.radioTextSelected
                      ]}>
                        {cat.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </ScrollView>
            </View>

            {/* Fiyat Aralığı */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Fiyat Aralığı</Text>
              <TextInput
                style={styles.formInput}
                placeholder="Örn: 200-400 TL"
                value={productPrice}
                onChangeText={setProductPrice}
              />
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              style={styles.submitButton}
              onPress={handleAddProduct}
              disabled={loadingProducts}
            >
              {loadingProducts ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.submitButtonText}>✅ Ürünü Ekle</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => { setShowAddProduct(false); resetProductForm(); }}
            >
              <Text style={styles.cancelButtonText}>İptal</Text>
            </TouchableOpacity>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    );
  }

  // Admin Panel Screen
  if (showAdmin) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.historyHeader}>
          <TouchableOpacity onPress={() => setShowAdmin(false)}>
            <Text style={styles.backButton}>← Geri</Text>
          </TouchableOpacity>
          <Text style={styles.historyTitle}>⚙️ Ürün Yönetimi</Text>
          <TouchableOpacity onPress={() => setShowAddProduct(true)}>
            <Text style={styles.addButton}>➕</Text>
          </TouchableOpacity>
        </View>

        {/* Add Product Button */}
        <TouchableOpacity 
          style={styles.addProductButton}
          onPress={() => setShowAddProduct(true)}
        >
          <Text style={styles.addProductButtonText}>➕ Yeni Ürün Ekle</Text>
        </TouchableOpacity>

        <ScrollView contentContainerStyle={styles.historyScrollView}>
          {loadingProducts ? (
            <ActivityIndicator size="large" color="#667eea" style={{ marginTop: 50 }} />
          ) : products.length === 0 ? (
            <View style={styles.emptyHistory}>
              <Text style={styles.emptyHistoryEmoji}>📦</Text>
              <Text style={styles.emptyHistoryText}>Henüz ürün eklenmemiş</Text>
              <Text style={styles.emptyHistorySubtext}>İlk ürünü backend'den ekleyin</Text>
            </View>
          ) : (
            products.map((product, index) => (
              <View key={product.id || index} style={styles.productCard}>
                <View style={styles.productCardHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.productName}>{product.name}</Text>
                    <Text style={styles.productBrand}>{product.brand || 'Marka belirtilmemiş'}</Text>
                  </View>
                  <TouchableOpacity
                    style={styles.deleteButton}
                    onPress={() => deleteProduct(product.id!, product.name)}
                  >
                    <Text style={styles.deleteButtonText}>🗑️</Text>
                  </TouchableOpacity>
                </View>
                
                <Text style={styles.productDescription} numberOfLines={2}>
                  {product.description}
                </Text>
                
                <View style={styles.productTags}>
                  {product.skin_types?.map((type, idx) => (
                    <View key={idx} style={styles.productTag}>
                      <Text style={styles.productTagText}>{type}</Text>
                    </View>
                  ))}
                  <View style={[styles.productTag, { backgroundColor: '#e8f5e9' }]}>
                    <Text style={[styles.productTagText, { color: '#2e7d32' }]}>{product.category}</Text>
                  </View>
                </View>
                
                {product.price_range && (
                  <Text style={styles.productPrice}>💰 {product.price_range}</Text>
                )}
              </View>
            ))
          )}
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Main App Screen - Dashboard
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.mainScrollView}>
        {/* Header */}
        <View style={styles.mainHeader}>
          <View>
            <Text style={styles.greeting}>Merhaba 👋</Text>
            <Text style={styles.mainTitle}>Cilt Analizi</Text>
          </View>
          <View style={styles.headerButtons}>
            {isAdmin && (
              <TouchableOpacity
                style={styles.adminButton}
                onPress={loadProducts}
                disabled={loadingProducts}
              >
                <Text style={styles.adminButtonText}>
                  {loadingProducts ? '⏳' : '⚙️'}
                </Text>
              </TouchableOpacity>
            )}
            <TouchableOpacity
              style={styles.historyButton}
              onPress={loadHistory}
              disabled={loadingHistory}
            >
              <Text style={styles.historyButtonText}>
                {loadingHistory ? '⏳' : '📊'} Geçmiş
              </Text>
            </TouchableOpacity>
          <TouchableOpacity
            style={styles.logoutButton}
              onPress={handleLogout}
          >
            <Text style={styles.logoutText}>Çıkış</Text>
          </TouchableOpacity>
          </View>
        </View>

        {/* Camera Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📸 Fotoğraf Seçin</Text>
          <Text style={styles.cardDescription}>
            Net bir yüz fotoğrafı seçin veya çekin
          </Text>
          
          <TouchableOpacity
            style={styles.cameraButton}
            onPress={pickImage}
          >
            <Text style={styles.cameraButtonText}>Galeri</Text>
          </TouchableOpacity>
          
          {image && (
            <View style={styles.imageContainer}>
              <Image source={{ uri: image }} style={styles.image} />
              
              <TouchableOpacity
                style={styles.analyzeButton}
                onPress={analyzeSkin}
                disabled={analyzing}
              >
                {analyzing ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.analyzeButtonText}>
                    🔍 Analiz Et
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Results */}
        {result && (
        <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>✨ Sonuçlar</Text>
            
            <View style={styles.resultBadge}>
              <Text style={styles.resultSkinType}>
                {result.skin_type === 'dry' && 'Kuru Cilt'}
                {result.skin_type === 'oily' && 'Yağlı Cilt'}
                {result.skin_type === 'normal' && 'Normal Cilt'}
              </Text>
              <Text style={styles.resultConfidence}>
                %{Math.round(result.confidence * 100)}
            </Text>
          </View>
          
            <Text style={styles.resultDescription}>
              {result.recommendations.description}
          </Text>
          
            <Text style={styles.productTitle}>💡 Öneriler</Text>
            {result.recommendations.products.slice(0, 3).map((product, idx) => (
              <Text key={idx} style={styles.productItem}>
                • {product}
              </Text>
            ))}
        </View>
      )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FE',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FE',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 18,
    fontWeight: '700',
    color: '#6366F1',
    letterSpacing: 0.5,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flexGrow: 1,
  },
  header: {
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
    backgroundColor: '#6366F1',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  logo: {
    fontSize: 64,
    marginBottom: 12,
    textShadowColor: 'rgba(0, 0, 0, 0.1)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  title: {
    fontSize: 34,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 8,
    letterSpacing: 0.5,
    textShadowColor: 'rgba(0, 0, 0, 0.1)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.95,
    fontWeight: '500',
    letterSpacing: 0.3,
  },
  formCard: {
    margin: 20,
    marginTop: -40,
    padding: 28,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  formTitle: {
    fontSize: 26,
    fontWeight: '800',
    marginBottom: 24,
    textAlign: 'center',
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  input: {
    backgroundColor: '#F3F4F6',
    padding: 18,
    borderRadius: 14,
    marginBottom: 16,
    fontSize: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    color: '#1F2937',
    fontWeight: '500',
  },
  primaryButton: {
    backgroundColor: '#6366F1',
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  switchText: {
    textAlign: 'center',
    marginTop: 20,
    color: '#6B7280',
    fontSize: 15,
    fontWeight: '500',
  },
  switchLink: {
    color: '#6366F1',
    fontWeight: '700',
  },
  mainScrollView: {
    padding: 20,
    paddingTop: 24,
  },
  mainHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 28,
  },
  greeting: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
    marginBottom: 4,
  },
  mainTitle: {
    fontSize: 30,
    fontWeight: '800',
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  logoutButton: {
    padding: 10,
    paddingHorizontal: 18,
    backgroundColor: '#FEE2E2',
    borderRadius: 12,
    shadowColor: '#EF4444',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  logoutText: {
    color: '#DC2626',
    fontWeight: '700',
    fontSize: 14,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 28,
    marginBottom: 20,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 12,
    elevation: 6,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: '800',
    marginBottom: 8,
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  cardDescription: {
    color: '#6B7280',
    marginBottom: 20,
    fontSize: 15,
    lineHeight: 22,
    fontWeight: '500',
  },
  cameraButton: {
    backgroundColor: '#6366F1',
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  cameraButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  imageContainer: {
    marginTop: 24,
  },
  image: {
    width: '100%',
    height: 320,
    borderRadius: 18,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  analyzeButton: {
    backgroundColor: '#10B981',
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  analyzeButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  resultCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 28,
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
    borderWidth: 1,
    borderColor: '#F0FDF4',
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 20,
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  resultBadge: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#EEF2FF',
    padding: 20,
    borderRadius: 16,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#E0E7FF',
  },
  resultSkinType: {
    fontSize: 19,
    fontWeight: '700',
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  resultConfidence: {
    fontSize: 26,
    fontWeight: '800',
    color: '#6366F1',
    letterSpacing: 0.5,
  },
  resultDescription: {
    fontSize: 16,
    lineHeight: 26,
    color: '#4B5563',
    marginBottom: 20,
    fontWeight: '500',
  },
  productTitle: {
    fontSize: 19,
    fontWeight: '800',
    marginBottom: 16,
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  productItem: {
    fontSize: 15,
    lineHeight: 26,
    color: '#4B5563',
    fontWeight: '500',
    paddingLeft: 8,
  },
  // History Styles
  headerButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  historyButton: {
    padding: 10,
    paddingHorizontal: 18,
    backgroundColor: '#EEF2FF',
    borderRadius: 12,
    marginRight: 8,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#E0E7FF',
  },
  historyButtonText: {
    color: '#6366F1',
    fontWeight: '700',
    fontSize: 14,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 24,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 2,
    borderBottomColor: '#F3F4F6',
  },
  backButton: {
    fontSize: 16,
    color: '#6366F1',
    fontWeight: '700',
    minWidth: 60,
  },
  historyTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  historyScrollView: {
    padding: 20,
    paddingTop: 20,
  },
  emptyHistory: {
    alignItems: 'center',
    marginTop: 120,
  },
  emptyHistoryEmoji: {
    fontSize: 72,
    marginBottom: 20,
  },
  emptyHistoryText: {
    fontSize: 20,
    fontWeight: '800',
    marginBottom: 8,
    color: '#1F2937',
    letterSpacing: 0.3,
  },
  emptyHistorySubtext: {
    fontSize: 15,
    color: '#6B7280',
    fontWeight: '500',
  },
  historyCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  historyCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  historyCardDate: {
    fontSize: 13,
    color: '#6B7280',
    flex: 1,
    fontWeight: '600',
  },
  historyBadge: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 14,
  },
  historyBadgeText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  historyCardConfidence: {
    fontSize: 18,
    fontWeight: '800',
    color: '#6366F1',
    marginBottom: 10,
    letterSpacing: 0.3,
  },
  historyCardDescription: {
    fontSize: 15,
    color: '#4B5563',
    lineHeight: 24,
    marginBottom: 10,
    fontWeight: '500',
  },
  historyCardRecommendations: {
    fontSize: 13,
    color: '#6B7280',
    fontStyle: 'italic',
    fontWeight: '500',
  },
  recommendationsContainer: {
    marginTop: 14,
    paddingTop: 14,
    borderTopWidth: 2,
    borderTopColor: '#F3F4F6',
  },
  recommendationsTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1F2937',
    marginBottom: 10,
    letterSpacing: 0.3,
  },
  recommendationItem: {
    fontSize: 14,
    color: '#4B5563',
    lineHeight: 24,
    marginBottom: 6,
    fontWeight: '500',
  },
  // Admin Panel Styles
  adminButton: {
    padding: 10,
    paddingHorizontal: 18,
    backgroundColor: '#FEF3C7',
    borderRadius: 12,
    marginRight: 8,
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#FDE68A',
  },
  adminButtonText: {
    fontSize: 18,
    fontWeight: '600',
  },
  productCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  productCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  productName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1F2937',
    marginBottom: 6,
    letterSpacing: 0.3,
  },
  productBrand: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '600',
  },
  productDescription: {
    fontSize: 15,
    color: '#4B5563',
    lineHeight: 24,
    marginBottom: 14,
    fontWeight: '500',
  },
  productTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 10,
  },
  productTag: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E0E7FF',
  },
  productTagText: {
    fontSize: 12,
    color: '#6366F1',
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  productPrice: {
    fontSize: 14,
    color: '#10B981',
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  deleteButton: {
    padding: 10,
    backgroundColor: '#FEE2E2',
    borderRadius: 12,
  },
  deleteButtonText: {
    fontSize: 20,
  },
  addButton: {
    fontSize: 26,
    color: '#6366F1',
    fontWeight: '700',
  },
  addProductButton: {
    backgroundColor: '#6366F1',
    padding: 18,
    marginHorizontal: 16,
    marginVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  addProductButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  // Form Styles
  formScrollView: {
    padding: 24,
    paddingTop: 20,
  },
  formGroup: {
    marginBottom: 24,
  },
  formLabel: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1F2937',
    marginBottom: 10,
    letterSpacing: 0.3,
  },
  formInput: {
    backgroundColor: '#F9FAFB',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
  },
  formTextArea: {
    height: 110,
    textAlignVertical: 'top',
  },
  checkboxGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  checkbox: {
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 14,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  checkboxSelected: {
    borderColor: '#6366F1',
    backgroundColor: '#EEF2FF',
  },
  checkboxText: {
    fontSize: 15,
    color: '#6B7280',
    fontWeight: '600',
  },
  checkboxTextSelected: {
    color: '#6366F1',
    fontWeight: '800',
  },
  radioGroup: {
    flexDirection: 'row',
    gap: 12,
  },
  radioButton: {
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 14,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  radioButtonSelected: {
    borderColor: '#10B981',
    backgroundColor: '#ECFDF5',
  },
  radioText: {
    fontSize: 15,
    color: '#6B7280',
    fontWeight: '600',
  },
  radioTextSelected: {
    color: '#10B981',
    fontWeight: '800',
  },
  submitButton: {
    backgroundColor: '#6366F1',
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 16,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  cancelButton: {
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 12,
    backgroundColor: '#F3F4F6',
  },
  cancelButtonText: {
    color: '#6B7280',
    fontSize: 16,
    fontWeight: '700',
  },
});
