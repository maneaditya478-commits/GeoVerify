import sys
import asyncio
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
    AdminPenaltiesConfig,
    ConfidenceBandsConfig
)
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.candidates import candidate_generator
from app.schemas.address import Coordinates
from app.services.address_parser import AddressParser


class AblationStudyRunner:
    """Executes multi-configuration ablation benchmarks."""

    def __init__(self, dataset_path: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.dataset_path = dataset_path or DatasetLoader.get_default_dataset_path()
        self.output_dir = output_dir or (Path(__file__).parent / "results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_ablation_configs(self) -> Dict[str, Phase6RankingConfig]:
        """Defines the ablation configurations to test."""
        configs = {}

        # 1. Full Phase 6 Ranking
        configs["Full_Phase6_Model"] = Phase6RankingConfig()

        # 2. Ablation: No Admin Penalties
        no_penalties = Phase6RankingConfig()
        no_penalties.penalties = AdminPenaltiesConfig(
            state_conflict=0.0,
            district_conflict=0.0,
            subdistrict_conflict=0.0,
            locality_conflict=0.0,
            pin_circle_conflict=0.0,
            entity_type_mismatch=0.0
        )
        configs["Ablation_No_Admin_Penalties"] = no_penalties

        # 3. Ablation: No Hierarchy / Parent-Child Compatibility
        no_parent_child = Phase6RankingConfig()
        no_parent_child.weights = RankingWeightsConfig(
            name_similarity=0.30,
            admin_context=0.30,
            parent_child_compatibility=0.0,
            pin_compatibility=0.10,
            geographic_compatibility=0.10,
            transliteration_phonetic=0.08,
            entity_type_compatibility=0.07,
            retrieval_consensus=0.03,
            data_quality=0.02
        )
        configs["Ablation_No_Parent_Child_Hierarchy"] = no_parent_child

        # 4. Ablation: No PIN Compatibility
        no_pin = Phase6RankingConfig()
        no_pin.weights = RankingWeightsConfig(
            name_similarity=0.28,
            admin_context=0.28,
            parent_child_compatibility=0.18,
            pin_compatibility=0.0,
            geographic_compatibility=0.12,
            transliteration_phonetic=0.07,
            entity_type_compatibility=0.05,
            retrieval_consensus=0.02,
            data_quality=0.0
        )
        configs["Ablation_No_PIN_Compatibility"] = no_pin

        # 5. Ablation: No Spatial / Geographic Proximity
        no_geo = Phase6RankingConfig()
        no_geo.weights = RankingWeightsConfig(
            name_similarity=0.28,
            admin_context=0.28,
            parent_child_compatibility=0.18,
            pin_compatibility=0.12,
            geographic_compatibility=0.0,
            transliteration_phonetic=0.07,
            entity_type_compatibility=0.05,
            retrieval_consensus=0.02,
            data_quality=0.0
        )
        configs["Ablation_No_Geographic_Proximity"] = no_geo

        # 6. Ablation: No Phonetic / Transliteration
        no_phonetic = Phase6RankingConfig()
        no_phonetic.weights = RankingWeightsConfig(
            name_similarity=0.27,
            admin_context=0.27,
            parent_child_compatibility=0.16,
            pin_compatibility=0.11,
            geographic_compatibility=0.11,
            transliteration_phonetic=0.0,
            entity_type_compatibility=0.05,
            retrieval_consensus=0.03,
            data_quality=0.0
        )
        configs["Ablation_No_Phonetic_Translit"] = no_phonetic

        # 7. Ablation: No Consensus Bonus
        no_consensus = Phase6RankingConfig()
        no_consensus.weights = RankingWeightsConfig(
            name_similarity=0.26,
            admin_context=0.26,
            parent_child_compatibility=0.15,
            pin_compatibility=0.10,
            geographic_compatibility=0.10,
            transliteration_phonetic=0.05,
            entity_type_compatibility=0.05,
            retrieval_consensus=0.0,
            data_quality=0.03
        )
        configs["Ablation_No_Consensus_Bonus"] = no_consensus

        # 8. Phase 5 Baseline (Raw Name + Admin without Phase 6 penalties)
        phase5_baseline = Phase6RankingConfig()
        phase5_baseline.weights = RankingWeightsConfig(
            name_similarity=0.40,
            admin_context=0.25,
            parent_child_compatibility=0.0,
            pin_compatibility=0.15,
            geographic_compatibility=0.15,
            transliteration_phonetic=0.0,
            entity_type_compatibility=0.05,
            retrieval_consensus=0.0,
            data_quality=0.0
        )
        phase5_baseline.penalties = AdminPenaltiesConfig(
            state_conflict=0.0,
            district_conflict=0.0,
            subdistrict_conflict=0.0,
            locality_conflict=0.0,
            pin_circle_conflict=0.0,
            entity_type_mismatch=0.0
        )
        configs["Phase5_Baseline"] = phase5_baseline

        return configs

    def evaluate_config_on_cases(
        self,
        config_name: str,
        config: Phase6RankingConfig,
        cases: List[BenchmarkRecord]
    ) -> Dict[str, Any]:
        """Evaluates a single ranking configuration across benchmark cases."""
        ranker = ContextAwareRanker(config=config)

        total_locality_cases = 0
        r1_hits = 0
        r3_hits = 0
        r5_hits = 0
        r10_hits = 0

        for case in cases:
            gt_loc = case.ground_truth.locality
            if not gt_loc:
                continue

            total_locality_cases += 1
            parsed = AddressParser.parse(case.address)

            # Generate candidates
            loc_candidates = candidate_generator.generate_candidates(
                parsed.locality or gt_loc,
                expected_type=EntityType.LOCALITY,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                limit=15
            )

            # Rank with this config
            ranked_results = ranker.rank_candidates(
                candidates=loc_candidates,
                query_text=parsed.locality or gt_loc,
                context_state=parsed.state or case.ground_truth.state,
                context_district=parsed.district or case.ground_truth.district,
                context_subdistrict=parsed.subdistrict or case.ground_truth.subdistrict,
                context_pin=parsed.pincode or case.ground_truth.pincode,
                expected_type=EntityType.LOCALITY
            )

            cand_names = [r.candidate.name.lower() for r in ranked_results]
            gt_lower = gt_loc.lower()

            if len(cand_names) >= 1 and any(gt_lower in n or n in gt_lower for n in cand_names[:1]):
                r1_hits += 1
            if len(cand_names) >= 1 and any(gt_lower in n or n in gt_lower for n in cand_names[:3]):
                r3_hits += 1
            if len(cand_names) >= 1 and any(gt_lower in n or n in gt_lower for n in cand_names[:5]):
                r5_hits += 1
            if len(cand_names) >= 1 and any(gt_lower in n or n in gt_lower for n in cand_names[:10]):
                r10_hits += 1

        r1 = round(r1_hits / max(1, total_locality_cases), 4)
        r3 = round(r3_hits / max(1, total_locality_cases), 4)
        r5 = round(r5_hits / max(1, total_locality_cases), 4)
        r10 = round(r10_hits / max(1, total_locality_cases), 4)

        return {
            "configuration": config_name,
            "total_locality_cases": total_locality_cases,
            "recall_at_1": r1,
            "recall_at_3": r3,
            "recall_at_5": r5,
            "recall_at_10": r10,
            "r1_percentage": round(r1 * 100, 2),
            "r5_percentage": round(r5 * 100, 2)
        }

    def run(self, sample_size: Optional[int] = None) -> List[Dict[str, Any]]:
        print("\n================ Starting Phase 6 Ablation Study ================")
        ds = DatasetLoader.load_from_json(self.dataset_path)
        cases = ds.cases[:sample_size] if sample_size else ds.cases
        print(f"Loaded {len(cases)} benchmark cases from {self.dataset_path}")

        ablation_configs = self._get_ablation_configs()
        results: List[Dict[str, Any]] = []

        for name, cfg in ablation_configs.items():
            print(f"  Evaluating configuration: {name} ...")
            res = self.evaluate_config_on_cases(name, cfg, cases)
            results.append(res)
            print(f"    -> Recall@1: {res['r1_percentage']}% | Recall@5: {res['r5_percentage']}%")

        # Export results
        df = pd.DataFrame(results)
        csv_path = self.output_dir / "ablation_results.csv"
        json_path = self.output_dir / "ablation_results.json"

        df.to_csv(csv_path, index=False, encoding="utf-8")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n[OK] Ablation Study Complete!")
        print(f"  Results saved to: {csv_path} and {json_path}")
        print("=================================================================\n")
        return results


def main():
    parser = argparse.ArgumentParser(description="Run Phase 6 Ranking Ablation Study")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json")
    parser.add_argument("--output", type=str, default="evaluation/results")
    parser.add_argument("--sample", type=int, default=None, help="Optional sample size for fast evaluation")
    args = parser.parse_args()

    runner = AblationStudyRunner(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output)
    )
    runner.run(sample_size=args.sample)


if __name__ == "__main__":
    main()
