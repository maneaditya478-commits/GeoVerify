"""Ambiguity detection engine for Indian geographic address candidates (Phase 6).

Calibrated to distinguish cross-jurisdictional geographic homonyms from intra-district
sub-localities with deterministic score delta thresholds.
"""

from typing import List, Optional, Union
from app.entity_resolution.models import EntityMatchResult, AmbiguityDetails, CandidateEntity
from app.entity_resolution.ranking_config import default_ranking_config


class AmbiguityDetector:
    """Detects multi-match ambiguities when address tokens map to multiple distinct geographic locations."""

    def __init__(self, default_threshold: Optional[float] = None):
        self.default_threshold = (
            default_threshold
            if default_threshold is not None
            else default_ranking_config.confidence.ambiguity_delta_threshold
        )

    def detect_ambiguity(
        self,
        ranked_candidates: List[EntityMatchResult],
        threshold: Optional[float] = None,
        min_candidate_score: float = 40.0
    ) -> AmbiguityDetails:
        """
        Analyzes ranked candidate entities.
        If top candidates have close scores (delta <= threshold) and belong to distinct
        administrative jurisdictions (different state or different district), marks as AMBIGUOUS.
        """
        if not ranked_candidates or len(ranked_candidates) <= 1:
            return AmbiguityDetails(
                is_ambiguous=False,
                top_candidates=ranked_candidates[:1] if ranked_candidates else []
            )

        margin_threshold = threshold if threshold is not None else self.default_threshold
        
        # Filter candidates meeting minimum candidate score
        valid_candidates = [c for c in ranked_candidates if c.match_score >= min_candidate_score]
        if len(valid_candidates) <= 1:
            return AmbiguityDetails(
                is_ambiguous=False,
                top_candidates=ranked_candidates[:3],
                score_margin=round(ranked_candidates[0].match_score - ranked_candidates[1].match_score, 2) if len(ranked_candidates) > 1 else None,
                suggested_disambiguations=[]
            )

        top1 = valid_candidates[0]
        top2 = valid_candidates[1]

        # Score delta
        delta = round(top1.match_score - top2.match_score, 2)

        # Check if top1 and top2 represent distinct administrative jurisdictions
        state1 = (top1.candidate.state or "").strip().lower()
        state2 = (top2.candidate.state or "").strip().lower()
        dist1 = (top1.candidate.district or "").strip().lower()
        dist2 = (top2.candidate.district or "").strip().lower()

        is_different_jurisdiction = (
            top1.candidate.id != top2.candidate.id and
            (
                (bool(state1 and state2) and state1 != state2) or
                (bool(dist1 and dist2) and dist1 != dist2)
            )
        )

        if is_different_jurisdiction and delta <= margin_threshold:
            # Build structured disambiguation suggestions
            suggestions = []
            if state1 != state2:
                suggestions.append("State name (e.g., 'Maharashtra', 'Karnataka')")
            if dist1 != dist2:
                suggestions.append("District or City name")
            suggestions.append("6-digit PIN code")
            suggestions.append("Prominent nearby landmark")

            reason = (
                f"Query token matches multiple distinct locations with high confidence "
                f"('{top1.candidate.name}' in {top1.candidate.district or ''}, {top1.candidate.state or ''} "
                f"vs '{top2.candidate.name}' in {top2.candidate.district or ''}, {top2.candidate.state or ''})."
            )

            return AmbiguityDetails(
                is_ambiguous=True,
                ambiguity_reason=reason,
                top_candidates=ranked_candidates[:5],
                score_margin=delta,
                suggested_disambiguations=suggestions
            )

        return AmbiguityDetails(
            is_ambiguous=False,
            top_candidates=ranked_candidates[:3],
            score_margin=delta,
            suggested_disambiguations=[]
        )


ambiguity_detector = AmbiguityDetector()
