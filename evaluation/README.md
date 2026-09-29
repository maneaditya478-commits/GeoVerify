# GeoVerify India Evaluation & Benchmarking Module

This module provides the independent benchmarking, statistical evaluation, error categorization, and latency profiling framework for GeoVerify India.

## Sub-Modules

| Module | Description |
| :--- | :--- |
| `schema.py` | Pydantic models for ground truth, benchmark records, and evaluation metrics |
| `generate_dataset.py` | Deterministic benchmark dataset generator with controlled perturbations |
| `load_dataset.py` | Dataset loader and validation utilities |
| `metrics.py` | Multi-tier accuracy, Candidate Recall@K, Ambiguity F1, and multi-class confusion matrix |
| `error_analysis.py` | Diagnostic classifier categorizing verification failures into 12 root-cause buckets |
| `performance.py` | Micro-benchmarking component latencies (Mean, Median, P50, P90, P95, P99) |
| `visualization.py` | Generates 7 matplotlib diagnostic charts |
| `report.py` | Generates comprehensive Markdown, JSON, and CSV evaluation reports |
| `run_benchmark.py` | Automated asynchronous benchmark execution CLI |

## Usage Commands

```bash
# 1. Generate 1000+ benchmark dataset
python -m evaluation.generate_dataset --size 1050 --seed 42

# 2. Run full benchmark suite
python -m evaluation.run_benchmark

# 3. Run fast smoke test (60 cases)
python -m evaluation.run_benchmark --smoke

# 4. Profile component performance
python -m evaluation.performance

# 5. Run evaluation tests
pytest evaluation/tests -v
```
