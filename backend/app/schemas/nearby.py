"""Schemas for nearby geographic intelligence."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.address import Coordinates


class NearbyPlace(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "EON Free Zone"})
    category: str = Field(..., json_schema_extra={"example": "commercial"})
    subtype: Optional[str] = Field(None, json_schema_extra={"example": "IT Park"})
    distance_km: float = Field(..., json_schema_extra={"example": 1.2})
    coordinates: Coordinates
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class NearbyPlacesResponse(BaseModel):
    center: Coordinates
    radius_km: float
    total_found: int
    places: List[NearbyPlace]
