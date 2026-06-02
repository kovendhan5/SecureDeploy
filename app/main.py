from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import uvicorn
from datetime import datetime, timezone
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SecureDeploy API",
    description="A secure, containerized Python FastAPI application for DevSecOps demo",
    version="1.0.0"
)

# Add CORS middleware for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, tags=["metrics"])


@app.get("/", tags=["root"])
async def read_root():
    """Root endpoint"""
    return {
        "message": "SecureDeploy API",
        "version": "1.0.0",
        "description": "Automated CI/CD pipeline with security scanning on Azure",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint - used by Kubernetes probes and smoke tests"""
    logger.debug("Health check called")
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/metrics", tags=["metrics"])
async def prometheus_metrics():
    """Prometheus metrics endpoint - automatically exposed by Instrumentator"""
    pass  # Instrumentator handles this


@app.get("/info", tags=["info"])
async def get_info():
    """Get application info"""
    return {
        "app": "SecureDeploy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    # Only used for local development
    # In Kubernetes, the container entrypoint uses uvicorn directly
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
