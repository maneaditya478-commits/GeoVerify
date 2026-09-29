"""Configuration for Context-Aware Candidate Ranking, Penalties, and Confidence Bands (Phase 6)."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class RankingWeightsConfig(BaseModel):
    """Normalized component weights for multi-factor candidate scoring (Total = 1.0 / 100%)."""
    name_similarity: float = Field(0.25, description="Exact, normalized, alias, and fuzzy name similarity")
    admin_context: float = Field(0.25, description="Agreement with extracted parent state/district/taluka")
    parent_child_compatibility: float = Field(0.15, description="Hierarchical multi-tier jurisdictional alignment")
    pin_compatibility: float = Field(0.10, description="PIN code match, postal circle, and distance alignment")
    geographic_compatibility: float = Field(0.10, description="Spatial point-in-polygon and bbox containment")
    transliteration_phonetic: float = Field(0.05, description="Devanagari transliteration and Indic phonetic agreement")
    entity_type_compatibility: float = Field(0.05, description="Target entity level match (Locality vs District vs State)")
    retrieval_consensus: float = Field(0.03, description="Consensus across independent retrieval channels")
    data_quality: float = Field(0.02, description="Source authority, completeness, and geometry freshness")


class AdminPenaltiesConfig(BaseModel):
    """Explicit penalty deductions (in score points) for administrative contradictions."""
    state_conflict: float = Field(-40.0, description="Candidate state contradicts asserted/verified state")
    district_conflict: float = Field(-25.0, description="Candidate district contradicts asserted/verified district")
    subdistrict_conflict: float = Field(-15.0, description="Candidate subdistrict contradicts asserted taluka")
    locality_conflict: float = Field(-10.0, description="Candidate locality contradicts asserted locality")
    pin_circle_conflict: float = Field(-20.0, description="PIN postal circle contradicts candidate state")
    entity_type_mismatch: float = Field(-30.0, description="Major mismatch (e.g. District outranking Locality)")


class ConfidenceBandsConfig(BaseModel):
    """Deterministic thresholds for entity match confidence categorization."""
    high_threshold: float = Field(85.0, description="Score >= 85: HIGH confidence")
    medium_threshold: float = Field(65.0, description="Score 65-84.9: MEDIUM confidence")
    low_threshold: float = Field(40.0, description="Score 40-64.9: LOW confidence")
    ambiguity_delta_threshold: float = Field(12.0, description="Score delta <= 12 across jurisdictions: AMBIGUOUS")


class Phase6RankingConfig(BaseModel):
    """Central configuration for Phase 6 Context-Aware Candidate Ranking."""
    weights: RankingWeightsConfig = Field(default_factory=RankingWeightsConfig)
    penalties: AdminPenaltiesConfig = Field(default_factory=AdminPenaltiesConfig)
    confidence: ConfidenceBandsConfig = Field(default_factory=ConfidenceBandsConfig)


# Default global ranking configuration
default_ranking_config = Phase6RankingConfig()
