"""Pydantic schemas and dataclasses for Address Entity Resolution & Ambiguity Detection."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.address import Coordinates


class EntityType(str, Enum):
    STATE = "state"
    DISTRICT = "district"
    SUBDISTRICT = "subdistrict"
    LOCALITY = "locality"
    VILLAGE = "village"
    TOWN = "town"
    CITY = "city"
    PINCODE = "pincode"
    LANDMARK = "landmark"
    ROAD = "road"
    POI = "poi"


class CandidateEntity(BaseModel):
    id: str = Field(..., description="Unique entity identifier or slug")
    name: str = Field(..., description="Canonical entity name in English")
    name_hi: Optional[str] = Field(None, description="Entity name in Hindi / Devanagari")
    name_mr: Optional[str] = Field(None, description="Entity name in Marathi")
    entity_type: EntityType = Field(..., description="Geographic administrative classification")
    state: Optional[str] = Field(None, description="Parent State name")
    state_code: Optional[str] = Field(None, description="2-letter State code")
    district: Optional[str] = Field(None, description="Parent District name")
    subdistrict: Optional[str] = Field(None, description="Parent Sub-District / Taluka name")
    pincode: Optional[str] = Field(None, description="Associated 6-digit postal code")
    coordinates: Optional[Coordinates] = Field(None, description="Centroid / Representative coordinates")
    bbox: Optional[List[float]] = Field(None, description="Bounding box [min_lon, min_lat, max_lon, max_lat]")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Raw name similarity ratio (0-1)")
    match_source: str = Field("catalog", description="Resolution strategy: exact, alias, transliteration, fuzzy")
    channels: List[str] = Field(default_factory=list, description="List of retrieval channels that discovered this candidate")


class AppliedPenalty(BaseModel):
    name: str = Field(..., description="Penalty rule identifier")
    deduction: float = Field(..., description="Negative score point deduction")
    reason: str = Field(..., description="Human-readable explanation of why penalty was applied")


class RankingExplanation(BaseModel):
    feature_contributions: Dict[str, float] = Field(default_factory=dict, description="Raw and weighted component contributions")
    applied_penalties: List[AppliedPenalty] = Field(default_factory=list, description="List of administrative or type conflict deductions")
    total_penalty_deduction: float = Field(0.0, description="Sum of penalty deductions")
    retrieval_channels: List[str] = Field(default_factory=list, description="Retrieval channels that found this entity")
    consensus_count: int = Field(1, description="Number of independent retrieval channels")
    rank: int = Field(1, description="Final rank of candidate (1-indexed)")
    score_delta_to_next: Optional[float] = Field(None, description="Score difference compared to the next candidate")
    admin_differences: List[str] = Field(default_factory=list, description="Administrative differences from contextual assertions")
    summary: str = Field("", description="Explainable ranking rationale")


class EntityMatchBreakdown(BaseModel):
    name_similarity: float = Field(..., description="Weighted name similarity score (0-40 or 0-25)")
    admin_context: float = Field(..., description="Administrative context agreement score (0-25)")
    parent_child_compatibility: float = Field(0.0, description="Hierarchical multi-tier jurisdictional alignment (0-15)")
    pin_compatibility: float = Field(..., description="Postal code compatibility score (0-15 or 0-10)")
    geographic_proximity: float = Field(..., description="Spatial proximity / coordinate score (0-15 or 0-10)")
    transliteration_phonetic: float = Field(0.0, description="Devanagari transliteration and Indic phonetic agreement (0-5)")
    entity_type_weight: float = Field(..., description="Classification confidence score (0-5)")
    retrieval_consensus: float = Field(0.0, description="Consensus across independent retrieval channels (0-3)")
    data_quality: float = Field(0.0, description="Source authority, completeness, and geometry freshness (0-2)")
    penalty_deduction: float = Field(0.0, description="Total penalty deduction applied (negative or zero)")
    total_score: float = Field(..., ge=0.0, le=100.0, description="Total Entity Match Score (0-100)")


class EntityMatchResult(BaseModel):
    candidate: CandidateEntity
    match_score: float = Field(..., ge=0.0, le=100.0, description="Entity Match Score (0-100)")
    breakdown: EntityMatchBreakdown
    match_confidence: str = Field("HIGH", description="HIGH, MEDIUM, LOW")
    ranking_explanation: Optional[RankingExplanation] = None


class AmbiguityDetails(BaseModel):
    is_ambiguous: bool = False
    ambiguity_reason: Optional[str] = None
    top_candidates: List[EntityMatchResult] = []
    score_margin: Optional[float] = None
    suggested_disambiguations: List[str] = []


class CompletenessCriteria(BaseModel):
    has_state: bool = False
    has_district: bool = False
    has_subdistrict: bool = False
    has_locality: bool = False
    has_pincode: bool = False
    has_premise: bool = False
    has_landmark: bool = False


class CompletenessBreakdown(BaseModel):
    state_points: float = 0.0
    district_points: float = 0.0
    subdistrict_points: float = 0.0
    locality_points: float = 0.0
    pincode_points: float = 0.0
    premise_points: float = 0.0
    landmark_points: float = 0.0
    total_score: float = 0.0


class CompletenessResult(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Address Completeness Score (0-100)")
    rating: str = Field("ADEQUATE", description="COMPLETE, ADEQUATE, PARTIAL, MINIMAL")
    criteria: CompletenessCriteria
    breakdown: CompletenessBreakdown
    missing_fields: List[str] = []


class ResolutionResult(BaseModel):
    query_text: str
    detected_script: str = "Latin"
    resolved_entities: Dict[str, Optional[CandidateEntity]] = {}
    candidate_matches: List[EntityMatchResult] = []
    ambiguity: AmbiguityDetails
    completeness: CompletenessResult
    entity_match_score: int = 0
