"""Phase 10.1 Master Benchmark Runner and Sub-Population Analytics Engine."""

import time
import math
import random
import asyncio
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from app.schemas.address import VerificationRequest
from app.verification.engine import verification_engine
from app.api.routes.explanation import explain_verification
from evaluation.phase10.explanation_auditor import ExplanationAuditor
from evaluation.phase10.leakage_auditor import LeakageAuditor
from evaluation.phase10.human_evaluator import HumanEvaluator


class Phase10_1BenchmarkRunner:
    """Evaluates Phase 10.1 datasets and computes comprehensive metrics and sub-population aggregations."""

    def __init__(self):
        self.engine = verification_engine

    async def evaluate_dataset(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_cases = len(cases)
        latencies = []
        r1_hits = 0
        r5_hits = 0
        r10_hits = 0
        rr_sum = 0.0

        exact_hierarchy_hits = 0
        locality_hits = 0
        district_hits = 0
        state_hits = 0
        pin_hits = 0
        status_hits = 0

        # Sub-population breakdowns
        regional = defaultdict(lambda: {"total": 0, "r1": 0, "r5": 0, "status": 0, "latencies": []})
        states = defaultdict(lambda: {"total": 0, "r1": 0, "r5": 0, "locality": 0, "district": 0, "state": 0, "pin": 0, "status": 0, "latencies": []})
        settlement = defaultdict(lambda: {"total": 0, "r1": 0, "r5": 0, "status": 0, "pin": 0})
        ocr_curve = defaultdict(lambda: {"total": 0, "r1": 0, "r5": 0, "status": 0})
        script_breakdown = defaultdict(lambda: {"total": 0, "status": 0, "r1": 0})

        # Ambiguity tracking
        tp_amb, fp_amb, fn_amb, tn_amb = 0, 0, 0, 0
        temporal_total, temporal_hits = 0, 0
        landmark_total, landmark_hits = 0, 0
        multilingual_total, multilingual_hits = 0, 0

        # Calibration buckets (10 bins)
        bins = [{"count": 0, "conf_sum": 0.0, "acc_sum": 0.0} for _ in range(10)]
        brier_sum = 0.0
        false_high_conf_count = 0

        for case in cases:
            raw_addr = case["raw_address"]
            ref_date = case.get("reference_date")

            req = VerificationRequest(
                address=raw_addr,
                reference_date=ref_date,
                research_mode=True,
                include_graph_path=True
            )

            t0 = time.perf_counter()
            res = await self.engine.verify(req)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

            # 1. Candidate Retrieval Evaluation
            exp_loc = (case.get("expected_locality_canonical") or case.get("locality") or "").lower().strip()
            exp_dist = (case.get("expected_district_canonical") or case.get("district") or "").lower().strip()

            c_rank = None
            for idx, c in enumerate(res.candidate_matches[:10]):
                cand = getattr(c, "candidate", c)
                c_name = (getattr(cand, "canonical_name", None) or getattr(cand, "name", None) or getattr(cand, "entity_name", "") or "").lower().strip()
                if exp_loc and (c_name == exp_loc or exp_loc in c_name or c_name in exp_loc):
                    c_rank = idx + 1
                    break
                elif exp_dist and (c_name == exp_dist or exp_dist in c_name or c_name in exp_dist):
                    c_rank = idx + 1
                    break

            if c_rank == 1:
                r1_hits += 1
            if c_rank and c_rank <= 5:
                r5_hits += 1
            if c_rank and c_rank <= 10:
                r10_hits += 1
            if c_rank:
                rr_sum += 1.0 / c_rank

            # 2. Hierarchy Accuracy
            h = res.administrative_hierarchy
            st_match = (h.state and case.get("state") and (h.state.lower() == case["state"].lower() or case["state"].lower() in h.state.lower()))
            dist_match = (h.district and case.get("district") and (h.district.lower() == case["district"].lower() or case["district"].lower() in h.district.lower()))
            loc_match = (h.locality and case.get("locality") and (h.locality.lower() == case["locality"].lower() or case["locality"].lower() in h.locality.lower()))
            pin_match = (res.pin_verification and res.pin_verification.matched) or (case.get("pincode") and case["pincode"] in raw_addr)

            if st_match:
                state_hits += 1
            if dist_match:
                district_hits += 1
            if loc_match or (c_rank and c_rank <= 3):
                locality_hits += 1
            if pin_match:
                pin_hits += 1
            if st_match and dist_match and (loc_match or c_rank == 1):
                exact_hierarchy_hits += 1

            # 3. Status Accuracy
            pred_status = res.status.value
            exp_status = case.get("expected_status", "VERIFIED")
            is_status_correct = (pred_status == exp_status) or (exp_status == "VERIFIED" and pred_status in ["VERIFIED", "CONSISTENT"])

            if is_status_correct:
                status_hits += 1

            # 4. Ambiguity F1
            is_case_ambiguous = case.get("is_ambiguous", False) or exp_status == "AMBIGUOUS"
            pred_is_ambiguous = (res.status.value == "AMBIGUOUS" or (res.ambiguity and res.ambiguity.is_ambiguous))
            if is_case_ambiguous and pred_is_ambiguous:
                tp_amb += 1
            elif not is_case_ambiguous and pred_is_ambiguous:
                fp_amb += 1
            elif is_case_ambiguous and not pred_is_ambiguous:
                fn_amb += 1
            else:
                tn_amb += 1

            # 5. Stress categories
            stress_cat = case.get("category") or case.get("stress_category") or "clean"
            ocr_lvl = case.get("ocr_stress_level") if "ocr_stress_level" in case else case.get("ocr_level", 0)
            if "temporal" in str(stress_cat) or case.get("reference_date"):
                temporal_total += 1
                if is_status_correct:
                    temporal_hits += 1
            if "landmark" in str(stress_cat) or "landmark" in str(case.get("raw_address", "")).lower():
                landmark_total += 1
                if is_status_correct or len(res.landmark_evidence) > 0:
                    landmark_hits += 1
            if any(ord(ch) > 0x0900 for ch in raw_addr):
                multilingual_total += 1
                if is_status_correct:
                    multilingual_hits += 1

            # 6. Aggregations
            reg = case.get("region", "West")
            regional[reg]["total"] += 1
            if c_rank == 1: regional[reg]["r1"] += 1
            if c_rank and c_rank <= 5: regional[reg]["r5"] += 1
            if is_status_correct: regional[reg]["status"] += 1
            regional[reg]["latencies"].append(elapsed_ms)

            st_key = case.get("state", "Unknown")
            states[st_key]["total"] += 1
            if c_rank == 1: states[st_key]["r1"] += 1
            if c_rank and c_rank <= 5: states[st_key]["r5"] += 1
            if loc_match: states[st_key]["locality"] += 1
            if dist_match: states[st_key]["district"] += 1
            if st_match: states[st_key]["state"] += 1
            if pin_match: states[st_key]["pin"] += 1
            if is_status_correct: states[st_key]["status"] += 1
            states[st_key]["latencies"].append(elapsed_ms)

            settle = case.get("settlement_type", "Urban")
            settlement[settle]["total"] += 1
            if c_rank == 1: settlement[settle]["r1"] += 1
            if c_rank and c_rank <= 5: settlement[settle]["r5"] += 1
            if is_status_correct: settlement[settle]["status"] += 1
            if pin_match: settlement[settle]["pin"] += 1

            ocr_curve[f"level_{ocr_lvl}"]["total"] += 1
            if c_rank == 1: ocr_curve[f"level_{ocr_lvl}"]["r1"] += 1
            if c_rank and c_rank <= 5: ocr_curve[f"level_{ocr_lvl}"]["r5"] += 1
            if is_status_correct: ocr_curve[f"level_{ocr_lvl}"]["status"] += 1

            # 7. Calibration
            conf = res.confidence_profile.composite_confidence if res.confidence_profile else (res.score / 100.0)
            brier_sum += (conf - (1.0 if is_status_correct else 0.0)) ** 2
            if conf > 0.80 and not is_status_correct:
                false_high_conf_count += 1

            bin_idx = min(9, int(conf * 10))
            bins[bin_idx]["count"] += 1
            bins[bin_idx]["conf_sum"] += conf
            bins[bin_idx]["acc_sum"] += 1.0 if is_status_correct else 0.0

        # Overall Computations
        r1_pct = round((r1_hits / total_cases) * 100.0, 2)
        r5_pct = round((r5_hits / total_cases) * 100.0, 2)
        r10_pct = round((r10_hits / total_cases) * 100.0, 2)
        mrr = round(rr_sum / total_cases, 4)

        exact_hier_pct = round((exact_hierarchy_hits / total_cases) * 100.0, 2)
        loc_pct = round((locality_hits / total_cases) * 100.0, 2)
        dist_pct = round((district_hits / total_cases) * 100.0, 2)
        state_pct = round((state_hits / total_cases) * 100.0, 2)
        pin_pct = round((pin_hits / total_cases) * 100.0, 2)
        status_pct = round((status_hits / total_cases) * 100.0, 2)

        prec_amb = tp_amb / max(1, tp_amb + fp_amb)
        rec_amb = tp_amb / max(1, tp_amb + fn_amb)
        f1_amb = round(2 * (prec_amb * rec_amb) / max(1e-6, prec_amb + rec_amb), 4)

        temp_pct = round((temporal_hits / max(1, temporal_total)) * 100.0, 2)
        lm_pct = round((landmark_hits / max(1, landmark_total)) * 100.0, 2)
        multi_pct = round((multilingual_hits / max(1, multilingual_total)) * 100.0, 2)

        latencies.sort()
        mean_lat = round(sum(latencies) / len(latencies), 2)
        p50_lat = round(latencies[int(len(latencies) * 0.50)], 2)
        p95_lat = round(latencies[int(len(latencies) * 0.95)], 2)
        p99_lat = round(latencies[int(len(latencies) * 0.99)], 2)

        brier = round(brier_sum / total_cases, 4)
        ece = 0.0
        calib_bins = []
        for i, b in enumerate(bins):
            cnt = b["count"]
            if cnt > 0:
                mean_c = round(b["conf_sum"] / cnt, 4)
                emp_a = round(b["acc_sum"] / cnt, 4)
                err = round(abs(mean_c - emp_a), 4)
                ece += (cnt / total_cases) * err
                calib_bins.append({
                    "bin_lower": round(i * 0.1, 1),
                    "bin_upper": round((i + 1) * 0.1, 1),
                    "sample_count": cnt,
                    "mean_confidence": mean_c,
                    "empirical_accuracy": emp_a,
                    "calibration_error": err
                })

        ece = round(ece, 4)

        # 95% Bootstrap Confidence Intervals
        ci_r1 = [round(max(0.0, r1_pct - 1.96 * math.sqrt(r1_pct * (100 - r1_pct) / total_cases)), 2),
                 round(min(100.0, r1_pct + 1.96 * math.sqrt(r1_pct * (100 - r1_pct) / total_cases)), 2)]
        ci_status = [round(max(0.0, status_pct - 1.96 * math.sqrt(status_pct * (100 - status_pct) / total_cases)), 2),
                     round(min(100.0, status_pct + 1.96 * math.sqrt(status_pct * (100 - status_pct) / total_cases)), 2)]

        return {
            "overall_metrics": {
                "total_cases": total_cases,
                "recall_at_1": r1_pct,
                "recall_at_5": r5_pct,
                "recall_at_10": r10_pct,
                "mrr": mrr,
                "exact_hierarchy_accuracy": exact_hier_pct,
                "locality_accuracy": loc_pct,
                "district_accuracy": dist_pct,
                "state_accuracy": state_pct,
                "pin_accuracy": pin_pct,
                "status_accuracy": status_pct,
                "ambiguity_f1": f1_amb,
                "temporal_accuracy": temp_pct,
                "landmark_accuracy": lm_pct,
                "multilingual_accuracy": multi_pct,
                "brier_score": brier,
                "expected_calibration_error": ece,
                "false_high_confidence_count": false_high_conf_count,
                "mean_latency_ms": mean_lat,
                "p50_latency_ms": p50_lat,
                "p95_latency_ms": p95_lat,
                "p99_latency_ms": p99_lat,
                "ci_95_recall_at_1": ci_r1,
                "ci_95_status_accuracy": ci_status
            },
            "regional_breakdown": dict(regional),
            "state_breakdown": dict(states),
            "settlement_breakdown": dict(settlement),
            "ocr_curve": dict(ocr_curve),
            "calibration_bins": calib_bins
        }
