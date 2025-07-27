from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
import pandas as pd
import io
from typing import List
from models import (
    PriceRecommendationRequest, 
    PriceRecommendationResponse, 
    CSVUploadResponse,
    User
)
from services.gemini import GeminiService
from services.db import db_service
from auth.auth0 import get_current_user


router = APIRouter(prefix="/api/v1", tags=["pricing"])
gemini_service = GeminiService()


@router.post("/recommend-price", response_model=PriceRecommendationResponse)
async def recommend_price(request: PriceRecommendationRequest):
    """
    Get AI-powered price recommendation for a single product (public endpoint)
    """
    try:
        recommendation = await gemini_service.get_price_recommendation(request)
        return recommendation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating price recommendation: {str(e)}"
        )


@router.post("/recommend-price-auth", response_model=PriceRecommendationResponse)
async def recommend_price_authenticated(
    request: PriceRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered price recommendation for a single product (authenticated endpoint)
    Saves the recommendation to user's history
    """
    try:
        # Get the recommendation
        recommendation = await gemini_service.get_price_recommendation(request)
        
        # Save to database for authenticated users
        suggestion_data = {
            "product_data": {
                "cost_price": request.cost_price,
                "competitor_price": request.competitor_price,
                "inventory_level": request.inventory_level,
                "season": request.season,
                "category": request.category
            },
            "suggested_price": recommendation.suggested_price,
            "reasoning": recommendation.reasoning,
            "confidence_score": recommendation.confidence_score
        }
        
        await db_service.save_price_suggestion(current_user, suggestion_data)
        
        return recommendation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating price recommendation: {str(e)}"
        )


@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload CSV file for batch price recommendations
    Protected endpoint requiring Auth0 JWT authentication
    
    Expected CSV columns:
    - cost_price: float
    - competitor_price: float (optional)
    - inventory_level: str (low/medium/high)
    - season: str
    - category: str
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['cost_price', 'inventory_level', 'season', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        total_products = len(df)
        successful_predictions = 0
        failed_predictions = 0
        results = []
        suggestions_to_save = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Create request object
                request_data = PriceRecommendationRequest(
                    cost_price=float(row['cost_price']),
                    competitor_price=float(row['competitor_price']) if pd.notna(row.get('competitor_price')) else None,
                    inventory_level=str(row['inventory_level']),
                    season=str(row['season']),
                    category=str(row['category'])
                )
                
                # Get recommendation
                recommendation = await gemini_service.get_price_recommendation(request_data)
                
                result = {
                    "row_number": index + 1,
                    "product_data": request_data.dict(),
                    "suggested_price": recommendation.suggested_price,
                    "reasoning": recommendation.reasoning,
                    "confidence_score": recommendation.confidence_score,
                    "status": "success"
                }
                
                results.append(result)
                successful_predictions += 1
                
                # Prepare for database save
                suggestions_to_save.append({
                    "product_data": request_data.dict(),
                    "suggested_price": recommendation.suggested_price,
                    "reasoning": recommendation.reasoning,
                    "confidence_score": recommendation.confidence_score
                })
                
            except Exception as e:
                result = {
                    "row_number": index + 1,
                    "product_data": row.to_dict(),
                    "error": str(e),
                    "status": "failed"
                }
                results.append(result)
                failed_predictions += 1
        
        # Save successful suggestions to database
        if suggestions_to_save:
            try:
                await db_service.batch_save_suggestions(current_user, suggestions_to_save)
            except Exception as e:
                print(f"Error saving suggestions to database: {e}")
                # Continue even if database save fails
        
        return CSVUploadResponse(
            total_products=total_products,
            successful_predictions=successful_predictions,
            failed_predictions=failed_predictions,
            results=results
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV file is empty"
        )
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error parsing CSV file. Please check the file format."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/history")
async def get_suggestion_history(
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's price suggestion history
    Protected endpoint requiring Auth0 JWT authentication
    """
    try:
        suggestions = await db_service.get_user_suggestions(
            user=current_user,
            limit=limit,
            skip=skip
        )
        
        stats = await db_service.get_suggestions_stats(current_user)
        
        return {
            "suggestions": suggestions,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total": stats.get("total_suggestions", 0)
            },
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestion history: {str(e)}"
        )


@router.get("/history/{suggestion_id}")
async def get_suggestion_detail(
    suggestion_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific price suggestion
    Protected endpoint requiring Auth0 JWT authentication
    """
    try:
        suggestion = await db_service.get_suggestion_by_id(suggestion_id, current_user)
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        return suggestion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestion details: {str(e)}"
        )
