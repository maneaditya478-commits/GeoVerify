"""Tests for Administrative Hierarchy Validator."""

import pytest
from app.verification.hierarchy import HierarchyValidator


def test_hierarchy_valid():
    validator = HierarchyValidator()
    res = validator.validate_hierarchy(
        state="Maharashtra",
        district="Pune",
        locality="Kharadi"
    )
    assert res.is_consistent is True
    assert len(res.mismatch_details) == 0
    assert len(res.hierarchy_chain) >= 4


def test_hierarchy_district_mismatch():
    validator = HierarchyValidator()
    # Kharadi is in Pune, but asserted under Kolhapur
    res = validator.validate_hierarchy(
        state="Maharashtra",
        district="Kolhapur",
        locality="Kharadi"
    )
    assert res.is_consistent is False
    assert len(res.mismatch_details) > 0
    assert any("Kolhapur" in m for m in res.mismatch_details)


def test_hierarchy_state_mismatch():
    validator = HierarchyValidator()
    # Pune district asserted under Karnataka
    res = validator.validate_hierarchy(
        state="Karnataka",
        district="Pune"
    )
    assert res.is_consistent is False
    assert any("Maharashtra" in m and "Karnataka" in m for m in res.mismatch_details)
