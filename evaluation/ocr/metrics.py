"""Evaluation Metrics for OCR Address Extraction & Geographic Verification (Phase 7).

Computes:
- Character Error Rate (CER) via Levenshtein edit distance
- Word Error Rate (WER)
- Address Region Precision, Recall, and IoU
- Field Extraction Accuracy (pincode, state, district, subdistrict, locality)
- Verification Status Accuracy (VERIFIED, CONSISTENT, etc.)
- Processing Latencies (P50, P90, P95, Mean)
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from rapidfuzz import distance, fuzz


class OCRMetricsCalculator:
    """Calculates quantitative benchmark evaluation metrics for OCR document verification."""

    @staticmethod
    def calculate_cer(reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate: LevenshteinDistance(ref, hyp) / len(ref)."""
        ref = reference.strip()
        hyp = hypothesis.strip()
        if not ref:
            return 0.0 if not hyp else 1.0
        dist = distance.Levenshtein.distance(ref, hyp)
        return float(dist / max(1, len(ref)))

    @staticmethod
    def calculate_wer(reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate based on word token Levenshtein distance."""
        ref_words = reference.strip().split()
        hyp_words = hypothesis.strip().split()
        if not ref_words:
            return 0.0 if not hyp_words else 1.0
        
        # Word sequence distance
        dist = distance.Levenshtein.distance(ref_words, hyp_words)
        return float(dist / max(1, len(ref_words)))

    @staticmethod
    def field_match(expected: Optional[str], predicted: Optional[str], threshold: float = 85.0) -> bool:
        """Checks if predicted address field matches ground-truth using fuzzy token matching."""
        if not expected and not predicted:
            return True
        if not expected or not predicted:
            return False
        
        exp_clean = expected.strip().lower()
        pred_clean = predicted.strip().lower()
        
        if exp_clean == pred_clean:
            return True
        
        # Exact numeric match for PIN codes
        if exp_clean.isdigit() and pred_clean.isdigit():
            return exp_clean == pred_clean

        score = max(
            fuzz.token_sort_ratio(exp_clean, pred_clean),
            fuzz.token_set_ratio(exp_clean, pred_clean),
            fuzz.partial_ratio(exp_clean, pred_clean),
        )
        return score >= threshold


class AggregateOCRBenchmarkResults:
    """Summarizes evaluation metrics over a test batch."""

    def __init__(self):
        self.total_cases = 0
        self.clean_cases = 0
        self.degraded_cases = 0
        self.negative_cases = 0

        self.cer_scores: List[float] = []
        self.wer_scores: List[float] = []
        
        self.region_tp = 0
        self.region_fp = 0
        self.region_fn = 0

        self.field_matches: Dict[str, int] = {
            "pincode": 0,
            "state": 0,
            "district": 0,
            "subdistrict": 0,
            "locality": 0,
        }
        self.field_totals: Dict[str, int] = {
            "pincode": 0,
            "state": 0,
            "district": 0,
            "subdistrict": 0,
            "locality": 0,
        }

        self.verification_status_matches = 0
        self.verification_status_totals = 0

        self.latencies_ms: List[float] = []
        self.stage_latencies_ms: Dict[str, List[float]] = {
            "validation": [],
            "preprocessing": [],
            "ocr": [],
            "region_detection": [],
            "field_extraction": [],
            "geographic_verification": [],
        }

    def compute_summary(self) -> Dict[str, Any]:
        """Calculates final aggregated benchmark scores."""
        mean_cer = float(np.mean(self.cer_scores)) if self.cer_scores else 0.0
        mean_wer = float(np.mean(self.wer_scores)) if self.wer_scores else 0.0

        reg_prec = self.region_tp / max(1, (self.region_tp + self.region_fp))
        reg_rec = self.region_tp / max(1, (self.region_tp + self.region_fn))
        reg_f1 = (2 * reg_prec * reg_rec) / max(1e-6, (reg_prec + reg_rec))

        field_accuracies = {}
        for k, tot in self.field_totals.items():
            field_accuracies[k] = round(self.field_matches[k] / max(1, tot) * 100.0, 2)

        status_acc = round(self.verification_status_matches / max(1, self.verification_status_totals) * 100.0, 2)

        lat = np.array(self.latencies_ms) if self.latencies_ms else np.array([0.0])

        return {
            "total_evaluated_cases": self.total_cases,
            "mean_cer_pct": round(mean_cer * 100.0, 2),
            "mean_wer_pct": round(mean_wer * 100.0, 2),
            "region_detection": {
                "precision": round(reg_prec * 100.0, 2),
                "recall": round(reg_rec * 100.0, 2),
                "f1_score": round(reg_f1 * 100.0, 2),
            },
            "field_extraction_accuracy": field_accuracies,
            "verification_status_accuracy_pct": status_acc,
            "latency_ms": {
                "mean": round(float(np.mean(lat)), 2),
                "p50": round(float(np.percentile(lat, 50)), 2),
                "p90": round(float(np.percentile(lat, 90)), 2),
                "p95": round(float(np.percentile(lat, 95)), 2),
            },
        }
