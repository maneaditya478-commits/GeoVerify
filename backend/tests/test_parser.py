"""Tests for Address Parser."""

import pytest
from app.services.address_parser import AddressParser


def test_parse_simple_address():
    addr = "Kharadi, Pune, Maharashtra 411014"
    parsed = AddressParser.parse(addr)
    assert parsed.locality == "Kharadi"
    assert parsed.district == "Pune"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "411014"
    assert parsed.parse_confidence == 1.0


def test_parse_complex_address():
    addr = "Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014"
    parsed = AddressParser.parse(addr)
    assert parsed.locality == "Kharadi"
    assert parsed.district == "Pune"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "411014"
    assert len(parsed.landmarks) > 0
    assert "Near EON IT Park" in parsed.landmarks[0]
    assert parsed.premise is not None


def test_parse_bangalore_address():
    addr = "Whitefield, Bengaluru, Karnataka 560066"
    parsed = AddressParser.parse(addr)
    assert parsed.locality == "Whitefield"
    assert parsed.state == "Karnataka"
    assert parsed.pincode == "560066"
    assert parsed.parse_confidence >= 0.75
