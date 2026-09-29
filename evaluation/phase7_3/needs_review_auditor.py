"""NEEDS_REVIEW Class Calibration Auditor for Phase 7.3.

Deep-dives into the NEEDS_REVIEW decision class:
- Measures Precision, Recall, F1, and Support
- Separates True Review vs False Positive Review vs False Negative Review
- Identifies specific trigger reasons (PIN mismatch, score band, partial address, missing coordinates)
"""

import os
import csv
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class NeedsReviewCaseRecord(BaseModel):
    case_id: str
    category: str
    expected_status: str
    predicted_status: str
    decision_type: str  # TRUE_POSITIVE, FALSE_POSITIVE, FALSE_NEGATIVE
    decision_score: float
    trigger_reason: str
    has_pin_mismatch: bool
    is_partial_address: bool
    missing_coordinates: bool
    corrective_action: str


class NeedsReviewSummary(BaseModel):
    total_evaluated: int = 0
    true_positive_count: int = 0
    false_positive_count: int = 0
    false_negative_count: int = 0
    true_negative_count: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    records: List[NeedsReviewCaseRecord] = Field(default_factory=list)


class NeedsReviewAuditor:
    """Audits and calibrates the NEEDS_REVIEW decision class."""

    @classmethod
    def audit_cases(cls, cases_data: List[Dict[str, Any]]) -> NeedsReviewSummary:
        tp = 0
        fp = 0
        fn = 0
        tn = 0
        records = []

        for d in cases_data:
            case_id = d.get("case_id", "")
            cat = d.get("category", "")
            exp = d.get("expected_status", "")
            pred = d.get("predicted_status", "")
            score = float(d.get("score", 0.0))
            rules = d.get("triggered_rules", [])

            is_exp_nr = (exp == "NEEDS_REVIEW")
            is_pred_nr = (pred == "NEEDS_REVIEW")

            has_pin_mism = any("PIN" in r and "DISCREPANCY" in r for r in rules)
            is_partial = any("MISSING" in r for r in rules)
            missing_coords = any("NO_COORDINATES" in r for r in rules)

            if is_exp_nr and is_pred_nr:
                tp += 1
                dec_type = "TRUE_POSITIVE"
                trigger = "BORDERLINE_GEOGRAPHIC_EVIDENCE" if score < 70 else "PIN_DISCREPANCY"
                action = "APPROPRIATE_OPERATOR_REVIEW"
            elif not is_exp_nr and is_pred_nr:
                fp += 1
                dec_type = "FALSE_POSITIVE"
                trigger = "MISSING_COORDINATES_PENALTY" if missing_coords else ("PARTIAL_ADDRESS_THRESHOLD" if is_partial else "SCORE_BAND_DOWNGRADE")
                action = "CALIBRATE_PARTIAL_SEMANTICS"
            elif is_exp_nr and not is_pred_nr:
                fn += 1
                dec_type = "FALSE_NEGATIVE"
                trigger = "OVER_OPTIMISTIC_UPGRADE" if pred in ["VERIFIED", "CONSISTENT"] else "OVER_PENALIZED_INCONSISTENT"
                action = "STRENGTHEN_REVIEW_BOUNDARY"
            else:
                tn += 1
                continue

            records.append(NeedsReviewCaseRecord(
                case_id=case_id,
                category=cat,
                expected_status=exp,
                predicted_status=pred,
                decision_type=dec_type,
                decision_score=score,
                trigger_reason=trigger,
                has_pin_mismatch=has_pin_mism,
                is_partial_address=is_partial,
                missing_coordinates=missing_coords,
                corrective_action=action,
            ))

        prec = round(tp / (tp + fp) * 100.0, 2) if (tp + fp) > 0 else 0.0
        rec = round(tp / (tp + fn) * 100.0, 2) if (tp + fn) > 0 else 0.0
        f1 = round(2 * prec * rec / (prec + rec), 2) if (prec + rec) > 0 else 0.0

        return NeedsReviewSummary(
            total_evaluated=len(cases_data),
            true_positive_count=tp,
            false_positive_count=fp,
            false_negative_count=fn,
            true_negative_count=tn,
            precision=prec,
            recall=rec,
            f1_score=f1,
            records=records,
        )

    @classmethod
    def export_csv(cls, summary: NeedsReviewSummary, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id",
                "category",
                "expected_status",
                "predicted_status",
                "decision_type",
                "decision_score",
                "trigger_reason",
                "has_pin_mismatch",
                "is_partial_address",
                "missing_coordinates",
                "corrective_action",
            ])
            for r in summary.records:
                writer.writerow([
                    r.case_id,
                    r.category,
                    r.expected_status,
                    r.predicted_status,
                    r.decision_type,
                    r.decision_score,
                    r.trigger_reason,
                    r.has_pin_mismatch,
                    r.is_partial_address,
                    r.missing_coordinates,
                    r.corrective_action,
                ])
