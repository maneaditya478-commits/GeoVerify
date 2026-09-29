"""Score Distribution & Calibration Auditor for Phase 7.3.

Audits verification consistency scores across 6 score bands:
[0-20, 21-40, 41-60, 61-70, 71-84, 85-100]
"""

import os
import csv
from typing import Dict, Any, List
from collections import defaultdict
from pydantic import BaseModel, Field


class ScoreBandMetric(BaseModel):
    band_name: str
    lower: int
    upper: int
    support: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    accuracy_pct: float = 0.0
    status_distribution: str = ""
    clean_mean_score: float = 0.0
    ocr_mean_score: float = 0.0


class ScoreDistributionAuditor:
    """Audits the score distributions, calibrations, and empirical accuracies per score band."""

    BANDS = [
        (0, 20, "0-20"),
        (21, 40, "21-40"),
        (41, 60, "41-60"),
        (61, 70, "61-70"),
        (71, 84, "71-84"),
        (85, 100, "85-100"),
    ]

    @classmethod
    def audit_scores(cls, cases_data: List[Dict[str, Any]]) -> List[ScoreBandMetric]:
        band_items = defaultdict(list)

        for d in cases_data:
            score = float(d.get("score", 0.0))
            for lower, upper, name in cls.BANDS:
                if lower <= score <= upper:
                    band_items[name].append(d)
                    break

        metrics = []
        for lower, upper, name in cls.BANDS:
            items = band_items[name]
            tot = len(items)
            if tot > 0:
                corr = sum(1 for x in items if x.get("correct", False))
                incorr = tot - corr
                acc = round(corr / tot * 100.0, 2)
                stat_counts = defaultdict(int)
                for x in items:
                    stat_counts[x.get("predicted_status", "UNKNOWN")] += 1
                stat_dist = ";".join(f"{k}:{v}" for k, v in stat_counts.items())
                clean_scores = [float(x.get("clean_score", x.get("score", 0.0))) for x in items]
                ocr_scores = [float(x.get("ocr_score", x.get("score", 0.0))) for x in items]
                c_mean = round(sum(clean_scores) / tot, 2)
                o_mean = round(sum(ocr_scores) / tot, 2)
            else:
                corr = 0
                incorr = 0
                acc = 0.0
                stat_dist = "none"
                c_mean = 0.0
                o_mean = 0.0

            metrics.append(ScoreBandMetric(
                band_name=name,
                lower=lower,
                upper=upper,
                support=tot,
                correct_count=corr,
                incorrect_count=incorr,
                accuracy_pct=acc,
                status_distribution=stat_dist,
                clean_mean_score=c_mean,
                ocr_mean_score=o_mean,
            ))

        return metrics

    @classmethod
    def export_csv(cls, metrics: List[ScoreBandMetric], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "band_name",
                "lower",
                "upper",
                "support",
                "correct_count",
                "incorrect_count",
                "accuracy_pct",
                "status_distribution",
                "clean_mean_score",
                "ocr_mean_score",
            ])
            for m in metrics:
                writer.writerow([
                    m.band_name,
                    m.lower,
                    m.upper,
                    m.support,
                    m.correct_count,
                    m.incorrect_count,
                    m.accuracy_pct,
                    m.status_distribution,
                    m.clean_mean_score,
                    m.ocr_mean_score,
                ])
