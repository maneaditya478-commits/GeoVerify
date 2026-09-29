"""Ranking Gap Diagnostic Tool for GeoVerify India (Phase 6).

Analyzes benchmark cases where the correct candidate is within the top-K candidate pool
(Recall@5) but is not ranked at rank 1 (Recall@1), classifying the failure root causes.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from evaluation.load_dataset import DatasetLoader
from app.services.address_parser import AddressParser
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.matcher import entity_matcher
from app.entity_resolution.models import EntityType, CandidateEntity, EntityMatchResult


def run_ranking_gap_analysis(
    dataset_path: Optional[Path] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    dataset_file = dataset_path or Path("evaluation/datasets/benchmark.json")
    out_path = output_dir or Path("evaluation/results")
    out_path.mkdir(parents=True, exist_ok=True)

    dataset = DatasetLoader.load_from_json(dataset_file)
    cases = dataset.cases

    gap_diagnostics = {
        "total_cases_evaluated": len(cases),
        "cases_with_gt_locality": 0,
        "recall_1_count": 0,
        "recall_5_count": 0,
        "gap_cases_count": 0,  # in Top-5 but NOT Rank 1
        "failure_classifications": {
            "CORRECT_CANDIDATE_RANKED_LOW": 0,
            "ADMIN_CONTEXT_ERROR": 0,
            "PIN_SIGNAL_ERROR": 0,
            "GEOGRAPHIC_SIGNAL_ERROR": 0,
            "NAME_SCORE_ERROR": 0,
            "ENTITY_TYPE_ERROR": 0,
            "AMBIGUITY_ERROR": 0,
            "MISSING_EVIDENCE": 0,
            "MULTIPLE_PLAUSIBLE_CANDIDATES": 0,
            "UNKNOWN": 0
        },
        "gap_records": []
    }

    flat_records = []

    for c in cases:
        gt = c.ground_truth
        if not gt.locality:
            continue

        gap_diagnostics["cases_with_gt_locality"] += 1
        addr = c.address
        parsed = AddressParser.parse(addr)
        gt_loc = gt.locality.lower()

        # Generate candidates using multi-channel retrieval
        query_loc = parsed.locality or gt.locality
        loc_candidates = candidate_generator.generate_candidates(
            query_loc,
            expected_type=EntityType.LOCALITY,
            context_state=parsed.state or gt.state,
            context_district=parsed.district or parsed.city or gt.district,
            context_pin=parsed.pincode or gt.pincode,
            limit=10
        )

        # Match and rank candidates with current matcher
        ranked_matches: List[EntityMatchResult] = []
        for cand in loc_candidates:
            m_res = entity_matcher.match_candidate(
                candidate=cand,
                query_text=query_loc,
                context_state=parsed.state or gt.state,
                context_district=parsed.district or parsed.city or gt.district,
                context_subdistrict=parsed.subdistrict or gt.subdistrict,
                context_pin=parsed.pincode or gt.pincode
            )
            ranked_matches.append(m_res)

        ranked_matches.sort(key=lambda m: m.match_score, reverse=True)

        # Find rank of correct candidate (1-indexed)
        correct_rank = None
        correct_match_res = None
        for idx, m in enumerate(ranked_matches, start=1):
            c_name = m.candidate.name.lower()
            if gt_loc in c_name or c_name in gt_loc:
                correct_rank = idx
                correct_match_res = m
                break

        if correct_rank == 1:
            gap_diagnostics["recall_1_count"] += 1
            gap_diagnostics["recall_5_count"] += 1
        elif correct_rank is not None and correct_rank <= 5:
            gap_diagnostics["recall_5_count"] += 1
            gap_diagnostics["gap_cases_count"] += 1

            # Top candidate that outranked the correct candidate
            top_match_res = ranked_matches[0]
            top_cand = top_match_res.candidate
            correct_cand = correct_match_res.candidate

            # Diagnose failure root cause
            score_delta = round(top_match_res.match_score - correct_match_res.match_score, 2)
            category = c.category.value

            # Determine cause
            if c.metadata.ambiguity or category == "AMBIGUOUS_NAME":
                cause = "AMBIGUITY_ERROR"
            elif top_cand.entity_type != correct_cand.entity_type:
                cause = "ENTITY_TYPE_ERROR"
            elif (
                top_match_res.breakdown.admin_context > correct_match_res.breakdown.admin_context
                and top_cand.district != gt.district
            ):
                cause = "ADMIN_CONTEXT_ERROR"
            elif (
                top_match_res.breakdown.pin_compatibility > correct_match_res.breakdown.pin_compatibility
                and top_cand.pincode != gt.pincode
            ):
                cause = "PIN_SIGNAL_ERROR"
            elif top_match_res.breakdown.name_similarity > correct_match_res.breakdown.name_similarity:
                cause = "NAME_SCORE_ERROR"
            elif score_delta <= 5.0:
                cause = "MULTIPLE_PLAUSIBLE_CANDIDATES"
            elif not parsed.district and not parsed.state and not parsed.pincode:
                cause = "MISSING_EVIDENCE"
            else:
                cause = "CORRECT_CANDIDATE_RANKED_LOW"

            gap_diagnostics["failure_classifications"][cause] += 1

            record_entry = {
                "case_id": c.id,
                "input_address": addr,
                "category": category,
                "correct_entity": f"{correct_cand.name} ({correct_cand.district}, {correct_cand.state})",
                "correct_rank": correct_rank,
                "correct_score": correct_match_res.match_score,
                "correct_sources": correct_cand.match_source,
                "predicted_entity": f"{top_cand.name} ({top_cand.district}, {top_cand.state})",
                "predicted_rank": 1,
                "predicted_score": top_match_res.match_score,
                "predicted_sources": top_cand.match_source,
                "score_delta": score_delta,
                "name_score_correct": correct_match_res.breakdown.name_similarity,
                "name_score_top": top_match_res.breakdown.name_similarity,
                "admin_score_correct": correct_match_res.breakdown.admin_context,
                "admin_score_top": top_match_res.breakdown.admin_context,
                "pin_score_correct": correct_match_res.breakdown.pin_compatibility,
                "pin_score_top": top_match_res.breakdown.pin_compatibility,
                "failure_classification": cause
            }

            gap_diagnostics["gap_records"].append(record_entry)
            flat_records.append(record_entry)

    # Save JSON report
    json_out = out_path / "ranking_gap_analysis.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(gap_diagnostics, f, indent=2, ensure_ascii=False)

    # Save CSV report
    csv_out = out_path / "ranking_gap_analysis.csv"
    if flat_records:
        pd.DataFrame(flat_records).to_csv(csv_out, index=False, encoding="utf-8")
    else:
        pd.DataFrame([{}]).to_csv(csv_out, index=False, encoding="utf-8")

    # Print summary
    total_loc = gap_diagnostics["cases_with_gt_locality"]
    r1 = gap_diagnostics["recall_1_count"]
    r5 = gap_diagnostics["recall_5_count"]
    gap = gap_diagnostics["gap_cases_count"]

    print("=================== RANKING GAP ANALYSIS (PHASE 6) ===================")
    print(f"Total Cases Evaluated (with Locality GT) : {total_loc}")
    print(f"Candidate Recall@1 Hits                 : {r1} ({r1 / total_loc * 100:.2f}%)")
    print(f"Candidate Recall@5 Hits                 : {r5} ({r5 / total_loc * 100:.2f}%)")
    print(f"Ranking Gap Cases (in Top 5 but not #1) : {gap} ({gap / total_loc * 100:.2f}%)")
    print("\nRoot Cause Failure Classification of Ranking Gap:")
    for k, v in gap_diagnostics["failure_classifications"].items():
        if v > 0:
            print(f"  {k:30s}: {v:4d} ({v / max(1, gap) * 100:.1f}%)")
    print(f"\nArtifacts Saved:")
    print(f"  JSON : {json_out}")
    print(f"  CSV  : {csv_out}")
    print("=======================================================================")

    return gap_diagnostics


def main():
    parser = argparse.ArgumentParser(description="Run Ranking Gap Diagnostic Analysis")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json", help="Path to benchmark dataset")
    parser.add_argument("--output", type=str, default="evaluation/results", help="Output directory")
    args = parser.parse_args()

    run_ranking_gap_analysis(dataset_path=Path(args.dataset), output_dir=Path(args.output))


if __name__ == "__main__":
    main()
