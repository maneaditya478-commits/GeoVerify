"""Health check route."""

from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "geocoder_provider": settings.GEOCODER_PROVIDER,
        "environment": settings.APP_ENV
    }
