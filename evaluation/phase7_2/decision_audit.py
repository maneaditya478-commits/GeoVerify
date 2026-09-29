"""Decision Engine & Status Confusion Matrix Auditor for Phase 7.2.

Audits:
1. Verification Status Confusion Matrix across 6 standard statuses:
   - VERIFIED
   - CONSISTENT
   - NEEDS_REVIEW
   - INCONSISTENT
   - AMBIGUOUS
   - UNABLE_TO_VERIFY
2. Calculates Macro/Weighted Precision, Recall, and F1
3. Tracks Decision Rule effectiveness and trigger frequencies
4. Bins verification scores across score bands:
   [0-20, 21-40, 41-60, 61-70, 71-84, 85-100]
"""

import csv
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pydantic import BaseModel, Field


STATUS_CLASSES = [
    "VERIFIED",
    "CONSISTENT",
    "NEEDS_REVIEW",
    "INCONSISTENT",
    "AMBIGUOUS",
    "UNABLE_TO_VERIFY",
]

SCORE_BANDS = [
    (0, 20, "0-20"),
    (21, 40, "21-40"),
    (41, 60, "41-60"),
    (61, 70, "61-70"),
    (71, 84, "71-84"),
    (85, 100, "85-100"),
]


class StatusMetric(BaseModel):
    status: str
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    support: int = 0


class DecisionRuleAudit(BaseModel):
    rule_name: str
    trigger_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    precision: float = 0.0


class ScoreBandAudit(BaseModel):
    band_name: str
    lower: int
    upper: int
    total_count: int = 0
    correct_count: int = 0
    accuracy: float = 0.0


class DecisionAuditSummary(BaseModel):
    total_evaluated: int
    accuracy_pct: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float
    per_class_metrics: Dict[str, StatusMetric] = Field(default_factory=dict)
    rule_audits: Dict[str, DecisionRuleAudit] = Field(default_factory=dict)
    score_band_audits: List[ScoreBandAudit] = Field(default_factory=list)


class DecisionEngineAuditor:
    """Audits decision rules, score calibrations, and status predictions."""

    @classmethod
    def audit_decisions(
        cls,
        ground_truth_statuses: List[str],
        predicted_statuses: List[str],
        scores: List[float],
        triggered_rules_per_case: List[List[str]],
    ) -> DecisionAuditSummary:
        n = min(len(ground_truth_statuses), len(predicted_statuses))
        if n == 0:
            return DecisionAuditSummary(
                total_evaluated=0,
                accuracy_pct=0.0,
                macro_precision=0.0,
                macro_recall=0.0,
                macro_f1=0.0,
                weighted_f1=0.0,
            )

        # 1. Build Confusion Matrix counts
        matrix: Dict[str, Dict[str, int]] = {s: {p: 0 for p in STATUS_CLASSES} for s in STATUS_CLASSES}
        total_correct = 0

        for i in range(n):
            gt = ground_truth_statuses[i]
            pred = predicted_statuses[i]
            if gt not in matrix:
                gt = "UNABLE_TO_VERIFY"
            if pred not in matrix:
                pred = "UNABLE_TO_VERIFY"
            matrix[gt][pred] += 1
            if gt == pred or (pred in ["VERIFIED", "CONSISTENT"] and gt == "VERIFIED"):
                total_correct += 1

        # 2. Per-class Precision, Recall, F1
        per_class: Dict[str, StatusMetric] = {}
        precisions = []
        recalls = []
        f1s = []
        supports = []

        for s in STATUS_CLASSES:
            tp = matrix[s][s]
            fp = sum(matrix[other][s] for other in STATUS_CLASSES if other != s)
            fn = sum(matrix[s][other] for other in STATUS_CLASSES if other != s)
            support = sum(matrix[s].values())

            prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            rec = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

            per_class[s] = StatusMetric(
                status=s,
                precision=round(prec * 100.0, 2),
                recall=round(rec * 100.0, 2),
                f1_score=round(f1 * 100.0, 2),
                support=support,
            )

            if support > 0:
                precisions.append(prec)
                recalls.append(rec)
                f1s.append(f1)
                supports.append(support)

        macro_p = (sum(precisions) / len(precisions) * 100.0) if precisions else 0.0
        macro_r = (sum(recalls) / len(recalls) * 100.0) if recalls else 0.0
        macro_f1 = (2 * macro_p * macro_r / (macro_p + macro_r)) if (macro_p + macro_r) > 0 else 0.0

        total_sup = sum(supports)
        weighted_f1 = sum(f1s[i] * supports[i] for i in range(len(f1s))) / total_sup * 100.0 if total_sup > 0 else 0.0

        # 3. Rule Effectiveness
        rule_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"trigger": 0, "correct": 0, "incorrect": 0})
        for i in range(n):
            gt = ground_truth_statuses[i]
            pred = predicted_statuses[i]
            is_match = (gt == pred) or (pred in ["VERIFIED", "CONSISTENT"] and gt == "VERIFIED")
            for r in triggered_rules_per_case[i]:
                rule_stats[r]["trigger"] += 1
                if is_match:
                    rule_stats[r]["correct"] += 1
                else:
                    rule_stats[r]["incorrect"] += 1

        rule_audits: Dict[str, DecisionRuleAudit] = {}
        for rname, st in rule_stats.items():
            prec = (st["correct"] / st["trigger"] * 100.0) if st["trigger"] > 0 else 0.0
            rule_audits[rname] = DecisionRuleAudit(
                rule_name=rname,
                trigger_count=st["trigger"],
                correct_count=st["correct"],
                incorrect_count=st["incorrect"],
                precision=round(prec, 2),
            )

        # 4. Score Band Audits
        score_band_audits: List[ScoreBandAudit] = []
        for low, high, label in SCORE_BANDS:
            tot = 0
            corr = 0
            for i in range(n):
                sc = scores[i]
                if low <= sc <= high:
                    tot += 1
                    gt = ground_truth_statuses[i]
                    pred = predicted_statuses[i]
                    if (gt == pred) or (pred in ["VERIFIED", "CONSISTENT"] and gt == "VERIFIED"):
                        corr += 1
            acc = (corr / tot * 100.0) if tot > 0 else 0.0
            score_band_audits.append(ScoreBandAudit(
                band_name=label,
                lower=low,
                upper=high,
                total_count=tot,
                correct_count=corr,
                accuracy=round(acc, 2),
            ))

        return DecisionAuditSummary(
            total_evaluated=n,
            accuracy_pct=round(total_correct / n * 100.0, 2),
            macro_precision=round(macro_p, 2),
            macro_recall=round(macro_r, 2),
            macro_f1=round(macro_f1, 2),
            weighted_f1=round(weighted_f1, 2),
            per_class_metrics=per_class,
            rule_audits=rule_audits,
            score_band_audits=score_band_audits,
        )

    @classmethod
    def export_confusion_matrix_csv(
        cls,
        ground_truth_statuses: List[str],
        predicted_statuses: List[str],
        file_path: str,
    ):
        matrix: Dict[str, Dict[str, int]] = {s: {p: 0 for p in STATUS_CLASSES} for s in STATUS_CLASSES}
        for i in range(min(len(ground_truth_statuses), len(predicted_statuses))):
            gt = ground_truth_statuses[i]
            pred = predicted_statuses[i]
            if gt in matrix and pred in matrix[gt]:
                matrix[gt][pred] += 1

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ground_truth / predicted"] + STATUS_CLASSES)
            for gt in STATUS_CLASSES:
                row = [gt] + [matrix[gt][p] for p in STATUS_CLASSES]
                writer.writerow(row)
