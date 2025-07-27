from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
import ssl
from typing import List, Optional
from datetime import datetime
from models import PriceSuggestion, User
from bson import ObjectId
from .local_storage import local_storage


class DatabaseService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.collection_name = "price_suggestions"
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_url = os.getenv("MONGODB_URL")
            if not mongodb_url:
                print("❌ MONGODB_URL environment variable is not set")
                self.client = None
                self.database = None
                return
            
            print(f"🔗 Connecting to MongoDB...")
            
            # Try the simplest possible connection first
            self.client = AsyncIOMotorClient(mongodb_url)
            
            # Test connection with a short timeout
            await self.client.admin.command('ping', maxTimeMS=5000)
            print("✅ Successfully connected to MongoDB Atlas")
            
            # Get database
            self.database = self.client.gemprice
            print("✅ Database 'gemprice' ready")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            print("📝 Database features will be limited without connection")
            # Set both to None so we know connection failed
            self.client = None
            self.database = None
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def save_price_suggestion(self, 
                                  user: User, 
                                  suggestion_data: dict) -> str:
        """
        Save a price suggestion to the database or local storage as fallback
        Returns the ObjectId of the saved document
        """
        try:
            if self.database is None:
                print("📁 Using local storage fallback")
                return await local_storage.save_price_suggestion(user, suggestion_data)
                
            collection = self.database[self.collection_name]
            
            # Create the document to insert
            document = {
                "user_id": user.sub,
                "product_data": suggestion_data.get("product_data", {}),
                "suggested_price": suggestion_data.get("suggested_price"),
                "reasoning": suggestion_data.get("reasoning"),
                "confidence_score": suggestion_data.get("confidence_score"),
                "timestamp": datetime.utcnow()
            }
            
            result = await collection.insert_one(document)
            print("💾 Saved to MongoDB")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving to MongoDB, using local storage: {e}")
            return await local_storage.save_price_suggestion(user, suggestion_data)
    
    async def get_user_suggestions(self, 
                                 user: User, 
                                 limit: int = 50, 
                                 skip: int = 0) -> List[dict]:
        """
        Get price suggestions for a specific user from database or local storage
        """
        try:
            if self.database is None:
                print("📁 Loading from local storage")
                return await local_storage.get_user_suggestions(user, limit, skip)
                
            collection = self.database[self.collection_name]
            
            cursor = collection.find(
                {"user_id": user.sub}
            ).sort("timestamp", -1).skip(skip).limit(limit)
            
            suggestions = []
            async for document in cursor:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                suggestions.append(document)
            
            print(f"📦 Loaded {len(suggestions)} suggestions from MongoDB")
            return suggestions
            
        except Exception as e:
            print(f"❌ Error retrieving from MongoDB, using local storage: {e}")
            return await local_storage.get_user_suggestions(user, limit, skip)
    
    async def get_suggestion_by_id(self, 
                                 suggestion_id: str, 
                                 user: User) -> Optional[dict]:
        """
        Get a specific suggestion by ID (only if it belongs to the user)
        """
        try:
            collection = self.database[self.collection_name]
            
            # Verify ObjectId format
            if not ObjectId.is_valid(suggestion_id):
                return None
            
            document = await collection.find_one({
                "_id": ObjectId(suggestion_id),
                "user_id": user.sub
            })
            
            if document:
                document["_id"] = str(document["_id"])
            
            return document
            
        except Exception as e:
            print(f"Error retrieving suggestion by ID: {e}")
            raise
    
    async def get_suggestions_stats(self, user: User) -> dict:
        """
        Get statistics about user's price suggestions from database or local storage
        """
        try:
            if self.database is None:
                print("📁 Getting stats from local storage")
                return await local_storage.get_suggestions_stats(user)
                
            collection = self.database[self.collection_name]
            
            # Count total suggestions
            total_count = await collection.count_documents({"user_id": user.sub})
            
            # Get average price
            pipeline = [
                {"$match": {"user_id": user.sub}},
                {"$group": {
                    "_id": None,
                    "avg_price": {"$avg": "$suggested_price"},
                    "min_price": {"$min": "$suggested_price"},
                    "max_price": {"$max": "$suggested_price"}
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            stats = {
                "total_suggestions": total_count,
                "average_price": result[0]["avg_price"] if result and result[0]["avg_price"] else 0,
                "min_price": result[0]["min_price"] if result and result[0]["min_price"] else 0,
                "max_price": result[0]["max_price"] if result and result[0]["max_price"] else 0
            }
            
            print(f"📊 MongoDB stats: {stats}")
            return stats
            
        except Exception as e:
            print(f"❌ Error getting MongoDB stats, using local storage: {e}")
            return await local_storage.get_suggestions_stats(user)
    
    async def batch_save_suggestions(self, 
                                   user: User, 
                                   suggestions: List[dict]) -> List[str]:
        """
        Save multiple price suggestions in batch
        Returns list of ObjectIds
        """
        try:
            collection = self.database[self.collection_name]
            
            documents = []
            for suggestion in suggestions:
                document = {
                    "user_id": user.sub,
                    "product_data": suggestion["product_data"],
                    "suggested_price": suggestion["suggested_price"],
                    "reasoning": suggestion["reasoning"],
                    "confidence_score": suggestion.get("confidence_score"),
                    "timestamp": datetime.utcnow()
                }
                documents.append(document)
            
            result = await collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
            
        except Exception as e:
            print(f"Error batch saving suggestions: {e}")
            raise


# Global database instance
db_service = DatabaseService()
