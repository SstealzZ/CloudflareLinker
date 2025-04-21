import os
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .api.api_v1.api import api_router
from .core.config import settings
from .core.database import engine, get_db
from .models.base import Base
from .services.scheduler import dns_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cloudflare Linker API",
    description="API for managing DNS records via Cloudflare API",
    version="0.1.0"
)

# Set up CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # During development, allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """
    Root endpoint for health check.
    
    Returns:
        Status message
    """
    return {"status": "ok", "message": "Cloudflare Linker API is running"}


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    
    Initializes the DNS update scheduler.
    """
    try:
        logger.info("Starting DNS update scheduler")
        dns_scheduler.start()
        logger.info("DNS update scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start DNS update scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    
    Stops the DNS update scheduler.
    """
    try:
        logger.info("Stopping DNS update scheduler")
        dns_scheduler.stop()
        logger.info("DNS update scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping DNS update scheduler: {e}") 