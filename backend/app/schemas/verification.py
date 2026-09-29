"""Schemas for the core verification results, scoring, and evidence."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.address import NormalizedAddress, ParsedAddress, GeocodingResult, Coordinates
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.schemas.nearby import NearbyPlace
from app.entity_resolution.models import CandidateEntity, EntityMatchResult, AmbiguityDetails, CompletenessResult


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONSISTENT = "CONSISTENT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INCONSISTENT = "INCONSISTENT"
    AMBIGUOUS = "AMBIGUOUS"
    UNABLE_TO_VERIFY = "UNABLE_TO_VERIFY"


class EvidenceSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CONFLICT = "CONFLICT"


class EvidenceSemanticState(str, Enum):
    SUPPORTED = "SUPPORTED"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class EvidenceItem(BaseModel):
    code: str = Field(..., json_schema_extra={"example": "STATE_MATCH"})
    category: str = Field(..., json_schema_extra={"example": "hierarchy"})
    passed: bool = True
    status: str = Field(..., json_schema_extra={"example": "PASSED"})
    severity: str = Field("INFO", description="INFO, WARNING, CONFLICT")
    semantic_state: EvidenceSemanticState = Field(EvidenceSemanticState.SUPPORTED, description="SUPPORTED, MISSING, CONFLICTING, UNKNOWN")
    weight: int = Field(..., json_schema_extra={"example": 10})
    score_contribution: float = Field(..., json_schema_extra={"example": 10.0})
    title: str = Field(..., json_schema_extra={"example": "State Verification"})
    description: str = Field(..., json_schema_extra={"example": "State 'Maharashtra' exists and matches administrative records."})


class PinVerificationResult(BaseModel):
    pincode: Optional[str] = None
    is_valid_format: bool = False
    matched: bool = False
    matched_post_offices: List[str] = []
    matched_district: Optional[str] = None
    matched_state: Optional[str] = None
    pin_centroid: Optional[Coordinates] = None
    distance_to_coordinates_km: Optional[float] = None
    evidence: str = "No PIN code provided or verified."
    source: str = "India Post (Department of Posts)"


class BoundaryVerificationResult(BaseModel):
    point_inside_state: bool = False
    point_inside_district: bool = False
    point_inside_subdistrict: Optional[bool] = None
    point_inside_locality: Optional[bool] = None
    detected_state: Optional[str] = None
    detected_district: Optional[str] = None
    detected_subdistrict: Optional[str] = None
    detected_locality: Optional[str] = None
    boundary_geojson: Optional[Dict[str, Any]] = None


class ScoreBreakdown(BaseModel):
    hierarchy_score: float = 0.0
    hierarchy_max: float = 25.0
    boundary_score: float = 0.0
    boundary_max: float = 25.0
    locality_score: float = 0.0
    locality_max: float = 20.0
    pincode_score: float = 0.0
    pincode_max: float = 15.0
    geocoding_score: float = 0.0
    geocoding_max: float = 10.0
    nearby_score: float = 0.0
    nearby_max: float = 5.0
    total_score: float = 0.0


class AddressScores(BaseModel):
    geographic_consistency: int = Field(..., ge=0, le=100, description="Deterministic GIS and hierarchy score (0-100)")
    address_completeness: int = Field(..., ge=0, le=100, description="Presence of required address components (0-100)")
    entity_match: int = Field(..., ge=0, le=100, description="Weighted entity resolution match score (0-100)")


class EvidenceGraphResponse(BaseModel):
    nodes: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    summary: str = ""
    conflicts_count: int = 0
    warnings_count: int = 0


class DataSourceAttribution(BaseModel):
    name: str
    source_url: str
    license: str
    version: str = "2026.1"
    coverage: str = "National (India)"


class VerificationResponse(BaseModel):
    verification_id: str
    timestamp: str
    status: VerificationStatus
    score: int = Field(..., ge=0, le=100, description="Geographic Consistency Score (0-100)")
    scores: Optional[AddressScores] = None
    summary: str
    explanation: List[str] = []
    warnings: List[str] = []
    evidence: List[EvidenceItem] = []
    normalized_address: NormalizedAddress
    parsed_address: ParsedAddress
    geocoding: Optional[GeocodingResult] = None
    administrative_hierarchy: AdministrativeHierarchyResult
    boundary_verification: BoundaryVerificationResult
    pin_verification: PinVerificationResult
    score_breakdown: ScoreBreakdown
    nearby_places: List[NearbyPlace] = []
    candidate_matches: List[EntityMatchResult] = []
    ambiguity: Optional[AmbiguityDetails] = None
    completeness: Optional[CompletenessResult] = None
    evidence_graph: Optional[EvidenceGraphResponse] = None
    data_sources: List[DataSourceAttribution] = []
