"""Phase 3 benchmark suite executing cases from address_benchmark.json."""

import json
from pathlib import Path
import pytest
from app.schemas.address import VerificationRequest
from app.verification.engine import verification_engine

BENCHMARK_PATH = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "address_benchmark.json"


@pytest.mark.asyncio
async def test_run_address_benchmark_suite():
    """Runs all benchmark test cases and verifies expected verification statuses."""
    assert BENCHMARK_PATH.exists()
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    cases = bench_data.get("cases", [])
    assert len(cases) >= 15

    for tc in cases:
        case_id = tc["id"]
        addr_input = tc["input"]
        expected_status = tc["expected_status"]

        req = VerificationRequest(address=addr_input, include_geojson=True)
        res = await verification_engine.verify(req)

        # Status match verification
        assert res.status.value == expected_status, (
            f"Case {case_id} failed: input='{addr_input}', "
            f"expected={expected_status}, got={res.status.value} (Summary: {res.summary})"
        )

        # Multi-score sanity check
        assert res.scores is not None
        assert 0 <= res.scores.geographic_consistency <= 100
        assert 0 <= res.scores.address_completeness <= 100
        assert 0 <= res.scores.entity_match <= 100

        # Evidence graph sanity check
        assert res.evidence_graph is not None
        assert len(res.evidence_graph.nodes) > 0
