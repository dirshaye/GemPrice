import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
from models import PriceRecommendationRequest, PriceRecommendationResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini service with API key validation"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("✅ GeminiService initialized successfully")

    def build_pricing_prompt(self, request: PriceRecommendationRequest) -> str:
        """Build the prompt for Gemini API"""
        return f"""
You are an expert pricing consultant. Analyze the following product data and provide pricing recommendations.

Product Details:
- Cost Price: ${request.cost_price}
- Competitor Price: ${request.competitor_price}
- Inventory Level: {request.inventory_level}
- Season: {request.season}
- Category: {request.category}

Please provide a pricing recommendation with the following considerations:
1. Maintain healthy profit margins (at least 20% above cost)
2. Consider competitive positioning
3. Factor in inventory levels (higher inventory = more aggressive pricing)
4. Adjust for seasonal demand
5. Category-specific pricing strategies

Respond with ONLY a valid JSON object in this exact format:
{{
    "suggested_price": 99.99,
    "reasoning": "Clear explanation of the pricing decision",
    "confidence_score": 0.85
}}

No additional text, explanations, or formatting - just the JSON object.
"""

    async def get_price_recommendation(self, request: PriceRecommendationRequest) -> PriceRecommendationResponse:
        """Get price recommendation from Gemini API"""
        try:
            # Build prompt
            prompt = self.build_pricing_prompt(request)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Parse JSON response
            try:
                result = json.loads(response.text.strip())
                
                # Validate required fields
                if not all(key in result for key in ['suggested_price', 'reasoning', 'confidence_score']):
                    raise ValueError("Missing required fields in Gemini response")
                
                return PriceRecommendationResponse(**result)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw response: {response.text}")
                
                # Fallback pricing logic
                markup_percentage = 1.5  # 50% markup
                fallback_price = request.cost_price * markup_percentage
                
                return PriceRecommendationResponse(
                    suggested_price=round(fallback_price, 2),
                    reasoning=f"Fallback pricing applied due to API parsing error. Applied {markup_percentage*100-100}% markup on cost price.",
                    confidence_score=0.6
                )
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            
            # Emergency fallback
            markup_percentage = 1.4  # 40% markup
            fallback_price = request.cost_price * markup_percentage
            
            return PriceRecommendationResponse(
                suggested_price=round(fallback_price, 2),
                reasoning=f"Emergency fallback pricing due to API error: {str(e)}. Applied {markup_percentage*100-100}% markup.",
                confidence_score=0.5
            )
