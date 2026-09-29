"""Error Matrix and Root-Cause Diagnostic Categorization for Phase 7.1.

Classifies all failures across the document extraction and geographic verification pipeline into:
1. Primary Root Cause Categories:
   - OCR_CHARACTER_ERROR: OCR misrecognized characters/digits
   - REGION_DETECTION_ERROR: Address bounding region omitted or truncated
   - DISTRICT_EXTRACTION_ERROR: District omitted or wrong admin entity parsed
   - LOCALITY_EXTRACTION_ERROR: Multi-token locality split or missed
   - PIN_EXTRACTION_ERROR: 6-digit postal code missed or corrupted
   - ENTITY_RESOLUTION_ERROR: Candidate generator / ranker retrieved suboptimal match
   - DECISION_ENGINE_ERROR: Status decision rule discrepancy (e.g., VERIFIED vs PARTIALLY_VERIFIED)
   - NEGATIVE_FALSE_POSITIVE: Address falsely detected on non-address document
2. Earliest Failure Stage:
   - IMAGE_PREPROCESSING
   - OCR_ENGINE
   - REGION_DETECTOR
   - FIELD_EXTRACTOR
   - PIN_RECOVERY
   - CANDIDATE_GENERATOR
   - ENTITY_RANKER
   - DECISION_ENGINE
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FailureRootCause(str, Enum):
    NONE = "NONE"
    OCR_CHARACTER_ERROR = "OCR_CHARACTER_ERROR"
    REGION_DETECTION_ERROR = "REGION_DETECTION_ERROR"
    DISTRICT_EXTRACTION_ERROR = "DISTRICT_EXTRACTION_ERROR"
    LOCALITY_EXTRACTION_ERROR = "LOCALITY_EXTRACTION_ERROR"
    PIN_EXTRACTION_ERROR = "PIN_EXTRACTION_ERROR"
    ENTITY_RESOLUTION_ERROR = "ENTITY_RESOLUTION_ERROR"
    DECISION_ENGINE_ERROR = "DECISION_ENGINE_ERROR"
    NEGATIVE_FALSE_POSITIVE = "NEGATIVE_FALSE_POSITIVE"


class PipelineFailureStage(str, Enum):
    NONE = "NONE"
    IMAGE_PREPROCESSING = "IMAGE_PREPROCESSING"
    OCR_ENGINE = "OCR_ENGINE"
    REGION_DETECTOR = "REGION_DETECTOR"
    FIELD_EXTRACTOR = "FIELD_EXTRACTOR"
    PIN_RECOVERY = "PIN_RECOVERY"
    CANDIDATE_GENERATOR = "CANDIDATE_GENERATOR"
    ENTITY_RANKER = "ENTITY_RANKER"
    DECISION_ENGINE = "DECISION_ENGINE"


class ErrorDiagnosis(BaseModel):
    case_id: str
    is_failure: bool
    root_cause: FailureRootCause = FailureRootCause.NONE
    earliest_failure_stage: PipelineFailureStage = PipelineFailureStage.NONE
    failure_details: str = ""
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    ground_truth_fields: Dict[str, Any] = Field(default_factory=dict)


class ErrorMatrixAnalyzer:
    """Diagnoses and categorizes failures across OCR extraction and geographic verification."""

    @classmethod
    def diagnose_case(
        cls,
        case_id: str,
        is_negative: bool,
        doc_cer: float,
        region_detected: bool,
        extracted_fields: Dict[str, Optional[str]],
        ground_truth: Optional[Dict[str, Optional[str]]],
        actual_status: str,
        expected_status: str,
    ) -> ErrorDiagnosis:
        # 1. Negative case analysis
        if is_negative:
            if region_detected and any(extracted_fields.values()):
                return ErrorDiagnosis(
                    case_id=case_id,
                    is_failure=True,
                    root_cause=FailureRootCause.NEGATIVE_FALSE_POSITIVE,
                    earliest_failure_stage=PipelineFailureStage.REGION_DETECTOR,
                    failure_details="Address falsely detected on negative non-address document",
                    extracted_fields=extracted_fields,
                )
            return ErrorDiagnosis(case_id=case_id, is_failure=False)

        if not ground_truth:
            return ErrorDiagnosis(case_id=case_id, is_failure=False)

        # 2. Region detection failure
        if not region_detected:
            return ErrorDiagnosis(
                case_id=case_id,
                is_failure=True,
                root_cause=FailureRootCause.REGION_DETECTION_ERROR,
                earliest_failure_stage=PipelineFailureStage.REGION_DETECTOR,
                failure_details="Address region was not detected in document",
                extracted_fields=extracted_fields,
                ground_truth_fields=ground_truth,
            )

        # 3. Check OCR Character degradation
        has_ocr_char_error = doc_cer > 0.05

        # 4. Check Field Extraction discrepancies
        pin_gt = ground_truth.get("pincode")
        pin_pred = extracted_fields.get("pincode")
        pin_mismatch = bool(pin_gt and pin_pred != pin_gt)

        dist_gt = ground_truth.get("district")
        dist_pred = extracted_fields.get("district")
        dist_mismatch = bool(dist_gt and (not dist_pred or dist_gt.lower() not in dist_pred.lower()))

        loc_gt = ground_truth.get("locality")
        loc_pred = extracted_fields.get("locality")
        loc_mismatch = bool(loc_gt and (not loc_pred or loc_gt.lower() not in loc_pred.lower()))

        status_mismatch = actual_status != expected_status

        # Determine earliest failure stage and root cause
        if pin_mismatch:
            if has_ocr_char_error:
                return ErrorDiagnosis(
                    case_id=case_id,
                    is_failure=True,
                    root_cause=FailureRootCause.OCR_CHARACTER_ERROR,
                    earliest_failure_stage=PipelineFailureStage.OCR_ENGINE,
                    failure_details=f"PIN corrupted in OCR: expected {pin_gt}, got {pin_pred}",
                    extracted_fields=extracted_fields,
                    ground_truth_fields=ground_truth,
                )
            return ErrorDiagnosis(
                case_id=case_id,
                is_failure=True,
                root_cause=FailureRootCause.PIN_EXTRACTION_ERROR,
                earliest_failure_stage=PipelineFailureStage.FIELD_EXTRACTOR,
                failure_details=f"PIN extraction failed: expected {pin_gt}, got {pin_pred}",
                extracted_fields=extracted_fields,
                ground_truth_fields=ground_truth,
            )

        if dist_mismatch:
            return ErrorDiagnosis(
                case_id=case_id,
                is_failure=True,
                root_cause=FailureRootCause.DISTRICT_EXTRACTION_ERROR,
                earliest_failure_stage=PipelineFailureStage.FIELD_EXTRACTOR,
                failure_details=f"District extraction mismatch: expected {dist_gt}, got {dist_pred}",
                extracted_fields=extracted_fields,
                ground_truth_fields=ground_truth,
            )

        if loc_mismatch:
            return ErrorDiagnosis(
                case_id=case_id,
                is_failure=True,
                root_cause=FailureRootCause.LOCALITY_EXTRACTION_ERROR,
                earliest_failure_stage=PipelineFailureStage.FIELD_EXTRACTOR,
                failure_details=f"Locality extraction mismatch: expected {loc_gt}, got {loc_pred}",
                extracted_fields=extracted_fields,
                ground_truth_fields=ground_truth,
            )

        if status_mismatch:
            return ErrorDiagnosis(
                case_id=case_id,
                is_failure=True,
                root_cause=FailureRootCause.DECISION_ENGINE_ERROR,
                earliest_failure_stage=PipelineFailureStage.DECISION_ENGINE,
                failure_details=f"Verification status mismatch: expected {expected_status}, got {actual_status}",
                extracted_fields=extracted_fields,
                ground_truth_fields=ground_truth,
            )

        return ErrorDiagnosis(
            case_id=case_id,
            is_failure=False,
            extracted_fields=extracted_fields,
            ground_truth_fields=ground_truth,
        )

    @classmethod
    def aggregate_error_matrix(cls, diagnoses: List[ErrorDiagnosis]) -> Dict[str, Any]:
        """Summarizes error matrix counts by root cause and earliest stage."""
        root_cause_counts: Dict[str, int] = {rc.value: 0 for rc in FailureRootCause}
        stage_counts: Dict[str, int] = {st.value: 0 for st in PipelineFailureStage}
        total_failures = 0

        for d in diagnoses:
            if d.is_failure:
                total_failures += 1
                root_cause_counts[d.root_cause.value] += 1
                stage_counts[d.earliest_failure_stage.value] += 1

        return {
            "total_evaluated": len(diagnoses),
            "total_failures": total_failures,
            "failure_rate_pct": round((total_failures / len(diagnoses) * 100.0), 2) if diagnoses else 0.0,
            "root_cause_distribution": root_cause_counts,
            "earliest_failure_stage_distribution": stage_counts,
        }
