"""FastAPI main application"""
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes
from app.database import init_db
from app.services.zap_scanner import ZAPScanner
from typing import Optional

logger = logging.getLogger(__name__)

# Global ZAP scanner instance
zap_scanner: Optional[ZAPScanner] = None


def get_zap_scanner() -> Optional[ZAPScanner]:
    """Get the global ZAP scanner instance"""
    return zap_scanner

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Advanced Security Platform - OWASP Top-10 aligned automated security scanning",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import auth
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes.router, prefix=settings.API_V1_PREFIX, tags=["security"])


def initialize_zap_scanner():
    """Initialize ZAP scanner with settings"""
    global zap_scanner
    try:
        zap_scanner = ZAPScanner(
            zap_url=settings.ZAP_URL,
            api_key=settings.ZAP_API_KEY,
            enabled=settings.ZAP_ENABLED
        )
        if zap_scanner.is_available():
            logger.info("ZAP scanner initialized and available")
        elif settings.ZAP_ENABLED:
            logger.warning("ZAP is enabled but not available. Check ZAP_URL and ensure ZAP is running.")
        else:
            logger.info("ZAP scanner is disabled")
    except Exception as e:
        logger.error(f"Failed to initialize ZAP scanner: {e}")
        zap_scanner = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and ZAP scanner on startup"""
    init_db()
    initialize_zap_scanner()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Advanced Security Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

