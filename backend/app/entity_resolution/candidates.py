"""Candidate generation engine for Indian geographic address entities."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz
from app.entity_resolution.models import CandidateEntity, EntityType
from app.schemas.address import Coordinates
from app.services.transliteration import transliteration_service

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "processed"


class CandidateGenerator:
    """Generates candidate geographic entities from reference catalogs across administrative levels."""

    def __init__(self):
        self.states = self._load_data("states.json")
        self.districts = self._load_data("districts.json")
        self.subdistricts = self._load_data("subdistricts.json")
        self.localities = self._load_data("localities.json")
        self.pincodes = self._load_data("pincodes.json")
        self.pois = self._load_data("pois.json")

    def _load_data(self, filename: str) -> List[Dict[str, Any]]:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def generate_candidates(
        self,
        token: str,
        expected_type: Optional[EntityType] = None,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_pin: Optional[str] = None,
        limit: int = 10
    ) -> List[CandidateEntity]:
        """
        Generates ranked candidate geographic entities matching the given query token.
        Applies exact, alias, transliteration, and fuzzy matching.
        """
        if not token or not token.strip():
            return []

        raw_query = token.strip()
        transliterated_query, _ = transliteration_service.transliterate_to_latin(raw_query)
        clean_query = transliterated_query.lower()
        candidates: List[CandidateEntity] = []

        # 1. State Candidates
        if not expected_type or expected_type == EntityType.STATE:
            for s in self.states:
                names = [s["name"].lower(), s["canonical_name"].lower()]
                if s.get("name_hi"): names.append(s["name_hi"].lower())
                if s.get("name_mr"): names.append(s["name_mr"].lower())
                names.extend([a.lower() for a in s.get("aliases", [])])

                score = self._compute_similarity(clean_query, raw_query, names)
                if score >= 0.70:
                    candidates.append(CandidateEntity(
                        id=f"state_{s['code'].lower()}",
                        name=s["canonical_name"],
                        name_hi=s.get("name_hi"),
                        name_mr=s.get("name_mr"),
                        entity_type=EntityType.STATE,
                        state=s["canonical_name"],
                        state_code=s["code"],
                        bbox=s.get("bbox"),
                        similarity_score=score,
                        match_source="exact" if score == 1.0 else "fuzzy"
                    ))

        # 2. District Candidates
        if not expected_type or expected_type in [EntityType.DISTRICT, EntityType.CITY]:
            for d in self.districts:
                names = [d["name"].lower(), d["canonical_name"].lower()]
                if d.get("name_hi"): names.append(d["name_hi"].lower())
                if d.get("name_mr"): names.append(d["name_mr"].lower())
                names.extend([a.lower() for a in d.get("aliases", [])])

                score = self._compute_similarity(clean_query, raw_query, names)
                if score >= 0.70:
                    d_id = d.get("id", f"dist_{d.get('canonical_name', d['name']).lower().replace(' ', '_')}")
                    candidates.append(CandidateEntity(
                        id=d_id,
                        name=d["canonical_name"],
                        name_hi=d.get("name_hi"),
                        name_mr=d.get("name_mr"),
                        entity_type=EntityType.DISTRICT,
                        state=d.get("state_name"),
                        state_code=d.get("state_code"),
                        district=d["canonical_name"],
                        bbox=d.get("bbox"),
                        similarity_score=score,
                        match_source="exact" if score == 1.0 else "fuzzy"
                    ))

        # 3. Sub-District Candidates
        if not expected_type or expected_type == EntityType.SUBDISTRICT:
            for sd in self.subdistricts:
                names = [sd["name"].lower(), sd["canonical_name"].lower()]
                if sd.get("name_hi"): names.append(sd["name_hi"].lower())
                if sd.get("name_mr"): names.append(sd["name_mr"].lower())
                names.extend([a.lower() for a in sd.get("aliases", [])])

                score = self._compute_similarity(clean_query, raw_query, names)
                if score >= 0.70:
                    sd_id = sd.get("id", f"subdist_{sd.get('canonical_name', sd['name']).lower().replace(' ', '_')}")
                    candidates.append(CandidateEntity(
                        id=sd_id,
                        name=sd["canonical_name"],
                        name_hi=sd.get("name_hi"),
                        name_mr=sd.get("name_mr"),
                        entity_type=EntityType.SUBDISTRICT,
                        state=sd.get("state_name"),
                        district=sd.get("district_name"),
                        subdistrict=sd["canonical_name"],
                        bbox=sd.get("bbox"),
                        similarity_score=score,
                        match_source="exact" if score == 1.0 else "fuzzy"
                    ))

        # 4. Locality / Village Candidates
        if not expected_type or expected_type in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]:
            for loc in self.localities:
                names = [loc["name"].lower(), loc.get("canonical_name", "").lower()]
                if loc.get("name_hi"): names.append(loc["name_hi"].lower())
                if loc.get("name_mr"): names.append(loc["name_mr"].lower())
                names.extend([a.lower() for a in loc.get("aliases", [])])

                score = self._compute_similarity(clean_query, raw_query, names)
                if score >= 0.70:
                    coords = None
                    if loc.get("coordinates"):
                        coords = Coordinates(
                            latitude=loc["coordinates"]["latitude"],
                            longitude=loc["coordinates"]["longitude"]
                        )
                    loc_id = loc.get("id", f"loc_{loc.get('canonical_name', loc['name']).lower().replace(' ', '_')}")
                    candidates.append(CandidateEntity(
                        id=loc_id,
                        name=loc["name"],
                        name_hi=loc.get("name_hi"),
                        name_mr=loc.get("name_mr"),
                        entity_type=EntityType.LOCALITY,
                        state=loc.get("state"),
                        district=loc.get("district"),
                        subdistrict=loc.get("subdistrict"),
                        pincode=loc.get("pincode"),
                        coordinates=coords,
                        bbox=loc.get("bbox"),
                        similarity_score=score,
                        match_source="exact" if score == 1.0 else "fuzzy"
                    ))

        # 5. PIN Code Candidates
        if not expected_type or expected_type == EntityType.PINCODE:
            for p in self.pincodes:
                pin_str = str(p["pincode"])
                if clean_query in pin_str or clean_query == pin_str:
                    score = 1.0 if clean_query == pin_str else 0.85
                    coords = None
                    if p.get("centroid"):
                        coords = Coordinates(
                            latitude=p["centroid"]["latitude"],
                            longitude=p["centroid"]["longitude"]
                        )
                    candidates.append(CandidateEntity(
                        id=f"pin_{pin_str}",
                        name=pin_str,
                        entity_type=EntityType.PINCODE,
                        state=p.get("state"),
                        district=p.get("district"),
                        pincode=pin_str,
                        coordinates=coords,
                        similarity_score=score,
                        match_source="pincode_match"
                    ))

        # 6. POI / Landmark Candidates
        if not expected_type or expected_type in [EntityType.LANDMARK, EntityType.POI]:
            for poi in self.pois:
                names = [poi["name"].lower()]
                names.extend([a.lower() for a in poi.get("aliases", [])])
                score = self._compute_similarity(clean_query, raw_query, names)
                if score >= 0.70:
                    coords = None
                    if poi.get("coordinates"):
                        coords = Coordinates(
                            latitude=poi["coordinates"]["latitude"],
                            longitude=poi["coordinates"]["longitude"]
                        )
                    poi_id = poi.get("id", f"poi_{poi['name'].lower().replace(' ', '_')}")
                    candidates.append(CandidateEntity(
                        id=poi_id,
                        name=poi["name"],
                        entity_type=EntityType.POI,
                        state=poi.get("state"),
                        district=poi.get("district"),
                        coordinates=coords,
                        similarity_score=score,
                        match_source="poi_match"
                    ))

        # Sort by similarity score descending
        candidates.sort(key=lambda c: c.similarity_score, reverse=True)
        return candidates[:limit]

    def _compute_similarity(self, clean_query: str, raw_query: str, candidate_names: List[str]) -> float:
        """Calculates normalized highest similarity score across all name variations."""
        best_ratio = 0.0
        for name in candidate_names:
            if not name:
                continue
            # Exact equality
            if clean_query == name or raw_query == name:
                return 1.0
            # Substring exact
            if clean_query in name or name in clean_query:
                sub_ratio = len(clean_query) / max(len(name), 1)
                best_ratio = max(best_ratio, min(0.95, sub_ratio))
            # RapidFuzz partial and full ratio
            r_ratio = fuzz.ratio(clean_query, name) / 100.0
            p_ratio = fuzz.partial_ratio(clean_query, name) / 100.0
            best_ratio = max(best_ratio, r_ratio, p_ratio * 0.9)

        return round(best_ratio, 3)


candidate_generator = CandidateGenerator()
