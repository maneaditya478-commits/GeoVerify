"""Landmark-Aware Spatial Matcher and Distance Bucketing Engine."""

import math
import re
from typing import Optional, List, Dict, Tuple
from app.landmarks.models import LandmarkEntity, LandmarkCategory, DistanceBucket, LandmarkEvidence
from app.landmarks.catalog import LANDMARK_CATALOG


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)


class LandmarkMatcher:
    """Identifies landmark references in text and assesses their spatial proximity and consistency."""

    def __init__(self, catalog: Optional[List[LandmarkEntity]] = None):
        self.catalog = catalog or LANDMARK_CATALOG
        self._index: Dict[str, LandmarkEntity] = {}
        self._build_index()

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text.strip().lower())

    def _build_index(self):
        for lm in self.catalog:
            # Primary name
            norm_name = self._normalize(lm.name)
            self._index[norm_name] = lm

            # Aliases
            for alias in lm.aliases:
                norm_alias = self._normalize(alias)
                self._index[norm_alias] = lm

    def match_landmark_mention(self, text: str) -> Optional[Tuple[LandmarkEntity, str]]:
        """Finds if a known landmark is mentioned in the given address or text snippet."""
        if not text:
            return None

        norm_text = self._normalize(text)

        # Check exact and substring matches, sorting by decreasing key length to match most specific landmark
        sorted_keys = sorted(self._index.keys(), key=len, reverse=True)
        for key in sorted_keys:
            # Word boundary search if length > 3
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, norm_text):
                return self._index[key], key

        return None

    def evaluate_spatial_proximity(
        self,
        landmark: LandmarkEntity,
        target_lat: Optional[float],
        target_lon: Optional[float],
        target_locality: Optional[str] = None,
        target_district: Optional[str] = None
    ) -> LandmarkEvidence:
        """Evaluates whether the landmark is consistent with the verified/candidate coordinates or locality."""
        if target_lat is not None and target_lon is not None:
            dist_km = haversine_distance_km(landmark.latitude, landmark.longitude, target_lat, target_lon)

            if dist_km <= 0.5:
                bucket = DistanceBucket.WITHIN_500M
                score = 1.0
                consistent = True
                explanation = f"Landmark '{landmark.name}' is within 500m ({dist_km * 1000:.0f}m) of target location."
            elif dist_km <= 1.0:
                bucket = DistanceBucket.FROM_500M_TO_1KM
                score = 0.95
                consistent = True
                explanation = f"Landmark '{landmark.name}' is within 1km ({dist_km:.2f}km) of target location."
            elif dist_km <= 5.0:
                bucket = DistanceBucket.FROM_1KM_TO_5KM
                score = 0.85
                consistent = True
                explanation = f"Landmark '{landmark.name}' is within 5km ({dist_km:.2f}km) of target location in {landmark.locality}."
            elif dist_km <= 15.0:
                bucket = DistanceBucket.FROM_5KM_TO_15KM
                score = 0.50
                consistent = True
                explanation = f"Landmark '{landmark.name}' is in the broader metropolitan area ({dist_km:.2f}km)."
            else:
                bucket = DistanceBucket.BEYOND_15KM
                score = 0.10
                consistent = False
                explanation = f"Spatial mismatch: Landmark '{landmark.name}' is {dist_km:.2f}km away from target coordinates."
        else:
            # Fallback to locality/district name consistency
            dist_km = None
            if target_locality and self._normalize(target_locality) == self._normalize(landmark.locality):
                bucket = DistanceBucket.WITHIN_500M
                score = 0.95
                consistent = True
                explanation = f"Landmark '{landmark.name}' resides in locality '{landmark.locality}'."
            elif target_district and self._normalize(target_district) == self._normalize(landmark.district):
                bucket = DistanceBucket.FROM_1KM_TO_5KM
                score = 0.80
                consistent = True
                explanation = f"Landmark '{landmark.name}' resides in district '{landmark.district}'."
            else:
                bucket = DistanceBucket.FROM_5KM_TO_15KM
                score = 0.50
                consistent = True
                explanation = f"Landmark '{landmark.name}' located in {landmark.locality}, {landmark.district}."

        return LandmarkEvidence(
            landmark_id=landmark.id,
            landmark_name=landmark.name,
            category=landmark.category,
            extracted_mention=landmark.name,
            target_locality=target_locality or landmark.locality,
            distance_km=dist_km,
            distance_bucket=bucket,
            spatial_consistency_score=score,
            is_consistent=consistent,
            explanation=explanation
        )

    def scan_and_evaluate(
        self,
        address_text: str,
        target_lat: Optional[float] = None,
        target_lon: Optional[float] = None,
        target_locality: Optional[str] = None,
        target_district: Optional[str] = None
    ) -> List[LandmarkEvidence]:
        """Convenience method to scan an address string and evaluate any detected landmarks."""
        results: List[LandmarkEvidence] = []
        match = self.match_landmark_mention(address_text)
        if match:
            lm, mention = match
            ev = self.evaluate_spatial_proximity(
                landmark=lm,
                target_lat=target_lat,
                target_lon=target_lon,
                target_locality=target_locality,
                target_district=target_district
            )
            results.append(ev)
        return results


# Global singleton instance
landmark_matcher = LandmarkMatcher()
