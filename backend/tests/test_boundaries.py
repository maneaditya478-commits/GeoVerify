"""Tests for Geographic Boundary Point-in-Polygon Service."""

import pytest
from app.schemas.address import Coordinates
from app.verification.boundaries import BoundaryVerificationService


def test_boundary_containment_valid():
    service = BoundaryVerificationService()
    coords = Coordinates(latitude=18.5514, longitude=73.9405)  # Kharadi, Pune
    res = service.verify_boundaries(
        coordinates=coords,
        asserted_state="Maharashtra",
        asserted_district="Pune",
        asserted_locality="Kharadi"
    )
    assert res.point_inside_state is True
    assert res.point_inside_district is True
    assert res.detected_state == "Maharashtra"
    assert res.detected_district == "Pune"
    assert res.boundary_geojson is not None


def test_boundary_district_mismatch():
    service = BoundaryVerificationService()
    # Point is in Pune, but asserted district is Kolhapur
    coords = Coordinates(latitude=18.5514, longitude=73.9405)
    res = service.verify_boundaries(
        coordinates=coords,
        asserted_state="Maharashtra",
        asserted_district="Kolhapur"
    )
    assert res.point_inside_district is False
    assert res.detected_district == "Pune"
