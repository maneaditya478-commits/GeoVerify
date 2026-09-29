"""Schema definitions for GeoVerify India Evaluation & Benchmarking Dataset."""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    DERIVED = "DERIVED"


class BenchmarkCategory(str, Enum):
    COMPLETE_VALID = "COMPLETE_VALID"
    PARTIAL_VALID = "PARTIAL_VALID"
    INFORMAL_SLANG = "INFORMAL_SLANG"
    DEVANAGARI_HINDI = "DEVANAGARI_HINDI"
    DEVANAGARI_MARATHI = "DEVANAGARI_MARATHI"
    MIXED_LANGUAGE = "MIXED_LANGUAGE"
    TYPO = "TYPO"
    MISSPELLING = "MISSPELLING"
    HISTORICAL_ALIAS = "HISTORICAL_ALIAS"
    AMBIGUOUS_LOCALITY = "AMBIGUOUS_LOCALITY"
    DISTRICT_MISMATCH = "DISTRICT_MISMATCH"
    STATE_MISMATCH = "STATE_MISMATCH"
    SUBDISTRICT_MISMATCH = "SUBDISTRICT_MISMATCH"
    LOCALITY_MISMATCH = "LOCALITY_MISMATCH"
    PIN_MISMATCH = "PIN_MISMATCH"
    INVALID_PIN = "INVALID_PIN"
    INCOMPLETE = "INCOMPLETE"
    WRONG_ADMIN_HIERARCHY = "WRONG_ADMIN_HIERARCHY"
    NEARBY_BUT_WRONG_LOCALITY = "NEARBY_BUT_WRONG_LOCALITY"


class Language(str, Enum):
    EN = "en"
    HI = "hi"
    MR = "mr"
    MIXED_HI_EN = "mixed_hi_en"
    MIXED_MR_EN = "mixed_mr_en"


class Script(str, Enum):
    LATIN = "latin"
    DEVANAGARI = "devanagari"
    MIXED = "mixed"


class ExpectedStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONSISTENT = "CONSISTENT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INCONSISTENT = "INCONSISTENT"
    AMBIGUOUS = "AMBIGUOUS"
    UNABLE_TO_VERIFY = "UNABLE_TO_VERIFY"


class CompletenessLevel(str, Enum):
    COMPLETE = "COMPLETE"
    ADEQUATE = "ADEQUATE"
    PARTIAL = "PARTIAL"
    MINIMAL = "MINIMAL"


class GroundTruth(BaseModel):
    country: str = "India"
    state: Optional[str] = None
    state_code: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    locality: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BenchmarkMetadata(BaseModel):
    completeness: CompletenessLevel = CompletenessLevel.COMPLETE
    ambiguity: bool = False
    perturbation_type: Optional[str] = None
    notes: Optional[str] = None


class BenchmarkRecord(BaseModel):
    id: str = Field(..., description="Unique case identifier (e.g. GV-000001)")
    address: str = Field(..., description="Input address string to evaluate")
    source_type: SourceType = Field(SourceType.SYNTHETIC, description="PUBLIC, SYNTHETIC, or DERIVED")
    ground_truth: GroundTruth = Field(..., description="Independent authoritative expected administrative values")
    category: BenchmarkCategory = Field(..., description="Evaluation test category")
    language: Language = Field(Language.EN, description="Language code")
    script: Script = Field(Script.LATIN, description="Script type")
    expected_status: ExpectedStatus = Field(..., description="Expected verification status")
    metadata: BenchmarkMetadata = Field(default_factory=BenchmarkMetadata, description="Case metadata")


class BenchmarkDataset(BaseModel):
    version: str = "1.0.0"
    generated_at: str
    total_cases: int
    cases: List[BenchmarkRecord]


class EvaluationResultRecord(BaseModel):
    case_id: str
    address: str
    category: str
    language: str
    script: str
    source_type: str
    
    # Ground truth vs predicted
    expected_state: Optional[str] = None
    predicted_state: Optional[str] = None
    state_matched: bool = False

    expected_district: Optional[str] = None
    predicted_district: Optional[str] = None
    district_matched: bool = False

    expected_subdistrict: Optional[str] = None
    predicted_subdistrict: Optional[str] = None
    subdistrict_matched: bool = False

    expected_locality: Optional[str] = None
    predicted_locality: Optional[str] = None
    locality_matched: bool = False

    expected_pincode: Optional[str] = None
    predicted_pincode: Optional[str] = None
    pincode_matched: bool = False

    exact_hierarchy_matched: bool = False

    # Status evaluation
    expected_status: str
    predicted_status: str
    status_matched: bool = False

    # Ambiguity
    expected_ambiguity: bool = False
    predicted_ambiguity: bool = False
    ambiguity_matched: bool = False

    # Candidate Recall
    candidate_recall_1: bool = False
    candidate_recall_3: bool = False
    candidate_recall_5: bool = False
    candidate_recall_10: bool = False

    # Scores
    consistency_score: int = 0
    completeness_score: int = 0
    entity_match_score: float = 0.0

    # Latency & Error
    latency_ms: float = 0.0
    error_category: Optional[str] = None
    notes: Optional[str] = None
