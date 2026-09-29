"""Ranking Regression Diagnostic and Classification Pipeline (Phase 6.1).

Identifies, classifies, and audits every case where Phase 5 baseline ranked the correct
candidate at Rank #1, but Phase 6 Context-Aware Ranker demoted it.
"""

import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.load_dataset import DatasetLoader
from evaluation.schema import BenchmarkDataset, BenchmarkRecord
from app.entity_resolution.models import EntityType, CandidateEntity, EntityMatchResult
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.ranking_config import (
    Phase6RankingConfig,
    RankingWeightsConfig,
    AdminPenaltiesConfig
)
from app.entity_resolution.candidates import candidate_generator
from app.services.address_parser import AddressParser


class RankingRegressionAnalyzer:
    """Analyzes ranking regressions between Phase 5 and Phase 6 candidate ranking."""

    def __init__(self, dataset_path: Optional[Path] = None, output_dir: Optional[Path] = None, smoke: bool = False, limit: Optional[int] = None):
        self.dataset_path = dataset_path or DatasetLoader.get_default_dataset_path()
        self.output_dir = output_dir or (Path(__file__).parent.parent / "results" / "phase6_1")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.smoke = smoke
        self.limit = limit

    def _get_phase5_ranker(self) -> ContextAwareRanker:
        """Constructs Phase 5 baseline ranker (Name 40%, Admin 25%, PIN 15%, Prox 15%, Type 5%, 0 penalties)."""
        p5_cfg = Phase6RankingConfig(
            weights=RankingWeightsConfig(
                name_similarity=0.40,
                admin_context=0.25,
                parent_child_compatibility=0.0,
                pin_compatibility=0.15,
                geographic_compatibility=0.15,
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
        return ContextAwareRanker(config=p5_cfg)

    def _get_phase6_ranker(self) -> ContextAwareRanker:
        """Constructs full Phase 6 context-aware ranker."""
        return ContextAwareRanker()

    def classify_regression(
        self,
        case: BenchmarkRecord,
        p5_truth_res: Optional[EntityMatchResult],
        p6_truth_res: Optional[EntityMatchResult],
        p6_top_res: EntityMatchResult,
        parsed_context: Dict[str, Any]
    ) -> str:
        """
        Deterministically classifies the root cause of the ranking regression.
        """
        gt_loc = (case.ground_truth.locality or "").lower()
        top_name = p6_top_res.candidate.name.lower()
        top_type = p6_top_res.candidate.entity_type

        # Check if truth candidate received severe penalties in Phase 6
        truth_penalties = p6_truth_res.ranking_explanation.applied_penalties if p6_truth_res and p6_truth_res.ranking_explanation else []
        top_penalties = p6_top_res.ranking_explanation.applied_penalties if p6_top_res.ranking_explanation else []

        penalty_names = [p.name for p in truth_penalties]

        # 1. Check for Entity Type Over-penalty / Under-penalty
        if "ENTITY_TYPE_MISMATCH" in penalty_names:
            return "ENTITY_TYPE_OVERPENALTY"
        if top_type in [EntityType.DISTRICT, EntityType.STATE] and top_name == gt_loc:
            return "ENTITY_TYPE_UNDERPENALTY"

        # 2. Check for Admin Context Over-penalty / Under-penalty
        if "STATE_CONFLICT" in penalty_names or "DISTRICT_CONFLICT" in penalty_names or "SUBDISTRICT_CONFLICT" in penalty_names:
            # Did the query text actually omit state/district or have a partial token?
            if not parsed_context.get("state") or not parsed_context.get("district"):
                return "ADMIN_CONTEXT_OVERPENALTY"
            return "ADMIN_CONTEXT_OVERPENALTY"

        # 3. Check for PIN Circle Over-penalty
        if "PIN_CIRCLE_CONFLICT" in penalty_names:
            return "PIN_OVERWEIGHT"

        # 4. Check Parent-Child Score Gap
        if p6_truth_res and p6_truth_res.breakdown.parent_child_compatibility < 5.0 and p6_top_res.breakdown.parent_child_compatibility >= 12.0:
            return "PARENT_CHILD_ERROR"

        # 5. Check Consensus Score Error
        if p6_top_res.breakdown.retrieval_consensus > (p6_truth_res.breakdown.retrieval_consensus if p6_truth_res else 0) + 1.5:
            return "CONSENSUS_SCORE_ERROR"

        # 6. Check Spatial Proximity Error
        if p6_top_res.breakdown.geographic_proximity > (p6_truth_res.breakdown.geographic_proximity if p6_truth_res else 0) + 5.0:
            return "SPATIAL_OVERWEIGHT"

        # 7. Check Phonetic / Transliteration Score Error
        if p6_top_res.breakdown.transliteration_phonetic > (p6_truth_res.breakdown.transliteration_phonetic if p6_truth_res else 0) + 2.0:
            return "PHONETIC_SCORE_ERROR"

        # 8. Check Name Score Weighting
        if p5_truth_res and p6_truth_res:
            p5_margin = p5_truth_res.breakdown.name_similarity
            p6_margin = p6_truth_res.breakdown.name_similarity
            if p5_margin >= 35.0 and p6_margin <= 20.0:
                return "NAME_SCORE_ERROR"

        # 9. Check Tie Breaking
        if p6_truth_res and abs(p6_truth_res.match_score - p6_top_res.match_score) < 0.5:
            return "TIE_BREAKING_ERROR"

        return "UNKNOWN"

    def run_regression_audit(self) -> Dict[str, Any]:
        print("\n================ Running Phase 6.1 Ranking Regression Audit ================")
        ds = DatasetLoader.load_from_json(self.dataset_path)
        cases = ds.cases

        p5_ranker = self._get_phase5_ranker()
        p6_ranker = self._get_phase6_ranker()

        total_evaluated = 0
        p5_r1_hits = 0
        p6_r1_hits = 0

        regressions: List[Dict[str, Any]] = []
        classification_counts: Dict[str, int] = {}
        penalty_audit_stats: Dict[str, Dict[str, int]] = {
            "STATE_CONFLICT": {"triggered": 0, "on_truth": 0, "caused_regression": 0},
            "DISTRICT_CONFLICT": {"triggered": 0, "on_truth": 0, "caused_regression": 0},
            "SUBDISTRICT_CONFLICT": {"triggered": 0, "on_truth": 0, "caused_regression": 0},
            "ENTITY_TYPE_MISMATCH": {"triggered": 0, "on_truth": 0, "caused_regression": 0},
            "PIN_CIRCLE_CONFLICT": {"triggered": 0, "on_truth": 0, "caused_regression": 0}
        }

        for case in cases:
            gt_loc = case.ground_truth.locality
            if not gt_loc:
                continue

            total_evaluated += 1
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

            parsed_context = {
                "state": parsed.state,
                "district": parsed.district,
                "subdistrict": parsed.subdistrict,
                "locality": parsed.locality,
                "pincode": parsed.pincode
            }

            # Phase 5 Ranking
            p5_res = p5_ranker.rank_candidates(
                candidates=cands,
                query_text=loc_query,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_subdistrict=parsed.subdistrict or case.ground_truth.subdistrict,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                expected_type=EntityType.LOCALITY
            )

            # Phase 6 Ranking
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

            p5_is_r1 = any(gt_lower in n or n in gt_lower for n in p5_names[:1])
            p6_is_r1 = any(gt_lower in n or n in gt_lower for n in p6_names[:1])

            if p5_is_r1: p5_r1_hits += 1
            if p6_is_r1: p6_r1_hits += 1

            # Find ranks of truth
            p5_truth_rank = next((idx + 1 for idx, n in enumerate(p5_names) if gt_lower in n or n in gt_lower), None)
            p6_truth_rank = next((idx + 1 for idx, n in enumerate(p6_names) if gt_lower in n or n in gt_lower), None)

            p5_truth_res = p5_res[p5_truth_rank - 1] if p5_truth_rank else None
            p6_truth_res = p6_res[p6_truth_rank - 1] if p6_truth_rank else None

            # Record penalty triggers
            for r in p6_res:
                if r.ranking_explanation:
                    for pen in r.ranking_explanation.applied_penalties:
                        if pen.name in penalty_audit_stats:
                            penalty_audit_stats[pen.name]["triggered"] += 1

            if p6_truth_res and p6_truth_res.ranking_explanation:
                for pen in p6_truth_res.ranking_explanation.applied_penalties:
                    if pen.name in penalty_audit_stats:
                        penalty_audit_stats[pen.name]["on_truth"] += 1

            # Check for ranking regression: Phase 5 was correct (Rank 1), but Phase 6 is not Rank 1
            if p5_is_r1 and not p6_is_r1:
                p6_top = p6_res[0]
                classification = self.classify_regression(
                    case=case,
                    p5_truth_res=p5_truth_res,
                    p6_truth_res=p6_truth_res,
                    p6_top_res=p6_top,
                    parsed_context=parsed_context
                )

                classification_counts[classification] = classification_counts.get(classification, 0) + 1

                # Record penalty causes
                if p6_truth_res and p6_truth_res.ranking_explanation:
                    for pen in p6_truth_res.ranking_explanation.applied_penalties:
                        if pen.name in penalty_audit_stats:
                            penalty_audit_stats[pen.name]["caused_regression"] += 1

                reg_record = {
                    "case_id": case.id,
                    "input_address": case.address,
                    "ground_truth": gt_loc,
                    "category": case.category.value,
                    "language": case.language.value,
                    "script": case.script.value,
                    "regression_classification": classification,
                    "phase5_top_candidate": p5_res[0].candidate.name if p5_res else "None",
                    "phase5_top_score": p5_res[0].match_score if p5_res else 0.0,
                    "phase5_rank_of_truth": p5_truth_rank,
                    "phase6_top_candidate": p6_top.candidate.name,
                    "phase6_top_score": p6_top.match_score,
                    "phase6_rank_of_truth": p6_truth_rank,
                    "phase6_truth_score": p6_truth_res.match_score if p6_truth_res else 0.0,
                    "truth_penalties": [p.model_dump() for p in (p6_truth_res.ranking_explanation.applied_penalties if p6_truth_res and p6_truth_res.ranking_explanation else [])],
                    "top_penalties": [p.model_dump() for p in (p6_top.ranking_explanation.applied_penalties if p6_top.ranking_explanation else [])],
                    "administrative_context": parsed_context,
                    "truth_entity_type": p6_truth_res.candidate.entity_type.value if p6_truth_res else "None",
                    "top_entity_type": p6_top.candidate.entity_type.value,
                    "p5_candidate_list": [r.candidate.name for r in p5_res[:5]],
                    "p6_candidate_list": [r.candidate.name for r in p6_res[:5]],
                    "p6_truth_breakdown": p6_truth_res.breakdown.model_dump() if p6_truth_res else {},
                    "p6_top_breakdown": p6_top.breakdown.model_dump()
                }
                regressions.append(reg_record)

        # Build penalty effectiveness summary
        penalty_rows = []
        for pen_name, stats in penalty_audit_stats.items():
            trig = stats["triggered"]
            on_truth = stats["on_truth"]
            caused_reg = stats["caused_regression"]
            correct_triggers = trig - on_truth
            effectiveness_pct = round((correct_triggers / max(1, trig)) * 100, 2)
            penalty_rows.append({
                "penalty_name": pen_name,
                "total_triggered": trig,
                "triggered_on_correct_truth": on_truth,
                "caused_ranking_regression": caused_reg,
                "correct_triggers": correct_triggers,
                "effectiveness_rate_pct": effectiveness_pct
            })

        df_penalties = pd.DataFrame(penalty_rows)
        penalty_csv_path = self.output_dir / "penalty_effectiveness.csv"
        df_penalties.to_csv(penalty_csv_path, index=False, encoding="utf-8")

        # Export regression JSON and CSV
        reg_json_path = self.output_dir / "ranking_regressions.json"
        reg_csv_path = self.output_dir / "ranking_regressions.csv"

        with open(reg_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "total_evaluated_cases": total_evaluated,
                "phase5_recall_at_1": round(p5_r1_hits / max(1, total_evaluated), 4),
                "phase6_recall_at_1": round(p6_r1_hits / max(1, total_evaluated), 4),
                "total_regressions": len(regressions),
                "classification_breakdown": classification_counts,
                "regressions": regressions
            }, f, indent=2)

        df_reg = pd.DataFrame([{
            "case_id": r["case_id"],
            "address": r["input_address"],
            "ground_truth": r["ground_truth"],
            "category": r["category"],
            "classification": r["regression_classification"],
            "phase5_top": r["phase5_top_candidate"],
            "phase5_score": r["phase5_top_score"],
            "phase6_top": r["phase6_top_candidate"],
            "phase6_score": r["phase6_top_score"],
            "phase6_truth_score": r["phase6_truth_score"],
            "phase6_truth_rank": r["phase6_rank_of_truth"]
        } for r in regressions])
        df_reg.to_csv(reg_csv_path, index=False, encoding="utf-8")

        print(f"\n[OK] Ranking Regression Audit Complete!")
        print(f"  Total Evaluated Cases: {total_evaluated}")
        print(f"  Phase 5 Recall@1     : {round(p5_r1_hits / max(1, total_evaluated) * 100, 2)}%")
        print(f"  Phase 6 Recall@1     : {round(p6_r1_hits / max(1, total_evaluated) * 100, 2)}%")
        print(f"  Total Regressions    : {len(regressions)}")
        print("\n  Classification Breakdown:")
        for cat, count in sorted(classification_counts.items(), key=lambda x: x[1], reverse=True):
            pct = round(count / max(1, len(regressions)) * 100, 1)
            print(f"    - {cat:30s}: {count:3d} ({pct}%)")

        print(f"\n  Files generated:")
        print(f"    - {reg_json_path}")
        print(f"    - {reg_csv_path}")
        print(f"    - {penalty_csv_path}")
        print("============================================================================\n")

        return {
            "total_regressions": len(regressions),
            "classification_breakdown": classification_counts,
            "regressions": regressions,
            "penalties": penalty_rows
        }


def main():
    parser = argparse.ArgumentParser(description="Run Phase 6.1 Ranking Regression Audit")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json")
    parser.add_argument("--output", type=str, default="evaluation/results/phase6_1")
    args = parser.parse_args()

    analyzer = RankingRegressionAnalyzer(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output)
    )
    analyzer.run_regression_audit()


if __name__ == "__main__":
    main()
