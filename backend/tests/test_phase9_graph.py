"""Unit tests for Phase 9 Geographic Relationship Graph."""

import pytest
from app.graph.models import GeographicNodeType, GeographicEdgeType, EvidencePath
from app.graph.graph_engine import GeographicGraph, geographic_graph
from app.graph.path_explainer import GraphPathExplainer


def test_graph_initialization():
    assert len(geographic_graph.nodes) > 100
    assert len(geographic_graph.edges) > 100
    assert "country_india" in geographic_graph.nodes


def test_find_nodes_by_name():
    mumbai_nodes = geographic_graph.find_nodes_by_name("Maharashtra")
    assert len(mumbai_nodes) >= 1
    state_node = geographic_graph.nodes[mumbai_nodes[0]]
    assert state_node.node_type == GeographicNodeType.STATE


def test_graph_traversal_path_locality_to_state():
    # Find path between Kothrud/Pune locality and Maharashtra state
    loc_ids = geographic_graph.find_nodes_by_name("Kothrud", GeographicNodeType.LOCALITY)
    state_ids = geographic_graph.find_nodes_by_name("Maharashtra", GeographicNodeType.STATE)

    assert len(loc_ids) >= 1
    assert len(state_ids) >= 1

    path = geographic_graph.find_path(loc_ids[0], state_ids[0], max_depth=4)
    assert path is not None
    assert path.total_depth >= 1
    assert path.is_valid_hierarchical_path is True


def test_extract_evidence_subgraph():
    subgraph = geographic_graph.extract_evidence_subgraph(
        locality="Kothrud",
        district="Pune",
        state="Maharashtra",
        pincode="411038"
    )
    assert len(subgraph.nodes) >= 3
    assert subgraph.is_consistent is True
    assert len(subgraph.paths) >= 1


def test_extract_evidence_subgraph_inconsistent():
    # Inconsistent: Kothrud (Pune, MH) with Bangalore district
    subgraph = geographic_graph.extract_evidence_subgraph(
        locality="Kothrud",
        district="Bengaluru Urban",
        state="Karnataka"
    )
    assert subgraph.is_consistent is False


def test_graph_path_explainer():
    subgraph = geographic_graph.extract_evidence_subgraph(
        locality="Kothrud",
        district="Pune",
        state="Maharashtra"
    )
    narratives = GraphPathExplainer.generate_subgraph_explanation(subgraph)
    assert len(narratives) >= 2
    assert any("Maharashtra" in n for n in narratives)
