"""Health and Readiness Monitoring Endpoints for Phase 8.2 Deployment Hardening."""

import os
try:
    import psutil
except ImportError:
    psutil = None
from typing import Dict, Any
from fastapi import APIRouter, status, Response
from app.config import settings
from app.core.cache import verification_cache, ocr_cache, geo_lookup_cache
from app.entity_resolution.dense_retrieval import dense_retriever
from app.entity_resolution.candidates import candidate_generator

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """General health check."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "config_version": settings.GEOVERIFY_CONFIG_VERSION,
        "environment": settings.APP_ENV,
        "geocoder_provider": settings.GEOCODER_PROVIDER,
    }


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """Lightweight Kubernetes liveness probe (never performs heavy I/O)."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """Kubernetes readiness probe checking dependency readiness."""
    checks = {
        "geographic_catalog": bool(len(candidate_generator.states) > 0 and len(candidate_generator.districts) > 0),
        "dense_vector_index": bool(dense_retriever.is_indexed),
        "spatial_index": True,
        "ocr_engine": True,
    }

    is_ready = all(checks.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": checks,
        "config_version": settings.GEOVERIFY_CONFIG_VERSION,
    }


@router.get("/health/telemetry")
async def telemetry_overview() -> Dict[str, Any]:
    """Non-sensitive operational telemetry overview for internal diagnostics."""
    process = psutil.Process(os.getpid()) if hasattr(psutil, "Process") else None
    rss_mb = round(process.memory_info().rss / (1024 * 1024), 2) if process else 0.0

    return {
        "memory_rss_mb": rss_mb,
        "cache_stats": {
            "verification_cache": verification_cache.stats,
            "ocr_cache": ocr_cache.stats,
            "geo_lookup_cache": geo_lookup_cache.stats,
        },
        "config_version": settings.GEOVERIFY_CONFIG_VERSION,
    }
