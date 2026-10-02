"""Phase 10.2 Candidate Universe & Ranking Bottleneck Audit Tool.

Analyzes the frozen 5,000-case Phase 10 independent benchmark to:
1. Determine Candidate Universe Coverage (Categories A to G)
2. Identify Top Ranking Failure Modes (Where correct entity was retrieved in Top 10 but not Rank 1)
3. Quantify feature differences between correct and wrong top candidates
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter

root_dir = Path(__file__).parent.parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.matcher import entity_matcher
from app.entity_resolution.models import EntityType


async def run_candidate_universe_audit():
    benchmark_path = root_dir / "evaluation" / "datasets" / "phase10_independent_dataset.json"
    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    engine = VerificationEngine()

    category_counts = Counter()
    ranking_failure_cases = []
    category_assignments = {}

    print(f"Starting Candidate Universe Audit across {len(cases)} frozen cases...")

    for idx, case in enumerate(cases):
        cid = case.get("id") or case.get("case_id") or f"case_{idx}"
        raw_addr = case["raw_address"]
        exp_loc = (case.get("locality") or case.get("expected_locality") or "").strip().lower()
        exp_dist = (case.get("district") or case.get("expected_district") or "").strip().lower()
        exp_state = (case.get("state") or case.get("expected_state") or "").strip().lower()
        exp_pin = str(case.get("pincode") or case.get("expected_pincode") or "").strip()

        # Generate candidates using standard candidate generator
        cands = candidate_generator.generate_candidates(raw_addr, limit=15)
        
        # Rank candidates using context-aware ranker
        ranked_cands = entity_matcher.rank_candidates(
            candidates=cands,
            query_text=raw_addr,
            context_state=case.get("state") or case.get("expected_state"),
            context_district=case.get("district") or case.get("expected_district"),
            context_pin=case.get("pincode") or case.get("expected_pincode")
        )

        # Check if correct entity was in retrieved list
        correct_rank = None
        correct_cand = None
        for r_idx, r in enumerate(ranked_cands):
            c = r.candidate
            c_name = c.name.lower()
            c_dist = (c.district or "").lower()
            c_state = (c.state or "").lower()
            
            name_match = (exp_loc and exp_loc in c_name) or (exp_dist and exp_dist in c_name)
            state_match = (not exp_state) or (exp_state in c_state) or (c_state in exp_state)
            dist_match = (not exp_dist) or (exp_dist in c_dist) or (c_dist in exp_dist)

            if name_match and (state_match or dist_match):
                correct_rank = r_idx + 1
                correct_cand = r
                break

        # Classify case
        if not cands or correct_rank is None:
            cat = "A_CORRECT_NOT_IN_UNIVERSE"
        elif correct_rank == 1:
            cat = "B_CORRECT_RETRIEVED_RANK_1"
        elif 2 <= correct_rank <= 5:
            cat = "C_CORRECT_RETRIEVED_RANK_2_5"
        elif 6 <= correct_rank <= 10:
            cat = "D_CORRECT_RETRIEVED_RANK_6_10"
        elif correct_rank > 10:
            cat = "E_CORRECT_RETRIEVED_RANK_GT10"
        else:
            cat = "F_GROUND_TRUTH_OR_SCHEMA_MISMATCH"

        category_counts[cat] += 1
        category_assignments[cid] = {
            "category": cat,
            "correct_rank": correct_rank,
            "total_candidates": len(cands),
            "top_predicted": ranked_cands[0].candidate.name if ranked_cands else None,
            "top_score": ranked_cands[0].match_score if ranked_cands else 0.0
        }

        # If correct candidate was in top 10 but not rank 1, record pairwise comparison
        if correct_rank and 2 <= correct_rank <= 10 and ranked_cands:
            top_wrong = ranked_cands[0]
            ranking_failure_cases.append({
                "case_id": cid,
                "raw_address": raw_addr,
                "expected": {
                    "locality": exp_loc,
                    "district": exp_dist,
                    "state": exp_state,
                    "pincode": exp_pin
                },
                "correct_candidate": {
                    "name": correct_cand.candidate.name,
                    "district": correct_cand.candidate.district,
                    "state": correct_cand.candidate.state,
                    "rank": correct_rank,
                    "score": correct_cand.match_score,
                    "breakdown": correct_cand.breakdown.model_dump()
                },
                "predicted_top_1": {
                    "name": top_wrong.candidate.name,
                    "district": top_wrong.candidate.district,
                    "state": top_wrong.candidate.state,
                    "score": top_wrong.match_score,
                    "breakdown": top_wrong.breakdown.model_dump()
                },
                "score_margin": round(top_wrong.match_score - correct_cand.match_score, 2)
            })

        if (idx + 1) % 1000 == 0:
            print(f"Processed {idx + 1} / {len(cases)} cases...")

    output_dir = root_dir / "evaluation" / "results" / "phase10_2" / "retrieval"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "ranking_error_cases.json", "w", encoding="utf-8") as f:
        json.dump(ranking_failure_cases, f, indent=2)

    total_cases = len(cases)
    cat_summary = {
        "total_cases": total_cases,
        "categories": {k: {"count": v, "pct": round((v / total_cases) * 100.0, 2)} for k, v in category_counts.items()},
        "total_ranking_failures_top10": len(ranking_failure_cases)
    }

    print("\n" + "=" * 60)
    print("CANDIDATE UNIVERSE CLASSIFICATION SUMMARY:")
    for k, v in cat_summary["categories"].items():
        print(f"  {k:35}: {v['count']:5} ({v['pct']}%)")
    print("=" * 60)

    return cat_summary, ranking_failure_cases


if __name__ == "__main__":
    asyncio.run(run_candidate_universe_audit())
