"""Staged Pipeline Tracer for Phase 7.2.

Captures complete step-by-step telemetry across every single stage of processing:
[Ground Truth -> OCR -> Normalization -> Extraction -> Provenance -> Assembly ->
 PIN Recovery -> Verification Input -> Candidate Generation -> Ranking ->
 Geographic Evidence -> Ambiguity Detection -> Decision Engine -> Final Status]
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.document.models import ExtractedAddressCandidate
from app.schemas.document import DocumentVerificationResponse
from app.schemas.verification import VerificationResponse


class StagedPipelineTrace(BaseModel):
    case_id: str
    ground_truth: Dict[str, Any] = Field(default_factory=dict)
    ocr: Dict[str, Any] = Field(default_factory=dict)
    normalized_text: str = ""
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    field_provenance: Dict[str, Any] = Field(default_factory=dict)
    assembled_address: str = ""
    pin_recovery: Dict[str, Any] = Field(default_factory=dict)
    verification_input: Dict[str, Any] = Field(default_factory=dict)
    candidate_generation: Dict[str, Any] = Field(default_factory=dict)
    ranking: Dict[str, Any] = Field(default_factory=dict)
    geographic_evidence: Dict[str, Any] = Field(default_factory=dict)
    ambiguity: Dict[str, Any] = Field(default_factory=dict)
    decision_engine: Dict[str, Any] = Field(default_factory=dict)
    final_status: Dict[str, Any] = Field(default_factory=dict)


class PipelineTracer:
    """Collects and formats structured execution traces without logging PII."""

    @classmethod
    def capture_trace(
        cls,
        case_id: str,
        ground_truth: Optional[Dict[str, Any]],
        doc_response: DocumentVerificationResponse,
        normalized_text: str = "",
    ) -> StagedPipelineTrace:
        candidate = doc_response.primary_candidate
        verif: Optional[VerificationResponse] = getattr(candidate, "verification_result", None) or doc_response.verification

        # 1. OCR Telemetry
        ocr_info = {
            "status": doc_response.ocr.status,
            "engine": doc_response.ocr.engine,
            "mean_confidence": doc_response.ocr.mean_confidence,
            "primary_language": doc_response.ocr.primary_language,
            "quality_status": doc_response.ocr.quality_status.value if hasattr(doc_response.ocr.quality_status, "value") else str(doc_response.ocr.quality_status),
        }

        # 2. Field Extractions & Provenance
        extracted = {}
        provenance = {}
        if candidate and candidate.fields:
            for fname, f in candidate.fields.items():
                extracted[fname] = f.normalized_value or f.raw_value
                provenance[fname] = {
                    "method": f.extraction_method.value if hasattr(f.extraction_method, "value") else str(f.extraction_method),
                    "confidence": f.confidence,
                    "correction_reason": f.correction_reason,
                }

        # 3. Candidate Generation & Ranking Telemetry
        cand_gen_info = {}
        ranking_info = {}
        geo_evidence = {}
        ambiguity_info = {}
        decision_info = {}
        final_info = {}

        if verif:
            top_cand = verif.candidate_matches[0].candidate if (verif.candidate_matches and len(verif.candidate_matches) > 0) else None
            top_res = verif.candidate_matches[0] if (verif.candidate_matches and len(verif.candidate_matches) > 0) else None

            cand_gen_info = {
                "top_candidate": top_cand.name if top_cand else None,
                "top_candidate_type": top_cand.entity_type.value if (top_cand and hasattr(top_cand.entity_type, "value")) else (str(top_cand.entity_type) if top_cand else None),
                "parent_district": top_cand.district if top_cand else None,
                "parent_state": top_cand.state if top_cand else None,
            }

            if top_res and top_res.ranking_explanation:
                ranking_info = {
                    "rank": getattr(top_res.ranking_explanation, "rank", 1),
                    "penalties": [p.model_dump() for p in getattr(top_res.ranking_explanation, "applied_penalties", [])],
                    "total_penalty": getattr(top_res.ranking_explanation, "total_penalty_deduction", 0.0),
                    "channels": getattr(top_res.ranking_explanation, "retrieval_channels", []),
                }

            geo_evidence = {
                "score": verif.score,
                "score_breakdown": verif.score_breakdown.model_dump() if verif.score_breakdown else {},
                "hierarchy_valid": verif.administrative_hierarchy.is_consistent if verif.administrative_hierarchy else False,
                "pin_valid": verif.pin_verification.matched if verif.pin_verification else False,
                "boundary_verified": verif.boundary_verification.point_inside_district if verif.boundary_verification else False,
            }

            if verif.ambiguity:
                ambiguity_info = {
                    "is_ambiguous": verif.ambiguity.is_ambiguous,
                    "reason": verif.ambiguity.ambiguity_reason,
                    "candidate_count": len(verif.ambiguity.top_candidates) if verif.ambiguity.top_candidates else 0,
                }

            status_val = verif.status.value if hasattr(verif.status, "value") else str(verif.status)
            decision_info = {
                "triggered_rules": [e.code for e in verif.evidence] if verif.evidence else [],
                "primary_status": status_val,
                "explanation": verif.explanation,
            }

            final_info = {
                "status": status_val,
                "score": verif.score,
            }

        return StagedPipelineTrace(
            case_id=case_id,
            ground_truth=ground_truth or {},
            ocr=ocr_info,
            normalized_text=normalized_text,
            extracted_fields=extracted,
            field_provenance=provenance,
            assembled_address=candidate.assembled_address if candidate else "",
            pin_recovery={
                "recovered": candidate.pin_recovered if candidate else False,
            },
            verification_input={
                "address": candidate.assembled_address if candidate else "",
                "structured": candidate.structured_components if candidate else {},
            },
            candidate_generation=cand_gen_info,
            ranking=ranking_info,
            geographic_evidence=geo_evidence,
            ambiguity=ambiguity_info,
            decision_engine=decision_info,
            final_status=final_info,
        )
