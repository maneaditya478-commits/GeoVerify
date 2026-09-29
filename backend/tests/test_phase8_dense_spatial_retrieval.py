"""Unit tests for Phase 8 Dense Geographic & Spatial Proximity Retrieval."""

import pytest
from app.entity_resolution.dense_retrieval import DenseGeographicRetriever
from app.entity_resolution.spatial_retrieval import SpatialProximityRetriever
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.models import EntityType
from app.schemas.address import Coordinates


class TestDenseGeographicRetriever:
    """Validates dense n-gram vectorization and candidate retrieval."""

    def setup_method(self):
        self.retriever = DenseGeographicRetriever()
        mock_states = [{"name": "Maharashtra", "canonical_name": "Maharashtra", "code": "MH"}]
        mock_districts = [{"name": "Pune", "canonical_name": "Pune", "state_name": "Maharashtra"}]
        mock_subdistricts = [{"name": "Haveli", "canonical_name": "Haveli", "district_name": "Pune", "state_name": "Maharashtra"}]
        mock_localities = [
            {"name": "Kothrud", "canonical_name": "Kothrud", "district": "Pune", "state": "Maharashtra", "pincode": "411038"},
            {"name": "Hinjawadi", "canonical_name": "Hinjawadi", "district": "Pune", "state": "Maharashtra", "pincode": "411057"},
        ]
        self.retriever.build_index(mock_states, mock_districts, mock_subdistricts, mock_localities)

    def test_dense_retrieval_exact_match(self):
        cands = self.retriever.retrieve(
            query="Kothrud Pune",
            types=[EntityType.LOCALITY],
            top_k=5,
            min_similarity=0.40,
        )
        assert len(cands) > 0
        assert cands[0].name == "Kothrud"
        assert cands[0].match_source == "dense_geographic"
        assert "dense_geographic" in cands[0].channels

    def test_dense_retrieval_typo_resilience(self):
        # "Kotrhud" (transposition typo)
        cands = self.retriever.retrieve(
            query="Kotrhud Pune",
            types=[EntityType.LOCALITY],
            top_k=5,
            min_similarity=0.25,
        )
        assert len(cands) > 0
        assert any(c.name == "Kothrud" for c in cands)


class TestSpatialProximityRetriever:
    """Validates Haversine distance and spatial coordinate retrieval."""

    def setup_method(self):
        self.retriever = SpatialProximityRetriever()
        mock_localities = [
            {
                "name": "Kothrud",
                "coordinates": {"latitude": 18.5074, "longitude": 73.8077},
                "district": "Pune",
                "state": "Maharashtra",
            },
            {
                "name": "Indiranagar",
                "coordinates": {"latitude": 12.9784, "longitude": 77.6408},
                "district": "Bengaluru",
                "state": "Karnataka",
            },
        ]
        mock_pincodes = [
            {
                "pincode": "411038",
                "centroid": {"latitude": 18.5074, "longitude": 73.8077},
                "state": "Maharashtra",
                "district": "Pune",
            }
        ]
        self.retriever.build_index(mock_localities, mock_pincodes)

    def test_haversine_distance(self):
        # Distance from Shivajinagar Pune (18.5314, 73.8446) to Kothrud (18.5074, 73.8077) ~ 4.7km
        dist = SpatialProximityRetriever.haversine_km(18.5314, 73.8446, 18.5074, 73.8077)
        assert 3.5 < dist < 6.0

    def test_retrieve_nearby_within_radius(self):
        center = Coordinates(latitude=18.5314, longitude=73.8446)
        cands = self.retriever.retrieve_nearby(
            center=center,
            types=[EntityType.LOCALITY, EntityType.PINCODE],
            radius_km=10.0,
            top_k=5,
        )
        assert len(cands) >= 1
        assert any(c.name == "Kothrud" for c in cands)
        assert all("spatial_proximity" in c.match_source for c in cands)


class TestCandidateGeneratorMultiChannelIntegration:
    """Validates that candidate generator produces dense and spatial candidates."""

    def test_generate_candidates_with_coordinates(self):
        coords = Coordinates(latitude=18.5074, longitude=73.8077)
        cands = candidate_generator.generate_candidates(
            token="Kothrud",
            context_state="Maharashtra",
            context_coordinates=coords,
            limit=5,
        )
        assert len(cands) > 0
        top_cand = cands[0]
        assert "kothrud" in top_cand.name.lower()
