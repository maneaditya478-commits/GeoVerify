"""Core multi-signal verification engine for GeoVerify India."""

from datetime import datetime, timezone
import uuid
from typing import Optional, List
from app.schemas.address import (
    VerificationRequest,
    NormalizedAddress,
    ParsedAddress,
    GeocodingResult
)
from app.schemas.verification import (
    VerificationResponse,
    VerificationStatus,
    DataSourceAttribution,
    AddressScores,
    EvidenceGraphResponse
)
from app.services.normalizer import AddressNormalizer
from app.services.address_parser import AddressParser
from app.services.geocoder import geocoder_service
from app.services.pin_validator import pin_validator
from app.services.nearby import nearby_service
from app.verification.hierarchy import hierarchy_validator
from app.verification.boundaries import boundary_service
from app.verification.evidence import EvidenceEngine
from app.verification.scoring import ScoringEngine
from app.entity_resolution.resolver import address_entity_resolver
from app.evidence.graph import evidence_graph_builder
from app.evidence.serializer import evidence_serializer

# Known ambiguous locality names that occur in multiple states
AMBIGUOUS_NAMES = ["rampur", "bilaspur", "aurangabad", "fatehpur", "balrampur"]

STANDARD_DATA_SOURCES = [
    DataSourceAttribution(
        name="Local Government Directory (LGD)",
        source_url="https://lgdirectory.gov.in/",
        license="GODL-India",
        version="2026.1",
        coverage="36 States & UTs, 750+ Districts, Sub-Districts"
    ),
    DataSourceAttribution(
        name="Survey of India (SOI)",
        source_url="https://surveyofindia.gov.in/",
        license="GODL-India",
        version="2026.1",
        coverage="National Boundary Polygons"
    ),
    DataSourceAttribution(
        name="India Post (Department of Posts)",
        source_url="https://data.gov.in/resource/all-india-pincode-directory",
        license="GODL-India",
        version="2026.1",
        coverage="All-India PIN Code Postal Directory"
    ),
    DataSourceAttribution(
        name="OpenStreetMap / Verified Gazetteers",
        source_url="https://www.openstreetmap.org/",
        license="ODbL",
        version="2026",
        coverage="Points of Interest & Urban Localities"
    )
]


