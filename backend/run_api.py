#!/usr/bin/env python3
"""Run FastAPI application"""
from dotenv import load_dotenv

# Load environment variables from .env file before importing app
load_dotenv()

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

