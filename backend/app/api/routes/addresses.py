"""Address parsing, normalization, geocoding and history routes."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.schemas.address import (
    FreeFormAddressRequest,
    StructuredAddressRequest,
    NormalizedAddress,
    ParsedAddress,
    GeocodingResult
)
from app.services.normalizer import AddressNormalizer
from app.services.address_parser import AddressParser
from app.services.geocoder import geocoder_service

router = APIRouter(prefix="/address", tags=["Address Operations"])

# In-memory history cache for quick retrieval without requiring persistent DB
VERIFICATION_HISTORY_CACHE: Dict[str, Any] = {}


@router.post("/parse", response_model=ParsedAddress)
async def parse_address(payload: FreeFormAddressRequest):
    """Parse a free-form Indian address string into structured administrative tokens."""
    return AddressParser.parse(payload.address)


@router.post("/normalize", response_model=NormalizedAddress)
async def normalize_address(payload: StructuredAddressRequest):
    """Normalize structured or unstructured address components."""
    return AddressNormalizer.normalize_address(
        address_text=payload.address_line,
        locality=payload.locality,
        subdistrict=payload.subdistrict,
        city=payload.city,
        district=payload.district,
        state=payload.state,
        pincode=payload.pincode
    )


@router.post("/geocode", response_model=Optional[GeocodingResult])
async def geocode_address(payload: FreeFormAddressRequest):
    """Geocode an address to latitude and longitude coordinates."""
    result = await geocoder_service.geocode(payload.address)
    if not result:
        raise HTTPException(status_code=404, detail="Coordinates could not be resolved for the given address.")
    return result


@router.get("/history")
async def get_history(limit: int = Query(20, ge=1, le=100)):
    """Retrieve recent address verification logs."""
    history = list(VERIFICATION_HISTORY_CACHE.values())
    history.reverse()
    return history[:limit]


@router.get("/{verification_id}")
async def get_verification_by_id(verification_id: str):
    """Retrieve a specific verification result by ID."""
    if verification_id not in VERIFICATION_HISTORY_CACHE:
        raise HTTPException(status_code=404, detail=f"Verification with ID '{verification_id}' not found.")
    return VERIFICATION_HISTORY_CACHE[verification_id]
