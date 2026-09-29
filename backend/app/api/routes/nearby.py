"""Nearby points of interest discovery API route."""

from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.address import Coordinates
from app.schemas.nearby import NearbyPlacesResponse
from app.services.nearby import nearby_service

router = APIRouter(tags=["Nearby Intelligence"])


@router.get("/nearby", response_model=NearbyPlacesResponse)
async def get_nearby_places(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Center latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Center longitude"),
    radius_km: float = Query(5.0, ge=0.5, le=50.0, description="Search radius in km"),
    category: Optional[str] = Query(None, description="Category filter (hospital, transit, commercial, police, post_office)"),
    max_results: int = Query(20, ge=1, le=50)
):
    """Retrieve nearby verified landmarks, hospitals, transit, and public services."""
    center = Coordinates(latitude=latitude, longitude=longitude)
    return nearby_service.find_nearby(
        center=center,
        radius_km=radius_km,
        category=category,
        max_results=max_results
    )
