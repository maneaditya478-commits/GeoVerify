"""Unit tests for DatasetLoader and dataset export."""

import pytest
from pathlib import Path
from evaluation.load_dataset import DatasetLoader
from evaluation.generate_dataset import BenchmarkGenerator, export_dataset


def test_dataset_loader_load_default():
    """Verify loading default benchmark dataset."""
    ds = DatasetLoader.load_default()
    assert ds.total_cases >= 1000
    assert len(ds.cases) >= 1000
    assert ds.cases[0].id.startswith("GV-")


def test_dataset_loader_missing_file():
    """Verify loading non-existent dataset raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        DatasetLoader.load_from_json(Path("non_existent_path.json"))


def test_export_dataset_roundtrip(tmp_path: Path):
    """Verify dataset export to JSON and CSV and reloading."""
    gen = BenchmarkGenerator(seed=99)
    ds = gen.generate(target_size=25)
    export_dataset(ds, tmp_path)

    json_file = tmp_path / "benchmark.json"
    csv_file = tmp_path / "benchmark.csv"

    assert json_file.exists()
    assert csv_file.exists()

    loaded = DatasetLoader.load_from_json(json_file)
    assert loaded.total_cases == ds.total_cases
