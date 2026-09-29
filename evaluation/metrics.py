"""Evaluation metrics calculation engine for GeoVerify India benchmarks."""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from evaluation.schema import EvaluationResultRecord, ExpectedStatus


class BenchmarkMetricsCalculator:
    """Computes transparent evaluation metrics for address resolution, ambiguity, and verification status."""

    @staticmethod
    def compute_accuracy_precision_recall_f1(tp: int, fp: int, fn: int, tn: int) -> Dict[str, float]:
        total = tp + fp + fn + tn
        acc = (tp + tn) / total if total > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        return {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn
        }

    @classmethod
    def evaluate_all(cls, records: List[EvaluationResultRecord]) -> Dict[str, Any]:
        if not records:
            return {"total_cases": 0}

        total_cases = len(records)

        # 1. Entity Resolution Accuracies
        state_applicable = [r for r in records if r.expected_state is not None]
        state_matched = sum(1 for r in state_applicable if r.state_matched)
        state_acc = state_matched / len(state_applicable) if state_applicable else 0.0

        dist_applicable = [r for r in records if r.expected_district is not None]
        dist_matched = sum(1 for r in dist_applicable if r.district_matched)
        dist_acc = dist_matched / len(dist_applicable) if dist_applicable else 0.0

        subdist_applicable = [r for r in records if r.expected_subdistrict is not None]
        subdist_matched = sum(1 for r in subdist_applicable if r.subdistrict_matched)
        subdist_acc = subdist_matched / len(subdist_applicable) if subdist_applicable else 0.0

        loc_applicable = [r for r in records if r.expected_locality is not None]
        loc_matched = sum(1 for r in loc_applicable if r.locality_matched)
        loc_acc = loc_matched / len(loc_applicable) if loc_applicable else 0.0

        pin_applicable = [r for r in records if r.expected_pincode is not None]
        pin_matched = sum(1 for r in pin_applicable if r.pincode_matched)
        pin_acc = pin_matched / len(pin_applicable) if pin_applicable else 0.0

        exact_hierarchy_matched = sum(1 for r in records if r.exact_hierarchy_matched)
        exact_hierarchy_acc = exact_hierarchy_matched / total_cases

        # 2. Candidate Recall@K
        r1 = sum(1 for r in loc_applicable if r.candidate_recall_1) / len(loc_applicable) if loc_applicable else 0.0
        r3 = sum(1 for r in loc_applicable if r.candidate_recall_3) / len(loc_applicable) if loc_applicable else 0.0
        r5 = sum(1 for r in loc_applicable if r.candidate_recall_5) / len(loc_applicable) if loc_applicable else 0.0
        r10 = sum(1 for r in loc_applicable if r.candidate_recall_10) / len(loc_applicable) if loc_applicable else 0.0

        # 3. Ambiguity Evaluation
        amb_tp = sum(1 for r in records if r.expected_ambiguity and r.predicted_ambiguity)
        amb_fp = sum(1 for r in records if not r.expected_ambiguity and r.predicted_ambiguity)
        amb_fn = sum(1 for r in records if r.expected_ambiguity and not r.predicted_ambiguity)
        amb_tn = sum(1 for r in records if not r.expected_ambiguity and not r.predicted_ambiguity)
        amb_metrics = cls.compute_accuracy_precision_recall_f1(amb_tp, amb_fp, amb_fn, amb_tn)

        # 4. Verification Status Multi-Class Evaluation & Confusion Matrix
        statuses = [s.value for s in ExpectedStatus]
        cm = {exp: {pred: 0 for pred in statuses} for exp in statuses}
        for r in records:
            if r.expected_status in cm and r.predicted_status in cm[r.expected_status]:
                cm[r.expected_status][r.predicted_status] += 1

        # Per-class metrics
        per_class_metrics = {}
        for s in statuses:
            tp = cm[s][s]
            fp = sum(cm[other][s] for other in statuses if other != s)
            fn = sum(cm[s][other] for other in statuses if other != s)
            tn = sum(cm[exp][pred] for exp in statuses if exp != s for pred in statuses if pred != s)
            m = cls.compute_accuracy_precision_recall_f1(tp, fp, fn, tn)
            m["support"] = sum(cm[s].values())
            per_class_metrics[s] = m

        status_correct = sum(1 for r in records if r.status_matched)
        overall_status_acc = status_correct / total_cases

        macro_f1 = float(np.mean([m["f1"] for m in per_class_metrics.values()]))
        supports = [m["support"] for m in per_class_metrics.values()]
        weighted_f1 = float(np.average([m["f1"] for m in per_class_metrics.values()], weights=supports)) if sum(supports) > 0 else 0.0

        # 5. Score Statistics
        consistency_scores = [r.consistency_score for r in records]
        completeness_scores = [r.completeness_score for r in records]
        entity_match_scores = [r.entity_match_score for r in records]

        score_stats = {
            "consistency_score": {
                "mean": round(float(np.mean(consistency_scores)), 2),
                "median": round(float(np.median(consistency_scores)), 2),
                "std": round(float(np.std(consistency_scores)), 2),
                "min": int(np.min(consistency_scores)),
                "max": int(np.max(consistency_scores))
            },
            "completeness_score": {
                "mean": round(float(np.mean(completeness_scores)), 2),
                "median": round(float(np.median(completeness_scores)), 2),
                "std": round(float(np.std(completeness_scores)), 2),
                "min": int(np.min(completeness_scores)),
                "max": int(np.max(completeness_scores))
            },
            "entity_match_score": {
                "mean": round(float(np.mean(entity_match_scores)), 2),
                "median": round(float(np.median(entity_match_scores)), 2),
                "std": round(float(np.std(entity_match_scores)), 2),
                "min": round(float(np.min(entity_match_scores)), 2),
                "max": round(float(np.max(entity_match_scores)), 2)
            }
        }

        # 6. Slice: By Script / Language
        script_metrics = {}
        for sc in set(r.script for r in records):
            sub = [r for r in records if r.script == sc]
            script_metrics[sc] = {
                "count": len(sub),
                "exact_hierarchy_acc": round(sum(1 for r in sub if r.exact_hierarchy_matched) / len(sub), 4),
                "status_acc": round(sum(1 for r in sub if r.status_matched) / len(sub), 4),
                "mean_latency_ms": round(float(np.mean([r.latency_ms for r in sub])), 2)
            }

        # 7. Slice: By Category
        category_metrics = {}
        for cat in set(r.category for r in records):
            sub = [r for r in records if r.category == cat]
            category_metrics[cat] = {
                "count": len(sub),
                "status_acc": round(sum(1 for r in sub if r.status_matched) / len(sub), 4),
                "exact_hierarchy_acc": round(sum(1 for r in sub if r.exact_hierarchy_matched) / len(sub), 4),
                "mean_consistency_score": round(float(np.mean([r.consistency_score for r in sub])), 2)
            }

        # 8. Latency Summary
        latencies = [r.latency_ms for r in records]
        latency_stats = {
            "mean_ms": round(float(np.mean(latencies)), 2),
            "median_ms": round(float(np.median(latencies)), 2),
            "p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "p90_ms": round(float(np.percentile(latencies, 90)), 2),
            "p95_ms": round(float(np.percentile(latencies, 95)), 2),
            "p99_ms": round(float(np.percentile(latencies, 99)), 2),
            "min_ms": round(float(np.min(latencies)), 2),
            "max_ms": round(float(np.max(latencies)), 2)
        }

        return {
            "total_cases": total_cases,
            "entity_resolution": {
                "state_accuracy": round(state_acc, 4),
                "district_accuracy": round(dist_acc, 4),
                "subdistrict_accuracy": round(subdist_acc, 4),
                "locality_accuracy": round(loc_acc, 4),
                "pincode_accuracy": round(pin_acc, 4),
                "exact_hierarchy_accuracy": round(exact_hierarchy_acc, 4)
            },
            "candidate_recall": {
                "recall_at_1": round(r1, 4),
                "recall_at_3": round(r3, 4),
                "recall_at_5": round(r5, 4),
                "recall_at_10": round(r10, 4)
            },
            "ambiguity": amb_metrics,
            "status_classification": {
                "overall_accuracy": round(overall_status_acc, 4),
                "macro_f1": round(macro_f1, 4),
                "weighted_f1": round(weighted_f1, 4),
                "per_class": per_class_metrics,
                "confusion_matrix": cm
            },
            "score_statistics": score_stats,
            "script_metrics": script_metrics,
            "category_metrics": category_metrics,
            "latency": latency_stats
        }
