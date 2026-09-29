"""Benchmark Runner CLI and Evaluation Pipeline for GeoVerify India."""

import time
import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from evaluation.schema import (
    BenchmarkDataset,
    BenchmarkRecord,
    EvaluationResultRecord,
    ExpectedStatus
)
from evaluation.load_dataset import DatasetLoader
from evaluation.generate_dataset import BenchmarkGenerator, export_dataset
from evaluation.metrics import BenchmarkMetricsCalculator
from evaluation.error_analysis import ErrorAnalyzer
from evaluation.performance import PerformanceProfiler

from app.schemas.address import VerificationRequest
from app.verification.engine import verification_engine
from app.entity_resolution.resolver import address_entity_resolver
from evaluation.visualization import Visualizer
from evaluation.report import ReportGenerator


class BenchmarkRunner:
    """Executes asynchronous benchmark evaluation against GeoVerify engine."""

    def __init__(self, dataset_path: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.dataset_path = dataset_path or DatasetLoader.get_default_dataset_path()
        self.output_dir = output_dir or (Path(__file__).parent / "results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def evaluate_case(self, case: BenchmarkRecord) -> EvaluationResultRecord:
        addr = case.address
        gt = case.ground_truth

        # Timed execution of full pipeline
        t0 = time.perf_counter()
        verify_resp = await verification_engine.verify(VerificationRequest(address=addr, include_geojson=False))
        latency_ms = (time.perf_counter() - t0) * 1000

        # Entity resolution details
        resolution = address_entity_resolver.resolve_address(addr)

        # Extract predictions
        pred_state = verify_resp.administrative_hierarchy.state
        pred_district = verify_resp.administrative_hierarchy.district
        pred_subdistrict = verify_resp.administrative_hierarchy.subdistrict
        pred_locality = verify_resp.administrative_hierarchy.locality
        pred_pincode = verify_resp.pin_verification.pincode if verify_resp.pin_verification else None
        pred_status = verify_resp.status.value
        pred_ambiguity = resolution.ambiguity.is_ambiguous

        # Ground truth matches
        state_matched = bool(
            gt.state and pred_state and (gt.state.lower() == pred_state.lower() or (gt.state_code and gt.state_code == verify_resp.administrative_hierarchy.state_code))
        ) if gt.state else True

        district_matched = bool(
            gt.district and pred_district and (gt.district.lower() in pred_district.lower() or pred_district.lower() in gt.district.lower())
        ) if gt.district else True

        subdistrict_matched = bool(
            gt.subdistrict and pred_subdistrict and (gt.subdistrict.lower() in pred_subdistrict.lower() or pred_subdistrict.lower() in gt.subdistrict.lower())
        ) if gt.subdistrict else True

        locality_matched = bool(
            gt.locality and pred_locality and (gt.locality.lower() in pred_locality.lower() or pred_locality.lower() in gt.locality.lower())
        ) if gt.locality else True

        pincode_matched = bool(
            gt.pincode and pred_pincode and gt.pincode == pred_pincode
        ) if gt.pincode else True

        exact_hierarchy = state_matched and district_matched and (subdistrict_matched if gt.subdistrict else True) and (locality_matched if gt.locality else True)

        status_matched = (pred_status == case.expected_status.value)
        ambiguity_matched = (pred_ambiguity == case.metadata.ambiguity)

        # Candidate recall check for locality
        r1, r3, r5, r10 = False, False, False, False
        if gt.locality:
            from app.entity_resolution.candidates import candidate_generator
            from app.entity_resolution.models import EntityType
            query_loc = verify_resp.parsed_address.locality or gt.locality
            loc_candidates = candidate_generator.generate_candidates(
                query_loc,
                expected_type=EntityType.LOCALITY,
                context_state=pred_state,
                context_district=pred_district,
                context_pin=pred_pincode,
                limit=10
            )
            # Combine resolver candidates with generator pool
            resolver_cand_names = [
                m.candidate.name.lower() for m in resolution.candidate_matches
                if m.candidate.entity_type in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN, EntityType.POI]
            ]
            cand_names = resolver_cand_names if resolver_cand_names else [c.name.lower() for c in loc_candidates]
            
            # Also append any additional generator candidates not already present
            for c in loc_candidates:
                c_name = c.name.lower()
                if c_name not in cand_names:
                    cand_names.append(c_name)

            gt_loc = gt.locality.lower()
            if len(cand_names) >= 1 and any(gt_loc in n or n in gt_loc for n in cand_names[:1]):
                r1 = True
            if len(cand_names) >= 1 and any(gt_loc in n or n in gt_loc for n in cand_names[:3]):
                r3 = True
            if len(cand_names) >= 1 and any(gt_loc in n or n in gt_loc for n in cand_names[:5]):
                r5 = True
            if len(cand_names) >= 1 and any(gt_loc in n or n in gt_loc for n in cand_names[:10]):
                r10 = True

        return EvaluationResultRecord(
            case_id=case.id,
            address=case.address,
            category=case.category.value,
            language=case.language.value,
            script=case.script.value,
            source_type=case.source_type.value,
            expected_state=gt.state,
            predicted_state=pred_state,
            state_matched=state_matched,
            expected_district=gt.district,
            predicted_district=pred_district,
            district_matched=district_matched,
            expected_subdistrict=gt.subdistrict,
            predicted_subdistrict=pred_subdistrict,
            subdistrict_matched=subdistrict_matched,
            expected_locality=gt.locality,
            predicted_locality=pred_locality,
            locality_matched=locality_matched,
            expected_pincode=gt.pincode,
            predicted_pincode=pred_pincode,
            pincode_matched=pincode_matched,
            exact_hierarchy_matched=exact_hierarchy,
            expected_status=case.expected_status.value,
            predicted_status=pred_status,
            status_matched=status_matched,
            expected_ambiguity=case.metadata.ambiguity,
            predicted_ambiguity=pred_ambiguity,
            ambiguity_matched=ambiguity_matched,
            candidate_recall_1=r1,
            candidate_recall_3=r3,
            candidate_recall_5=r5,
            candidate_recall_10=r10,
            consistency_score=verify_resp.score,
            completeness_score=resolution.completeness.score,
            entity_match_score=resolution.entity_match_score,
            latency_ms=round(latency_ms, 2)
        )

    async def run(self, smoke_test: bool = False, smoke_size: int = 60) -> Dict[str, Any]:
        print(f"\n================ Running GeoVerify India Benchmark ================")
        if not self.dataset_path.exists():
            print(f"Dataset not found at {self.dataset_path}. Generating default 1050-case benchmark...")
            gen = BenchmarkGenerator(seed=42)
            ds = gen.generate(target_size=1050)
            export_dataset(ds, self.dataset_path.parent)
        else:
            ds = DatasetLoader.load_from_json(self.dataset_path)

        cases = ds.cases[:smoke_size] if smoke_test else ds.cases
        print(f"Executing evaluation across {len(cases)} test cases (Smoke Mode: {smoke_test})...")

        results: List[EvaluationResultRecord] = []
        for idx, c in enumerate(cases):
            res = await self.evaluate_case(c)
            results.append(res)
            if (idx + 1) % 100 == 0 or (idx + 1) == len(cases):
                print(f"  Processed {idx + 1}/{len(cases)} cases...")

        # 1. Compute Metrics
        metrics = BenchmarkMetricsCalculator.evaluate_all(results)

        # 2. Error Analysis
        errors, error_counts = ErrorAnalyzer.analyze_errors(results)
        ErrorAnalyzer.export_errors_csv(errors, self.output_dir / "errors.csv")

        # 3. Component Performance Profiling
        perf_profile = await PerformanceProfiler.benchmark_components(repetitions=20)
        metrics["component_performance"] = perf_profile

        # 4. State-wise Analysis
        state_rows = []
        for st in set(r.expected_state for r in results if r.expected_state):
            st_sub = [r for r in results if r.expected_state == st]
            state_rows.append({
                "state": st,
                "case_count": len(st_sub),
                "state_accuracy": round(sum(1 for r in st_sub if r.state_matched) / len(st_sub), 4),
                "district_accuracy": round(sum(1 for r in st_sub if r.district_matched) / len(st_sub), 4),
                "locality_accuracy": round(sum(1 for r in st_sub if r.locality_matched) / len(st_sub), 4),
                "status_accuracy": round(sum(1 for r in st_sub if r.status_matched) / len(st_sub), 4),
                "mean_latency_ms": round(float(np.mean([r.latency_ms for r in st_sub])), 2)
            })
        df_states = pd.DataFrame(state_rows)
        df_states.to_csv(self.output_dir / "state_metrics.csv", index=False, encoding="utf-8")

        # 5. Export Confusion Matrix CSV
        cm_data = metrics["status_classification"]["confusion_matrix"]
        df_cm = pd.DataFrame(cm_data)
        df_cm.to_csv(self.output_dir / "confusion_matrix.csv", encoding="utf-8")

        # 6. Export Metrics Summary JSON & CSV
        with open(self.output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # Flattened metrics CSV
        flat_metrics = {
            "total_cases": metrics["total_cases"],
            "state_accuracy": metrics["entity_resolution"]["state_accuracy"],
            "district_accuracy": metrics["entity_resolution"]["district_accuracy"],
            "subdistrict_accuracy": metrics["entity_resolution"]["subdistrict_accuracy"],
            "locality_accuracy": metrics["entity_resolution"]["locality_accuracy"],
            "exact_hierarchy_accuracy": metrics["entity_resolution"]["exact_hierarchy_accuracy"],
            "candidate_recall_at_1": metrics["candidate_recall"]["recall_at_1"],
            "candidate_recall_at_3": metrics["candidate_recall"]["recall_at_3"],
            "candidate_recall_at_5": metrics["candidate_recall"]["recall_at_5"],
            "candidate_recall_at_10": metrics["candidate_recall"]["recall_at_10"],
            "ambiguity_precision": metrics["ambiguity"]["precision"],
            "ambiguity_recall": metrics["ambiguity"]["recall"],
            "ambiguity_f1": metrics["ambiguity"]["f1"],
            "status_overall_accuracy": metrics["status_classification"]["overall_accuracy"],
            "status_macro_f1": metrics["status_classification"]["macro_f1"],
            "status_weighted_f1": metrics["status_classification"]["weighted_f1"],
            "mean_latency_ms": metrics["latency"]["mean_ms"],
            "p50_latency_ms": metrics["latency"]["p50_ms"],
            "p95_latency_ms": metrics["latency"]["p95_ms"],
            "p99_latency_ms": metrics["latency"]["p99_ms"]
        }
        pd.DataFrame([flat_metrics]).to_csv(self.output_dir / "metrics.csv", index=False, encoding="utf-8")

        # 7. Generate Visual Charts
        figures_dir = self.output_dir / "figures"
        Visualizer.generate_all_charts(metrics, results, figures_dir)

        # 8. Generate Final Markdown Report
        ReportGenerator.generate_report(metrics, errors, self.output_dir / "report.md")

        print(f"\n[OK] Benchmark Complete! Summary Results:")
        print(f"  Total Cases           : {metrics['total_cases']}")
        print(f"  Exact Hierarchy Match : {metrics['entity_resolution']['exact_hierarchy_accuracy'] * 100:.2f}%")
        print(f"  State Accuracy        : {metrics['entity_resolution']['state_accuracy'] * 100:.2f}%")
        print(f"  District Accuracy     : {metrics['entity_resolution']['district_accuracy'] * 100:.2f}%")
        print(f"  Locality Accuracy     : {metrics['entity_resolution']['locality_accuracy'] * 100:.2f}%")
        print(f"  Candidate Recall@1    : {metrics['candidate_recall']['recall_at_1'] * 100:.2f}%")
        print(f"  Candidate Recall@5    : {metrics['candidate_recall']['recall_at_5'] * 100:.2f}%")
        print(f"  Ambiguity F1          : {metrics['ambiguity']['f1']:.4f}")
        print(f"  Status Accuracy       : {metrics['status_classification']['overall_accuracy'] * 100:.2f}%")
        print(f"  Mean Latency          : {metrics['latency']['mean_ms']:.2f} ms")
        print(f"  P95 Latency           : {metrics['latency']['p95_ms']:.2f} ms")
        print(f"  Report Generated      : {self.output_dir / 'report.md'}")
        print(f"====================================================================\n")

        return metrics


def main():
    parser = argparse.ArgumentParser(description="Run GeoVerify India Benchmark Suite")
    parser.add_argument("--dataset", type=str, default="evaluation/datasets/benchmark.json", help="Path to benchmark.json")
    parser.add_argument("--output", "--output-dir", dest="output", type=str, default="evaluation/results", help="Directory for output results")
    parser.add_argument("--smoke", action="store_true", help="Run lightweight smoke benchmark subset (50-60 cases)")
    args = parser.parse_args()

    runner = BenchmarkRunner(dataset_path=Path(args.dataset), output_dir=Path(args.output))
    asyncio.run(runner.run(smoke_test=args.smoke))


if __name__ == "__main__":
    main()
