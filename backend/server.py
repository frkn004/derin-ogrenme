from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta, timezone
import torch
import json
import numpy as np
from PIL import Image, ImageOps
from torchvision import transforms
from torchvision.models import vit_b_16
import torch.nn.functional as F
import asyncio
import aiohttp
import aiofiles
from io import BytesIO
import bcrypt
import jwt
from enum import Enum
# PDF generation imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64

# Import new services
from iyzico_service import iyzico_service
from admin_service import AdminService
from recommendation_engine import RecommendationEngine


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'dermavision-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_HOURS = 24 * 7  # 7 days

# Create the main app without a prefix
app = FastAPI(title="DermaVision AI", description="AI-Powered Skin Analysis Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# Global variables for model
model = None
meta = None
val_transform = None
idx_to_class = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize services
admin_service = None
recommendation_engine = None

# Package types
class PackageType(str, Enum):
    DEMO = "demo"
    STANDARD = "standard"
    PREMIUM = "premium"

# Package configurations
PACKAGE_CREDITS = {
    PackageType.DEMO: 5,
    PackageType.STANDARD: 300,
    PackageType.PREMIUM: 1000
}

# Skin care recommendations database
SKIN_RECOMMENDATIONS = {
    "dry": {
        "description": "Cildiniz kuru tip bir cilt. Nem kaybının önlenmesi ve derinlemesine nemlendirme ihtiyacınız var.",
        "products": [
            "Hyaluronik asit içeren serum - Yoğun nemlendirme için",
            "Ceramid içeren gece kremi - Bariyer fonksiyonu için",
            "Gentle cleanser - Doğal yağları korumak için",
            "Sunscreen SPF 30+ - Günlük koruma için",
            "Argan yağı - Doğal nemlendirici olarak"
        ],
        "tips": [
            "Günde 2-3 kez nemlendirici kullanın",
            "Sıcak su yerine ılık su kullanın",
            "Alkol içermeyen ürünleri tercih edin",
            "Hava nemlendiricisi kullanmayı düşünün"
        ]
    },
    "oily": {
        "description": "Cildiniz yağlı tip bir cilt. Sebum üretiminin kontrolü ve gözeneklerin temizlenmesi gerekiyor.",
        "products": [
            "Niacinamide serum - Sebum kontrolü için",
            "Salisilik asit içeren temizleyici - Gözenek temizliği için",
            "Oil-free moisturizer - Hafif nemlendirme için",
            "Clay mask (haftada 2 kez) - Derin temizlik için",
            "Retinol (gece) - Hücre yenilenmesi için"
        ],
        "tips": [
            "Günde 2 kez yüzünüzü temizleyin",
            "Yağlı ürünlerden kaçının",
            "Düzenli eksfoliye yapın",
            "Çok fazla temizlemekten kaçının"
        ]
    },
    "normal": {
        "description": "Cildiniz normal tip bir cilt. Mevcut dengeyi korumak ve sağlıklı görünümü sürdürmek önemli.",
        "products": [
            "Vitamin C serumu - Antioksidan koruma için",
            "Hafif nemlendirici - Dengeyi korumak için",
            "Gentle cleanser - Günlük temizlik için",
            "Sunscreen SPF 30+ - Koruma için",
            "Hyaluronik asit - Ekstra nem için"
        ],
        "tips": [
            "Basit bir rutin izleyin",
            "Güneş korumasını ihmal etmeyin",
            "Cildinizi aşırı ürünle yormayın",
            "Düzenli egzersiz yapın"
        ]
    }
}

# Define Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    package_type: PackageType = PackageType.DEMO
    credits_remaining: int = PACKAGE_CREDITS[PackageType.DEMO]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    package_type: PackageType
    credits_remaining: int
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SkinAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    skin_type: str
    confidence: float
    probabilities: Dict[str, float]
    recommendations: Dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    image_data: Optional[str] = None  # Base64 encoded image for PDF

class DashboardStats(BaseModel):
    total_analyses: int
    credits_remaining: int
    package_type: PackageType
    recent_analyses: List[SkinAnalysisResult]

# New models for payment and admin
class PaymentRequest(BaseModel):
    package_type: str  # 'standard' or 'premium'

class PaymentCallbackRequest(BaseModel):
    token: str

class ProductRecommendationCreate(BaseModel):
    name: str
    description: str
    skin_types: List[str]
    category: str
    brand: Optional[str] = ""
    price_range: Optional[str] = ""
    ingredients: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    usage_instructions: Optional[str] = ""

class AdminUserUpdate(BaseModel):
    package_type: str
    credits_remaining: int

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token gerekli")
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Geçersiz token")
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz token")

def generate_pdf_report(analysis: SkinAnalysisResult, user_name: str) -> BytesIO:
    """Generate PDF report for skin analysis"""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch)
    
    # Register UTF-8 compatible font
    try:
        # Try to use system fonts that support Turkish characters
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        turkish_font = 'DejaVuSans'
        turkish_font_bold = 'DejaVuSans-Bold'
    except:
        # Fallback to Helvetica (may not show Turkish characters correctly)
        turkish_font = 'Helvetica'
        turkish_font_bold = 'Helvetica-Bold'
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles with Turkish-compatible fonts
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e40af'),
        fontName=turkish_font_bold
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#374151'),
        fontName=turkish_font_bold
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor('#374151'),
        fontName=turkish_font
    )
    
    # Content
    story = []
    
    # Title
    story.append(Paragraph("DermaVision AI", title_style))
    story.append(Paragraph("Cilt Analizi Raporu", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # User Info
    user_data = [
        ['Hasta Adı:', user_name],
        ['Analiz Tarihi:', analysis.timestamp.strftime('%d.%m.%Y %H:%M')],
        ['Rapor ID:', analysis.id[:8]]
    ]
    
    user_table = Table(user_data, colWidths=[2*inch, 3*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), turkish_font),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    story.append(user_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Analysis Results
    story.append(Paragraph("Analiz Sonuçları", subtitle_style))
    
    # Skin type result
    skin_type_turkish = {
        'dry': 'Kuru Cilt',
        'oily': 'Yağlı Cilt', 
        'normal': 'Normal Cilt'
    }.get(analysis.skin_type, analysis.skin_type)
    
    confidence_percent = round(analysis.confidence * 100)
    
    result_text = f"""<b>Tespit Edilen Cilt Tipi:</b> {skin_type_turkish}<br/>
    <b>Güven Oranı:</b> %{confidence_percent}<br/><br/>
    {analysis.recommendations.get('description', '')}
    """
    
    story.append(Paragraph(result_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Probability Distribution
    story.append(Paragraph("Detaylı Analiz Dağılımı", subtitle_style))
    
    prob_data = [['Cilt Tipi', 'Olasılık']]
    for skin_type, prob in analysis.probabilities.items():
        turkish_name = {
            'dry': 'Kuru Cilt',
            'oily': 'Yağlı Cilt',
            'normal': 'Normal Cilt'
        }.get(skin_type, skin_type)
        prob_data.append([turkish_name, f"%{round(prob * 100)}"])
    
    prob_table = Table(prob_data, colWidths=[2.5*inch, 1.5*inch])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), turkish_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    story.append(prob_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Product Recommendations
    if 'products' in analysis.recommendations:
        story.append(Paragraph("Önerilen Ürünler", subtitle_style))
        
        for i, product in enumerate(analysis.recommendations['products'], 1):
            story.append(Paragraph(f"{i}. {product}", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Care Tips
    if 'tips' in analysis.recommendations:
        story.append(Paragraph("Bakım Önerileri", subtitle_style))
        
        for i, tip in enumerate(analysis.recommendations['tips'], 1):
            story.append(Paragraph(f"{i}. {tip}", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_text = """<i>Bu rapor DermaVision AI tarafından oluşturulmuştur. 
    Sonuçlar bilgilendirme amaçlıdır ve profesyonel tıbbi görüş yerine geçmez.</i>
    """
    story.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

async def download_file(url: str, destination: Path) -> None:
    """Download file from URL to destination"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
            else:
                raise HTTPException(status_code=500, detail=f"Failed to download file: {response.status}")

async def load_skin_model():
    """Load the skin analysis model and metadata"""
    global model, meta, val_transform, idx_to_class
    
    try:
        # Create models directory
        models_dir = ROOT_DIR / "models"
        models_dir.mkdir(exist_ok=True)
        
        meta_path = models_dir / "vit_b16_skin_meta.json"
        model_path = models_dir / "vit_b16_skin_state_dict.pth"
        
        # Download files if they don't exist
        if not meta_path.exists():
            logger.info("Downloading metadata file...")
            await download_file(
                "https://customer-assets.emergentagent.com/job_dermavision/artifacts/ddujbajp_vit_b16_skin_meta.json",
                meta_path
            )
        
        if not model_path.exists():
            logger.info("Downloading model file (this may take a while)...")
            await download_file(
                "https://customer-assets.emergentagent.com/job_dermavision/artifacts/o2vspe0s_vit_b16_skin_state_dict.pth",
                model_path
            )
        
        # Load metadata
        with open(meta_path, "r") as f:
            meta = json.load(f)
        
        # Setup model architecture
        model = vit_b_16(weights=None)
        in_ftrs = model.heads.head.in_features
        model.heads.head = torch.nn.Linear(in_ftrs, len(meta["class_to_idx"]))
        
        # Load model weights
        state = torch.load(model_path, map_location=device)
        model.load_state_dict(state)
        model.to(device).eval()
        
        # Setup transform
        val_transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((meta["img_size"], meta["img_size"]),
                              interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize(mean=meta["normalize_mean"], std=meta["normalize_std"]),
        ])
        
        # Create idx to class mapping
        idx_to_class = {int(k): v for k, v in meta["idx_to_class"].items()}
        
        logger.info("Skin analysis model loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

def predict_skin_type(image_bytes: bytes) -> tuple:
    """Predict skin type from image bytes"""
    try:
        # Open and process image
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = ImageOps.exif_transpose(img)
        
        # Transform image
        x = val_transform(np.array(img)).unsqueeze(0).to(device)
        
        # Make prediction
        with torch.no_grad():
            logits = model(x)
            probs = F.softmax(logits, dim=1).cpu().numpy()[0]
            pred_idx = int(probs.argmax())
            pred_label = idx_to_class[pred_idx]
        
        # Convert probabilities to dict
        prob_dict = {idx_to_class[i]: float(prob) for i, prob in enumerate(probs)}
        
        return pred_label, float(probs[pred_idx]), prob_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

async def seed_initial_recommendations():
    """Seed database with initial product recommendations"""
    try:
        initial_recommendations = [
            {
                "id": "rec_cleanser_cerave",
                "name": "CeraVe Nemlendirici Temizleyici",
                "description": "Ceramid içeren, hassas ciltler için geliştirilmiş gentle temizleyici",
                "skin_types": ["dry", "normal"],
                "category": "cleanser",
                "brand": "CeraVe",
                "price_range": "₺80-120",
                "ingredients": ["Ceramidler", "Hyaluronik Asit", "Niacinamide"],
                "benefits": ["Nem bariyerini korur", "24 saat nemlendirme", "Paraben free"],
                "usage_instructions": "Nemli cilde uygulayın, nazikçe masaj yapın ve ılık suyla durulayın.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            },
            {
                "id": "rec_cleanser_laroche",
                "name": "La Roche Posay Effaclar Gel",
                "description": "Yağlı ve akneye eğilimli ciltler için temizleyici jel",
                "skin_types": ["oily"],
                "category": "cleanser",
                "brand": "La Roche Posay",
                "price_range": "₺90-130",
                "ingredients": ["Zinc Pidolate", "Thermal Spring Water"],
                "benefits": ["Sebum kontrolü", "Gözenek temizliği", "pH dengeleyici"],
                "usage_instructions": "Sabah ve akşam nemli cilde uygulayın, köpürtün ve durulayın.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            },
            {
                "id": "rec_serum_ordinary",
                "name": "The Ordinary Hyaluronic Acid 2% + B5",
                "description": "Yoğun nemlendirme sağlayan hyaluronik asit serumu",
                "skin_types": ["dry", "normal", "oily"],
                "category": "serum",
                "brand": "The Ordinary",
                "price_range": "₺60-90",
                "ingredients": ["Hyaluronic Acid", "Vitamin B5", "Sodium Hyaluronate"],
                "benefits": ["Yoğun nemlendirme", "Cildi dolgunlaştırır", "Her cilt tipine uygun"],
                "usage_instructions": "Temiz cilde birkaç damla uygulayın, nemlendirici öncesi kullanın.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            },
            {
                "id": "rec_moisturizer_nivea",
                "name": "Nivea Soft Nemlendirici Krem",
                "description": "Günlük kullanım için hafif dokulu nemlendirici",
                "skin_types": ["normal", "dry"],
                "category": "moisturizer",
                "brand": "Nivea",
                "price_range": "₺25-40",
                "ingredients": ["Jojoba Oil", "Vitamin E"],
                "benefits": ["24 saat nemlendirme", "Hızlı emilim", "Yapışkan his yok"],
                "usage_instructions": "Temiz ve kuru cilde nazikçe uygulayın, masaj yapın.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            },
            {
                "id": "rec_sunscreen_vichy",
                "name": "Vichy Capital Soleil SPF 50+",
                "description": "Yüksek koruma faktörlü güneş kremi",
                "skin_types": ["normal", "oily", "dry"],
                "category": "sunscreen",
                "brand": "Vichy",
                "price_range": "₺120-160",
                "ingredients": ["Mexoryl SX", "Mexoryl XL", "Thermal Water"],
                "benefits": ["UVA/UVB koruması", "Su geçirmez", "Beyaz iz bırakmaz"],
                "usage_instructions": "Güneşe çıkmadan 30 dk önce cilde uygulayın, 2 saatte bir yenileyin.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            },
            {
                "id": "rec_toner_pixi",
                "name": "Pixi Glow Tonic",
                "description": "Glikolik asit içeren aydınlatıcı toner",
                "skin_types": ["oily", "normal"],
                "category": "toner",
                "brand": "Pixi",
                "price_range": "₺180-220",
                "ingredients": ["Glycolic Acid", "Aloe Vera", "Ginseng"],
                "benefits": ["Cilt dokusunu iyileştirir", "Gözenekleri temizler", "Parlaklık verir"],
                "usage_instructions": "Akşam temizlik sonrası pamuk ile cilde uygulayın, günde 1 kez.",
                "created_at": datetime.now(timezone.utc),
                "active": True
            }
        ]
        
        await db.product_recommendations.insert_many(initial_recommendations)
        logger.info(f"Seeded {len(initial_recommendations)} initial product recommendations")
        
    except Exception as e:
        logger.error(f"Error seeding recommendations: {str(e)}")

# Authentication Routes
@api_router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu email adresi zaten kayıtlı")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    # Save to database
    user_dict = new_user.dict()
    user_dict["hashed_password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user_data.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**new_user.dict())
    )

@api_router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user"""
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Geçersiz email veya şifre")
    
    # Update last login
    await db.users.update_one(
        {"email": user_data.email},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    # Create token
    access_token = create_access_token(data={"sub": user_data.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    user_id = current_user["id"]
    
    # Get analysis count
    total_analyses = await db.skin_analyses.count_documents({"user_id": user_id})
    
    # Get recent analyses
    recent_analyses_cursor = db.skin_analyses.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(5)
    
    recent_analyses = await recent_analyses_cursor.to_list(5)
    recent_analyses = [SkinAnalysisResult(**analysis) for analysis in recent_analyses]
    
    return DashboardStats(
        total_analyses=total_analyses,
        credits_remaining=current_user["credits_remaining"],
        package_type=current_user["package_type"],
        recent_analyses=recent_analyses
    )

# Skin Analysis Routes
@api_router.post("/analyze-skin", response_model=SkinAnalysisResult)
async def analyze_skin(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Analyze uploaded skin image"""
    
    # Check if user has credits
    if current_user["credits_remaining"] <= 0:
        raise HTTPException(status_code=400, detail="Kredileriniz tükendi. Lütfen paket yükseltmesi yapın.")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Sadece resim dosyaları kabul edilir")
    
    # Check if model is loaded
    if model is None:
        raise HTTPException(status_code=500, detail="Model henüz yüklenmedi")
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Predict skin type
        skin_type, confidence, probabilities = predict_skin_type(image_bytes)
        
        # Get recommendations
        recommendations = SKIN_RECOMMENDATIONS.get(skin_type, {})
        
        # Convert image to base64 for PDF generation (if user has standard/premium)
        image_data = None
        if current_user["package_type"] in ["standard", "premium"]:
            image_data = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create result
        result = SkinAnalysisResult(
            user_id=current_user["id"],
            skin_type=skin_type,
            confidence=confidence,
            probabilities=probabilities,
            recommendations=recommendations,
            image_data=image_data
        )
        
        # Save to database
        await db.skin_analyses.insert_one(result.dict())
        
        # Deduct credit
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$inc": {"credits_remaining": -1}}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@api_router.get("/analysis-history", response_model=List[SkinAnalysisResult])
async def get_analysis_history(current_user: dict = Depends(get_current_user)):
    """Get user's analysis history"""
    try:
        analyses = await db.skin_analyses.find(
            {"user_id": current_user["id"]}
        ).sort("timestamp", -1).limit(50).to_list(50)
        return [SkinAnalysisResult(**analysis) for analysis in analyses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geçmiş alınamadı: {str(e)}")

@api_router.get("/analysis/{analysis_id}/pdf")
async def download_analysis_pdf(analysis_id: str, token: str = None, current_user: dict = Depends(get_current_user)):
    """Download PDF report for specific analysis"""
    
    # Check if user has access to PDF feature
    if current_user["package_type"] == "demo":
        raise HTTPException(status_code=403, detail="PDF raporu için Standart veya Premium paket gereklidir")
    
    # Get analysis
    analysis_doc = await db.skin_analyses.find_one({
        "id": analysis_id,
        "user_id": current_user["id"]
    })
    
    if not analysis_doc:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    
    analysis = SkinAnalysisResult(**analysis_doc)
    
    try:
        # Generate PDF
        pdf_buffer = generate_pdf_report(analysis, current_user["full_name"])
        pdf_content = pdf_buffer.getvalue()
        
        logger.info(f"Generated PDF size: {len(pdf_content)} bytes for analysis {analysis_id}")
        
        # Return PDF with proper headers
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=dermavision_analiz_{analysis_id[:8]}.pdf",
                "Content-Length": str(len(pdf_content)),
                "Cache-Control": "no-cache",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF oluşturulamadı: {str(e)}")

# Payment Routes
@api_router.post("/payment/initialize")
async def initialize_payment(payment_request: PaymentRequest, current_user: dict = Depends(get_current_user)):
    """Initialize İyzico payment for package upgrade"""
    try:
        # Create checkout form
        result = iyzico_service.create_checkout_form(current_user, payment_request.package_type)
        
        if result['success']:
            # Store payment session in database
            payment_session = {
                "user_id": current_user["id"],
                "package_type": payment_request.package_type,
                "token": result['token'],
                "conversation_id": result['conversation_id'],
                "status": "initialized",
                "created_at": datetime.now(timezone.utc)
            }
            
            await db.payment_sessions.insert_one(payment_session)
            
            return {
                "success": True,
                "checkout_form_content": result['checkout_form_content'],
                "payment_page_url": result['payment_page_url'],
                "token": result['token']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        logger.error(f"Payment initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ödeme başlatılamadı")

@api_router.post("/payment/callback")
async def payment_callback(callback_request: PaymentCallbackRequest, current_user: dict = Depends(get_current_user)):
    """Handle İyzico payment callback"""
    try:
        # Retrieve payment result
        result = iyzico_service.retrieve_checkout_form_result(callback_request.token)
        
        if result['success'] and result['payment_status'] == 'SUCCESS':
            # Get payment session
            payment_session = await db.payment_sessions.find_one({"token": callback_request.token})
            
            if payment_session:
                # Update user package
                package_type = payment_session['package_type']
                credits = PACKAGE_CREDITS.get(package_type, 300)
                
                await db.users.update_one(
                    {"id": current_user["id"]},
                    {
                        "$set": {
                            "package_type": package_type,
                            "credits_remaining": credits
                        }
                    }
                )
                
                # Update payment session status
                await db.payment_sessions.update_one(
                    {"token": callback_request.token},
                    {
                        "$set": {
                            "status": "completed",
                            "payment_id": result.get('payment_id'),
                            "completed_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                return {
                    "success": True,
                    "message": "Ödeme başarılı! Paketiniz güncellendi.",
                    "package_type": package_type,
                    "credits": credits
                }
            else:
                raise HTTPException(status_code=404, detail="Ödeme oturumu bulunamadı")
        else:
            return {
                "success": False,
                "message": "Ödeme başarısız oldu",
                "error": result.get('error', 'Bilinmeyen hata')
            }
            
    except Exception as e:
        logger.error(f"Payment callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ödeme sonucu işlenemedi")

# Package Management Routes (Updated)
@api_router.post("/upgrade-package/{package_type}")
async def upgrade_package(package_type: PackageType, current_user: dict = Depends(get_current_user)):
    """Direct package upgrade (for admin use)"""
    if package_type == PackageType.DEMO:
        raise HTTPException(status_code=400, detail="Demo paketine geçiş yapılamaz")
    
    # Update user package directly (admin function)
    await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "package_type": package_type,
                "credits_remaining": PACKAGE_CREDITS[package_type]
            }
        }
    )
    
    return {"message": f"Paket {package_type.value} olarak güncellendi", "credits": PACKAGE_CREDITS[package_type]}

# Admin Routes
@api_router.get("/admin/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    # Check if user is admin (you can add admin role check here)
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:  # Replace with actual admin emails
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    stats = await admin_service.get_dashboard_stats()
    return stats

@api_router.get("/admin/users")
async def get_admin_users(skip: int = 0, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Get users list for admin"""
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    users = await admin_service.get_users_list(skip, limit)
    return users

@api_router.get("/admin/user/{user_id}")
async def get_admin_user_details(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed user information"""
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    user = await admin_service.get_user_details(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    return user

@api_router.put("/admin/user/{user_id}/package")
async def update_user_package_admin(user_id: str, update_data: AdminUserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user package (admin only)"""
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    success = await admin_service.update_user_package(user_id, update_data.package_type, update_data.credits_remaining)
    if success:
        return {"message": "Kullanıcı paketi güncellendi"}
    else:
        raise HTTPException(status_code=400, detail="Güncelleme başarısız")

@api_router.get("/admin/logs")
async def get_admin_logs(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get system logs"""
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    logs = await admin_service.get_system_logs(skip, limit)
    return logs

# Product Recommendations Routes
@api_router.post("/admin/recommendations")
async def create_product_recommendation(recommendation: ProductRecommendationCreate, current_user: dict = Depends(get_current_user)):
    """Create new product recommendation"""
    if current_user.get("email") not in ["admin@dermavision.ai", "muratsimsek003@gmail.com"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    rec_id = await admin_service.create_product_recommendation(recommendation.dict())
    if rec_id:
        return {"message": "Ürün önerisi oluşturuldu", "id": rec_id}
    else:
        raise HTTPException(status_code=400, detail="Ürün önerisi oluşturulamadı")

@api_router.get("/recommendations/{skin_type}")
async def get_recommendations(skin_type: str, current_user: dict = Depends(get_current_user)):
    """Get personalized product recommendations"""
    try:
        # Get user's latest analysis for confidence score
        latest_analysis = await db.skin_analyses.find_one(
            {"user_id": current_user["id"]},
            sort=[("timestamp", -1)]
        )
        
        confidence = latest_analysis.get("confidence", 0.8) if latest_analysis else 0.8
        
        recommendations = await recommendation_engine.get_personalized_recommendations(
            current_user["id"], skin_type, confidence
        )
        
        return recommendations
    except Exception as e:
        logger.error(f"Get recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Öneriler alınamadı")

@api_router.post("/recommendations/{recommendation_id}/interact")
async def track_recommendation_interaction(
    recommendation_id: str, 
    interaction_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Track user interaction with recommendations"""
    await recommendation_engine.track_recommendation_interaction(
        current_user["id"], recommendation_id, interaction_type
    )
    return {"message": "Etkileşim kaydedildi"}

@api_router.get("/recommendations/trending")
async def get_trending_products():
    """Get trending products"""
    trending = await recommendation_engine.get_trending_products()
    return trending

# General Routes
@api_router.get("/")
async def root():
    return {"message": "DermaVision AI - Cilt Analizi Sistemi"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global admin_service, recommendation_engine
    
    # Initialize services
    admin_service = AdminService(db)
    recommendation_engine = RecommendationEngine(db)
    
    # Load ML model
    await load_skin_model()
    
    # Seed initial product recommendations if collection is empty
    existing_recs = await db.product_recommendations.count_documents({})
    if existing_recs == 0:
        await seed_initial_recommendations()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
