import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.load_dataset import DatasetLoader
from evaluation.schema import BenchmarkRecord
from app.entity_resolution.models import EntityType
from app.entity_resolution.ambiguity import AmbiguityDetector
from app.entity_resolution.ranking import context_aware_ranker
from app.entity_resolution.candidates import candidate_generator
from app.services.address_parser import AddressParser


class AmbiguityCalibrator:
    """Evaluates ambiguity detection across multiple score margin thresholds."""

    def __init__(self, dataset_path: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.dataset_path = dataset_path or DatasetLoader.get_default_dataset_path()
        self.output_dir = output_dir or (Path(__file__).parent / "results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_thresholds(
        self,
        thresholds: List[float] = [5.0, 8.0, 10.0, 12.0, 15.0, 20.0]
    ) -> List[Dict[str, Any]]:
        print("\n================ Running Ambiguity Calibration Suite ================")
        ds = DatasetLoader.load_from_json(self.dataset_path)
        cases = ds.cases
        print(f"Loaded {len(cases)} benchmark cases from {self.dataset_path}")

        detector = AmbiguityDetector()

        # Precompute candidate rankings for cases
        case_rankings = []
        for case in cases:
            parsed = AddressParser.parse(case.address)
            loc_query = parsed.locality or (case.ground_truth.locality if case.ground_truth else case.address)

            cands = candidate_generator.generate_candidates(
                loc_query,
                expected_type=EntityType.LOCALITY,
                context_state=parsed.state,
                context_district=parsed.district,
                context_pin=parsed.pincode,
                limit=10
            )

            ranked = context_aware_ranker.rank_candidates(
                candidates=cands,
                query_text=loc_query,
                context_state=parsed.state,
                context_district=parsed.district,
                context_pin=parsed.pincode,
                expected_type=EntityType.LOCALITY
            )

            case_rankings.append({
                "case": case,
                "expected_ambiguous": bool(case.metadata.ambiguity),
                "ranked": ranked
            })

        results = []
        for t in thresholds:
            tp, fp, fn, tn = 0, 0, 0, 0
            for item in case_rankings:
                expected = item["expected_ambiguous"]
                amb_res = detector.detect_ambiguity(item["ranked"], threshold=t)
                predicted = amb_res.is_ambiguous

                if predicted and expected:
                    tp += 1
                elif predicted and not expected:
                    fp += 1
                elif not predicted and expected:
                    fn += 1
                else:
                    tn += 1

            precision = round(tp / max(1, (tp + fp)), 4)
            recall = round(tp / max(1, (tp + fn)), 4)
            f1 = round(2 * (precision * recall) / max(1e-6, (precision + recall)), 4)

            results.append({
                "threshold_delta": t,
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "true_negatives": tn,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            })
            print(f"  Threshold Delta: {t:4.1f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")

        # Export JSON & CSV
        df = pd.DataFrame(results)
        csv_path = self.output_dir / "ambiguity_calibration.csv"
        json_path = self.output_dir / "ambiguity_calibration.json"

        df.to_csv(csv_path, index=False, encoding="utf-8")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n[OK] Calibration complete! Results exported to:")
        print(f"  - {csv_path}")
        print(f"  - {json_path}")
        print("====================================================================\n")

        return results


def main():
    parser = argparse.ArgumentParser(description="Calibrate Ambiguity Delta Thresholds")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json")
    parser.add_argument("--output", type=str, default="evaluation/results")
    args = parser.parse_args()

    calibrator = AmbiguityCalibrator(
        dataset_path=Path(args.dataset),
        output_dir=Path(args.output)
    )
    calibrator.evaluate_thresholds()


if __name__ == "__main__":
    main()
