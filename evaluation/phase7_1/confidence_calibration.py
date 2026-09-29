"""Confidence Calibration and Reliability Curve Analysis for Phase 7.1.

Evaluates whether model confidence scores reliably reflect empirical extraction
and verification accuracy across 5 distinct confidence buckets:
- [0.0 - 0.20]
- (0.20 - 0.40]
- (0.40 - 0.60]
- (0.60 - 0.80]
- (0.80 - 1.00]

Calculates:
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)
- Brier Score
"""

from typing import List, Dict, Any, Optional
import math
from pydantic import BaseModel, Field


class CalibrationBucket(BaseModel):
    bin_range: str
    bin_lower: float
    bin_upper: float
    count: int = 0
    mean_confidence: float = 0.0
    empirical_accuracy: float = 0.0
    calibration_gap: float = 0.0


class CalibrationReport(BaseModel):
    total_samples: int
    expected_calibration_error_pct: float
    max_calibration_error_pct: float
    brier_score: float
    buckets: List[CalibrationBucket] = Field(default_factory=list)


class ConfidenceCalibrationAnalyzer:
    """Computes reliability diagram statistics and calibration errors."""

    @classmethod
    def evaluate_calibration(
        cls,
        confidences: List[float],
        outcomes: List[bool],
    ) -> CalibrationReport:
        n = min(len(confidences), len(outcomes))
        if n == 0:
            return CalibrationReport(
                total_samples=0,
                expected_calibration_error_pct=0.0,
                max_calibration_error_pct=0.0,
                brier_score=0.0,
                buckets=[],
            )

        bin_bounds = [
            (0.0, 0.20, "0-20%"),
            (0.20, 0.40, "21-40%"),
            (0.40, 0.60, "41-60%"),
            (0.60, 0.80, "61-80%"),
            (0.80, 1.00, "81-100%"),
        ]

        buckets: List[CalibrationBucket] = []
        total_ece = 0.0
        max_gap = 0.0
        brier_sum = 0.0

        for lower, upper, label in bin_bounds:
            bin_confs = []
            bin_accs = []
            for i in range(n):
                c = confidences[i]
                y = 1.0 if outcomes[i] else 0.0
                brier_sum += (c - y) ** 2

                # Include lower bound for first bin, strictly greater for subsequent
                in_bin = (lower <= c <= upper) if lower == 0.0 else (lower < c <= upper)
                if in_bin:
                    bin_confs.append(c)
                    bin_accs.append(y)

            count = len(bin_confs)
            if count > 0:
                mean_c = sum(bin_confs) / count
                emp_acc = sum(bin_accs) / count
                gap = abs(emp_acc - mean_c)
                total_ece += (count / n) * gap
                max_gap = max(max_gap, gap)
            else:
                mean_c = (lower + upper) / 2.0
                emp_acc = 0.0
                gap = 0.0

            buckets.append(CalibrationBucket(
                bin_range=label,
                bin_lower=lower,
                bin_upper=upper,
                count=count,
                mean_confidence=round(mean_c * 100.0, 2),
                empirical_accuracy=round(emp_acc * 100.0, 2),
                calibration_gap=round(gap * 100.0, 2),
            ))

        brier_score = round(brier_sum / n, 4)
        ece_pct = round(total_ece * 100.0, 2)
        mce_pct = round(max_gap * 100.0, 2)

        return CalibrationReport(
            total_samples=n,
            expected_calibration_error_pct=ece_pct,
            max_calibration_error_pct=mce_pct,
            brier_score=brier_score,
            buckets=buckets,
        )
