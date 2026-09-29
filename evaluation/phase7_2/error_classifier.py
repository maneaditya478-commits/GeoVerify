"""Earliest Failure Root-Cause Error Classifier for Phase 7.2.

Pinpoints the exact earliest stage where the correct ground truth was lost across:
1. OCR_ERROR
2. NORMALIZATION_ERROR
3. ADDRESS_REGION_ERROR
4. FIELD_EXTRACTION_ERROR
5. FIELD_PROVENANCE_ERROR
6. ADDRESS_ASSEMBLY_ERROR
7. PIN_RECOVERY_ERROR
8. ENTITY_RESOLUTION_ERROR
9. CANDIDATE_RECALL_ERROR
10. RANKING_ERROR
11. GEOGRAPHIC_EVIDENCE_ERROR
12. AMBIGUITY_ERROR
13. DECISION_ENGINE_ERROR
14. BENCHMARK_LABEL_ERROR
15. UNKNOWN
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from evaluation.phase7_2.pipeline_trace import StagedPipelineTrace


class FailureStageClass(str, Enum):
    NONE = "NONE"
    OCR_ERROR = "OCR_ERROR"
    NORMALIZATION_ERROR = "NORMALIZATION_ERROR"
    ADDRESS_REGION_ERROR = "ADDRESS_REGION_ERROR"
    FIELD_EXTRACTION_ERROR = "FIELD_EXTRACTION_ERROR"
    FIELD_PROVENANCE_ERROR = "FIELD_PROVENANCE_ERROR"
    ADDRESS_ASSEMBLY_ERROR = "ADDRESS_ASSEMBLY_ERROR"
    PIN_RECOVERY_ERROR = "PIN_RECOVERY_ERROR"
    ENTITY_RESOLUTION_ERROR = "ENTITY_RESOLUTION_ERROR"
    CANDIDATE_RECALL_ERROR = "CANDIDATE_RECALL_ERROR"
    RANKING_ERROR = "RANKING_ERROR"
    GEOGRAPHIC_EVIDENCE_ERROR = "GEOGRAPHIC_EVIDENCE_ERROR"
    AMBIGUITY_ERROR = "AMBIGUITY_ERROR"
    DECISION_ENGINE_ERROR = "DECISION_ENGINE_ERROR"
    BENCHMARK_LABEL_ERROR = "BENCHMARK_LABEL_ERROR"
    UNKNOWN = "UNKNOWN"


class CaseFailureDiagnosis(BaseModel):
    case_id: str
    is_failure: bool
    earliest_error: FailureStageClass = FailureStageClass.NONE
    explanation: str = ""
    evidence_trail: Dict[str, Any] = Field(default_factory=dict)


class EarliestFailureClassifier:
    """Classifies root cause by checking each pipeline stage sequentially."""

    @classmethod
    def classify_trace(cls, trace: StagedPipelineTrace, is_negative: bool = False) -> CaseFailureDiagnosis:
        gt = trace.ground_truth
        if is_negative:
            # Negative document: should produce no valid address or NOT_FOUND / UNABLE_TO_VERIFY
            final_status = trace.final_status.get("status", "UNVERIFIED")
            if trace.extracted_fields and final_status in ["VERIFIED", "CONSISTENT"]:
                return CaseFailureDiagnosis(
                    case_id=trace.case_id,
                    is_failure=True,
                    earliest_error=FailureStageClass.ADDRESS_REGION_ERROR,
                    explanation="Negative document falsely segmented and verified as valid address",
                    evidence_trail={"extracted": trace.extracted_fields, "status": final_status},
                )
            return CaseFailureDiagnosis(case_id=trace.case_id, is_failure=False)

        if not gt:
            return CaseFailureDiagnosis(case_id=trace.case_id, is_failure=False)

        # 1. Check Address Region Detection
        if not trace.extracted_fields and not trace.assembled_address:
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.ADDRESS_REGION_ERROR,
                explanation="Address region failed detection or segmentation",
                evidence_trail={"ground_truth": gt},
            )

        # 2. Check OCR / Field Extraction
        gt_pin = gt.get("pincode")
        pred_pin = trace.extracted_fields.get("pincode")
        if gt_pin and pred_pin and pred_pin != gt_pin:
            # Check if OCR corrupted it
            if any(c.isalpha() for c in trace.ocr.get("text", "")):
                return CaseFailureDiagnosis(
                    case_id=trace.case_id,
                    is_failure=True,
                    earliest_error=FailureStageClass.OCR_ERROR,
                    explanation=f"OCR character corruption in PIN: expected {gt_pin}, extracted {pred_pin}",
                    evidence_trail={"gt_pin": gt_pin, "pred_pin": pred_pin},
                )
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.FIELD_EXTRACTION_ERROR,
                explanation=f"Field extraction error in PIN: expected {gt_pin}, got {pred_pin}",
                evidence_trail={"gt_pin": gt_pin, "pred_pin": pred_pin},
            )

        gt_dist = gt.get("district")
        pred_dist = trace.extracted_fields.get("district")
        if gt_dist and pred_dist and gt_dist.lower() not in pred_dist.lower() and pred_dist.lower() not in gt_dist.lower():
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.FIELD_EXTRACTION_ERROR,
                explanation=f"District extraction mismatch: expected {gt_dist}, extracted {pred_dist}",
                evidence_trail={"gt_dist": gt_dist, "pred_dist": pred_dist},
            )

        # 3. Check Address Assembly
        if gt_pin and gt_pin not in trace.assembled_address and pred_pin == gt_pin:
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.ADDRESS_ASSEMBLY_ERROR,
                explanation="Extracted PIN omitted from assembled address string",
                evidence_trail={"extracted_pin": pred_pin, "assembled_address": trace.assembled_address},
            )

        # 4. Check Entity Resolution & Candidate Ranking
        cand_top = trace.candidate_generation.get("top_candidate")
        gt_loc = gt.get("locality")
        if gt_loc and cand_top and gt_loc.lower() not in cand_top.lower() and cand_top.lower() not in gt_loc.lower():
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.ENTITY_RESOLUTION_ERROR,
                explanation=f"Entity resolution selected wrong candidate: expected {gt_loc}, resolved {cand_top}",
                evidence_trail={"gt_locality": gt_loc, "candidate": cand_top},
            )

        # 5. Check Ambiguity
        if trace.ambiguity.get("is_ambiguous", False) and not gt.get("is_genuinely_ambiguous", False):
            # False positive ambiguity
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.AMBIGUITY_ERROR,
                explanation="False positive ambiguity triggered on unambiguous address",
                evidence_trail=trace.ambiguity,
            )

        # 6. Check Verification Status & Decision Engine
        expected_status = gt.get("expected_status", "VERIFIED")
        final_status = trace.final_status.get("status", "UNVERIFIED")
        score = trace.final_status.get("score", 0.0)

        status_matches = (final_status == expected_status) or (final_status in ["VERIFIED", "CONSISTENT"] and expected_status == "VERIFIED")

        if not status_matches:
            # Geographic evidence was collected, candidate was correct, but decision rule rejected or downgraded
            return CaseFailureDiagnosis(
                case_id=trace.case_id,
                is_failure=True,
                earliest_error=FailureStageClass.DECISION_ENGINE_ERROR,
                explanation=f"Decision engine returned {final_status} (score: {score}) instead of {expected_status}",
                evidence_trail={
                    "expected": expected_status,
                    "actual": final_status,
                    "score": score,
                    "geo_evidence": trace.geographic_evidence,
                    "decision": trace.decision_engine,
                },
            )

        return CaseFailureDiagnosis(case_id=trace.case_id, is_failure=False)
