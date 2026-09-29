"""Clean vs OCR Status Gap Decomposer for Phase 7.3.

Decomposes the Clean vs OCR status accuracy gap into exact attribution categories:
1. OCR_EXTRACTION_ERROR
2. OCR_DIGIT_ERROR
3. NORMALIZATION_ERROR
4. FIELD_LOSS_ASSEMBLY_ERROR
5. ENTITY_RESOLUTION_DRIFT
6. DECISION_THRESHOLD_COMPLETENESS
7. PROVENANCE_DISCREPANCY
"""

import os
import csv
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class GapAttributionRow(BaseModel):
    cause: str
    cases: int
    percentage: float
    status_impact_pct: float
    corrective_action: str


class OCRGapDecomposer:
    """Attributes and quantifies every component of the Clean vs OCR status gap."""

    @classmethod
    def decompose_gap(
        cls,
        clean_accuracy: float,
        ocr_accuracy: float,
        paired_cases: List[Dict[str, Any]],
    ) -> List[GapAttributionRow]:
        total_paired = len(paired_cases)
        total_gap = max(0.0, round(clean_accuracy - ocr_accuracy, 2))

        # Categorize causes
        counts = {
            "OCR Extraction Noise (Blur / Heavy Skew)": 0,
            "OCR Digit / PIN Misreading": 0,
            "Address Region Segmentation Offset": 0,
            "Multi-Token Locality Field Loss": 0,
            "Address Assembly Format Loss": 0,
            "Entity Resolution Candidate Drift": 0,
            "Strict Completeness / Partial Penalty": 0,
            "Decision Threshold Sensitivity": 0,
        }

        for c in paired_cases:
            clean_correct = c.get("clean_status_match", False)
            ocr_correct = c.get("ocr_status_match", False)
            if clean_correct and not ocr_correct:
                # Disagreement case
                root = c.get("root_cause", "")
                if "OCR_ERROR" in root or "OCR_NOISE" in root:
                    counts["OCR Extraction Noise (Blur / Heavy Skew)"] += 1
                elif "PIN" in root or "DIGIT" in root:
                    counts["OCR Digit / PIN Misreading"] += 1
                elif "REGION" in root:
                    counts["Address Region Segmentation Offset"] += 1
                elif "FIELD" in root:
                    counts["Multi-Token Locality Field Loss"] += 1
                elif "ASSEMBLY" in root:
                    counts["Address Assembly Format Loss"] += 1
                elif "ENTITY" in root or "RESOLUTION" in root:
                    counts["Entity Resolution Candidate Drift"] += 1
                elif "COMPLETENESS" in root:
                    counts["Strict Completeness / Partial Penalty"] += 1
                else:
                    counts["Decision Threshold Sensitivity"] += 1

        total_disagreements = max(1, sum(counts.values()))
        rows = []
        for cause, count in counts.items():
            pct = round(count / total_paired * 100.0, 2) if total_paired > 0 else 0.0
            impact = round(count / total_disagreements * total_gap, 2)
            if "OCR" in cause:
                action = "IMPROVE_IMAGE_PREPROCESSING_AND_NORMALIZATION"
            elif "PIN" in cause:
                action = "APPLY_PIN_FIRST_RECOVERY"
            elif "Region" in cause:
                action = "ENHANCE_ADDRESS_BLOCK_HEURISTICS"
            elif "Field" in cause or "Assembly" in cause:
                action = "PRESERVE_STRUCTURED_FIELDS_IN_HANDOFF"
            elif "Completeness" in cause:
                action = "CALIBRATE_PARTIAL_SEMANTICS_NO_PENALTY"
            else:
                action = "CALIBRATE_DECISION_THRESHOLDS"

            rows.append(GapAttributionRow(
                cause=cause,
                cases=count,
                percentage=pct,
                status_impact_pct=impact,
                corrective_action=action,
            ))

        return rows

    @classmethod
    def export_csv(cls, rows: List[GapAttributionRow], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "cause",
                "cases",
                "percentage",
                "status_impact_pct",
                "corrective_action",
            ])
            for r in rows:
                writer.writerow([
                    r.cause,
                    r.cases,
                    r.percentage,
                    r.status_impact_pct,
                    r.corrective_action,
                ])
