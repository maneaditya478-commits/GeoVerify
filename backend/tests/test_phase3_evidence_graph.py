"""Phase 3 tests for Directed Evidence Graph, Relationships, and Severity Levels."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.evidence.graph import evidence_graph_builder
from app.evidence.nodes import NodeType, NodeStatus
from app.evidence.relationships import RelationshipType, EdgeSeverity
from app.evidence.serializer import evidence_serializer
from app.schemas.hierarchy import AdministrativeHierarchyResult, HierarchyNode
from app.schemas.verification import BoundaryVerificationResult, PinVerificationResult
from app.schemas.address import Coordinates, VerificationRequest
from app.schemas.nearby import NearbyPlace



def test_evidence_graph_builder_valid():
    """Verify directed evidence graph construction for consistent address."""
    hierarchy = AdministrativeHierarchyResult(
        country="India",
        state="Maharashtra",
        state_code="MH",
        district="Pune",
        subdistrict="Haveli",
        locality="Kharadi",
        is_consistent=True
    )
    boundary = BoundaryVerificationResult(
        point_inside_state=True,
        point_inside_district=True,
        point_inside_subdistrict=True,
        point_inside_locality=True
    )
    pin = PinVerificationResult(
        pincode="411014",
        is_valid_format=True,
        matched=True,
        matched_state="Maharashtra"
    )
    coords = Coordinates(latitude=18.5514, longitude=73.9405)
    nearby = [
        NearbyPlace(
            name="Pune International Airport",
            category="transit",
            distance_km=4.5,
            coordinates=Coordinates(latitude=18.5822, longitude=73.9197)
        )
    ]

    graph = evidence_graph_builder.build_graph(
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        coordinates=coords,
        nearby_places=nearby
    )

    assert len(graph.nodes) >= 6
    assert len(graph.edges) >= 5
    assert graph.conflicts_count == 0
    assert any(n.node_type == NodeType.STATE and n.label == "Maharashtra" for n in graph.nodes)
    assert any(n.node_type == NodeType.DISTRICT and n.label == "Pune" for n in graph.nodes)
    assert any(n.node_type == NodeType.SUBDISTRICT and n.label == "Haveli" for n in graph.nodes)
    assert any(e.relationship == RelationshipType.INSIDE_POLYGON and e.severity == EdgeSeverity.INFO for e in graph.edges)


def test_evidence_graph_conflict_edges():
    """Verify that district or boundary mismatches produce CONFLICT edge severity."""
    hierarchy = AdministrativeHierarchyResult(
        country="India",
        state="Maharashtra",
        district="Kolhapur",
        is_consistent=False,
        mismatch_details=["District 'Kolhapur' conflicts with resolved locality"]
    )
    boundary = BoundaryVerificationResult(
        point_inside_state=True,
        point_inside_district=False  # Outside Kolhapur
    )
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=False)
    coords = Coordinates(latitude=18.5514, longitude=73.9405)

    graph = evidence_graph_builder.build_graph(
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        coordinates=coords
    )

    assert graph.conflicts_count >= 1
    assert any(e.severity == EdgeSeverity.CONFLICT for e in graph.edges)


def test_evidence_serializer():
    """Verify evidence graph serializer formats for Cytoscape and JSON."""
    hierarchy = AdministrativeHierarchyResult(country="India", state="Maharashtra", district="Pune", is_consistent=True)
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)
    coords = Coordinates(latitude=18.5514, longitude=73.9405)

    graph = evidence_graph_builder.build_graph(hierarchy=hierarchy, boundary=boundary, pin=pin, coordinates=coords)
    cy_data = evidence_serializer.to_cytoscape(graph)
    assert "elements" in cy_data
    assert len(cy_data["elements"]) > 0


@pytest.mark.asyncio
async def test_api_evidence_graph_endpoint():
    """Test verification response contains evidence_graph and GET /api/evidence/{verification_id} retrieves it."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"address": "Kharadi, Pune, Maharashtra 411014"}
        verify_resp = await ac.post("/api/verify", json=payload)
        assert verify_resp.status_code == 200
        v_data = verify_resp.json()
        v_id = v_data["verification_id"]
        assert "evidence_graph" in v_data
        assert len(v_data["evidence_graph"]["nodes"]) > 0

        # Retrieve through dedicated evidence endpoint
        ev_resp = await ac.get(f"/api/evidence/{v_id}")
        assert ev_resp.status_code == 200
        ev_data = ev_resp.json()
        assert "nodes" in ev_data
        assert "relationships" in ev_data


def test_evidence_serializer_to_dict():
    """Verify to_dict serialization method produces compliant structure."""
    hierarchy = AdministrativeHierarchyResult(country="India", state="Maharashtra", district="Pune", is_consistent=True)
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)
    graph = evidence_graph_builder.build_graph(hierarchy=hierarchy, boundary=boundary, pin=pin)
    d = evidence_serializer.to_dict(graph)
    assert "nodes" in d
    assert "relationships" in d
    assert "summary" in d
    assert d["conflicts_count"] == 0


def test_evidence_graph_with_circle_mismatch():
    """Verify evidence graph handles PIN circle mismatch edge severity."""
    hierarchy = AdministrativeHierarchyResult(country="India", state="Maharashtra", district="Pune", is_consistent=True)
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(
        pincode="560066",
        is_valid_format=True,
        matched=False,
        matched_state="Karnataka",
        postal_circle="5 - Karnataka Circle"
    )
    graph = evidence_graph_builder.build_graph(hierarchy=hierarchy, boundary=boundary, pin=pin)
    assert any(e.relationship == RelationshipType.POSTAL_AREA_OF and not e.passed for e in graph.edges)
    assert any(n.node_type == NodeType.PINCODE and n.status == NodeStatus.WARNING for n in graph.nodes)

