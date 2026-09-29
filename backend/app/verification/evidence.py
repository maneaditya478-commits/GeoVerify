"""Evidence extraction and explainability narrative generator for GeoVerify India."""

from typing import List, Tuple
from app.config import settings
from app.schemas.address import NormalizedAddress, ParsedAddress, GeocodingResult
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.schemas.verification import EvidenceItem, BoundaryVerificationResult, PinVerificationResult
from app.schemas.nearby import NearbyPlace


class EvidenceEngine:
    """Evaluates multi-signal data to generate structured evidence and explainable narratives."""

    @classmethod
    def generate_evidence(
        cls,
        normalized: NormalizedAddress,
        parsed: ParsedAddress,
        geocoding: GeocodingResult,
        hierarchy: AdministrativeHierarchyResult,
        boundary: BoundaryVerificationResult,
        pin: PinVerificationResult,
        nearby: List[NearbyPlace]
    ) -> Tuple[List[EvidenceItem], List[str], List[str]]:
        items: List[EvidenceItem] = []
        explanation: List[str] = []
        warnings: List[str] = []

        # 1. Administrative Hierarchy Evidence (Weight: 25)
        if hierarchy.state:
            if any(n.level == "state" and n.matched for n in hierarchy.hierarchy_chain):
                items.append(EvidenceItem(
                    code="STATE_VERIFIED",
                    category="hierarchy",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=10,
                    score_contribution=10.0,
                    title="State Authority Match",
                    description=f"State '{hierarchy.state}' is a recognized Indian administrative entity."
                ))
                explanation.append(f"✓ State '{hierarchy.state}' exists")
            else:
                items.append(EvidenceItem(
                    code="STATE_MISMATCH",
                    category="hierarchy",
                    passed=False,
                    status="FAILED",
                    severity="CONFLICT",
                    weight=10,
                    score_contribution=0.0,
                    title="State Authority Match",
                    description=f"State '{hierarchy.state}' could not be validated against official registry."
                ))
                explanation.append(f"✗ Unrecognized state '{hierarchy.state}'")
                warnings.append(f"State '{hierarchy.state}' not found in administrative records.")

        if hierarchy.district:
            dist_node = next((n for n in hierarchy.hierarchy_chain if n.level == "district"), None)
            if dist_node and dist_node.matched:
                items.append(EvidenceItem(
                    code="DISTRICT_HIERARCHY_VERIFIED",
                    category="hierarchy",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=15,
                    score_contribution=15.0,
                    title="District Administrative Hierarchy",
                    description=f"District '{hierarchy.district}' is verified under state '{hierarchy.state}'."
                ))
                explanation.append(f"✓ District '{hierarchy.district}' belongs to {hierarchy.state or 'declared state'}")
            else:
                items.append(EvidenceItem(
                    code="DISTRICT_HIERARCHY_MISMATCH",
                    category="hierarchy",
                    passed=False,
                    status="FAILED",
                    severity="CONFLICT",
                    weight=15,
                    score_contribution=0.0,
                    title="District Administrative Hierarchy",
                    description=dist_node.evidence if dist_node else f"District mismatch detected."
                ))
                explanation.append(f"✗ District mismatch: {dist_node.evidence if dist_node else 'Invalid district'}")
                warnings.append(dist_node.evidence if dist_node else f"District hierarchy mismatch detected.")

        # 2. Geometric Boundary Match Evidence (Weight: 25)
        if geocoding:
            if boundary.point_inside_state:
                items.append(EvidenceItem(
                    code="BOUNDARY_STATE_CONTAINMENT",
                    category="boundary",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=10,
                    score_contribution=10.0,
                    title="State Polygon Containment",
                    description=f"Point coordinates fall strictly inside {boundary.detected_state or hierarchy.state} boundary."
                ))
                explanation.append(f"✓ Coordinates fall within expected state boundary")
            else:
                items.append(EvidenceItem(
                    code="BOUNDARY_STATE_ESCAPE",
                    category="boundary",
                    passed=False,
                    status="FAILED",
                    severity="CONFLICT",
                    weight=10,
                    score_contribution=0.0,
                    title="State Polygon Containment",
                    description=f"Point coordinates do not fall inside expected state polygon (detected: {boundary.detected_state or 'None'})."
                ))
                explanation.append(f"✗ Point coordinates fall outside expected state boundary")
                warnings.append("Point-in-polygon check failed: coordinates are outside the declared state boundary.")

            if boundary.point_inside_district:
                items.append(EvidenceItem(
                    code="BOUNDARY_DISTRICT_CONTAINMENT",
                    category="boundary",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=15,
                    score_contribution=15.0,
                    title="District Polygon Containment",
                    description=f"Point coordinates fall strictly inside {boundary.detected_district or hierarchy.district} district polygon."
                ))
                explanation.append(f"✓ Coordinates fall within expected district ({boundary.detected_district or hierarchy.district})")
            else:
                items.append(EvidenceItem(
                    code="BOUNDARY_DISTRICT_ESCAPE",
                    category="boundary",
                    passed=False,
                    status="FAILED",
                    severity="CONFLICT",
                    weight=15,
                    score_contribution=0.0,
                    title="District Polygon Containment",
                    description=f"Coordinates do not match expected district boundary (detected: {boundary.detected_district or 'None'})."
                ))
                explanation.append(f"✗ Coordinates outside expected district boundary (detected: {boundary.detected_district or 'None'})")
                warnings.append(f"Coordinates fall inside district '{boundary.detected_district or 'unknown'}', which conflicts with asserted district.")
        else:
            items.append(EvidenceItem(
                code="NO_COORDINATES",
                category="boundary",
                passed=False,
                status="SKIPPED",
                severity="WARNING",
                weight=25,
                score_contribution=0.0,
                title="Geospatial Boundary Check",
                description="Unable to perform point-in-polygon verification because coordinates could not be resolved."
            ))
            explanation.append("✗ Coordinates could not be resolved for boundary verification")

        # 3. Locality Match Evidence (Weight: 20)
        loc_name = normalized.locality or parsed.locality
        if loc_name:
            loc_node = next((n for n in hierarchy.hierarchy_chain if n.level == "locality"), None)
            if loc_node and loc_node.matched:
                items.append(EvidenceItem(
                    code="LOCALITY_VERIFIED",
                    category="locality",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=20,
                    score_contribution=20.0,
                    title="Locality Consistency",
                    description=f"Locality '{loc_name}' is documented within target jurisdiction."
                ))
                explanation.append(f"✓ Locality '{loc_name}' identified and consistent")
            else:
                items.append(EvidenceItem(
                    code="LOCALITY_CONFLICT",
                    category="locality",
                    passed=False,
                    status="WARNING",
                    severity="CONFLICT",
                    weight=20,
                    score_contribution=5.0,
                    title="Locality Consistency",
                    description=f"Locality '{loc_name}' was found but mapped to conflicting district or boundary."
                ))
                explanation.append(f"✗ Locality conflict: {loc_node.evidence if loc_node else 'Locality mismatch'}")
                warnings.append(f"Locality '{loc_name}' does not geographically belong to the supplied district.")
        else:
            items.append(EvidenceItem(
                code="LOCALITY_MISSING",
                category="locality",
                passed=False,
                status="WARNING",
                severity="WARNING",
                weight=20,
                score_contribution=5.0,
                title="Locality Information",
                description="No specific locality / village identified in address."
            ))
            explanation.append("— No granular locality specified")

        # 4. PIN Code Consistency Evidence (Weight: 15)
        if pin.pincode:
            if pin.matched and pin.is_valid_format:
                items.append(EvidenceItem(
                    code="PINCODE_CONSISTENT",
                    category="pincode",
                    passed=True,
                    status="PASSED",
                    severity="INFO",
                    weight=15,
                    score_contribution=15.0,
                    title="PIN Code Consistency",
                    description=pin.evidence
                ))
                explanation.append(f"✓ PIN code '{pin.pincode}' is consistent with postal circle and region")
            elif pin.is_valid_format:
                items.append(EvidenceItem(
                    code="PINCODE_DISCREPANCY",
                    category="pincode",
                    passed=False,
                    status="WARNING",
                    severity="WARNING",
                    weight=15,
                    score_contribution=5.0,
                    title="PIN Code Discrepancy",
                    description=pin.evidence
                ))
                explanation.append(f"✗ PIN code '{pin.pincode}' conflicts with geographic location")
                warnings.append(f"PIN code '{pin.pincode}' postal region does not match the geographic coordinates or district.")
            else:
                items.append(EvidenceItem(
                    code="PINCODE_INVALID_FORMAT",
                    category="pincode",
                    passed=False,
                    status="FAILED",
                    severity="CONFLICT",
                    weight=15,
                    score_contribution=0.0,
                    title="PIN Code Format",
                    description=pin.evidence
                ))
                explanation.append(f"✗ PIN code '{pin.pincode}' is not a valid 6-digit format")
                warnings.append(f"Supplied PIN code '{pin.pincode}' is malformed.")
        else:
            items.append(EvidenceItem(
                code="PINCODE_NOT_PROVIDED",
                category="pincode",
                passed=False,
                status="SKIPPED",
                severity="WARNING",
                weight=15,
                score_contribution=5.0,
                title="PIN Code Check",
                description="No PIN code provided in input address."
            ))
            explanation.append("— PIN code omitted from input")

        # 5. Geocoding Quality Evidence (Weight: 10)
        if geocoding:
            geocoding_score = round(geocoding.confidence * 10.0, 1)
            items.append(EvidenceItem(
                code="GEOCODING_RESOLVED",
                category="geocoding",
                passed=True,
                status="PASSED",
                severity="INFO",
                weight=10,
                score_contribution=geocoding_score,
                title="Geocoding Quality",
                description=f"Coordinates obtained via {geocoding.source} with confidence {int(geocoding.confidence*100)}%."
            ))
            explanation.append(f"✓ Coordinates obtained ({geocoding.coordinates.latitude:.4f}, {geocoding.coordinates.longitude:.4f})")
        else:
            items.append(EvidenceItem(
                code="GEOCODING_UNRESOLVED",
                category="geocoding",
                passed=False,
                status="FAILED",
                severity="WARNING",
                weight=10,
                score_contribution=0.0,
                title="Geocoding Quality",
                description="Could not resolve geographic coordinates for the address."
            ))
            explanation.append("✗ Unable to geocode address to coordinates")
            warnings.append("Geocoding service could not establish latitude/longitude.")

        # 6. Nearby Entities Evidence (Weight: 5)
        if nearby and len(nearby) > 0:
            items.append(EvidenceItem(
                code="NEARBY_CONFIRMATION",
                category="nearby",
                passed=True,
                status="PASSED",
                severity="INFO",
                weight=5,
                score_contribution=5.0,
                title="Nearby Entity Context",
                description=f"Found {len(nearby)} nearby verified entities ({', '.join([p.name for p in nearby[:3]])})."
            ))
            explanation.append(f"✓ Found {len(nearby)} contextual geographic landmarks nearby")
        else:
            items.append(EvidenceItem(
                code="NEARBY_NONE",
                category="nearby",
                passed=False,
                status="WARNING",
                severity="INFO",
                weight=5,
                score_contribution=2.0,
                title="Nearby Entity Context",
                description="No nearby points of interest found within search radius."
            ))
            explanation.append("— No nearby landmarks detected in specified radius")

        return items, explanation, warnings
