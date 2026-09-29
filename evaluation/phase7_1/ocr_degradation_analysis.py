"""OCR Degradation Impact Analysis for Phase 7.1.

Measures the delta in verification accuracy and entity retrieval when processing:
1. Clean Ground-Truth Typed Text (Ideal Scenario)
2. OCR-Extracted Text from Image/Document (Real-World Pipeline)

Quantifies the exact degradation caused by optical noise, character substitutions,
and OCR bounding box segmentation errors.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DegradationDelta(BaseModel):
    metric_name: str
    clean_text_score: float
    ocr_extracted_score: float
    degradation_delta: float
    percentage_retention: float


class OCRDegradationSummary(BaseModel):
    total_compared_cases: int
    recall_at_1_delta: DegradationDelta
    recall_at_5_delta: DegradationDelta
    district_accuracy_delta: DegradationDelta
    locality_accuracy_delta: DegradationDelta
    verification_status_delta: DegradationDelta


class OCRDegradationAnalyzer:
    """Computes comparison deltas between clean text verification and OCR pipeline."""

    @classmethod
    def analyze_degradation(
        cls,
        clean_evaluations: List[Dict[str, Any]],
        ocr_evaluations: List[Dict[str, Any]],
    ) -> OCRDegradationSummary:
        total = min(len(clean_evaluations), len(ocr_evaluations))
        if total == 0:
            dummy_delta = DegradationDelta(
                metric_name="None",
                clean_text_score=0.0,
                ocr_extracted_score=0.0,
                degradation_delta=0.0,
                percentage_retention=100.0,
            )
            return OCRDegradationSummary(
                total_compared_cases=0,
                recall_at_1_delta=dummy_delta,
                recall_at_5_delta=dummy_delta,
                district_accuracy_delta=dummy_delta,
                locality_accuracy_delta=dummy_delta,
                verification_status_delta=dummy_delta,
            )

        def _calc_delta(name: str, clean_key: str, ocr_key: str) -> DegradationDelta:
            clean_correct = sum(1 for c in clean_evaluations[:total] if c.get(clean_key, False))
            ocr_correct = sum(1 for o in ocr_evaluations[:total] if o.get(ocr_key, False))

            clean_score = round((clean_correct / total) * 100.0, 2)
            ocr_score = round((ocr_correct / total) * 100.0, 2)
            delta = round(ocr_score - clean_score, 2)
            retention = round((ocr_score / clean_score * 100.0), 2) if clean_score > 0 else 100.0

            return DegradationDelta(
                metric_name=name,
                clean_text_score=clean_score,
                ocr_extracted_score=ocr_score,
                degradation_delta=delta,
                percentage_retention=retention,
            )

        return OCRDegradationSummary(
            total_compared_cases=total,
            recall_at_1_delta=_calc_delta("Recall@1", "recall_at_1", "recall_at_1"),
            recall_at_5_delta=_calc_delta("Recall@5", "recall_at_5", "recall_at_5"),
            district_accuracy_delta=_calc_delta("District Accuracy", "district_match", "district_match"),
            locality_accuracy_delta=_calc_delta("Locality Accuracy", "locality_match", "locality_match"),
            verification_status_delta=_calc_delta("Verification Status Accuracy", "status_match", "status_match"),
        )
