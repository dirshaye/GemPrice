from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

# Load environment variables FIRST
load_dotenv()

from models import User
from routers.price import router as price_router
from services.db import db_service
from auth.auth0 import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown events
    """
    # Startup
    print("Starting up GemPrice API...")
    try:
        await db_service.connect()
        print("Database connection established")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        # You might want to exit here in production
    
    yield
    
    # Shutdown
    print("Shutting down GemPrice API...")
    try:
        await db_service.disconnect()
        print("Database connection closed")
    except Exception as e:
        print(f"Error closing database connection: {e}")


# Create FastAPI app
app = FastAPI(
    title="GemPrice API",
    description="AI-Powered Dynamic Pricing System using Gemini API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(price_router)


# User-specific endpoints
@app.get("/api/v1/user/suggestions")
async def get_user_suggestions(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's pricing suggestion history
    """
    try:
        suggestions = await db_service.get_user_suggestions(current_user, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"Error in get_user_suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve suggestions: {str(e)}"
        )


@app.get("/api/v1/user/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's pricing statistics
    """
    try:
        stats = await db_service.get_suggestions_stats(current_user)
        return stats
    except Exception as e:
        print(f"Error in get_user_stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


# Admin endpoints (moved from main endpoints)
@app.get("/admin/health")
async def admin_health_check():
    """
    Comprehensive health check endpoint for admin use
    """
    try:
        # Test database connection
        if db_service.client:
            await db_service.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        # Check required environment variables
        required_env_vars = ["GEMINI_API_KEY", "MONGODB_URL", "AUTH0_DOMAIN", "AUTH0_AUDIENCE"]
        env_status = {}
        
        for var in required_env_vars:
            env_status[var] = "set" if os.getenv(var) else "missing"
        
        return {
            "status": "healthy",
            "database": db_status,
            "environment": env_status,
            "timestamp": "2025-01-24T00:00:00Z"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-24T00:00:00Z"
            }
        )


@app.get("/admin/system-info")
async def get_system_info():
    """
    Get detailed system information for admin dashboard
    """
    try:
        # Database stats
        db_stats = {}
        if db_service.client:
            db_stats = {
                "connection": "active",
                "database_name": "gemprice"
            }
            try:
                # Get collection stats
                collection = db_service.database[db_service.collection_name]
                total_suggestions = await collection.count_documents({})
                db_stats["total_price_suggestions"] = total_suggestions
            except:
                db_stats["total_price_suggestions"] = "unknown"
        else:
            db_stats = {"connection": "inactive"}
        
        return {
            "system": {
                "api_version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "uptime": "system_uptime_placeholder"
            },
            "database": db_stats,
            "apis": {
                "gemini": "active" if os.getenv("GEMINI_API_KEY") else "inactive",
                "auth0": "active" if os.getenv("AUTH0_DOMAIN") else "inactive",
                "currency": "active"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get system info: {str(e)}"}
        )


@app.get("/")
async def root():
    """
    Root endpoint providing API information
    """
    return {
        "message": "Welcome to GemPrice API",
        "description": "AI-Powered Dynamic Pricing System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "AI-powered pricing with Google Gemini",
            "Multi-currency support with live exchange rates",
            "User authentication with Auth0",
            "MongoDB Atlas data persistence",
            "Product name-based intelligent pricing"
        ],
        "endpoints": {
            "price_recommendation": "/api/v1/recommend-price-auth",
            "user_history": "/api/v1/user/suggestions",
            "user_stats": "/api/v1/user/stats"
        }
    }


@app.get("/health")
async def simple_health_check():
    """
    Simple health check endpoint for load balancers
    """
    return {"status": "ok", "service": "gemprice-api"}


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Custom 500 handler
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
