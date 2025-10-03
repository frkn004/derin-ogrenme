from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
from datetime import datetime
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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="DermaVision AI", description="AI-Powered Skin Analysis Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global variables for model
model = None
meta = None
val_transform = None
idx_to_class = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Skin care recommendations database
SKIN_RECOMMENDATIONS = {
    "dry": {
        "description": "Cildınız kuru tip bir cilt. Nem kaybının önlenmesi ve derinlemesine nemlendirme ihtiyacınız var.",
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
        "description": "Cildınız yağlı tip bir cilt. Sebum üretiminin kontrolü ve gözeneklerin temizlenmesi gerekiyor.",
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
        "description": "Cildınız normal tip bir cilt. Mevcut dengeyi korumak ve sağlıklı görünümü sürdürmek önemli.",
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
class SkinAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    skin_type: str
    confidence: float
    probabilities: Dict[str, float]
    recommendations: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

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

# API Routes
@api_router.get("/")
async def root():
    return {"message": "DermaVision AI - Cilt Analizi Sistemi"}

@api_router.post("/analyze-skin", response_model=SkinAnalysisResult)
async def analyze_skin(file: UploadFile = File(...)):
    """Analyze uploaded skin image"""
    
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
            skin_type=skin_type,
            confidence=confidence,
            probabilities=probabilities,
            recommendations=recommendations
        )
        
        # Save to database
        await db.skin_analyses.insert_one(result.dict())
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@api_router.get("/analysis-history", response_model=List[SkinAnalysisResult])
async def get_analysis_history():
    """Get analysis history"""
    try:
        analyses = await db.skin_analyses.find().sort("timestamp", -1).limit(50).to_list(50)
        return [SkinAnalysisResult(**analysis) for analysis in analyses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geçmiş alınamadı: {str(e)}")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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
