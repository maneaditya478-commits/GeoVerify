"""Top-1 Candidate Failure Analyzer for Phase 8.

Identifies cases where target entity is present in top-5 / top-10 candidates
(Recall@5 / Recall@10 success) but fails to achieve rank 1 (Recall@1 failure).
Outputs diagnostic CSV with feature contributions and applied penalties.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import ContextAwareRanker
from app.services.address_parser import AddressParser


class Top1FailureAnalyzer:
    """Diagnoses Recall@1 ranking failures."""

    def __init__(self):
        self.ranker = ContextAwareRanker()
        self.parser = AddressParser()

    def analyze_cases(self, benchmark_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        failures = []

        for case in benchmark_cases:
            raw_text = case.get("raw_text", "")
            exp_loc = case.get("expected_locality")
            exp_dist = case.get("expected_district")
            exp_state = case.get("expected_state")
            exp_pin = case.get("expected_pincode")

            parsed = self.parser.parse(raw_text)
            query_tok = parsed.locality or parsed.district or parsed.city or raw_text

            candidates = candidate_generator.generate_candidates(
                token=query_tok,
                context_state=exp_state or parsed.state,
                context_district=exp_dist or parsed.district,
                context_pin=exp_pin or parsed.pincode,
                limit=10,
            )

            if not candidates:
                continue

            # Score candidates
            scored = []
            for c in candidates:
                res = self.ranker.score_candidate(
                    candidate=c,
                    query_text=query_tok,
                    context_state=exp_state or parsed.state,
                    context_district=exp_dist or parsed.district,
                    context_pin=exp_pin or parsed.pincode,
                )
                scored.append((res.match_score, c, res))

            scored.sort(key=lambda x: x[0], reverse=True)

            # Check if ground truth matches
            top1_c = scored[0][1]
            top1_matches = (
                (exp_loc and exp_loc.lower() in top1_c.name.lower())
                or (exp_dist and top1_c.district and exp_dist.lower() in top1_c.district.lower())
            )

            if not top1_matches:
                # Check if present in top 5
                in_top5 = False
                found_rank = -1
                for rank_idx, (score, cand, res) in enumerate(scored[:5], start=1):
                    if (exp_loc and exp_loc.lower() in cand.name.lower()) or (
                        exp_dist and cand.district and exp_dist.lower() in cand.district.lower()
                    ):
                        in_top5 = True
                        found_rank = rank_idx
                        break

                if in_top5:
                    top_score, top_cand, top_res = scored[0]
                    target_score, target_cand, target_res = scored[found_rank - 1]
                    failures.append({
                        "case_id": case.get("id", "unknown"),
                        "raw_text": raw_text,
                        "expected_locality": exp_loc,
                        "expected_district": exp_dist,
                        "target_rank": found_rank,
                        "top1_candidate_name": top_cand.name,
                        "top1_candidate_district": top_cand.district,
                        "top1_score": top_score,
                        "target_score": target_score,
                        "score_gap": round(top_score - target_score, 2),
                        "top1_channels": ",".join(top_cand.channels or [top_cand.match_source]),
                        "target_channels": ",".join(target_cand.channels or [target_cand.match_source]),
                        "applied_penalties_on_target": ",".join(
                            p.name for p in target_res.ranking_explanation.applied_penalties
                        )
                        if target_res.ranking_explanation
                        else "",
                    })

        return failures

    def save_analysis_csv(self, failures: List[Dict[str, Any]], out_path: Path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "case_id",
            "raw_text",
            "expected_locality",
            "expected_district",
            "target_rank",
            "top1_candidate_name",
            "top1_candidate_district",
            "top1_score",
            "target_score",
            "score_gap",
            "top1_channels",
            "target_channels",
            "applied_penalties_on_target",
        ]
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for fail in failures:
                writer.writerow(fail)
