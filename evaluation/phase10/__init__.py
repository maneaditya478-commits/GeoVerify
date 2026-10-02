"""Phase 10 Independent Generalization & Validation Package."""

from evaluation.phase10.independent_dataset_generator import (
    generate_independent_phase10_benchmark,
    save_frozen_independent_dataset,
)
from evaluation.phase10.independent_benchmark_runner import (
    Phase10IndependentRunner,
    DatasetIntegrityError,
    BenchmarkResult,
)
from evaluation.phase10.explanation_auditor import (
    ExplanationAuditor,
    ExplanationAuditReport,
)
from evaluation.phase10.leakage_auditor import (
    LeakageAuditor,
    LeakageAuditResult,
)
from evaluation.phase10.human_evaluator import (
    HumanEvaluator,
    HumanEvaluationReport,
)

__all__ = [
    "generate_independent_phase10_benchmark",
    "save_frozen_independent_dataset",
    "Phase10IndependentRunner",
    "DatasetIntegrityError",
    "BenchmarkResult",
    "ExplanationAuditor",
    "ExplanationAuditReport",
    "LeakageAuditor",
    "LeakageAuditResult",
    "HumanEvaluator",
    "HumanEvaluationReport",
]
