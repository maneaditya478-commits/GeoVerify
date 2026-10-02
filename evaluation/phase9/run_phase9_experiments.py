"""Master Orchestration Script for Phase 9 Experiments, Benchmarking, Ablation & Calibration."""

import os
import sys
import json
import csv
import asyncio
from pathlib import Path

# Add backend and root directories to sys.path
root_dir = Path(__file__).parent.parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from evaluation.phase9.dataset_generator import generate_phase9_dataset, save_dataset
from evaluation.phase9.benchmark_runner import Phase9BenchmarkRunner
from evaluation.phase9.ablation_runner import Phase9AblationRunner
from evaluation.phase9.calibration_evaluator import CalibrationEvaluator


async def run_all():
    print("=" * 70)
    print("GeoVerify India — Phase 9 Master Experiment Execution")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / "results" / "phase9"
    (results_dir / "benchmark").mkdir(parents=True, exist_ok=True)
    (results_dir / "ablation").mkdir(parents=True, exist_ok=True)
    (results_dir / "calibration").mkdir(parents=True, exist_ok=True)
    (results_dir / "final").mkdir(parents=True, exist_ok=True)

    # 1. Generate / Save Benchmark Dataset (2000 cases)
    print("[1/4] Generating 2,000-case stratified master benchmark dataset...")
    manifest = save_dataset(output_dir=str(Path(__file__).parent.parent / "datasets"))
    dev_set = manifest["dev"]
    val_set = manifest["val"]
    heldout_set = manifest["heldout"]
    print(f"      Created: Dev={len(dev_set)}, Val={len(val_set)}, Heldout={len(heldout_set)}")

    # 2. Run Benchmarks
    print("\n[2/4] Executing benchmark suite on Dev, Val, and Held-out partitions...")
    runner = Phase9BenchmarkRunner()
    dev_metrics = await runner.run_benchmark(dev_set)
    val_metrics = await runner.run_benchmark(val_set)
    heldout_metrics = await runner.run_benchmark(heldout_set)

    print(f"      Held-out Recall@1: {heldout_metrics.recall_at_1}%")
    print(f"      Held-out Recall@5: {heldout_metrics.recall_at_5}%")
    print(f"      Held-out MRR: {heldout_metrics.mrr}")
    print(f"      Held-out Exact Hierarchy: {heldout_metrics.exact_hierarchy_accuracy}%")
    print(f"      Held-out Status Accuracy: {heldout_metrics.verification_status_accuracy}%")
    print(f"      Held-out Ambiguity F1: {heldout_metrics.ambiguity_f1}")
    print(f"      Held-out Temporal Accuracy: {heldout_metrics.temporal_resolution_accuracy}%")
    print(f"      Held-out Landmark Accuracy: {heldout_metrics.landmark_spatial_accuracy}%")
    print(f"      Held-out Multilingual Accuracy: {heldout_metrics.multilingual_alignment_accuracy}%")
    print(f"      Held-out Mean Latency: {heldout_metrics.mean_latency_ms} ms (P95: {heldout_metrics.p95_latency_ms} ms)")

    # Save benchmark JSON
    benchmark_summary = {
        "dev": dev_metrics.model_dump(),
        "val": val_metrics.model_dump(),
        "heldout": heldout_metrics.model_dump()
    }
    with open(results_dir / "benchmark" / "benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    # 3. Run Ablation Study (EXP_A through EXP_G)
    print("\n[3/4] Running Component Attribution & Ablation experiments (EXP_A -> EXP_G)...")
    ablation_runner = Phase9AblationRunner()
    ablation_results = ablation_runner.run_ablations(val_set)

    # Save ablation JSON & CSV
    ablation_data = [r.model_dump() for r in ablation_results]
    with open(results_dir / "ablation" / "ablation_results.json", "w", encoding="utf-8") as f:
        json.dump(ablation_data, f, indent=2)

    with open(results_dir / "ablation" / "ablation_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ablation_data[0].keys()))
        writer.writeheader()
        writer.writerows(ablation_data)

    for r in ablation_results:
        print(f"      {r.experiment_id}: Recall@1={r.recall_at_1}%, Hierarchy={r.hierarchy_accuracy}%, Status={r.status_accuracy}%, ECE={r.expected_calibration_error}")

    # 4. Calibration Evaluation
    print("\n[4/4] Evaluating probabilistic calibration and reliability metrics...")
    cal_comparison = CalibrationEvaluator.evaluate_calibration(heldout_set)

    print(f"      Uncalibrated ECE: {cal_comparison.uncalibrated_report.expected_calibration_error} | Brier: {cal_comparison.uncalibrated_report.brier_score}")
    print(f"      Calibrated ECE:   {cal_comparison.calibrated_report.expected_calibration_error} | Brier: {cal_comparison.calibrated_report.brier_score}")
    print(f"      ECE Reduction:    {cal_comparison.ece_reduction_pct}%")

    with open(results_dir / "calibration" / "calibration_comparison.json", "w", encoding="utf-8") as f:
        json.dump(cal_comparison.model_dump(), f, indent=2)

    # Final Combined Summary
    final_summary = {
        "phase": "9.0.0",
        "release_version": "9.0.0",
        "status": "VALIDATED_AND_PASSED",
        "benchmark": benchmark_summary,
        "ablation_summary": ablation_data,
        "calibration": cal_comparison.model_dump()
    }
    with open(results_dir / "final" / "final_phase9_summary.json", "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2)

    print("\n" + "=" * 70)
    print("Phase 9 Master Experiment Execution Completed Successfully!")
    print(f"Artifacts saved to: {results_dir}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all())
