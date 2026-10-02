"""Temporal Geography Resolver for historical aliases, renamings, and date validity."""

import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from app.temporal.models import (
    HistoricalNameRecord,
    TemporalRelationshipType,
    TemporalEntityType,
    TemporalStatus,
    TemporalEvidence
)
from app.temporal.catalog import HISTORICAL_RECORDS


class TemporalResolver:
    """Resolves historical and transitional geographic names to canonical entities with date sensitivity."""

    def __init__(self, records: Optional[List[HistoricalNameRecord]] = None):
        self.records = records or HISTORICAL_RECORDS
        self._historical_index: Dict[str, List[HistoricalNameRecord]] = {}
        self._current_index: Dict[str, List[HistoricalNameRecord]] = {}
        self._build_indexes()

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text.strip().lower())

    def _build_indexes(self):
        for rec in self.records:
            # Index by historical name
            norm_hist = self._normalize(rec.historical_name)
            self._historical_index.setdefault(norm_hist, []).append(rec)

            # Index by current name
            norm_curr = self._normalize(rec.current_name)
            self._current_index.setdefault(norm_curr, []).append(rec)

            # Index by synonyms
            for syn in rec.synonyms:
                norm_syn = self._normalize(syn)
                self._historical_index.setdefault(norm_syn, []).append(rec)

    def _parse_year(self, date_str: Optional[str]) -> Optional[int]:
        if not date_str:
            return None
        match = re.search(r"\b(19\d\d|20\d\d)\b", str(date_str))
        if match:
            return int(match.group(1))
        return None

    def resolve_name(
        self,
        name: str,
        entity_type: Optional[TemporalEntityType] = None,
        reference_date: Optional[str] = None
    ) -> Optional[TemporalEvidence]:
        """Resolves an entity name (historical or current) given an optional reference date."""
        if not name or not name.strip():
            return None

        norm = self._normalize(name)
        ref_year = self._parse_year(reference_date)

        # 1. Check if name matches a historical record
        if norm in self._historical_index:
            for rec in self._historical_index[norm]:
                if entity_type and rec.entity_type != entity_type:
                    continue

                eff_year = rec.effective_year or (self._parse_year(rec.effective_date) if rec.effective_date else 2000)

                if ref_year is not None:
                    # Date is supplied: check whether the historical name was valid on that reference date
                    if ref_year <= eff_year:
                        status = TemporalStatus.VALID_FOR_DATE
                        explanation = (
                            f"Name '{rec.historical_name}' was the official/valid name in {ref_year} "
                            f"(before transition to '{rec.current_name}' in {eff_year})."
                        )
                        is_valid = True
                    else:
                        status = TemporalStatus.HISTORICAL
                        explanation = (
                            f"Name '{rec.historical_name}' is a historical name superseded by "
                            f"'{rec.current_name}' in {eff_year} (reference date: {ref_year})."
                        )
                        is_valid = False
                else:
                    # No reference date: historical alias in modern context
                    status = TemporalStatus.HISTORICAL
                    explanation = (
                        f"Name '{rec.historical_name}' is historically known as '{rec.current_name}' "
                        f"(renamed/transitioned in {eff_year})."
                    )
                    is_valid = True

                return TemporalEvidence(
                    status=status,
                    detected_name=name,
                    canonical_current_name=rec.current_name,
                    relationship=rec.relationship,
                    entity_type=rec.entity_type,
                    reference_date=reference_date,
                    effective_date=rec.effective_date,
                    is_valid_for_reference_date=is_valid,
                    authority_note=rec.authority_note,
                    explanation=explanation
                )

        # 2. Check if name is current, but reference_date is historical (e.g. "Mumbai" in 1970)
        if norm in self._current_index and ref_year is not None:
            for rec in self._current_index[norm]:
                if entity_type and rec.entity_type != entity_type:
                    continue

                eff_year = rec.effective_year or (self._parse_year(rec.effective_date) if rec.effective_date else 2000)
                if ref_year < eff_year:
                    status = TemporalStatus.OUTSIDE_DATE_RANGE
                    explanation = (
                        f"Name '{rec.current_name}' was adopted in {eff_year}. For reference date {ref_year}, "
                        f"the historical administrative name was '{rec.historical_name}'."
                    )
                    return TemporalEvidence(
                        status=status,
                        detected_name=name,
                        canonical_current_name=rec.current_name,
                        relationship=rec.relationship,
                        entity_type=rec.entity_type,
                        reference_date=reference_date,
                        effective_date=rec.effective_date,
                        is_valid_for_reference_date=False,
                        authority_note=rec.authority_note,
                        explanation=explanation
                    )
                else:
                    status = TemporalStatus.CURRENT
                    explanation = f"Name '{rec.current_name}' was the valid administrative name in {ref_year}."
                    return TemporalEvidence(
                        status=status,
                        detected_name=name,
                        canonical_current_name=rec.current_name,
                        relationship=rec.relationship,
                        entity_type=rec.entity_type,
                        reference_date=reference_date,
                        effective_date=rec.effective_date,
                        is_valid_for_reference_date=True,
                        authority_note=rec.authority_note,
                        explanation=explanation
                    )

        return None

    def get_canonical_name(self, name: str, reference_date: Optional[str] = None) -> str:
        """Returns the canonical modern name for any historical or current name."""
        ev = self.resolve_name(name, reference_date=reference_date)
        if ev:
            return ev.canonical_current_name
        return name

    def scan_text_for_temporal_entities(
        self,
        text: str,
        reference_date: Optional[str] = None
    ) -> List[TemporalEvidence]:
        """Scans a free-form address string for any historical geographic mentions."""
        if not text:
            return []

        results: List[TemporalEvidence] = []
        tokens = re.findall(r"\b[\w\'-]+\b", text)
        normalized_tokens = [self._normalize(t) for t in tokens]

        # Scan single tokens and bigrams
        seen_canonical = set()
        for i, token in enumerate(normalized_tokens):
            if token in self._historical_index:
                ev = self.resolve_name(tokens[i], reference_date=reference_date)
                if ev and ev.canonical_current_name not in seen_canonical:
                    results.append(ev)
                    seen_canonical.add(ev.canonical_current_name)

        # Bigrams (e.g. "Madras State", "Mysore State")
        for i in range(len(tokens) - 1):
            bigram = f"{normalized_tokens[i]} {normalized_tokens[i+1]}"
            if bigram in self._historical_index:
                raw_bigram = f"{tokens[i]} {tokens[i+1]}"
                ev = self.resolve_name(raw_bigram, reference_date=reference_date)
                if ev and ev.canonical_current_name not in seen_canonical:
                    results.append(ev)
                    seen_canonical.add(ev.canonical_current_name)

        return results


# Global singleton instance
temporal_resolver = TemporalResolver()
