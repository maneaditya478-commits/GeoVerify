"""Automated Error Categorization and Diagnostic Analyzer for GeoVerify India."""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from pathlib import Path
from evaluation.schema import EvaluationResultRecord


class ErrorAnalyzer:
    """Classifies verification errors into diagnostic failure categories and generates error logs."""

    @staticmethod
    def classify_error(record: EvaluationResultRecord) -> str:
        cat = record.category.upper()
        
        # 1. Ambiguity Failures
        if record.expected_ambiguity != record.predicted_ambiguity:
            return "AMBIGUITY"

        # 2. Status Discrepancies
        if not record.status_matched:
            if "PIN" in cat:
                return "PIN_MISMATCH"
            elif "STATE" in cat or "DISTRICT" in cat or "SUBDISTRICT" in cat or "HIERARCHY" in cat or "MISMATCH" in cat:
                return "ADMINISTRATIVE_MISMATCH"
            elif "DEVANAGARI" in cat or "MIXED" in cat:
                return "TRANSLITERATION_FAILURE"
            elif "TYPO" in cat or "MISSPELLING" in cat:
                return "TYPOGRAPHY"
            elif "INCOMPLETE" in cat:
                return "INCOMPLETE_ADDRESS"
            elif record.predicted_status == "UNABLE_TO_VERIFY":
                return "PARSING_ERROR"
            else:
                return "SCORING_ERROR"

        # 3. Entity Resolution Misses
        if not record.exact_hierarchy_matched:
            if "TYPO" in cat or "MISSPELLING" in cat:
                return "FUZZY_MATCH_FAILURE"
            elif "DEVANAGARI" in cat or "MIXED" in cat:
                return "LANGUAGE_FAILURE"
            elif "HISTORICAL" in cat:
                return "FUZZY_MATCH_FAILURE"
            elif "INCOMPLETE" in cat:
                return "INCOMPLETE_ADDRESS"
            else:
                return "PARSING_ERROR"

        return "NONE"

    @classmethod
    def analyze_errors(cls, records: List[EvaluationResultRecord]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        errors: List[Dict[str, Any]] = []
        category_counts: Dict[str, int] = {}

        for r in records:
            err_type = cls.classify_error(r)
            r.error_category = err_type if err_type != "NONE" else None

            if err_type != "NONE":
                category_counts[err_type] = category_counts.get(err_type, 0) + 1
                errors.append({
                    "case_id": r.case_id,
                    "address": r.address,
                    "category": r.category,
                    "language": r.language,
                    "script": r.script,
                    "expected_status": r.expected_status,
                    "predicted_status": r.predicted_status,
                    "expected_state": r.expected_state,
                    "predicted_state": r.predicted_state,
                    "expected_district": r.expected_district,
                    "predicted_district": r.predicted_district,
                    "expected_locality": r.expected_locality,
                    "predicted_locality": r.predicted_locality,
                    "expected_pincode": r.expected_pincode,
                    "predicted_pincode": r.predicted_pincode,
                    "expected_ambiguity": r.expected_ambiguity,
                    "predicted_ambiguity": r.predicted_ambiguity,
                    "failure_category": err_type,
                    "consistency_score": r.consistency_score,
                    "entity_match_score": r.entity_match_score,
                    "notes": r.notes or ""
                })

        return errors, category_counts

    @staticmethod
    def export_errors_csv(errors: List[Dict[str, Any]], output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(errors)
        df.to_csv(output_path, index=False, encoding="utf-8")
