from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Annotated
from datetime import datetime
try:
    from bson import ObjectId
except ImportError:
    # Fallback for when pymongo/bson is not installed
    class ObjectId:
        def __init__(self, oid=None):
            self._id = oid or "507f1f77bcf86cd799439011"
        
        def __str__(self):
            return str(self._id)
        
        @classmethod
        def is_valid(cls, oid):
            return True


# Simple string-based ID for compatibility
PyObjectId = Annotated[str, Field(description="MongoDB ObjectId as string")]


class PriceRecommendationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cost_price": 10.0,
                "competitor_price": 13.5,
                "inventory_level": "high",
                "season": "summer",
                "category": "skincare"
            }
        }
    )
    
    cost_price: float = Field(..., gt=0, description="Product cost price")
    competitor_price: Optional[float] = Field(None, gt=0, description="Competitor price")
    inventory_level: str = Field(..., description="Inventory level: low, medium, high")
    season: str = Field(..., description="Current season")
    category: str = Field(..., description="Product category")


class PriceRecommendationResponse(BaseModel):
    suggested_price: float
    reasoning: str
    confidence_score: Optional[float] = None


class PriceSuggestion(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(default="", alias="_id")
    user_id: str
    product_data: PriceRecommendationRequest
    suggested_price: float
    reasoning: str
    confidence_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CSVUploadResponse(BaseModel):
    total_products: int
    successful_predictions: int
    failed_predictions: int
    results: list[dict]


class User(BaseModel):
    sub: str  # Auth0 user ID
    email: Optional[str] = None
    name: Optional[str] = None
