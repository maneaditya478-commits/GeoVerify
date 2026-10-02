"""Unit tests for Phase 9 Temporal Geography Engine."""

import pytest
from app.temporal.models import (
    TemporalRelationshipType,
    TemporalEntityType,
    TemporalStatus,
    TemporalEvidence,
)
from app.temporal.resolver import TemporalResolver, temporal_resolver
from app.temporal.catalog import get_all_temporal_records


def test_temporal_catalog_completeness():
    records = get_all_temporal_records()
    assert len(records) >= 25
    names = [r.historical_name.lower() for r in records]
    assert "bombay" in names
    assert "poona" in names
    assert "calcutta" in names
    assert "madras" in names
    assert "bangalore" in names
    assert "allahabad" in names


def test_resolve_historical_name_no_date():
    ev = temporal_resolver.resolve_name("Bombay")
    assert ev is not None
    assert ev.canonical_current_name == "Mumbai"
    assert ev.status == TemporalStatus.HISTORICAL
    assert ev.relationship == TemporalRelationshipType.RENAMED_TO
    assert ev.is_valid_for_reference_date is True


def test_resolve_historical_name_with_valid_historical_date():
    # Bombay was official in 1985 (renamed in 1995)
    ev = temporal_resolver.resolve_name("Bombay", reference_date="1985-05-15")
    assert ev is not None
    assert ev.canonical_current_name == "Mumbai"
    assert ev.status == TemporalStatus.VALID_FOR_DATE
    assert ev.is_valid_for_reference_date is True


def test_resolve_historical_name_with_post_transition_date():
    # Bombay used in 2020 (post 1995 renaming)
    ev = temporal_resolver.resolve_name("Bombay", reference_date="2020-01-01")
    assert ev is not None
    assert ev.canonical_current_name == "Mumbai"
    assert ev.status == TemporalStatus.HISTORICAL
    assert ev.is_valid_for_reference_date is False


def test_resolve_current_name_with_pre_transition_date():
    # Mumbai used for reference date 1970 (when it was officially Bombay)
    ev = temporal_resolver.resolve_name("Mumbai", reference_date="1970-01-01")
    assert ev is not None
    assert ev.canonical_current_name == "Mumbai"
    assert ev.status == TemporalStatus.OUTSIDE_DATE_RANGE
    assert ev.is_valid_for_reference_date is False


def test_resolve_bangalore_bengaluru():
    ev = temporal_resolver.resolve_name("Bangalore")
    assert ev is not None
    assert ev.canonical_current_name == "Bengaluru"


def test_scan_text_for_temporal_entities():
    text = "Flat 102, Nariman Point, Bombay 400021, Maharashtra"
    results = temporal_resolver.scan_text_for_temporal_entities(text)
    assert len(results) >= 1
    assert any(r.canonical_current_name == "Mumbai" for r in results)


def test_canonical_name_helper():
    assert temporal_resolver.get_canonical_name("Poona") == "Pune"
    assert temporal_resolver.get_canonical_name("Madras") == "Chennai"
    assert temporal_resolver.get_canonical_name("Calcutta") == "Kolkata"
    assert temporal_resolver.get_canonical_name("UnknownCityXYZ") == "UnknownCityXYZ"
