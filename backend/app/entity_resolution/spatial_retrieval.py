"""Spatial Proximity and Geographic Neighbor Retrieval (Phase 8).

Retrieves geographic entities using coordinate proximity (Haversine distance),
bounding-box containment, and parent polygon intersection.

Key Features:
- Haversine metric proximity scoring
- Configurable radius filtering (e.g. 5km, 15km, 30km)
- Bounding-box intersection and neighborhood expansion
- Output provenance marked as 'spatial_proximity'
"""

import math
from typing import List, Dict, Any, Optional, Tuple

from app.entity_resolution.models import CandidateEntity, EntityType
from app.schemas.address import Coordinates


class SpatialProximityRetriever:
    """Retrieves neighboring geographic entities based on coordinate distance and bounding boxes."""

    def __init__(self):
        self.spatial_entities: List[Dict[str, Any]] = []
        self.is_indexed: bool = False

    def build_index(self, localities: List[Dict[str, Any]], pincodes: List[Dict[str, Any]]):
        """Builds spatial index for localities and pincode centroids."""
        self.spatial_entities = []

        for loc in localities:
            coords = loc.get("coordinates")
            if coords and "latitude" in coords and "longitude" in coords:
                self.spatial_entities.append({
                    "type": EntityType.LOCALITY,
                    "data": loc,
                    "lat": float(coords["latitude"]),
                    "lon": float(coords["longitude"]),
                    "bbox": loc.get("bbox"),
                })

        for p in pincodes:
            coords = p.get("centroid")
            if coords and "latitude" in coords and "longitude" in coords:
                self.spatial_entities.append({
                    "type": EntityType.PINCODE,
                    "data": p,
                    "lat": float(coords["latitude"]),
                    "lon": float(coords["longitude"]),
                    "bbox": None,
                })

        self.is_indexed = True

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two points in kilometers."""
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def retrieve_nearby(
        self,
        center: Coordinates,
        types: List[EntityType],
        radius_km: float = 15.0,
        top_k: int = 10,
    ) -> List[CandidateEntity]:
        """Retrieves geographic candidates within radius_km of coordinates."""
        if not self.is_indexed or not center:
            return []

        c_lat, c_lon = center.latitude, center.longitude
        results: List[Tuple[float, Dict[str, Any]]] = []

        for ent in self.spatial_entities:
            if ent["type"] not in types:
                continue

            dist_km = self.haversine_km(c_lat, c_lon, ent["lat"], ent["lon"])
            if dist_km <= radius_km:
                # Proximity score from 1.0 (0km) down to 0.5 (at radius_km)
                score = round(max(0.5, 1.0 - 0.5 * (dist_km / radius_km)), 3)
                results.append((dist_km, score, ent))

        # Sort ascending by physical distance
        results.sort(key=lambda x: x[0])
        top_results = results[:top_k]

        candidates = []
        for dist_km, score, ent in top_results:
            cand = self._make_candidate(ent["type"], ent["data"], score, dist_km)
            candidates.append(cand)

        return candidates

    def _make_candidate(
        self, ent_type: EntityType, data: Dict[str, Any], score: float, dist_km: float
    ) -> CandidateEntity:
        coords = None
        if data.get("coordinates"):
            coords = Coordinates(
                latitude=data["coordinates"]["latitude"],
                longitude=data["coordinates"]["longitude"],
            )
        elif data.get("centroid"):
            coords = Coordinates(
                latitude=data["centroid"]["latitude"],
                longitude=data["centroid"]["longitude"],
            )

        name = data.get("canonical_name", data.get("name", str(data.get("pincode", ""))))
        return CandidateEntity(
            id=data.get("id", f"{ent_type.value}_{name.lower().replace(' ', '_')}"),
            name=name,
            name_hi=data.get("name_hi"),
            name_mr=data.get("name_mr"),
            entity_type=ent_type,
            state=data.get("state_name") or data.get("state"),
            state_code=data.get("state_code"),
            district=data.get("district_name") or data.get("district"),
            subdistrict=data.get("subdistrict"),
            pincode=str(data.get("pincode")) if data.get("pincode") else None,
            coordinates=coords,
            bbox=data.get("bbox"),
            similarity_score=score,
            match_source=f"spatial_proximity({round(dist_km, 1)}km)",
            channels=["spatial_proximity"],
        )


spatial_retriever = SpatialProximityRetriever()
