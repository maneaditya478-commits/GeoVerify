"""Dataset loader and validation utilities for GeoVerify India benchmarks."""

import json
from pathlib import Path
from typing import Optional, List
from evaluation.schema import BenchmarkDataset, BenchmarkRecord


class DatasetLoader:
    """Loads and validates benchmark datasets from disk."""

    @staticmethod
    def load_from_json(path: Path) -> BenchmarkDataset:
        if not path.exists():
            raise FileNotFoundError(f"Benchmark file not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return BenchmarkDataset.model_validate(data)

    @staticmethod
    def get_default_dataset_path() -> Path:
        return Path(__file__).parent / "datasets" / "benchmark.json"

    @classmethod
    def load_default(cls) -> BenchmarkDataset:
        return cls.load_from_json(cls.get_default_dataset_path())
