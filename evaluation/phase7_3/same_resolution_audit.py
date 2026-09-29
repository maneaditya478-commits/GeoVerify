"""Same-Resolution-Different-Status Auditor for Phase 7.3.

Audits cases where the candidate entity was resolved identically between Clean and OCR input,
yet the final verification decision status diverged.
"""

import os
import csv
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SameResolutionGapCase(BaseModel):
    case_id: str
    clean_status: str
    ocr_status: str
    candidate_same: bool
    clean_score: float
    ocr_score: float
    score_delta: float
    clean_fields: str
    ocr_fields: str
    missing_fields: str
    conflicting_fields: str
    provenance_changes: str
    triggered_rules_clean: str
    triggered_rules_ocr: str
    root_cause: str


class SameResolutionAuditor:
    """Audits divergence in status when candidate resolution is identical."""

    @classmethod
    def audit_case(
        cls,
        case_id: str,
        clean_res: Dict[str, Any],
        ocr_res: Dict[str, Any],
        ground_truth: Dict[str, Any],
    ) -> Optional[SameResolutionGapCase]:
        clean_top_cand = clean_res.get("top_candidate")
        ocr_top_cand = ocr_res.get("top_candidate")
        candidate_same = bool(clean_top_cand and ocr_top_cand and clean_top_cand == ocr_top_cand)

        clean_status = clean_res.get("status", "UNVERIFIED")
        ocr_status = ocr_res.get("status", "UNVERIFIED")

        # Disagreement case where candidates are the same
        if candidate_same and clean_status != ocr_status:
            clean_score = float(clean_res.get("score", 0.0))
            ocr_score = float(ocr_res.get("score", 0.0))
            score_delta = round(ocr_score - clean_score, 2)

            clean_f = clean_res.get("fields", {})
            ocr_f = ocr_res.get("fields", {})

            missing = [k for k in clean_f if k not in ocr_f]
            conflicts = [k for k in ocr_f if k in clean_f and ocr_f[k] != clean_f[k]]

            # Root cause diagnosis
            if "pincode" in conflicts:
                root_cause = "OCR_EXTRACTION_ERROR"
            elif missing and ("locality" in missing or "district" in missing):
                root_cause = "MISSING_INFORMATION"
            elif "COMPLETENESS" in str(ocr_res.get("rules", [])):
                root_cause = "COMPLETENESS_ERROR"
            elif score_delta < -15.0 and not conflicts:
                root_cause = "DECISION_RULE_ERROR"
            elif ocr_status == "NEEDS_REVIEW" and clean_status in ["VERIFIED", "CONSISTENT"]:
                root_cause = "THRESHOLD_ERROR"
            elif conflicts:
                root_cause = "TRUE_GEOGRAPHIC_CONFLICT"
            else:
                root_cause = "MISSING_INFORMATION"

            return SameResolutionGapCase(
                case_id=case_id,
                clean_status=clean_status,
                ocr_status=ocr_status,
                candidate_same=candidate_same,
                clean_score=clean_score,
                ocr_score=ocr_score,
                score_delta=score_delta,
                clean_fields=";".join(f"{k}={v}" for k, v in clean_f.items()),
                ocr_fields=";".join(f"{k}={v}" for k, v in ocr_f.items()),
                missing_fields=",".join(missing) if missing else "none",
                conflicting_fields=",".join(conflicts) if conflicts else "none",
                provenance_changes=";".join(f"{k}:{v}" for k, v in ocr_res.get("provenance", {}).items()),
                triggered_rules_clean=",".join(clean_res.get("rules", [])),
                triggered_rules_ocr=",".join(ocr_res.get("rules", [])),
                root_cause=root_cause,
            )
        return None

    @classmethod
    def export_csv(cls, gap_cases: List[SameResolutionGapCase], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id",
                "clean_status",
                "ocr_status",
                "candidate_same",
                "clean_score",
                "ocr_score",
                "score_delta",
                "clean_fields",
                "ocr_fields",
                "missing_fields",
                "conflicting_fields",
                "provenance_changes",
                "triggered_rules_clean",
                "triggered_rules_ocr",
                "root_cause",
            ])
            for c in gap_cases:
                writer.writerow([
                    c.case_id,
                    c.clean_status,
                    c.ocr_status,
                    c.candidate_same,
                    c.clean_score,
                    c.ocr_score,
                    c.score_delta,
                    c.clean_fields,
                    c.ocr_fields,
                    c.missing_fields,
                    c.conflicting_fields,
                    c.provenance_changes,
                    c.triggered_rules_clean,
                    c.triggered_rules_ocr,
                    c.root_cause,
                ])
