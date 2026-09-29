"""Tests for PIN Code Validator."""

import pytest
from app.services.pin_validator import PinValidator
from app.schemas.address import Coordinates


def test_pin_validator_valid():
    validator = PinValidator()
    res = validator.validate("411014", state="Maharashtra", district="Pune")
    assert res.is_valid_format is True
    assert res.matched is True
    assert res.matched_state == "Maharashtra"
    assert "Kharadi B.O" in res.matched_post_offices


def test_pin_validator_invalid_format():
    validator = PinValidator()
    res = validator.validate("ABC1234")
    assert res.is_valid_format is False
    assert res.matched is False


def test_pin_validator_circle_mismatch():
    validator = PinValidator()
    # 411014 belongs to MH, but user supplies Delhi
    res = validator.validate("411014", state="Delhi", district="New Delhi")
    assert res.is_valid_format is True
    assert res.matched is False
    assert "differs from PIN circle" in res.evidence


def test_pin_distance_check():
    validator = PinValidator()
    coords = Coordinates(latitude=18.5514, longitude=73.9405)
    res = validator.validate("411014", coordinates=coords)
    assert res.distance_to_coordinates_km is not None
    assert res.distance_to_coordinates_km < 10.0
