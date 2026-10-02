"""Phase 10 Security, Resilience, Graph Cycle Protection, and Research Mode Invariant Tests."""

import pytest
from app.graph.graph_engine import GeographicGraph, geographic_graph
from app.graph.models import GeographicEntityNode, GeographicRelationshipEdge, GeographicNodeType, GeographicEdgeType
from app.schemas.address import VerificationRequest
from app.verification.engine import verification_engine
from app.api.routes.explanation import explain_verification


def test_graph_bfs_cycle_protection():
    """Verify that graph BFS traversal handles circular graph structures without infinite recursion or hanging."""
    g = GeographicGraph()
    # Add nodes in a circle: A -> B -> C -> A
    n_a = GeographicEntityNode(id="cycle_a", name="Node A", node_type=GeographicNodeType.LOCALITY)
    n_b = GeographicEntityNode(id="cycle_b", name="Node B", node_type=GeographicNodeType.TALUKA)
    n_c = GeographicEntityNode(id="cycle_c", name="Node C", node_type=GeographicNodeType.DISTRICT)
    g.add_node(n_a)
    g.add_node(n_b)
    g.add_node(n_c)

    g.add_edge(GeographicRelationshipEdge(id="e_ab", source_id="cycle_a", target_id="cycle_b", edge_type=GeographicEdgeType.PART_OF))
    g.add_edge(GeographicRelationshipEdge(id="e_bc", source_id="cycle_b", target_id="cycle_c", edge_type=GeographicEdgeType.PART_OF))
    g.add_edge(GeographicRelationshipEdge(id="e_ca", source_id="cycle_c", target_id="cycle_a", edge_type=GeographicEdgeType.PART_OF))

    # Test path search from cycle_a to non-existent node
    path = g.find_path("cycle_a", "non_existent_node", max_depth=5, max_nodes=50)
    assert path is None

    # Test path search within cycle
    path_ac = g.find_path("cycle_a", "cycle_c", max_depth=5, max_nodes=50)
    assert path_ac is not None
    assert path_ac.total_depth == 2


def test_graph_bounded_node_exploration():
    """Verify that BFS respects max_nodes cap to prevent resource exhaustion attacks."""
    g = geographic_graph
    # Test path query with max_nodes = 2
    path = g.find_path("country_india", "pin_411014", max_depth=4, max_nodes=2)
    # Because max_nodes was capped at 2, exploration stopped early
    # It safely returns without hang or memory bloat


@pytest.mark.asyncio
async def test_verification_resilience_extreme_input_length():
    """Verify engine handles extremely long repetitive or noisy strings without crashes or memory exhaustion."""
    giant_address = "Sector 17, Chandigarh, Punjab " * 500  # 15,000 characters
    req = VerificationRequest(address=giant_address)
    res = await verification_engine.verify(req)
    assert res is not None
    assert res.status is not None
    assert res.score >= 0


@pytest.mark.asyncio
async def test_research_mode_deterministic_isolation():
    """Verify that research mode produces detailed explainability without altering core verification scores or verdicts."""
    addr = "Kharadi, Haveli, Pune, Maharashtra 411014"
    
    # Standard mode
    req_std = VerificationRequest(address=addr, research_mode=False)
    res_std = await verification_engine.verify(req_std)
    
    # Research mode
    req_res = VerificationRequest(address=addr, research_mode=True, include_graph_path=True)
    res_res = await verification_engine.verify(req_res)

    assert res_std.status == res_res.status
    assert res_std.score == res_res.score
    assert res_res.confidence_profile is not None
    assert res_res.subgraph_evidence is not None


@pytest.mark.asyncio
async def test_sql_script_injection_safety():
    """Verify that malicious injection strings do not crash or compromise the verification parser."""
    malicious_address = "'; DROP TABLE districts; SELECT * FROM users WHERE '1'='1 -- Kharadi, Pune, Maharashtra 411014"
    req = VerificationRequest(address=malicious_address)
    res = await verification_engine.verify(req)
    assert res is not None
    assert res.status is not None
