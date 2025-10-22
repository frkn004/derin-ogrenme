from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
security = HTTPBearer()

# Global variables for model
model = None
meta = None
val_transform = None
idx_to_class = None
device = "cuda" if torch.cuda.is_available() else "cpu"

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

class DashboardStats(BaseModel):
    total_analyses: int
    credits_remaining: int
    package_type: PackageType
    recent_analyses: List[SkinAnalysisResult]

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
        
        # Create result
        result = SkinAnalysisResult(
            user_id=current_user["id"],
            skin_type=skin_type,
            confidence=confidence,
            probabilities=probabilities,
            recommendations=recommendations
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

# Package Management Routes
@api_router.post("/upgrade-package/{package_type}")
async def upgrade_package(package_type: PackageType, current_user: dict = Depends(get_current_user)):
    """Upgrade user package (placeholder for payment integration)"""
    if package_type == PackageType.DEMO:
        raise HTTPException(status_code=400, detail="Demo paketine geçiş yapılamaz")
    
    # TODO: Add payment processing here
    
    # Update user package
    await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "package_type": package_type,
                "credits_remaining": PACKAGE_CREDITS[package_type]
            }
        }
    )
    
    return {"message": f"Paket {package_type.value} olarak yükseltildi", "credits": PACKAGE_CREDITS[package_type]}

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
    """Load model on startup"""
    await load_skin_model()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
