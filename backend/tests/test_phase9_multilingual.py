"""Unit tests for Phase 9 Multilingual Alignment & Abbreviations."""

import pytest
from app.services.multilingual_alignment import (
    MultilingualAlignmentEngine,
    multilingual_alignment_engine,
)


def test_detect_scripts_pure_latin():
    primary, scripts, is_mixed = multilingual_alignment_engine.detect_scripts("Kothrud, Pune, Maharashtra 411038")
    assert primary == "Latin"
    assert is_mixed is False


def test_detect_scripts_pure_devanagari():
    primary, scripts, is_mixed = multilingual_alignment_engine.detect_scripts("कोथरूड, पुणे, महाराष्ट्र ४११०३८")
    assert primary == "Devanagari"
    assert is_mixed is False


def test_detect_scripts_mixed():
    primary, scripts, is_mixed = multilingual_alignment_engine.detect_scripts("Kothrud, पुणे, Maharashtra 411038")
    assert is_mixed is True
    assert "Latin" in scripts
    assert "Devanagari" in scripts


def test_expand_administrative_abbreviations_marathi():
    res = multilingual_alignment_engine.align_and_expand("मु.पो. कोथरूड, ता. हवेली, जि. पुणे")
    assert "District" in res.expanded_address or "Taluka" in res.expanded_address
    assert len(res.expanded_tokens) >= 2


def test_extract_hints():
    res = multilingual_alignment_engine.align_and_expand("Plot 12, ता. हवेली, जि. पुणे")
    assert res.extracted_district_hint == "पुणे"
    assert res.extracted_taluka_hint == "हवेली"


def test_expand_english_abbreviations():
    res = multilingual_alignment_engine.align_and_expand("Flat 10, Dt. Pune, Tal. Haveli")
    assert "District" in res.expanded_address
    assert "Taluka" in res.expanded_address
