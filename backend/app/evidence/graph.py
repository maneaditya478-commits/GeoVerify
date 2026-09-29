"""Evidence Graph Builder constructing directed verification graphs."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.evidence.nodes import EvidenceNode, NodeType, NodeStatus
from app.evidence.relationships import EvidenceEdge, RelationshipType, EdgeSeverity
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.schemas.verification import BoundaryVerificationResult, PinVerificationResult, EvidenceItem
from app.schemas.address import Coordinates
from app.schemas.nearby import NearbyPlace


class EvidenceGraph(BaseModel):
    nodes: List[EvidenceNode] = Field(default_factory=list)
    edges: List[EvidenceEdge] = Field(default_factory=list)
    summary: str = ""
    conflicts_count: int = 0
    warnings_count: int = 0


class EvidenceGraphBuilder:
    """Constructs a directed evidence graph representing hierarchical, boundary, and contextual links."""

    @classmethod
    def build_graph(
        cls,
        hierarchy: AdministrativeHierarchyResult,
        boundary: BoundaryVerificationResult,
        pin: PinVerificationResult,
        coordinates: Optional[Coordinates] = None,
        nearby_places: Optional[List[NearbyPlace]] = None,
        evidence_items: Optional[List[EvidenceItem]] = None
    ) -> EvidenceGraph:
        nodes: List[EvidenceNode] = []
        edges: List[EvidenceEdge] = []
        node_map: Dict[str, EvidenceNode] = {}
        conflicts = 0
        warnings = 0

        # Helper to add node if not exists
        def add_node(n: EvidenceNode):
            if n.id not in node_map:
                node_map[n.id] = n
                nodes.append(n)

        # 1. Country Node
        country_id = "country_india"
        add_node(EvidenceNode(
            id=country_id,
            label=hierarchy.country or "India",
            node_type=NodeType.COUNTRY,
            level="Country",
            status=NodeStatus.VERIFIED
        ))

        # 2. State Node
        state_id = None
        if hierarchy.state:
            state_id = f"state_{hierarchy.state.lower().replace(' ', '_')}"
            state_status = NodeStatus.VERIFIED if hierarchy.state_code else NodeStatus.CONSISTENT
            add_node(EvidenceNode(
                id=state_id,
                label=hierarchy.state,
                node_type=NodeType.STATE,
                level="State",
                status=state_status,
                properties={"state_code": hierarchy.state_code}
            ))
            # Edge: State -> Country
            edges.append(EvidenceEdge(
                id=f"edge_{state_id}_{country_id}",
                source=state_id,
                target=country_id,
                relationship=RelationshipType.LOCATED_IN,
                label="part of",
                severity=EdgeSeverity.INFO,
                passed=True,
                evidence_text=f"State '{hierarchy.state}' is an administrative subdivision of India"
            ))

        # 3. District Node
        dist_id = None
        if hierarchy.district:
            dist_id = f"dist_{hierarchy.district.lower().replace(' ', '_')}"
            dist_status = NodeStatus.VERIFIED if hierarchy.is_consistent else NodeStatus.CONFLICT
            add_node(EvidenceNode(
                id=dist_id,
                label=hierarchy.district,
                node_type=NodeType.DISTRICT,
                level="District",
                status=dist_status
            ))
            if state_id:
                has_mismatch = any("District" in m for m in hierarchy.mismatch_details)
                sev = EdgeSeverity.CONFLICT if has_mismatch else EdgeSeverity.INFO
                if has_mismatch: conflicts += 1
                edges.append(EvidenceEdge(
                    id=f"edge_{dist_id}_{state_id}",
                    source=dist_id,
                    target=state_id,
                    relationship=RelationshipType.MISMATCH_WITH if has_mismatch else RelationshipType.LOCATED_IN,
                    label="mismatch with" if has_mismatch else "located in",
                    severity=sev,
                    passed=not has_mismatch,
                    evidence_text=f"District '{hierarchy.district}' evaluated under state '{hierarchy.state}'"
                ))

        # 4. Sub-District Node
        subdist_id = None
        if hierarchy.subdistrict:
            subdist_id = f"subdist_{hierarchy.subdistrict.lower().replace(' ', '_')}"
            add_node(EvidenceNode(
                id=subdist_id,
                label=hierarchy.subdistrict,
                node_type=NodeType.SUBDISTRICT,
                level="Sub-District / Taluka",
                status=NodeStatus.VERIFIED if boundary.point_inside_subdistrict is not False else NodeStatus.WARNING
            ))
            if dist_id:
                edges.append(EvidenceEdge(
                    id=f"edge_{subdist_id}_{dist_id}",
                    source=subdist_id,
                    target=dist_id,
                    relationship=RelationshipType.LOCATED_IN,
                    label="taluka of",
                    severity=EdgeSeverity.INFO,
                    passed=True,
                    evidence_text=f"Sub-district '{hierarchy.subdistrict}' situated in district '{hierarchy.district}'"
                ))

        # 5. Locality Node
        loc_id = None
        if hierarchy.locality:
            loc_id = f"loc_{hierarchy.locality.lower().replace(' ', '_')}"
            loc_status = NodeStatus.VERIFIED if hierarchy.is_consistent else NodeStatus.WARNING
            add_node(EvidenceNode(
                id=loc_id,
                label=hierarchy.locality,
                node_type=NodeType.LOCALITY,
                level="Locality",
                status=loc_status
            ))
            parent_id = subdist_id or dist_id
            if parent_id:
                edges.append(EvidenceEdge(
                    id=f"edge_{loc_id}_{parent_id}",
                    source=loc_id,
                    target=parent_id,
                    relationship=RelationshipType.LOCATED_IN,
                    label="located in",
                    severity=EdgeSeverity.INFO,
                    passed=True,
                    evidence_text=f"Locality '{hierarchy.locality}' within administrative division"
                ))

        # 6. PIN Node
        if pin and pin.pincode:
            pin_id = f"pin_{pin.pincode}"
            pin_status = NodeStatus.VERIFIED if pin.matched else (NodeStatus.CONFLICT if not pin.is_valid_format else NodeStatus.WARNING)
            if pin_status == NodeStatus.CONFLICT: conflicts += 1
            if pin_status == NodeStatus.WARNING: warnings += 1

            add_node(EvidenceNode(
                id=pin_id,
                label=f"PIN {pin.pincode}",
                node_type=NodeType.PINCODE,
                level="Postal Code",
                status=pin_status,
                properties={"distance_km": pin.distance_to_coordinates_km, "circle_state": pin.matched_state}
            ))

            target_loc = loc_id or dist_id
            if target_loc:
                edges.append(EvidenceEdge(
                    id=f"edge_{pin_id}_{target_loc}",
                    source=pin_id,
                    target=target_loc,
                    relationship=RelationshipType.POSTAL_AREA_OF,
                    label="serves area",
                    severity=EdgeSeverity.INFO if pin.matched else EdgeSeverity.WARNING,
                    passed=pin.matched,
                    evidence_text=pin.evidence
                ))

        # 7. Coordinates Node & Boundary Intersect Edges
        if coordinates:
            coord_id = "coords_point"
            add_node(EvidenceNode(
                id=coord_id,
                label=f"({coordinates.latitude:.4f}°, {coordinates.longitude:.4f}°)",
                node_type=NodeType.COORDINATES,
                level="Spatial Point",
                status=NodeStatus.VERIFIED if (boundary.point_inside_district and boundary.point_inside_state) else NodeStatus.CONFLICT,
                properties={"latitude": coordinates.latitude, "longitude": coordinates.longitude}
            ))

            if loc_id and boundary.point_inside_locality:
                edges.append(EvidenceEdge(
                    id=f"edge_{coord_id}_{loc_id}",
                    source=coord_id,
                    target=loc_id,
                    relationship=RelationshipType.INSIDE_POLYGON,
                    label="inside locality",
                    severity=EdgeSeverity.INFO,
                    passed=True,
                    evidence_text="Coordinates fall within verified locality boundary"
                ))

            if subdist_id and boundary.point_inside_subdistrict is not None:
                passed = boundary.point_inside_subdistrict is True
                sev = EdgeSeverity.INFO if passed else EdgeSeverity.CONFLICT
                if not passed: conflicts += 1
                edges.append(EvidenceEdge(
                    id=f"edge_{coord_id}_{subdist_id}",
                    source=coord_id,
                    target=subdist_id,
                    relationship=RelationshipType.INSIDE_POLYGON if passed else RelationshipType.MISMATCH_WITH,
                    label="inside subdistrict" if passed else "outside subdistrict",
                    severity=sev,
                    passed=passed,
                    evidence_text=f"Point coordinates {'verified inside' if passed else 'fall outside'} asserted subdistrict boundary"
                ))

            if dist_id:
                passed = boundary.point_inside_district
                sev = EdgeSeverity.INFO if passed else EdgeSeverity.CONFLICT
                if not passed: conflicts += 1
                edges.append(EvidenceEdge(
                    id=f"edge_{coord_id}_{dist_id}",
                    source=coord_id,
                    target=dist_id,
                    relationship=RelationshipType.INSIDE_POLYGON if passed else RelationshipType.MISMATCH_WITH,
                    label="inside district" if passed else "outside district",
                    severity=sev,
                    passed=passed,
                    evidence_text=f"Point coordinates {'verified inside' if passed else 'fall outside'} asserted district boundary"
                ))

            if state_id:
                passed = boundary.point_inside_state
                sev = EdgeSeverity.INFO if passed else EdgeSeverity.CONFLICT
                if not passed: conflicts += 1
                edges.append(EvidenceEdge(
                    id=f"edge_{coord_id}_{state_id}",
                    source=coord_id,
                    target=state_id,
                    relationship=RelationshipType.INSIDE_POLYGON if passed else RelationshipType.MISMATCH_WITH,
                    label="inside state" if passed else "outside state",
                    severity=sev,
                    passed=passed,
                    evidence_text=f"Point coordinates {'verified inside' if passed else 'fall outside'} asserted state boundary"
                ))

        # 8. Top Nearby Context POIs
        if nearby_places and loc_id:
            for i, poi in enumerate(nearby_places[:3]):
                poi_id = f"poi_{i}_{poi.name.lower().replace(' ', '_')[:15]}"
                add_node(EvidenceNode(
                    id=poi_id,
                    label=f"{poi.name} ({poi.distance_km}km)",
                    node_type=NodeType.POI,
                    level="Contextual POI",
                    status=NodeStatus.CONSISTENT,
                    properties={"category": poi.category, "distance_km": poi.distance_km}
                ))
                edges.append(EvidenceEdge(
                    id=f"edge_{poi_id}_{loc_id}",
                    source=poi_id,
                    target=loc_id,
                    relationship=RelationshipType.IN_VICINITY_OF,
                    label=f"{poi.distance_km}km from",
                    severity=EdgeSeverity.INFO,
                    passed=True,
                    evidence_text=f"{poi.name} ({poi.category}) located {poi.distance_km}km away"
                ))

        summary = f"Evidence graph with {len(nodes)} nodes, {len(edges)} verified relationships ({conflicts} conflicts, {warnings} warnings)."

        return EvidenceGraph(
            nodes=nodes,
            edges=edges,
            summary=summary,
            conflicts_count=conflicts,
            warnings_count=warnings
        )


evidence_graph_builder = EvidenceGraphBuilder()
