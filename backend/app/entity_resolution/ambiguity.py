"""Ambiguity detection engine for Indian geographic address candidates."""

from typing import List, Optional
from app.entity_resolution.models import EntityMatchResult, AmbiguityDetails


class AmbiguityDetector:
    """Detects multi-match ambiguities when address tokens map to multiple distinct geographic locations."""

    DEFAULT_AMBIGUITY_THRESHOLD: float = 12.0  # Max score difference between top-1 and top-2 to trigger ambiguity

    @classmethod
    def detect_ambiguity(
        cls,
        ranked_candidates: List[EntityMatchResult],
        threshold: Optional[float] = None
    ) -> AmbiguityDetails:
        """
        Analyzes ranked candidate entities.
        If top candidates have close scores and belong to different administrative jurisdictions, marks as AMBIGUOUS.
        """
        if not ranked_candidates or len(ranked_candidates) <= 1:
            return AmbiguityDetails(
                is_ambiguous=False,
                top_candidates=ranked_candidates[:1] if ranked_candidates else []
            )

        margin_threshold = threshold if threshold is not None else cls.DEFAULT_AMBIGUITY_THRESHOLD
        top1 = ranked_candidates[0]
        top2 = ranked_candidates[1]

        # Score delta
        delta = round(top1.match_score - top2.match_score, 2)

        # Check if top1 and top2 are distinct entities (different state or different district)
        is_different_entity = (
            top1.candidate.id != top2.candidate.id and
            (
                (top1.candidate.state != top2.candidate.state and top1.candidate.state and top2.candidate.state) or
                (top1.candidate.district != top2.candidate.district and top1.candidate.district and top2.candidate.district)
            )
        )

        if is_different_entity and delta <= margin_threshold:
            # Build disambiguation suggestions
            suggestions = []
            if top1.candidate.state != top2.candidate.state:
                suggestions.append("State name (e.g., 'Maharashtra', 'Karnataka')")
            if top1.candidate.district != top2.candidate.district:
                suggestions.append("District or City name")
            suggestions.append("6-digit PIN code")
            suggestions.append("Prominent nearby landmark")

            reason = (
                f"Query token matches multiple distinct locations with high confidence "
                f"('{top1.candidate.name}' in {top1.candidate.district}, {top1.candidate.state} "
                f"vs '{top2.candidate.name}' in {top2.candidate.district}, {top2.candidate.state})."
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
