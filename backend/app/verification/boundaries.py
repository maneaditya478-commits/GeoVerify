"""Geographic point-in-polygon boundary verification using Shapely."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from shapely.geometry import Point, Polygon, mapping
from app.schemas.address import Coordinates
from app.schemas.verification import BoundaryVerificationResult


class BoundaryVerificationService:
    """Performs geometric Point-in-Polygon validation against authoritative Indian boundary polygons."""

    def __init__(self):
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
        self.states_data = []
        self.districts_data = []
        self.subdistricts_data = []
        self.localities_data = []

        if (data_dir / "states.json").exists():
            with open(data_dir / "states.json", "r", encoding="utf-8") as f:
                self.states_data = json.load(f)

        if (data_dir / "districts.json").exists():
            with open(data_dir / "districts.json", "r", encoding="utf-8") as f:
                self.districts_data = json.load(f)

        if (data_dir / "subdistricts.json").exists():
            with open(data_dir / "subdistricts.json", "r", encoding="utf-8") as f:
                self.subdistricts_data = json.load(f)

        if (data_dir / "localities.json").exists():
            with open(data_dir / "localities.json", "r", encoding="utf-8") as f:
                self.localities_data = json.load(f)

    def verify_boundaries(
        self,
        coordinates: Optional[Coordinates],
        asserted_state: Optional[str] = None,
        asserted_district: Optional[str] = None,
        asserted_subdistrict: Optional[str] = None,
        asserted_locality: Optional[str] = None
    ) -> BoundaryVerificationResult:
        if not coordinates:
            return BoundaryVerificationResult(
                point_inside_state=False,
                point_inside_district=False,
                detected_state=None,
                detected_district=None,
                boundary_geojson=None
            )

        pt = Point(coordinates.longitude, coordinates.latitude)

        # 1. Point in State Polygon check
        detected_state = None
        point_inside_state = False
        state_geojson_feature = None

        for s in self.states_data:
            poly_coords = s.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if poly.contains(pt) or poly.touches(pt):
                    detected_state = s["canonical_name"]
                    point_inside_state = True
                    state_geojson_feature = {
                        "type": "Feature",
                        "properties": {"name": s["canonical_name"], "level": "state", "code": s["code"]},
                        "geometry": mapping(poly)
                    }
                    break

        if not detected_state:
            for s in self.states_data:
                bbox = s.get("bbox")
                if bbox and bbox[0] <= coordinates.longitude <= bbox[2] and bbox[1] <= coordinates.latitude <= bbox[3]:
                    detected_state = s["canonical_name"]
                    point_inside_state = True
                    break

        if asserted_state and detected_state:
            if asserted_state.lower() != detected_state.lower():
                point_inside_state = False

        # 2. Point in District Polygon check
        detected_district = None
        point_inside_district = False
        district_geojson_feature = None

        for d in self.districts_data:
            poly_coords = d.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if poly.contains(pt) or poly.touches(pt):
                    detected_district = d["canonical_name"]
                    point_inside_district = True
                    district_geojson_feature = {
                        "type": "Feature",
                        "properties": {"name": d["canonical_name"], "level": "district", "state": d.get("state_name")},
                        "geometry": mapping(poly)
                    }
                    break

        if not detected_district:
            for d in self.districts_data:
                bbox = d.get("bbox")
                if bbox and bbox[0] <= coordinates.longitude <= bbox[2] and bbox[1] <= coordinates.latitude <= bbox[3]:
                    detected_district = d["canonical_name"]
                    point_inside_district = True
                    break

        if asserted_district and detected_district:
            if asserted_district.lower() not in detected_district.lower() and detected_district.lower() not in asserted_district.lower():
                point_inside_district = False

        # 3. Point in Sub-District Polygon check
        detected_subdistrict = None
        point_inside_subdistrict = False
        subdist_geojson_feature = None

        for sd in self.subdistricts_data:
            poly_coords = sd.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if poly.contains(pt) or poly.touches(pt):
                    detected_subdistrict = sd["canonical_name"]
                    point_inside_subdistrict = True
                    subdist_geojson_feature = {
                        "type": "Feature",
                        "properties": {"name": sd["canonical_name"], "level": "subdistrict", "type": sd.get("admin_type", "Taluka")},
                        "geometry": mapping(poly)
                    }
                    break

        if not detected_subdistrict:
            for sd in self.subdistricts_data:
                bbox = sd.get("bbox")
                if bbox and bbox[0] <= coordinates.longitude <= bbox[2] and bbox[1] <= coordinates.latitude <= bbox[3]:
                    detected_subdistrict = sd["canonical_name"]
                    point_inside_subdistrict = True
                    break

        if asserted_subdistrict and detected_subdistrict:
            if asserted_subdistrict.lower() not in detected_subdistrict.lower() and detected_subdistrict.lower() not in asserted_subdistrict.lower():
                point_inside_subdistrict = False

        # 4. Point in Locality Polygon check
        detected_locality = None
        point_inside_locality = False
        locality_geojson_feature = None

        for loc in self.localities_data:
            poly_coords = loc.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if poly.contains(pt) or poly.touches(pt):
                    detected_locality = loc["name"]
                    point_inside_locality = True
                    locality_geojson_feature = {
                        "type": "Feature",
                        "properties": {"name": loc["name"], "level": "locality"},
                        "geometry": mapping(poly)
                    }
                    break

        if asserted_locality and detected_locality:
            if asserted_locality.lower() not in detected_locality.lower() and detected_locality.lower() not in asserted_locality.lower():
                point_inside_locality = False

        # Assemble GeoJSON FeatureCollection
        features = []
        if state_geojson_feature:
            features.append(state_geojson_feature)
        if district_geojson_feature:
            features.append(district_geojson_feature)
        if subdist_geojson_feature:
            features.append(subdist_geojson_feature)
        if locality_geojson_feature:
            features.append(locality_geojson_feature)

        geojson_collection = {
            "type": "FeatureCollection",
            "features": features
        } if features else None

        return BoundaryVerificationResult(
            point_inside_state=point_inside_state,
            point_inside_district=point_inside_district,
            point_inside_subdistrict=point_inside_subdistrict if detected_subdistrict else None,
            point_inside_locality=point_inside_locality if detected_locality else None,
            detected_state=detected_state,
            detected_district=detected_district,
            detected_subdistrict=detected_subdistrict,
            detected_locality=detected_locality,
            boundary_geojson=geojson_collection
        )


boundary_service = BoundaryVerificationService()