class VerificationEngine:
    """Coordinates multi-signal verification pipeline."""

    async def verify(self, request: VerificationRequest) -> VerificationResponse:
        verification_id = f"gv_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Parse or Extract Components
        raw_text = request.address or ""
        struct = request.structured

        if struct:
            locality_in = struct.locality or struct.address_line or request.locality
            subdistrict_in = struct.subdistrict or request.subdistrict
            city_in = struct.city
            district_in = struct.district or struct.city or request.district
            state_in = struct.state or request.state
            pincode_in = struct.pincode or request.pincode
            parsed = ParsedAddress(
                premise=struct.address_line,
                locality=locality_in,
                subdistrict=subdistrict_in,
                city=city_in,
                district=district_in,
                state=state_in,
                pincode=pincode_in,
                parse_confidence=0.9
            )
        else:
            parsed = AddressParser.parse(raw_text)
            locality_in = request.locality or parsed.locality
            subdistrict_in = request.subdistrict or parsed.subdistrict
            city_in = parsed.city
            district_in = request.district or parsed.district
            state_in = request.state or parsed.state
            pincode_in = request.pincode or parsed.pincode
            if request.locality: parsed.locality = request.locality
            if request.subdistrict: parsed.subdistrict = request.subdistrict
            if request.district: parsed.district = request.district
            if request.state: parsed.state = request.state
            if request.pincode: parsed.pincode = request.pincode

        # 2. Address Normalization
        normalized: NormalizedAddress = AddressNormalizer.normalize_address(
            address_text=raw_text,
            locality=locality_in,
            subdistrict=subdistrict_in,
            city=city_in,
            district=district_in,
            state=state_in,
            pincode=pincode_in
        )

        effective_locality = normalized.locality or parsed.locality
        effective_subdistrict = normalized.subdistrict or parsed.subdistrict
        effective_district = normalized.district or parsed.district
        effective_state = normalized.state or parsed.state
        effective_pin = normalized.pincode or parsed.pincode

        # 3. Geocoding
        geocoding_query = normalized.normalized_text or raw_text
        geocoding: Optional[GeocodingResult] = await geocoder_service.geocode(
            query=geocoding_query,
            locality=effective_locality,
            district=effective_district,
            state=effective_state,
            pincode=effective_pin
        )
        coords = geocoding.coordinates if geocoding else None

        # 4. Entity Resolution, Candidate Matching & Ambiguity
        resolution = address_entity_resolver.resolve_address(
            address_text=raw_text,
            parsed_override=parsed,
            context_coordinates=coords
        )

        is_ambiguous = resolution.ambiguity.is_ambiguous
        if effective_locality and effective_locality.lower() in AMBIGUOUS_NAMES:
            if not effective_state and not effective_district and not effective_pin:
                is_ambiguous = True

        # 5. Administrative Hierarchy Verification
        hierarchy_res = hierarchy_validator.validate_hierarchy(
            state=effective_state,
            district=effective_district,
            subdistrict=effective_subdistrict,
            locality=effective_locality
        )

        # 6. Geometric Boundary Verification (Point-in-Polygon)
        boundary_res = boundary_service.verify_boundaries(
            coordinates=coords,
            asserted_state=effective_state,
            asserted_district=effective_district,
            asserted_subdistrict=effective_subdistrict,
            asserted_locality=effective_locality
        )

        # 7. PIN Code Validation
        pin_res = pin_validator.validate(
            pincode=effective_pin,
            state=effective_state,
            district=effective_district,
            coordinates=coords
        )

        # 8. Nearby Intelligence
        nearby_places = []
        if coords:
            radius = request.radius_km or 5.0
            nearby_resp = nearby_service.find_nearby(center=coords, radius_km=radius)
            nearby_places = nearby_resp.places

        # 9. Evidence Generation & Explainability
        evidence_items, explanation, warnings = EvidenceEngine.generate_evidence(
            normalized=normalized,
            parsed=parsed,
            geocoding=geocoding,
            hierarchy=hierarchy_res,
            boundary=boundary_res,
            pin=pin_res,
            nearby=nearby_places
        )

        # 10. Scoring & Status Determination
        score, score_breakdown, status, summary = ScoringEngine.calculate_score(
            evidence_items=evidence_items,
            hierarchy=hierarchy_res,
            boundary=boundary_res,
            pin=pin_res,
            is_ambiguous=is_ambiguous,
            top_candidate=resolution.candidate_matches[0] if resolution.candidate_matches else None,
            ambiguity_details=resolution.ambiguity
        )

        # 11. Evidence Graph Construction
        graph_obj = evidence_graph_builder.build_graph(
            hierarchy=hierarchy_res,
            boundary=boundary_res,
            pin=pin_res,
            coordinates=coords,
            nearby_places=nearby_places,
            evidence_items=evidence_items
        )
        graph_resp = EvidenceGraphResponse(
            nodes=[n.model_dump() for n in graph_obj.nodes],
            relationships=[e.model_dump() for e in graph_obj.edges],
            summary=graph_obj.summary,
            conflicts_count=graph_obj.conflicts_count,
            warnings_count=graph_obj.warnings_count
        )

        # Multi-Scores
        multi_scores = AddressScores(
            geographic_consistency=score,
            address_completeness=resolution.completeness.score,
            entity_match=resolution.entity_match_score
        )

        # GeoJSON filtering if requested
        if not request.include_geojson:
            boundary_res.boundary_geojson = None

        return VerificationResponse(
            verification_id=verification_id,
            timestamp=timestamp,
            status=status,
            score=score,
            scores=multi_scores,
            summary=summary,
            explanation=explanation,
            warnings=warnings,
            evidence=evidence_items,
            normalized_address=normalized,
            parsed_address=parsed,
            geocoding=geocoding,
            administrative_hierarchy=hierarchy_res,
            boundary_verification=boundary_res,
            pin_verification=pin_res,
            score_breakdown=score_breakdown,
            nearby_places=nearby_places,
            candidate_matches=resolution.candidate_matches,
            ambiguity=resolution.ambiguity,
            completeness=resolution.completeness,
            evidence_graph=graph_resp,
            data_sources=STANDARD_DATA_SOURCES
        )


verification_engine = VerificationEngine()

