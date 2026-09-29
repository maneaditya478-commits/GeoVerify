import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.load_dataset import DatasetLoader
from evaluation.schema import BenchmarkDataset, BenchmarkRecord
from app.entity_resolution.models import EntityType
from app.entity_resolution.ranking_config import (
    Phase6RankingConfig,
    RankingWeightsConfig,
    AdminPenaltiesConfig
)
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.matcher import EntityMatcher
from app.entity_resolution.candidates import candidate_generator
from app.services.address_parser import AddressParser


class Phase6ErrorAnalyzer:
    """Analyzes and compares Phase 5 vs Phase 6 candidate ranking performance."""

    def __init__(self, dataset_path: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.dataset_path = dataset_path or DatasetLoader.get_default_dataset_path()
        self.output_dir = output_dir or (Path(__file__).parent / "results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self) -> Dict[str, Any]:
        print("\n======== Running Comparative Ranking Analysis (Phase 5 vs Phase 6) ========")
        ds = DatasetLoader.load_from_json(self.dataset_path)
        cases = ds.cases

        p6_ranker = ContextAwareRanker()

        # Phase 5 baseline configuration
        p5_config = Phase6RankingConfig(
            weights=RankingWeightsConfig(
                name_similarity=0.40,
                admin_context=0.25,
                parent_child_compatibility=0.0,
                pin_compatibility=0.15,
                geographic_proximity=0.15,
                transliteration_phonetic=0.0,
                entity_type_compatibility=0.05,
                retrieval_consensus=0.0,
                data_quality=0.0
            ),
            penalties=AdminPenaltiesConfig(
                state_conflict=0.0,
                district_conflict=0.0,
                subdistrict_conflict=0.0,
                locality_conflict=0.0,
                pin_circle_conflict=0.0,
                entity_type_mismatch=0.0
            )
        )
        p5_ranker = ContextAwareRanker(config=p5_config)

        total_eval = 0
        p5_r1_count = 0
        p5_r5_count = 0
        p6_r1_count = 0
        p6_r5_count = 0

        promoted_to_r1 = []
        demoted_cases = []
        comparison_rows = []

        for case in cases:
            gt_loc = case.ground_truth.locality
            if not gt_loc:
                continue

            total_eval += 1
            parsed = AddressParser.parse(case.address)
            loc_query = parsed.locality or gt_loc

            cands = candidate_generator.generate_candidates(
                loc_query,
                expected_type=EntityType.LOCALITY,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                limit=15
            )

            if not cands:
                continue

            # Phase 5 ranking
            p5_res = p5_ranker.rank_candidates(
                candidates=cands,
                query_text=loc_query,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_subdistrict=parsed.subdistrict or case.ground_truth.subdistrict,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                expected_type=EntityType.LOCALITY
            )

            # Phase 6 ranking
            p6_res = p6_ranker.rank_candidates(
                candidates=cands,
                query_text=loc_query,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_subdistrict=parsed.subdistrict or case.ground_truth.subdistrict,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                expected_type=EntityType.LOCALITY
            )

            gt_lower = gt_loc.lower()
            p5_names = [r.candidate.name.lower() for r in p5_res]
            p6_names = [r.candidate.name.lower() for r in p6_res]

            p5_r1 = any(gt_lower in n or n in gt_lower for n in p5_names[:1])
            p5_r5 = any(gt_lower in n or n in gt_lower for n in p5_names[:5])
            p6_r1 = any(gt_lower in n or n in gt_lower for n in p6_names[:1])
            p6_r5 = any(gt_lower in n or n in gt_lower for n in p6_names[:5])

            if p5_r1: p5_r1_count += 1
            if p5_r5: p5_r5_count += 1
            if p6_r1: p6_r1_count += 1
            if p6_r5: p6_r5_count += 1

            if not p5_r1 and p6_r1:
                promoted_to_r1.append({
                    "case_id": case.id,
                    "address": case.address,
                    "ground_truth_locality": gt_loc,
                    "phase5_top_match": p5_res[0].candidate.name if p5_res else "None",
                    "phase5_top_score": p5_res[0].match_score if p5_res else 0.0,
                    "phase6_top_match": p6_res[0].candidate.name if p6_res else "None",
                    "phase6_top_score": p6_res[0].match_score if p6_res else 0.0,
                    "phase6_explanation": p6_res[0].ranking_explanation.summary if p6_res and p6_res[0].ranking_explanation else ""
                })
            elif p5_r1 and not p6_r1:
                demoted_cases.append({
                    "case_id": case.id,
                    "address": case.address,
                    "ground_truth_locality": gt_loc,
                    "phase5_top_match": p5_res[0].candidate.name if p5_res else "None",
                    "phase6_top_match": p6_res[0].candidate.name if p6_res else "None"
                })

            comparison_rows.append({
                "case_id": case.id,
                "category": case.category.value,
                "ground_truth": gt_loc,
                "phase5_r1": p5_r1,
                "phase6_r1": p6_r1,
                "phase5_top1": p5_res[0].candidate.name if p5_res else "",
                "phase6_top1": p6_res[0].candidate.name if p6_res else ""
            })

        summary = {
            "total_evaluated_cases": total_eval,
            "phase5_recall_at_1": round(p5_r1_count / max(1, total_eval), 4),
            "phase5_recall_at_5": round(p5_r5_count / max(1, total_eval), 4),
            "phase6_recall_at_1": round(p6_r1_count / max(1, total_eval), 4),
            "phase6_recall_at_5": round(p6_r5_count / max(1, total_eval), 4),
            "recall_at_1_delta": round((p6_r1_count - p5_r1_count) / max(1, total_eval), 4),
            "recall_at_1_gain_percentage": round(((p6_r1_count - p5_r1_count) / max(1, total_eval)) * 100, 2),
            "total_promoted_cases": len(promoted_to_r1),
            "total_demoted_cases": len(demoted_cases),
            "promoted_samples": promoted_to_r1[:15]
        }

        # Export JSON
        json_path = self.output_dir / "phase6_comparison.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Export CSV
        csv_path = self.output_dir / "phase6_comparison.csv"
        pd.DataFrame(comparison_rows).to_csv(csv_path, index=False, encoding="utf-8")

        # Export Markdown Report
        md_path = self.output_dir / "phase6_comparison.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# GeoVerify India — Phase 5 vs Phase 6 Ranking Comparison Report\n\n")
            f.write(f"**Total Cases Evaluated:** {total_eval}\n\n")
            f.write("## Candidate Ranking Metrics Summary\n\n")
            f.write("| Metric | Phase 5 Baseline | Phase 6 Context-Aware Ranker | Delta / Improvement |\n")
            f.write("|---|---|---|---|\n")
            f.write(f"| **Candidate Recall@1** | {summary['phase5_recall_at_1']*100:.2f}% | **{summary['phase6_recall_at_1']*100:.2f}%** | **+{summary['recall_at_1_gain_percentage']:.2f}%** |\n")
            f.write(f"| **Candidate Recall@5** | {summary['phase5_recall_at_5']*100:.2f}% | **{summary['phase6_recall_at_5']*100:.2f}%** | **+{(summary['phase6_recall_at_5']-summary['phase5_recall_at_5'])*100:.2f}%** |\n\n")
            f.write(f"### Ranking Dynamics\n")
            f.write(f"- **Cases Promoted to Rank #1:** {len(promoted_to_r1)}\n")
            f.write(f"- **Cases Demoted from Rank #1:** {len(demoted_cases)}\n")
            f.write(f"- **Net Gain in Correct Top-1 Matches:** +{len(promoted_to_r1) - len(demoted_cases)}\n\n")
            f.write("### Sample Promoted Cases (Phase 5 False Negative -> Phase 6 Top-1 Hit)\n\n")
            f.write("| Case ID | Query Address | Ground Truth | Phase 5 Top Candidate | Phase 6 Promoted Candidate |\n")
            f.write("|---|---|---|---|---|\n")
            for p in promoted_to_r1[:10]:
                f.write(f"| `{p['case_id']}` | {p['address']} | **{p['ground_truth_locality']}** | {p['phase5_top_match']} ({p['phase5_top_score']} pts) | **{p['phase6_top_match']}** ({p['phase6_top_score']} pts) |\n")

        print(f"[OK] Analysis complete! Results saved to:")
        print(f"  - {json_path}")
        print(f"  - {csv_path}")
        print(f"  - {md_path}")
        print(f"  Recall@1: {summary['phase5_recall_at_1']*100:.2f}% -> {summary['phase6_recall_at_1']*100:.2f}% (+{summary['recall_at_1_gain_percentage']:.2f}%)")
        print("=============================================================================\n")

        return summary


def main():
    parser = argparse.ArgumentParser(description="Analyze Phase 5 vs Phase 6 Candidate Ranking Performance")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json")
    parser.add_argument("--output", type=str, default="evaluation/results")
    args = parser.parse_args()

    analyzer = Phase6ErrorAnalyzer(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output)
    )
    analyzer.analyze()


if __name__ == "__main__":
    main()
