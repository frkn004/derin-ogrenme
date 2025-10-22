from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_personalized_recommendations(self, user_id: str, skin_type: str, confidence: float) -> List[Dict]:
        """Get personalized product recommendations based on skin analysis"""
        try:
            # Get user's analysis history
            user_analyses = await self.db.skin_analyses.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(5).to_list(5)
            
            # Get base recommendations for skin type
            base_recommendations = await self.db.product_recommendations.find({
                "skin_types": skin_type,
                "active": True
            }).to_list(20)
            
            # Apply personalization logic
            personalized_recs = await self._apply_personalization_logic(
                base_recommendations, 
                user_analyses, 
                skin_type, 
                confidence
            )
            
            # Limit to top 8 recommendations
            return personalized_recs[:8]
            
        except Exception as e:
            logger.error(f"Personalized recommendations error: {str(e)}")
            return await self._get_fallback_recommendations(skin_type)
    
    async def _apply_personalization_logic(self, recommendations: List[Dict], user_analyses: List[Dict], skin_type: str, confidence: float) -> List[Dict]:
        """Apply AI-driven personalization logic"""
        try:
            # Score each recommendation
            scored_recommendations = []
            
            for rec in recommendations:
                score = await self._calculate_recommendation_score(
                    rec, user_analyses, skin_type, confidence
                )
                rec["personalization_score"] = score
                rec["recommendation_reason"] = await self._generate_recommendation_reason(
                    rec, skin_type, confidence
                )
                scored_recommendations.append(rec)
            
            # Sort by score (highest first)
            scored_recommendations.sort(key=lambda x: x["personalization_score"], reverse=True)
            
            return scored_recommendations
            
        except Exception as e:
            logger.error(f"Personalization logic error: {str(e)}")
            return recommendations
    
    async def _calculate_recommendation_score(self, recommendation: Dict, user_analyses: List[Dict], skin_type: str, confidence: float) -> float:
        """Calculate personalization score for a recommendation"""
        base_score = 50.0  # Base score
        
        # Boost score if recommendation is for primary skin type
        if skin_type in recommendation.get("skin_types", []):
            base_score += 30.0
        
        # Adjust based on confidence level
        confidence_bonus = confidence * 10  # 0-10 points based on confidence
        base_score += confidence_bonus
        
        # Category priority scoring
        category_priorities = {
            "cleanser": 20,
            "moisturizer": 25,
            "serum": 15,
            "sunscreen": 20,
            "treatment": 10
        }
        
        category_bonus = category_priorities.get(recommendation.get("category", ""), 5)
        base_score += category_bonus
        
        # Skin type specific adjustments
        if skin_type == "oily":
            if "oil-free" in recommendation.get("description", "").lower():
                base_score += 15
            if "mattifying" in recommendation.get("description", "").lower():
                base_score += 10
        elif skin_type == "dry":
            if "hydrating" in recommendation.get("description", "").lower():
                base_score += 15
            if "moisturizing" in recommendation.get("description", "").lower():
                base_score += 10
        elif skin_type == "normal":
            if "gentle" in recommendation.get("description", "").lower():
                base_score += 10
            if "balanced" in recommendation.get("description", "").lower():
                base_score += 10
        
        # Add some randomization for variety (±5 points)
        randomization = random.uniform(-5, 5)
        base_score += randomization
        
        return round(base_score, 2)
    
    async def _generate_recommendation_reason(self, recommendation: Dict, skin_type: str, confidence: float) -> str:
        """Generate personalized recommendation reason"""
        skin_type_turkish = {
            "dry": "kuru",
            "oily": "yağlı", 
            "normal": "normal"
        }.get(skin_type, "normal")
        
        reasons = {
            "dry": [
                f"{recommendation['name']}, kuru cilt tipiniz için özel olarak formüle edilmiştir.",
                f"Bu ürün, cildinizin nem ihtiyacını karşılamak için idealdir.",
                f"Kuru cilt tipinize uygun nemlendirici özellikler içerir."
            ],
            "oily": [
                f"{recommendation['name']}, yağlı cilt tipinizin ihtiyaçlarına göre seçilmiştir.",
                f"Bu ürün, sebum dengesini sağlamaya yardımcı olur.",
                f"Yağlı cilt tipiniz için gözenek temizleyici özelliklere sahiptir."
            ],
            "normal": [
                f"{recommendation['name']}, normal cilt tipinizi korumak için uygundur.",
                f"Bu ürün, cildinizin doğal dengesini korur.",
                f"Normal cilt tipiniz için günlük bakım rutininde kullanabilirsiniz."
            ]
        }
        
        # Add confidence-based reasoning
        if confidence > 0.8:
            confidence_text = " Yüksek güven oranıyla belirlenen cilt tipinize göre önerilmiştir."
        elif confidence > 0.6:
            confidence_text = " Cilt analiz sonuçlarınıza göre uygun bulunmuştur."
        else:
            confidence_text = " Genel cilt bakım rutininiz için önerilmektedir."
        
        reason = random.choice(reasons.get(skin_type, reasons["normal"]))
        return reason + confidence_text
    
    async def _get_fallback_recommendations(self, skin_type: str) -> List[Dict]:
        """Get fallback recommendations if personalization fails"""
        fallback_recs = [
            {
                "id": "fallback_1",
                "name": "CeraVe Nemlendirici Temizleyici",
                "description": "Hassas ciltler için geliştirilmiş, ceramid içeren gentle temizleyici",
                "category": "cleanser",
                "brand": "CeraVe",
                "skin_types": ["dry", "normal"],
                "benefits": ["Ceramid içerir", "Hassas ciltler için", "Nem bariyerini korur"]
            },
            {
                "id": "fallback_2",
                "name": "La Roche Posay Effaclar Gel",
                "description": "Yağlı ve akneye eğilimli ciltler için temizleyici jel",
                "category": "cleanser",
                "brand": "La Roche Posay",
                "skin_types": ["oily"],
                "benefits": ["Sebum kontrolü", "Gözenek temizliği", "pH dengeleyici"]
            },
            {
                "id": "fallback_3",
                "name": "The Ordinary Hyaluronic Acid 2% + B5",
                "description": "Yoğun nemlendirme sağlayan hyaluronik asit serumu",
                "category": "serum",
                "brand": "The Ordinary",
                "skin_types": ["dry", "normal", "oily"],
                "benefits": ["Yoğun nemlendirme", "Cildi dolgunlaştırır", "Her cilt tipine uygun"]
            }
        ]
        
        # Filter by skin type if possible
        filtered_recs = [rec for rec in fallback_recs if skin_type in rec["skin_types"]]
        return filtered_recs if filtered_recs else fallback_recs
    
    async def track_recommendation_interaction(self, user_id: str, recommendation_id: str, interaction_type: str):
        """Track user interaction with recommendations for ML improvement"""
        try:
            interaction = {
                "user_id": user_id,
                "recommendation_id": recommendation_id,
                "interaction_type": interaction_type,  # 'view', 'click', 'purchase', 'like', 'dislike'
                "timestamp": datetime.now(),
                "context": "skin_analysis_result"
            }
            
            await self.db.recommendation_interactions.insert_one(interaction)
            logger.info(f"Tracked recommendation interaction: {interaction_type} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Track recommendation interaction error: {str(e)}")
    
    async def get_trending_products(self, limit: int = 5) -> List[Dict]:
        """Get trending products based on user interactions"""
        try:
            # Aggregate interaction data to find trending products
            trending = await self.db.recommendation_interactions.aggregate([
                {"$match": {"interaction_type": {"$in": ["click", "like", "purchase"]}}},
                {"$group": {
                    "_id": "$recommendation_id",
                    "interaction_count": {"$sum": 1}
                }},
                {"$sort": {"interaction_count": -1}},
                {"$limit": limit}
            ]).to_list(limit)
            
            # Get full product details
            trending_products = []
            for item in trending:
                product = await self.db.product_recommendations.find_one({"id": item["_id"]})
                if product:
                    product["interaction_count"] = item["interaction_count"]
                    trending_products.append(product)
            
            return trending_products
            
        except Exception as e:
            logger.error(f"Get trending products error: {str(e)}")
            return await self._get_fallback_recommendations("normal")
