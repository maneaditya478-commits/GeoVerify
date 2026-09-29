"""Entity resolution module for GeoVerify India."""

from app.entity_resolution.models import (
    EntityType,
    CandidateEntity,
    EntityMatchBreakdown,
    EntityMatchResult,
    AmbiguityDetails,
    CompletenessCriteria,
    CompletenessBreakdown,
    CompletenessResult,
    ResolutionResult
)
from app.entity_resolution.candidates import candidate_generator, CandidateGenerator
from app.entity_resolution.matcher import entity_matcher, EntityMatcher
from app.entity_resolution.ambiguity import ambiguity_detector, AmbiguityDetector
from app.entity_resolution.resolver import address_entity_resolver, AddressEntityResolver

__all__ = [
    "EntityType",
    "CandidateEntity",
    "EntityMatchBreakdown",
    "EntityMatchResult",
    "AmbiguityDetails",
    "CompletenessCriteria",
    "CompletenessBreakdown",
    "CompletenessResult",
    "ResolutionResult",
    "candidate_generator",
    "CandidateGenerator",
    "entity_matcher",
    "EntityMatcher",
    "ambiguity_detector",
    "AmbiguityDetector",
    "address_entity_resolver",
    "AddressEntityResolver"
]
