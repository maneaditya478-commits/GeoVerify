"""Pydantic schemas for addresses and parsing."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FreeFormAddressRequest(BaseModel):
    address: str = Field(..., min_length=2, json_schema_extra={"example": "Kharadi, Pune, Maharashtra 411014"})


class StructuredAddressRequest(BaseModel):
    address_line: Optional[str] = Field(None, json_schema_extra={"example": "Flat 402, Ganga Carnation, Near EON IT Park"})
    locality: Optional[str] = Field(None, json_schema_extra={"example": "Kharadi"})
    subdistrict: Optional[str] = Field(None, json_schema_extra={"example": "Haveli"})
    city: Optional[str] = Field(None, json_schema_extra={"example": "Pune"})
    district: Optional[str] = Field(None, json_schema_extra={"example": "Pune"})
    state: Optional[str] = Field(None, json_schema_extra={"example": "Maharashtra"})
    pincode: Optional[str] = Field(None, json_schema_extra={"example": "411014"})


class VerificationRequest(BaseModel):
    address: Optional[str] = Field(None, json_schema_extra={"example": "Kharadi, Pune, Maharashtra 411014"})
    structured: Optional[StructuredAddressRequest] = None
    radius_km: Optional[float] = Field(5.0, ge=0.5, le=50.0, description="Nearby search radius in km")
    include_geojson: bool = Field(True, description="Whether to include GeoJSON boundaries in response")


class TransformationStep(BaseModel):
    field: str
    original_value: str
    transformed_value: str
    rule_applied: str


class NormalizedAddress(BaseModel):
    original_input: str
    normalized_text: str
    locality: Optional[str] = None
    subdistrict: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    pincode: Optional[str] = None
    transformations: List[TransformationStep] = []


class ParsedAddress(BaseModel):
    premise: Optional[str] = None
    locality: Optional[str] = None
    subdistrict: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    pincode: Optional[str] = None
    landmarks: List[str] = []
    unparsed_tokens: List[str] = []
    parse_confidence: float = Field(..., ge=0.0, le=1.0)


class Coordinates(BaseModel):
    latitude: float = Field(..., json_schema_extra={"example": 18.5514})
    longitude: float = Field(..., json_schema_extra={"example": 73.9405})


class GeocodingResult(BaseModel):
    coordinates: Coordinates
    display_name: str
    source: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    match_level: Optional[str] = None
