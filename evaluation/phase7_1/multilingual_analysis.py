"""Multilingual & Indic Script Robustness Analysis for Phase 7.1.

Stratifies OCR and Geographic Extraction performance by:
- Language: English (eng), Hindi (hin), Marathi (mar), Mixed
- Script: Latin, Devanagari, Mixed
- Character type: Devanagari numerals vs Hindu-Arabic numerals
- Administrative prefixes: जि., ता., गा., पत्ता, etc.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from pydantic import BaseModel, Field


class LanguageStratifiedMetrics(BaseModel):
    language: str
    script: str
    total_cases: int = 0
    mean_cer: float = 0.0
    mean_wer: float = 0.0
    region_precision: float = 0.0
    region_recall: float = 0.0
    region_f1: float = 0.0
    pincode_accuracy: float = 0.0
    state_accuracy: float = 0.0
    district_accuracy: float = 0.0
    locality_accuracy: float = 0.0
    verification_status_accuracy: float = 0.0


class MultilingualAnalyzer:
    """Computes stratified evaluations for Indic and multilingual documents."""

    @classmethod
    def evaluate_strata(cls, case_evaluations: List[Dict[str, Any]]) -> Dict[str, LanguageStratifiedMetrics]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for c in case_evaluations:
            lang = c.get("language", "eng")
            script = c.get("script", "Latin")
            key = f"{lang}_{script}"
            grouped[key].append(c)

        stratified_results: Dict[str, LanguageStratifiedMetrics] = {}

        for key, cases in grouped.items():
            total = len(cases)
            if total == 0:
                continue

            lang, script = key.split("_", 1)
            cer_list = [c.get("doc_cer", 0.0) for c in cases]
            wer_list = [c.get("doc_wer", 0.0) for c in cases]

            region_tp = sum(1 for c in cases if c.get("region_tp", False))
            region_fp = sum(1 for c in cases if c.get("region_fp", False))
            region_fn = sum(1 for c in cases if c.get("region_fn", False))

            prec = (region_tp / (region_tp + region_fp) * 100.0) if (region_tp + region_fp) > 0 else 100.0
            rec = (region_tp / (region_tp + region_fn) * 100.0) if (region_tp + region_fn) > 0 else 100.0
            f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

            pin_acc = sum(1 for c in cases if c.get("pincode_match", False)) / total * 100.0
            state_acc = sum(1 for c in cases if c.get("state_match", False)) / total * 100.0
            dist_acc = sum(1 for c in cases if c.get("district_match", False)) / total * 100.0
            loc_acc = sum(1 for c in cases if c.get("locality_match", False)) / total * 100.0
            status_acc = sum(1 for c in cases if c.get("status_match", False)) / total * 100.0

            stratified_results[key] = LanguageStratifiedMetrics(
                language=lang,
                script=script,
                total_cases=total,
                mean_cer=round(sum(cer_list) / total, 4),
                mean_wer=round(sum(wer_list) / total, 4),
                region_precision=round(prec, 2),
                region_recall=round(rec, 2),
                region_f1=round(f1, 2),
                pincode_accuracy=round(pin_acc, 2),
                state_accuracy=round(state_acc, 2),
                district_accuracy=round(dist_acc, 2),
                locality_accuracy=round(loc_acc, 2),
                verification_status_accuracy=round(status_acc, 2),
            )

        return stratified_results
