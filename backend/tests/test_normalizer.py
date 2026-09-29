"""Tests for Address Normalizer."""

import pytest
from app.services.normalizer import AddressNormalizer


def test_clean_text():
    raw = "  Flat  102,   Near EON IT Park,   Kharadi,, Pune, Rd.  "
    cleaned, transformations = AddressNormalizer.clean_text(raw)
    assert "  " not in cleaned
    assert ",," not in cleaned
    assert "Road" in cleaned
    assert len(transformations) > 0


def test_normalize_state_direct():
    state, code, trans = AddressNormalizer.normalize_state("Maharashtra")
    assert state == "Maharashtra"
    assert code == "MH"


def test_normalize_state_alias():
    state, code, trans = AddressNormalizer.normalize_state("MH")
    assert state == "Maharashtra"
    assert code == "MH"
    assert len(trans) > 0


def test_normalize_state_typo():
    state, code, trans = AddressNormalizer.normalize_state("Maharaashtra")
    assert state == "Maharashtra"
    assert code == "MH"
    assert any("Fuzzy" in t.rule_applied or "alias" in t.rule_applied for t in trans)


def test_normalize_district_aliases():
    dist, trans = AddressNormalizer.normalize_district("Poona")
    assert dist == "Pune"
    assert len(trans) > 0

    dist2, trans2 = AddressNormalizer.normalize_district("BLR")
    assert dist2 == "Bengaluru Urban"


def test_normalize_pincode():
    pin, trans = AddressNormalizer.normalize_pincode("411 014")
    assert pin == "411014"
    assert len(trans) > 0

    invalid_pin, _ = AddressNormalizer.normalize_pincode("012345")
    assert invalid_pin is None
