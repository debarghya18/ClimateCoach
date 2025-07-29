"""
Climate AI Platform - Main Application
A comprehensive platform for climate analysis using autonomous AI agents
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from app.core.config import get_settings
from app.core.database import init_db
from app.core.security import get_current_user
from app.api.v1 import auth, climate, agents, dashboard, gdpr
from app.agents.climate_analyzer import ClimateAnalysisAgent
from app.agents.recommendation_engine import RecommendationAgent
from app.services.data_collector import DataCollectionService
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.audit_log import AuditLogMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Climate AI Platform...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI agents
    app.state.climate_agent = ClimateAnalysisAgent()
    app.state.recommendation_agent = RecommendationAgent()
    app.state.data_collector = DataCollectionService()
    
    logger.info("Application startup complete")
    yield
    
    logger.info("Shutting down Climate AI Platform...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI agents for climate challenge analysis and adaptation",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Security middleware
security = HTTPBearer()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com", "*.yourdomain.com"]
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditLogMiddleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(climate.router, prefix="/api/v1/climate", tags=["climate-data"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["ai-agents"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(gdpr.router, prefix="/api/v1/gdpr", tags=["gdpr-compliance"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    with open("app/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/status")
async def get_system_status(current_user=Depends(get_current_user)):
    """Get comprehensive system status"""
    try:
        climate_agent_status = await app.state.climate_agent.get_status()
        recommendation_agent_status = await app.state.recommendation_agent.get_status()
        data_collector_status = await app.state.data_collector.get_status()
        
        return {
            "system": "operational",
            "agents": {
                "climate_analyzer": climate_agent_status,
                "recommendation_engine": recommendation_agent_status,
                "data_collector": data_collector_status
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="System status unavailable")


@app.post("/api/v1/analyze")
async def trigger_analysis(
    background_tasks: BackgroundTasks,
    location_data: dict,
    current_user=Depends(get_current_user)
):
    """Trigger comprehensive climate analysis"""
    try:
        # Add background task for analysis
        background_tasks.add_task(
            run_comprehensive_analysis,
            location_data,
            current_user.id
        )
        
        return {
            "message": "Analysis started",
            "status": "processing",
            "estimated_completion": "5-10 minutes"
        }
    except Exception as e:
        logger.error(f"Analysis trigger failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")


async def run_comprehensive_analysis(location_data: dict, user_id: int):
    """Run comprehensive climate analysis in background"""
    try:
        logger.info(f"Starting analysis for user {user_id}")
        
        # Collect data
        climate_data = await app.state.data_collector.collect_climate_data(location_data)
        
        # Analyze with AI agents
        analysis_result = await app.state.climate_agent.analyze(climate_data)
        recommendations = await app.state.recommendation_agent.generate_recommendations(
            analysis_result, location_data
        )
        
        # Store results (implementation depends on your database schema)
        # await store_analysis_results(user_id, analysis_result, recommendations)
        
        logger.info(f"Analysis completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
