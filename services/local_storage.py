import json
import os
from datetime import datetime
from typing import List, Optional
from models import User

class LocalStorageService:
    """
    Local file-based storage as fallback when MongoDB is unavailable
    """
    def __init__(self):
        self.storage_dir = "local_data"
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            print(f"📁 Created local storage directory: {self.storage_dir}")
    
    def get_user_file_path(self, user_id: str) -> str:
        """Get the file path for a user's data"""
        # Clean user_id for filename (remove special characters)
        clean_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
        return os.path.join(self.storage_dir, f"user_{clean_user_id}.json")
    
    def load_user_data(self, user_id: str) -> List[dict]:
        """Load user's price suggestions from local file"""
        try:
            file_path = self.get_user_file_path(user_id)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get('suggestions', [])
            return []
        except Exception as e:
            print(f"❌ Error loading user data: {e}")
            return []
    
    def save_user_data(self, user_id: str, suggestions: List[dict]):
        """Save user's price suggestions to local file"""
        try:
            file_path = self.get_user_file_path(user_id)
            data = {
                'user_id': user_id,
                'suggestions': suggestions,
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Saved user data to {file_path}")
        except Exception as e:
            print(f"❌ Error saving user data: {e}")
    
    async def save_price_suggestion(self, user: User, suggestion_data: dict) -> str:
        """Save a price suggestion for a user"""
        try:
            # Load existing suggestions
            suggestions = self.load_user_data(user.sub)
            
            # Create new suggestion entry
            new_suggestion = {
                "_id": f"local_{len(suggestions)}_{int(datetime.now().timestamp())}",
                "user_id": user.sub,
                "product_data": suggestion_data.get("product_data", {}),
                "suggested_price": suggestion_data.get("suggested_price"),
                "reasoning": suggestion_data.get("reasoning"),
                "confidence_score": suggestion_data.get("confidence_score"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to suggestions list
            suggestions.append(new_suggestion)
            
            # Keep only last 100 suggestions per user
            suggestions = suggestions[-100:]
            
            # Save to file
            self.save_user_data(user.sub, suggestions)
            
            return new_suggestion["_id"]
            
        except Exception as e:
            print(f"❌ Error saving price suggestion: {e}")
            raise
    
    async def get_user_suggestions(self, user: User, limit: int = 50, skip: int = 0) -> List[dict]:
        """Get price suggestions for a user"""
        try:
            suggestions = self.load_user_data(user.sub)
            
            # Sort by timestamp (newest first)
            suggestions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Apply skip and limit
            return suggestions[skip:skip + limit]
            
        except Exception as e:
            print(f"❌ Error retrieving user suggestions: {e}")
            raise
    
    async def get_suggestions_stats(self, user: User) -> dict:
        """Get statistics about user's price suggestions"""
        try:
            suggestions = self.load_user_data(user.sub)
            
            if not suggestions:
                return {
                    "total_suggestions": 0,
                    "average_price": 0,
                    "min_price": 0,
                    "max_price": 0
                }
            
            prices = []
            for suggestion in suggestions:
                price = suggestion.get('suggested_price')
                if price is not None:
                    try:
                        # Handle different price formats
                        if isinstance(price, str):
                            # Remove currency symbols and convert to float
                            price_str = price.replace('$', '').replace(',', '').strip()
                            price = float(price_str)
                        elif isinstance(price, (int, float)):
                            price = float(price)
                        prices.append(price)
                    except (ValueError, TypeError):
                        continue
            
            if not prices:
                return {
                    "total_suggestions": len(suggestions),
                    "average_price": 0,
                    "min_price": 0,
                    "max_price": 0
                }
            
            return {
                "total_suggestions": len(suggestions),
                "average_price": sum(prices) / len(prices),
                "min_price": min(prices),
                "max_price": max(prices)
            }
            
        except Exception as e:
            print(f"❌ Error getting suggestions stats: {e}")
            raise

# Global local storage instance
local_storage = LocalStorageService()
