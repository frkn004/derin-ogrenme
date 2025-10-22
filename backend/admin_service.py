from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_dashboard_stats(self) -> Dict:
        """Get admin dashboard statistics"""
        try:
            # User statistics
            total_users = await self.db.users.count_documents({})
            active_subscriptions = await self.db.users.count_documents({
                "package_type": {"$ne": "demo"}
            })
            
            # Analysis statistics
            total_analyses = await self.db.skin_analyses.count_documents({})
            today_analyses = await self.db.skin_analyses.count_documents({
                "timestamp": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)}
            })
            
            # Revenue statistics (mock data for demo)
            monthly_revenue = {
                "standard": active_subscriptions * 0.7 * 300,  # Estimate 70% standard
                "premium": active_subscriptions * 0.3 * 1000   # Estimate 30% premium
            }
            
            # Package distribution
            package_stats = await self.db.users.aggregate([
                {"$group": {
                    "_id": "$package_type",
                    "count": {"$sum": 1}
                }}
            ]).to_list(10)
            
            return {
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "total_analyses": total_analyses,
                "today_analyses": today_analyses,
                "monthly_revenue": monthly_revenue,
                "package_distribution": {item["_id"]: item["count"] for item in package_stats}
            }
            
        except Exception as e:
            logger.error(f"Admin stats error: {str(e)}")
            return {}
    
    async def get_users_list(self, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Get paginated users list"""
        try:
            users = await self.db.users.find(
                {},
                {"hashed_password": 0}  # Exclude sensitive data
            ).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
            
            return users
            
        except Exception as e:
            logger.error(f"Get users error: {str(e)}")
            return []
    
    async def get_user_details(self, user_id: str) -> Optional[Dict]:
        """Get detailed user information"""
        try:
            user = await self.db.users.find_one(
                {"id": user_id},
                {"hashed_password": 0}
            )
            
            if user:
                # Get user's analyses
                analyses = await self.db.skin_analyses.find(
                    {"user_id": user_id}
                ).sort("timestamp", -1).limit(10).to_list(10)
                
                user["recent_analyses"] = analyses
                
            return user
            
        except Exception as e:
            logger.error(f"Get user details error: {str(e)}")
            return None
    
    async def update_user_package(self, user_id: str, package_type: str, credits: int) -> bool:
        """Update user package and credits"""
        try:
            result = await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "package_type": package_type,
                        "credits_remaining": credits,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Update user package error: {str(e)}")
            return False
    
    async def get_system_logs(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get system activity logs"""
        try:
            # Get recent analyses as activity logs
            logs = await self.db.skin_analyses.find({}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
            
            # Add user info to logs
            for log in logs:
                user = await self.db.users.find_one(
                    {"id": log["user_id"]},
                    {"full_name": 1, "email": 1}
                )
                if user:
                    log["user_info"] = {
                        "name": user.get("full_name", "Unknown"),
                        "email": user.get("email", "Unknown")
                    }
            
            return logs
            
        except Exception as e:
            logger.error(f"Get system logs error: {str(e)}")
            return []
    
    async def create_product_recommendation(self, recommendation_data: Dict) -> str:
        """Create a new product recommendation"""
        try:
            recommendation = {
                "id": f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "name": recommendation_data["name"],
                "description": recommendation_data["description"],
                "skin_types": recommendation_data["skin_types"],  # ['dry', 'oily', 'normal']
                "category": recommendation_data["category"],  # 'cleanser', 'moisturizer', 'serum', etc.
                "brand": recommendation_data.get("brand", ""),
                "price_range": recommendation_data.get("price_range", ""),
                "ingredients": recommendation_data.get("ingredients", []),
                "benefits": recommendation_data.get("benefits", []),
                "usage_instructions": recommendation_data.get("usage_instructions", ""),
                "created_at": datetime.now(timezone.utc),
                "active": True
            }
            
            await self.db.product_recommendations.insert_one(recommendation)
            
            return recommendation["id"]
            
        except Exception as e:
            logger.error(f"Create product recommendation error: {str(e)}")
            return ""
    
    async def get_product_recommendations(self, skin_type: Optional[str] = None) -> List[Dict]:
        """Get product recommendations, optionally filtered by skin type"""
        try:
            query = {"active": True}
            if skin_type:
                query["skin_types"] = skin_type
            
            recommendations = await self.db.product_recommendations.find(query).sort("created_at", -1).to_list(100)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Get product recommendations error: {str(e)}")
            return []
    
    async def update_product_recommendation(self, recommendation_id: str, update_data: Dict) -> bool:
        """Update product recommendation"""
        try:
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.db.product_recommendations.update_one(
                {"id": recommendation_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Update product recommendation error: {str(e)}")
            return False
    
    async def delete_product_recommendation(self, recommendation_id: str) -> bool:
        """Soft delete product recommendation"""
        try:
            result = await self.db.product_recommendations.update_one(
                {"id": recommendation_id},
                {"$set": {"active": False, "deleted_at": datetime.now(timezone.utc)}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Delete product recommendation error: {str(e)}")
            return False
