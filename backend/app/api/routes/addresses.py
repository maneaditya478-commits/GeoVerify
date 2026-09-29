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


@router.post("/resolve")
async def resolve_address_entities(payload: FreeFormAddressRequest):
    """Resolve address text into structured geographic entities, ranked candidates, ambiguity, and completeness."""
    from app.entity_resolution.resolver import address_entity_resolver
    return address_entity_resolver.resolve_address(payload.address)


@router.get("/candidates/search")
@router.get("/candidates")
async def get_address_candidates(
    q: str = Query(..., min_length=2, description="Search token or place name"),
    state: Optional[str] = Query(None, description="Optional State filter context"),
    district: Optional[str] = Query(None, description="Optional District filter context"),
    limit: int = Query(10, ge=1, le=50)
):
    """Generate and rank candidate geographic entities matching a query token."""
    from app.entity_resolution.candidates import candidate_generator
    from app.entity_resolution.matcher import entity_matcher
    candidates = candidate_generator.generate_candidates(
        token=q, context_state=state, context_district=district, limit=limit
    )
    ranked = [
        entity_matcher.match_candidate(c, query_text=q, context_state=state, context_district=district)
        for c in candidates
    ]
    ranked.sort(key=lambda r: r.match_score, reverse=True)
    return {"query": q, "total_candidates": len(ranked), "candidates": ranked}


@router.post("/ambiguity")
async def check_address_ambiguity(payload: FreeFormAddressRequest):
    """Analyze whether the provided address token or text matches multiple ambiguous geographic entities."""
    from app.entity_resolution.resolver import address_entity_resolver
    resolution = address_entity_resolver.resolve_address(payload.address)
    return resolution.ambiguity


@router.post("/completeness")
async def check_address_completeness(payload: FreeFormAddressRequest):
    """Calculate the Address Completeness Score and evaluate missing geographic administrative components."""
    from app.services.address_parser import AddressParser
    from app.entity_resolution.resolver import address_entity_resolver
    parsed = AddressParser.parse(payload.address)
    return address_entity_resolver.calculate_completeness(parsed)


@router.get("/{verification_id}")
async def get_verification_by_id(verification_id: str):
    """Retrieve a specific verification result by ID."""
    if verification_id not in VERIFICATION_HISTORY_CACHE:
        raise HTTPException(status_code=404, detail=f"Verification with ID '{verification_id}' not found.")
    return VERIFICATION_HISTORY_CACHE[verification_id]


