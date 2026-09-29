"""Multi-Stage Candidate Generation Engine for Indian Geographic Entities.

Implements multi-channel independent candidate retrieval:
- Exact Retrieval (canonical normalized)
- Alias Retrieval (historical, common, abbreviation, colloquial)
- Transliteration Retrieval (Devanagari & multi-form)
- Phonetic Retrieval (Indian place-name phonetic matching)
- Fuzzy Retrieval (length-adaptive bounded edit distance)
- Administrative Context Retrieval (hierarchy-aware candidate generation)
- PIN-Constrained Retrieval (circle and postal district matching)
- Geographic Bounding Box Retrieval
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from rapidfuzz import fuzz

from app.entity_resolution.models import CandidateEntity, EntityType
from app.schemas.address import Coordinates
from app.services.transliteration import transliteration_service
from app.services.phonetic import phonetic_service

PROCESSED_DIR = Path(__file__).parent.parent.parent.parent / "data" / "processed"
ALIASES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "reference" / "aliases"


class MultiStageCandidateGenerator:
    """Multi-channel candidate generator for Indian geographic entities."""

    def __init__(self):
        self.states = self._load_json(PROCESSED_DIR / "states.json")
        self.districts = self._load_json(PROCESSED_DIR / "districts.json")
        self.subdistricts = self._load_json(PROCESSED_DIR / "subdistricts.json")
        self.localities = self._load_json(PROCESSED_DIR / "localities.json")
        self.pincodes = self._load_json(PROCESSED_DIR / "pincodes.json")
        self.pois = self._load_json(PROCESSED_DIR / "pois.json")
        
        # Load structured external reference aliases
        self.aliases = []
        if ALIASES_DIR.exists():
            for fpath in ALIASES_DIR.glob("*.json"):
                self.aliases.extend(self._load_json(fpath))

        # Build in-memory fast lookups
        self._build_indices()

    def _load_json(self, path: Path) -> List[Dict[str, Any]]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def _build_indices(self):
        """Builds multi-tier indices for fast exact, alias, and administrative retrieval."""
        self.alias_map: Dict[str, List[Dict[str, Any]]] = {}
        for a in self.aliases:
            key = self._canonical_key(a.get("alias", ""))
            if key:
                self.alias_map.setdefault(key, []).append(a)

        # District to localities index
        self.district_to_localities: Dict[str, List[Dict[str, Any]]] = {}
        # State to districts / localities index
        self.state_to_districts: Dict[str, List[Dict[str, Any]]] = {}
        self.state_to_localities: Dict[str, List[Dict[str, Any]]] = {}
        # PIN to localities index
        self.pin_to_localities: Dict[str, List[Dict[str, Any]]] = {}

        for loc in self.localities:
            st = self._canonical_key(loc.get("state", ""))
            dist = self._canonical_key(loc.get("district", ""))
            pin = loc.get("pincode")

            if st:
                self.state_to_localities.setdefault(st, []).append(loc)
            if dist:
                self.district_to_localities.setdefault(dist, []).append(loc)
            if pin:
                self.pin_to_localities.setdefault(pin, []).append(loc)

        for d in self.districts:
            st = self._canonical_key(d.get("state_name", ""))
            if st:
                self.state_to_districts.setdefault(st, []).append(d)

    @staticmethod
    def _canonical_key(text: str) -> str:
        """Canonical normalization: unicode NFC, lowercase, stripped punctuation, collapsed spaces."""
        if not text:
            return ""
        norm = unicodedata.normalize("NFKC", text).lower().strip()
        norm = re.sub(r"[^\w\s]", " ", norm)
        return re.sub(r"\s+", " ", norm).strip()

    def generate_candidates(
        self,
        token: str,
        expected_type: Optional[EntityType] = None,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_subdistrict: Optional[str] = None,
        context_pin: Optional[str] = None,
        context_coordinates: Optional[Coordinates] = None,
        limit: int = 10
    ) -> List[CandidateEntity]:
        """
        Executes multi-channel independent candidate generation.
        Merges, deduplicates, and ranks candidates across all channels.
        """
        if not token and not (context_state or context_district or context_pin):
            return []

        raw_query = token.strip() if token else ""
        norm_forms = transliteration_service.generate_normalized_forms(raw_query)
        clean_query = norm_forms["transliterated_form"]
        phonetic_query = norm_forms["phonetic_form"]

        channel_results: Dict[str, List[CandidateEntity]] = {
            "exact": [],
            "alias": [],
            "normalized": [],
            "transliteration": [],
            "phonetic": [],
            "fuzzy": [],
            "admin_context": [],
            "pin": [],
            "geographic": []
        }

        # Determine target entity categories to evaluate
        types_to_check = [expected_type] if expected_type else [
            EntityType.STATE,
            EntityType.DISTRICT,
            EntityType.SUBDISTRICT,
            EntityType.LOCALITY,
            EntityType.PINCODE,
            EntityType.POI
        ]

        # 1. Channel: Exact & Normalized Retrieval
        if clean_query:
            channel_results["exact"] = self._retrieve_exact(clean_query, raw_query, types_to_check)
            channel_results["normalized"] = self._retrieve_normalized(clean_query, types_to_check)

        # 2. Channel: Alias Retrieval
        if clean_query or raw_query:
            channel_results["alias"] = self._retrieve_aliases(clean_query, raw_query, types_to_check)

        # 3. Channel: Transliteration Retrieval
        if transliteration_service.detect_script(raw_query) in ["Devanagari", "Mixed"]:
            channel_results["transliteration"] = self._retrieve_transliteration(raw_query, clean_query, types_to_check)

        # 4. Channel: Phonetic Retrieval
        if clean_query:
            channel_results["phonetic"] = self._retrieve_phonetic(clean_query, phonetic_query, types_to_check)

        # 5. Channel: Length-Adaptive Fuzzy Retrieval
        if clean_query and len(clean_query) >= 3:
            channel_results["fuzzy"] = self._retrieve_fuzzy(clean_query, types_to_check)

        # 6. Channel: Administrative Context Retrieval
        if context_state or context_district or context_subdistrict:
            channel_results["admin_context"] = self._retrieve_admin_context(
                clean_query, context_state, context_district, context_subdistrict, types_to_check
            )

        # 7. Channel: PIN-Constrained Retrieval
        if context_pin or (clean_query and clean_query.isdigit() and len(clean_query) == 6):
            target_pin = context_pin or clean_query
            channel_results["pin"] = self._retrieve_pin_constrained(target_pin, clean_query, types_to_check)

        # 8. Channel: Geographic Bounding Box Retrieval
        if context_coordinates:
            channel_results["geographic"] = self._retrieve_geographic(context_coordinates, types_to_check)

        # Merge, deduplicate, and assign multi-channel scores
        merged_candidates = self._merge_and_rank_candidates(channel_results, limit=limit)

        return merged_candidates

    # ---------------- Channel Implementations ----------------

    def _retrieve_exact(self, clean_query: str, raw_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        q_key = self._canonical_key(clean_query)
        r_key = self._canonical_key(raw_query)

        if EntityType.STATE in types:
            for s in self.states:
                names = [self._canonical_key(s["name"]), self._canonical_key(s.get("canonical_name", ""))]
                if q_key in names or r_key in names:
                    cands.append(self._make_state_candidate(s, score=1.0, source="exact"))

        if any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.districts:
                names = [self._canonical_key(d["name"]), self._canonical_key(d.get("canonical_name", ""))]
                if q_key in names or r_key in names:
                    cands.append(self._make_district_candidate(d, score=1.0, source="exact"))

        if EntityType.SUBDISTRICT in types:
            for sd in self.subdistricts:
                names = [self._canonical_key(sd["name"]), self._canonical_key(sd.get("canonical_name", ""))]
                if q_key in names or r_key in names:
                    cands.append(self._make_subdistrict_candidate(sd, score=1.0, source="exact"))

        if any(t in types for t in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]):
            for loc in self.localities:
                names = [self._canonical_key(loc["name"]), self._canonical_key(loc.get("canonical_name", ""))]
                if q_key in names or r_key in names:
                    cands.append(self._make_locality_candidate(loc, score=1.0, source="exact"))

        if EntityType.PINCODE in types:
            for p in self.pincodes:
                if str(p["pincode"]) == clean_query:
                    cands.append(self._make_pincode_candidate(p, score=1.0, source="exact"))

        return cands

    def _retrieve_aliases(self, clean_query: str, raw_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        q_key = self._canonical_key(clean_query)
        r_key = self._canonical_key(raw_query)

        # Check structured alias map
        alias_entries = self.alias_map.get(q_key, []) + self.alias_map.get(r_key, [])
        for entry in alias_entries:
            canon = entry.get("canonical")
            confidence = entry.get("confidence", 0.95)
            # Find in catalog
            matched = self._retrieve_exact(canon, canon, types)
            for m in matched:
                m.similarity_score = max(m.similarity_score, confidence)
                m.match_source = "alias"
                cands.append(m)

        # Check in-catalog embedded aliases
        if any(t in types for t in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]):
            for loc in self.localities:
                aliases = [self._canonical_key(a) for a in loc.get("aliases", [])]
                if q_key in aliases or r_key in aliases:
                    cands.append(self._make_locality_candidate(loc, score=0.98, source="alias"))

        if any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.districts:
                aliases = [self._canonical_key(a) for a in d.get("aliases", [])]
                if q_key in aliases or r_key in aliases:
                    cands.append(self._make_district_candidate(d, score=0.98, source="alias"))

        if EntityType.STATE in types:
            for s in self.states:
                aliases = [self._canonical_key(a) for a in s.get("aliases", [])]
                if q_key in aliases or r_key in aliases:
                    cands.append(self._make_state_candidate(s, score=0.98, source="alias"))

        return cands

    def _retrieve_normalized(self, clean_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        # Strip common geographical stop suffixes (gaon, bypass, area, town, layout, sector, road, market)
        stripped = re.sub(r"\b(gaon|bypass|area|town|layout|sector|road|market|depot|phase \d+|extension|west|east|north|south)\b", "", clean_query).strip()
        stripped_key = self._canonical_key(stripped)
        if stripped_key and stripped_key != self._canonical_key(clean_query):
            cands.extend(self._retrieve_exact(stripped_key, stripped_key, types))
            for c in cands:
                c.similarity_score = min(c.similarity_score, 0.92)
                c.match_source = "normalized"
        return cands

    def _retrieve_transliteration(self, raw_query: str, clean_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        # Match Devanagari Hindi / Marathi attributes directly from catalogs
        if any(t in types for t in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]):
            for loc in self.localities:
                dev_names = [loc.get("name_hi", ""), loc.get("name_mr", "")]
                if any(raw_query in n or n in raw_query for n in dev_names if n):
                    cands.append(self._make_locality_candidate(loc, score=0.98, source="transliteration"))

        if any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.districts:
                dev_names = [d.get("name_hi", ""), d.get("name_mr", "")]
                if any(raw_query in n or n in raw_query for n in dev_names if n):
                    cands.append(self._make_district_candidate(d, score=0.98, source="transliteration"))

        if EntityType.STATE in types:
            for s in self.states:
                dev_names = [s.get("name_hi", ""), s.get("name_mr", "")]
                if any(raw_query in n or n in raw_query for n in dev_names if n):
                    cands.append(self._make_state_candidate(s, score=0.98, source="transliteration"))

        return cands

    def _retrieve_phonetic(self, clean_query: str, phonetic_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        if any(t in types for t in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]):
            for loc in self.localities:
                names = [loc["name"], loc.get("canonical_name", "")] + loc.get("aliases", [])
                for n in names:
                    sim = phonetic_service.compute_phonetic_similarity(clean_query, n)
                    if sim >= 0.85:
                        cands.append(self._make_locality_candidate(loc, score=sim, source="phonetic"))
                        break

        if any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.districts:
                names = [d["name"], d.get("canonical_name", "")] + d.get("aliases", [])
                for n in names:
                    sim = phonetic_service.compute_phonetic_similarity(clean_query, n)
                    if sim >= 0.85:
                        cands.append(self._make_district_candidate(d, score=sim, source="phonetic"))
                        break

        if EntityType.STATE in types:
            for s in self.states:
                names = [s["name"], s.get("canonical_name", "")] + s.get("aliases", [])
                for n in names:
                    sim = phonetic_service.compute_phonetic_similarity(clean_query, n)
                    if sim >= 0.85:
                        cands.append(self._make_state_candidate(s, score=sim, source="phonetic"))
                        break

        return cands

    def _retrieve_fuzzy(self, clean_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        # Length-adaptive fuzzy thresholds:
        # short words (<=5 chars): threshold 0.75
        # medium words (6-10 chars): threshold 0.65
        # long words (>10 chars): threshold 0.60
        q_len = len(clean_query)
        threshold = 0.75 if q_len <= 5 else (0.65 if q_len <= 10 else 0.60)

        if any(t in types for t in [EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN]):
            for loc in self.localities:
                names = [loc["name"].lower(), loc.get("canonical_name", "").lower()] + [a.lower() for a in loc.get("aliases", [])]
                best_sim = self._calc_fuzzy_ratio(clean_query, names)
                if best_sim >= threshold:
                    cands.append(self._make_locality_candidate(loc, score=best_sim, source="fuzzy"))

        if any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.districts:
                names = [d["name"].lower(), d.get("canonical_name", "").lower()] + [a.lower() for a in d.get("aliases", [])]
                best_sim = self._calc_fuzzy_ratio(clean_query, names)
                if best_sim >= threshold:
                    cands.append(self._make_district_candidate(d, score=best_sim, source="fuzzy"))

        if EntityType.STATE in types:
            for s in self.states:
                names = [s["name"].lower(), s.get("canonical_name", "").lower()] + [a.lower() for a in s.get("aliases", [])]
                best_sim = self._calc_fuzzy_ratio(clean_query, names)
                if best_sim >= threshold:
                    cands.append(self._make_state_candidate(s, score=best_sim, source="fuzzy"))

        return cands

    def _retrieve_admin_context(
        self,
        clean_query: str,
        context_state: Optional[str],
        context_district: Optional[str],
        context_subdistrict: Optional[str],
        types: List[EntityType]
    ) -> List[CandidateEntity]:
        cands = []
        st_key = self._canonical_key(context_state) if context_state else ""
        dist_key = self._canonical_key(context_district) if context_district else ""

        # Retrieve localities in known district/state
        candidate_pool = []
        if dist_key and dist_key in self.district_to_localities:
            candidate_pool = self.district_to_localities[dist_key]
        elif st_key and st_key in self.state_to_localities:
            candidate_pool = self.state_to_localities[st_key]

        for loc in candidate_pool:
            score = 0.85
            if clean_query:
                names = [loc["name"].lower(), loc.get("canonical_name", "").lower()] + [a.lower() for a in loc.get("aliases", [])]
                ratio = self._calc_fuzzy_ratio(clean_query, names)
                score = max(score, ratio)
            cands.append(self._make_locality_candidate(loc, score=score, source="admin_context"))

        # Retrieve districts in known state
        if st_key and st_key in self.state_to_districts and any(t in types for t in [EntityType.DISTRICT, EntityType.CITY]):
            for d in self.state_to_districts[st_key]:
                score = 0.85
                if clean_query:
                    names = [d["name"].lower(), d.get("canonical_name", "").lower()] + [a.lower() for a in d.get("aliases", [])]
                    ratio = self._calc_fuzzy_ratio(clean_query, names)
                    score = max(score, ratio)
                cands.append(self._make_district_candidate(d, score=score, source="admin_context"))

        return cands

    def _retrieve_pin_constrained(self, target_pin: str, clean_query: str, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        # Direct PIN match
        if target_pin in self.pin_to_localities:
            for loc in self.pin_to_localities[target_pin]:
                cands.append(self._make_locality_candidate(loc, score=0.95, source="pin_constrained"))

        # Postal circle prefix (first 2 digits)
        circle_prefix = target_pin[:2]
        for p in self.pincodes:
            if str(p["pincode"]).startswith(circle_prefix):
                cands.append(self._make_pincode_candidate(p, score=0.90, source="pin_circle"))

        return cands

    def _retrieve_geographic(self, coords: Coordinates, types: List[EntityType]) -> List[CandidateEntity]:
        cands = []
        lat, lon = coords.latitude, coords.longitude
        for loc in self.localities:
            bbox = loc.get("bbox")
            if bbox and len(bbox) == 4:
                min_lon, min_lat, max_lon, max_lat = bbox
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    cands.append(self._make_locality_candidate(loc, score=0.90, source="geographic_bbox"))
        return cands

    # ---------------- Deduplication & Multi-Channel Ranking ----------------

    def _merge_and_rank_candidates(
        self,
        channel_results: Dict[str, List[CandidateEntity]],
        limit: int
    ) -> List[CandidateEntity]:
        """
        Merges candidates from all channels, accumulates channel evidence, and re-ranks.
        """
        entity_map: Dict[str, CandidateEntity] = {}
        channel_hits: Dict[str, Set[str]] = {}

        for channel, cands in channel_results.items():
            for c in cands:
                key = f"{c.entity_type.value}_{c.name.lower()}_{c.district or ''}_{c.state or ''}"
                channel_hits.setdefault(key, set()).add(channel)

                if key not in entity_map:
                    entity_map[key] = c
                else:
                    # Keep highest similarity score and record additional match channels
                    existing = entity_map[key]
                    if c.similarity_score > existing.similarity_score:
                        existing.similarity_score = c.similarity_score
                        existing.match_source = c.match_source

        # Multi-channel consensus boost:
        # If candidate was retrieved by >= 2 independent channels, apply a multi-channel bonus
        merged_list = list(entity_map.values())
        for c in merged_list:
            key = f"{c.entity_type.value}_{c.name.lower()}_{c.district or ''}_{c.state or ''}"
            hits = channel_hits.get(key, set())
            if len(hits) >= 2 and c.similarity_score < 1.0:
                bonus = min(0.08, len(hits) * 0.03)
                c.similarity_score = min(1.0, round(c.similarity_score + bonus, 3))
                c.match_source = f"multi_channel({','.join(sorted(hits))})"

        # Sort descending by similarity score
        merged_list.sort(key=lambda x: x.similarity_score, reverse=True)
        return merged_list[:limit]

    # ---------------- Helper Constructors ----------------

    def _calc_fuzzy_ratio(self, query: str, candidate_names: List[str]) -> float:
        best = 0.0
        for name in candidate_names:
            if not name:
                continue
            r = fuzz.ratio(query, name) / 100.0
            pr = fuzz.partial_ratio(query, name) / 100.0
            tsr = fuzz.token_sort_ratio(query, name) / 100.0
            best = max(best, r, pr * 0.90, tsr * 0.95)
        return round(best, 3)

    def _make_state_candidate(self, s: Dict[str, Any], score: float, source: str) -> CandidateEntity:
        return CandidateEntity(
            id=f"state_{s['code'].lower()}",
            name=s.get("canonical_name", s["name"]),
            name_hi=s.get("name_hi"),
            name_mr=s.get("name_mr"),
            entity_type=EntityType.STATE,
            state=s.get("canonical_name", s["name"]),
            state_code=s["code"],
            bbox=s.get("bbox"),
            similarity_score=score,
            match_source=source
        )

    def _make_district_candidate(self, d: Dict[str, Any], score: float, source: str) -> CandidateEntity:
        d_id = d.get("id", f"dist_{d.get('canonical_name', d['name']).lower().replace(' ', '_')}")
        return CandidateEntity(
            id=d_id,
            name=d.get("canonical_name", d["name"]),
            name_hi=d.get("name_hi"),
            name_mr=d.get("name_mr"),
            entity_type=EntityType.DISTRICT,
            state=d.get("state_name"),
            state_code=d.get("state_code"),
            district=d.get("canonical_name", d["name"]),
            bbox=d.get("bbox"),
            similarity_score=score,
            match_source=source
        )

    def _make_subdistrict_candidate(self, sd: Dict[str, Any], score: float, source: str) -> CandidateEntity:
        sd_id = sd.get("id", f"subdist_{sd.get('canonical_name', sd['name']).lower().replace(' ', '_')}")
        return CandidateEntity(
            id=sd_id,
            name=sd.get("canonical_name", sd["name"]),
            name_hi=sd.get("name_hi"),
            name_mr=sd.get("name_mr"),
            entity_type=EntityType.SUBDISTRICT,
            state=sd.get("state_name"),
            district=sd.get("district_name"),
            subdistrict=sd.get("canonical_name", sd["name"]),
            bbox=sd.get("bbox"),
            similarity_score=score,
            match_source=source
        )

    def _make_locality_candidate(self, loc: Dict[str, Any], score: float, source: str) -> CandidateEntity:
        coords = None
        if loc.get("coordinates"):
            coords = Coordinates(latitude=loc["coordinates"]["latitude"], longitude=loc["coordinates"]["longitude"])
        loc_id = loc.get("id", f"loc_{loc.get('canonical_name', loc['name']).lower().replace(' ', '_')}")
        return CandidateEntity(
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
            match_source=source
        )

    def _make_pincode_candidate(self, p: Dict[str, Any], score: float, source: str) -> CandidateEntity:
        coords = None
        if p.get("centroid"):
            coords = Coordinates(latitude=p["centroid"]["latitude"], longitude=p["centroid"]["longitude"])
        pin_str = str(p["pincode"])
        return CandidateEntity(
            id=f"pin_{pin_str}",
            name=pin_str,
            entity_type=EntityType.PINCODE,
            state=p.get("state"),
            district=p.get("district"),
            pincode=pin_str,
            coordinates=coords,
            similarity_score=score,
            match_source=source
        )


candidate_generator = MultiStageCandidateGenerator()
CandidateGenerator = MultiStageCandidateGenerator
