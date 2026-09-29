"""Nearby geographic intelligence service for Indian POIs and amenities."""

import json
from pathlib import Path
from typing import List, Optional
from app.schemas.address import Coordinates
from app.schemas.nearby import NearbyPlace, NearbyPlacesResponse
from app.services.pin_validator import haversine_distance


class NearbyIntelligenceService:
    """Finds nearby landmarks, hospitals, transit hubs, and government offices around a coordinate."""

    def __init__(self):
        self.pois: List[dict] = []
        data_file = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "pois.json"
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                self.pois = json.load(f)

    def find_nearby(
        self,
        center: Coordinates,
        radius_km: float = 5.0,
        category: Optional[str] = None,
        max_results: int = 20
    ) -> NearbyPlacesResponse:
        results: List[NearbyPlace] = []

        for p in self.pois:
            if category and p.get("category", "").lower() != category.lower():
                continue

            poi_coords = Coordinates(
                latitude=p["coordinates"]["latitude"],
                longitude=p["coordinates"]["longitude"]
            )
            dist = haversine_distance(center, poi_coords)
            if dist <= radius_km:
                results.append(NearbyPlace(
                    name=p["name"],
                    category=p["category"],
                    subtype=p.get("subtype"),
                    distance_km=dist,
                    coordinates=poi_coords,
                    address=p.get("address"),
                    district=p.get("district"),
                    state=p.get("state")
                ))

        # Sort by distance ascending
        results.sort(key=lambda x: x.distance_km)
        sliced = results[:max_results]

        return NearbyPlacesResponse(
            center=center,
            radius_km=radius_km,
            total_found=len(sliced),
            places=sliced
        )


nearby_service = NearbyIntelligenceService()
