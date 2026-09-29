"""Comprehensive Structured Decision Trace for Phase 7.3.

Provides full step-by-step explainability and telemetry for each benchmark verification run:
[Raw Input -> OCR Extraction -> Normalization -> Provenance -> Assembly ->
 Candidate Retrieval -> Ranking -> Geographic Evidence -> Completeness ->
 Ambiguity -> Calibrated Decision -> Final Status]
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StructuredDecisionTrace(BaseModel):
    case_id: str
    input_type: str = "ocr_document"  # "clean_text" or "ocr_document"
    raw_input: str = ""
    ocr_text: str = ""
    normalized_text: str = ""
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    field_provenance: Dict[str, Any] = Field(default_factory=dict)
    assembled_address: str = ""
    candidate_count: int = 0
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    ranking: List[Dict[str, Any]] = Field(default_factory=list)
    geographic_evidence: Dict[str, Any] = Field(default_factory=dict)
    hierarchy_checks: Dict[str, Any] = Field(default_factory=dict)
    pin_evidence: Dict[str, Any] = Field(default_factory=dict)
    spatial_evidence: Dict[str, Any] = Field(default_factory=dict)
    completeness: Dict[str, Any] = Field(default_factory=dict)
    ambiguity: Dict[str, Any] = Field(default_factory=dict)
    score_components: Dict[str, Any] = Field(default_factory=dict)
    penalties: Dict[str, Any] = Field(default_factory=dict)
    triggered_rules: List[str] = Field(default_factory=list)
    final_score: float = 0.0
    final_status: str = "UNVERIFIED"
    ground_truth_status: str = ""
    correct: bool = False
    error_category: str = "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
