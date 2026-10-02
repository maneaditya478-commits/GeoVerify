"""Unit tests for Phase 9 Landmark-Aware Spatial Reasoning."""

import pytest
from app.landmarks.models import LandmarkCategory, DistanceBucket
from app.landmarks.catalog import get_all_landmarks
from app.landmarks.spatial_matcher import landmark_matcher, haversine_distance_km


def test_landmark_catalog():
    landmarks = get_all_landmarks()
    assert len(landmarks) >= 15
    names = [lm.name.lower() for lm in landmarks]
    assert any("shaniwar wada" in n for n in names)
    assert any("iit bombay" in n for n in names)
    assert any("india gate" in n for n in names)


def test_haversine_distance():
    # Distance between Pune Station (18.5284, 73.8744) and Shaniwar Wada (18.5196, 73.8553) ~ 2.2 km
    dist = haversine_distance_km(18.5284, 73.8744, 18.5196, 73.8553)
    assert 1.5 < dist < 3.0


def test_landmark_mention_matching():
    match = landmark_matcher.match_landmark_mention("Plot 5, Near Shaniwar Wada, Pune")
    assert match is not None
    lm, mention = match
    assert lm.district == "Pune"
    assert "Shaniwar Wada" in lm.name


def test_spatial_proximity_bucketing_close():
    match = landmark_matcher.match_landmark_mention("Near Shaniwar Wada")
    assert match is not None
    lm, _ = match
    # Target right next to Shaniwar Wada
    ev = landmark_matcher.evaluate_spatial_proximity(
        landmark=lm,
        target_lat=18.5197,
        target_lon=73.8554
    )
    assert ev.distance_bucket == DistanceBucket.WITHIN_500M
    assert ev.is_consistent is True
    assert ev.spatial_consistency_score >= 0.95


def test_spatial_proximity_bucketing_far_mismatch():
    match = landmark_matcher.match_landmark_mention("Near Shaniwar Wada")
    assert match is not None
    lm, _ = match
    # Target in Mumbai (19.0760, 72.8777)
    ev = landmark_matcher.evaluate_spatial_proximity(
        landmark=lm,
        target_lat=19.0760,
        target_lon=72.8777
    )
    assert ev.distance_bucket == DistanceBucket.BEYOND_15KM
    assert ev.is_consistent is False
    assert ev.spatial_consistency_score <= 0.20


def test_scan_and_evaluate():
    results = landmark_matcher.scan_and_evaluate("Flat 204, Opposite IIT Bombay, Powai, Mumbai 400076")
    assert len(results) >= 1
    assert any("IIT Bombay" in r.landmark_name for r in results)
