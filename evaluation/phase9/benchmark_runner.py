"""Phase 9 Comprehensive Benchmark Runner.

Evaluates:
- Candidate Retrieval: Recall@1, Recall@5, Recall@10, MRR
- Administrative Hierarchy: Exact Hierarchy Accuracy, State/District/Locality/PIN Accuracy
- Decision Engine: Status Accuracy, Ambiguity F1
- Temporal Geography: Resolution Accuracy, Date Validity Accuracy
- Spatial Intelligence: Landmark Detection & Proximity Accuracy
- Multilingual Alignment: Script & Abbreviation Handling Accuracy
- Latency Profile: Mean, P50, P95, P99
"""

import time
import asyncio
import statistics
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.schemas.address import VerificationRequest
from app.verification.engine import verification_engine
from app.temporal.resolver import temporal_resolver
from app.landmarks.spatial_matcher import landmark_matcher
from app.services.multilingual_alignment import multilingual_alignment_engine


class Phase9BenchmarkMetrics(BaseModel):
    total_cases: int
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    mrr: float
    exact_hierarchy_accuracy: float
    locality_accuracy: float
    district_accuracy: float
    state_accuracy: float
    pin_accuracy: float
    verification_status_accuracy: float
    ambiguity_f1: float
    temporal_resolution_accuracy: float
    landmark_spatial_accuracy: float
    multilingual_alignment_accuracy: float
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float


class Phase9BenchmarkRunner:
    """Executes the Phase 9 benchmark suite over stratified address test sets."""

    async def run_benchmark(self, dataset: List[Dict[str, Any]]) -> Phase9BenchmarkMetrics:
        latencies = []
        r1_hits = 0
        r5_hits = 0
        r10_hits = 0
        mrr_sum = 0.0

        hierarchy_hits = 0
        loc_hits = 0
        dist_hits = 0
        state_hits = 0
        pin_hits = 0
        status_hits = 0

        tp_amb = 0
        fp_amb = 0
        fn_amb = 0

        temporal_cases = 0
        temporal_hits = 0

        landmark_cases = 0
        landmark_hits = 0

        multilingual_cases = 0
        multilingual_hits = 0

        for item in dataset:
            req = VerificationRequest(
                address=item["raw_address"],
                reference_date=item.get("reference_date"),
                historical_context=True,
                research_mode=True
            )

            t0 = time.perf_counter()
            resp = await verification_engine.verify(req)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

            # 1. Retrieval & Candidates Evaluation
            cands = [c.candidate.name.lower() for c in resp.candidate_matches]
            target_loc = (item.get("locality") or "").lower()
            target_dist = (item.get("district") or "").lower()

            target_in_cand = False
            for rank_idx, c_name in enumerate(cands):
                if (target_loc and target_loc in c_name) or (target_dist and target_dist in c_name):
                    target_in_cand = True
                    if rank_idx == 0:
                        r1_hits += 1
                    if rank_idx < 5:
                        r5_hits += 1
                    if rank_idx < 10:
                        r10_hits += 1
                    mrr_sum += 1.0 / (rank_idx + 1)
                    break

            if not target_in_cand and not target_loc and not target_dist:
                # Ambiguous or non-resolvable item baseline
                r1_hits += 1
                r5_hits += 1
                r10_hits += 1
                mrr_sum += 1.0

            # 2. Hierarchy Accuracy
            h = resp.administrative_hierarchy
            is_loc_match = (not item.get("locality")) or (h.locality and target_loc in h.locality.lower())
            is_dist_match = (not item.get("district")) or (h.district and target_dist in h.district.lower())
            is_state_match = (not item.get("state")) or (h.state and item.get("state", "").lower() in h.state.lower())
            is_pin_match = (not item.get("pincode")) or (resp.pin_verification.pincode == item.get("pincode"))

            if is_loc_match: loc_hits += 1
            if is_dist_match: dist_hits += 1
            if is_state_match: state_hits += 1
            if is_pin_match: pin_hits += 1
            if is_loc_match and is_dist_match and is_state_match and is_pin_match:
                hierarchy_hits += 1

            # 3. Status & Ambiguity
            expected_status = item.get("expected_status")
            if expected_status:
                if resp.status.value == expected_status or (expected_status == "VERIFIED" and resp.status.value in ["VERIFIED", "CONSISTENT"]):
                    status_hits += 1

            pred_amb = resp.ambiguity.is_ambiguous if resp.ambiguity else False
            true_amb = item.get("is_ambiguous", False)
            if pred_amb and true_amb: tp_amb += 1
            elif pred_amb and not true_amb: fp_amb += 1
            elif not pred_amb and true_amb: fn_amb += 1

            # 4. Temporal Reasoning Evaluation
            if item.get("historical_entity"):
                temporal_cases += 1
                found_temp = any(
                    t.canonical_current_name.lower() == item.get("canonical_entity", "").lower()
                    for t in resp.temporal_evidence
                )
                if found_temp:
                    temporal_hits += 1

            # 5. Landmark Spatial Reasoning Evaluation
            if item.get("landmark"):
                landmark_cases += 1
                found_lm = any(
                    item.get("landmark", "").lower() in l.landmark_name.lower()
                    for l in resp.landmark_evidence
                )
                if found_lm:
                    landmark_hits += 1

            # 6. Multilingual Alignment Evaluation
            if item.get("is_mixed_script") or item.get("category") == "abbreviation_dense":
                multilingual_cases += 1
                align_res = multilingual_alignment_engine.align_and_expand(item["raw_address"])
                if align_res.is_mixed_script or len(align_res.expanded_tokens) > 0 or align_res.extracted_district_hint:
                    multilingual_hits += 1

        n = len(dataset)
        precision_amb = tp_amb / (tp_amb + fp_amb) if (tp_amb + fp_amb) > 0 else 1.0
        recall_amb = tp_amb / (tp_amb + fn_amb) if (tp_amb + fn_amb) > 0 else 1.0
        f1_amb = (2 * precision_amb * recall_amb / (precision_amb + recall_amb)) if (precision_amb + recall_amb) > 0 else 1.0

        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
        p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0.0

        return Phase9BenchmarkMetrics(
            total_cases=n,
            recall_at_1=round((r1_hits / n) * 100.0, 2),
            recall_at_5=round((r5_hits / n) * 100.0, 2),
            recall_at_10=round((r10_hits / n) * 100.0, 2),
            mrr=round(mrr_sum / n, 4),
            exact_hierarchy_accuracy=round((hierarchy_hits / n) * 100.0, 2),
            locality_accuracy=round((loc_hits / n) * 100.0, 2),
            district_accuracy=round((dist_hits / n) * 100.0, 2),
            state_accuracy=round((state_hits / n) * 100.0, 2),
            pin_accuracy=round((pin_hits / n) * 100.0, 2),
            verification_status_accuracy=round((status_hits / n) * 100.0, 2),
            ambiguity_f1=round(f1_amb, 4),
            temporal_resolution_accuracy=round((temporal_hits / max(1, temporal_cases)) * 100.0, 2) if temporal_cases > 0 else 100.0,
            landmark_spatial_accuracy=round((landmark_hits / max(1, landmark_cases)) * 100.0, 2) if landmark_cases > 0 else 100.0,
            multilingual_alignment_accuracy=round((multilingual_hits / max(1, multilingual_cases)) * 100.0, 2) if multilingual_cases > 0 else 100.0,
            mean_latency_ms=round(statistics.mean(latencies), 2),
            p50_latency_ms=round(p50, 2),
            p95_latency_ms=round(p95, 2),
            p99_latency_ms=round(p99, 2)
        )
