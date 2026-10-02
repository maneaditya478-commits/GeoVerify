"""Phase 10 Benchmark Leakage & Shortcut Auditor.

Scans the codebase for test-specific constants, case-specific conditionals,
hardcoded benchmark IDs, or dataset-tailored lookup tables.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class LeakageAuditResult(BaseModel):
    benchmark_specific_rules_count: int = 0
    case_specific_conditionals_count: int = 0
    flagged_patterns: List[str] = Field(default_factory=list)
    audit_passed: bool = True
    summary: str = ""


class LeakageAuditor:
    """Scans python code in backend/app for suspicious shortcuts or leakage."""

    SUSPICIOUS_PATTERNS = [
        r"P10_IND_\d+",
        r"P9_\d+",
        r"if\s+address\s*==\s*['\"].+['\"]:\s*return",
        r"if\s+raw_address\s*==\s*['\"].+['\"]:\s*return",
        r"BENCHMARK_OVERRIDE",
    ]

    @classmethod
    def audit_codebase(cls, root_dir: str = "backend/app") -> LeakageAuditResult:
        app_path = Path(root_dir)
        flagged = []

        if app_path.exists():
            for py_file in app_path.rglob("*.py"):
                text = py_file.read_text(encoding="utf-8")
                for pat in cls.SUSPICIOUS_PATTERNS:
                    matches = re.findall(pat, text)
                    if matches:
                        flagged.append(f"File {py_file.name}: matches pattern '{pat}' -> {matches}")

        passed = len(flagged) == 0
        summary = (
            "Leakage audit PASSED: 0 benchmark-specific rules, 0 case-specific conditionals found in codebase."
            if passed else f"Leakage audit FAILED: {len(flagged)} suspicious patterns found."
        )

        return LeakageAuditResult(
            benchmark_specific_rules_count=len(flagged),
            case_specific_conditionals_count=len(flagged),
            flagged_patterns=flagged,
            audit_passed=passed,
            summary=summary
        )
