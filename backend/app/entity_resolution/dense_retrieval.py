"""Dense & Subword Representation Retrieval for Geographic Entities (Phase 8).

Implements deterministic character n-gram and administrative hierarchy vector
representations for geographic candidate retrieval.

Key Capabilities:
- Character 3-gram and 4-gram vectorization
- Multi-field administrative vector composition (name + parent district + state)
- Subword cosine similarity ranking
- Zero external network dependencies, 100% deterministic and reproducible
"""

import math
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter

from app.entity_resolution.models import CandidateEntity, EntityType
from app.schemas.address import Coordinates


class DenseGeographicRetriever:
    """Deterministic dense n-gram vector retriever for Indian geographic entities."""

    def __init__(self):
        self.entity_vectors: List[Dict[str, Any]] = []
        self.is_indexed: bool = False

    def build_index(
        self,
        states: List[Dict[str, Any]],
        districts: List[Dict[str, Any]],
        subdistricts: List[Dict[str, Any]],
        localities: List[Dict[str, Any]],
    ):
        """Indexes geographic entities into dense character n-gram vectors."""
        self.entity_vectors = []

        # Index States
        for s in states:
            name = s.get("canonical_name", s.get("name", ""))
            raw_text = f"{name} {s.get('name_hi', '')} {s.get('name_mr', '')}"
            vec = self._vectorize(raw_text)
            norm = self._norm(vec)
            self.entity_vectors.append({
                "type": EntityType.STATE,
                "data": s,
                "vector": vec,
                "norm": norm,
                "name": name,
            })

        # Index Districts
        for d in districts:
            name = d.get("canonical_name", d.get("name", ""))
            st = d.get("state_name", "")
            raw_text = f"{name} {d.get('name_hi', '')} {d.get('name_mr', '')} {st}"
            vec = self._vectorize(raw_text)
            norm = self._norm(vec)
            self.entity_vectors.append({
                "type": EntityType.DISTRICT,
                "data": d,
                "vector": vec,
                "norm": norm,
                "name": name,
                "state": st,
            })

        # Index Sub-districts
        for sd in subdistricts:
            name = sd.get("canonical_name", sd.get("name", ""))
            dist = sd.get("district_name", "")
            st = sd.get("state_name", "")
            raw_text = f"{name} {sd.get('name_hi', '')} {dist} {st}"
            vec = self._vectorize(raw_text)
            norm = self._norm(vec)
            self.entity_vectors.append({
                "type": EntityType.SUBDISTRICT,
                "data": sd,
                "vector": vec,
                "norm": norm,
                "name": name,
                "district": dist,
                "state": st,
            })

        # Index Localities
        for loc in localities:
            name = loc.get("canonical_name", loc.get("name", ""))
            dist = loc.get("district", "")
            st = loc.get("state", "")
            pin = loc.get("pincode", "")
            raw_text = f"{name} {loc.get('name_hi', '')} {loc.get('name_mr', '')} {dist} {st} {pin}"
            vec = self._vectorize(raw_text)
            norm = self._norm(vec)
            name_vec = self._vectorize(name)
            name_norm = self._norm(name_vec)
            self.entity_vectors.append({
                "type": EntityType.LOCALITY,
                "data": loc,
                "vector": vec,
                "norm": norm,
                "name_vector": name_vec,
                "name_norm": name_norm,
                "name": name,
                "district": dist,
                "state": st,
                "pincode": pin,
            })

        self.is_indexed = True

    def _vectorize(self, text: str) -> Dict[str, float]:
        """Extracts 1-gram, 2-gram, 3-gram, and 4-gram frequency representation."""
        clean = re.sub(r"[^\w\s]", "", text.lower())
        tokens = clean.split()
        ngrams: Counter = Counter()

        for tok in tokens:
            for c in tok:
                ngrams[c] += 0.4
            # 2-grams
            for i in range(len(tok) - 1):
                ngrams[tok[i : i + 2]] += 0.8
            # 3-grams
            for i in range(len(tok) - 2):
                ngrams[tok[i : i + 3]] += 1.0
            # 4-grams
            for i in range(len(tok) - 3):
                ngrams[tok[i : i + 4]] += 1.2

        return dict(ngrams)

    def _norm(self, vec: Dict[str, float]) -> float:
        return math.sqrt(sum(v * v for v in vec.values()))

    def _cosine_similarity(
        self,
        query_vec: Dict[str, float],
        query_norm: float,
        target_vec: Dict[str, float],
        target_norm: float,
    ) -> float:
        if query_norm == 0.0 or target_norm == 0.0:
            return 0.0
        # Dot product over intersection of n-grams
        common_keys = query_vec.keys() & target_vec.keys()
        dot = sum(query_vec[k] * target_vec[k] for k in common_keys)
        return dot / (query_norm * target_norm)

    def retrieve(
        self,
        query: str,
        types: List[EntityType],
        top_k: int = 10,
        min_similarity: float = 0.25,
    ) -> List[CandidateEntity]:
        """Retrieves top-k candidates using dense n-gram cosine similarity."""
        if not self.is_indexed or not query:
            return []

        query_vec = self._vectorize(query)
        query_norm = self._norm(query_vec)
        if query_norm == 0.0:
            return []

        # Also extract token-level query vectors for multi-token resilience
        query_tokens = [t.strip() for t in query.split() if len(t.strip()) >= 2]
        token_vecs = [(self._vectorize(t), self._norm(self._vectorize(t))) for t in query_tokens]

        scored: List[Tuple[float, Dict[str, Any]]] = []

        for item in self.entity_vectors:
            if item["type"] not in types:
                continue

            sim_full = self._cosine_similarity(query_vec, query_norm, item["vector"], item["norm"])
            sim_name = 0.0
            if "name_vector" in item and item["name_norm"] > 0.0:
                sim_name = self._cosine_similarity(query_vec, query_norm, item["name_vector"], item["name_norm"])
                # Also check each query token against entity name
                for t_vec, t_norm in token_vecs:
                    if t_norm > 0.0:
                        t_sim = self._cosine_similarity(t_vec, t_norm, item["name_vector"], item["name_norm"])
                        if t_sim > sim_name:
                            sim_name = t_sim

            sim = max(sim_full, sim_name)

            if sim >= min_similarity:
                scored.append((sim, item))

        # Sort descending
        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:top_k]

        candidates = []
        for sim, match in top_matches:
            ent_type = match["type"]
            data = match["data"]
            cand = self._make_candidate(ent_type, data, round(sim, 3))
            candidates.append(cand)

        return candidates

    def _make_candidate(self, ent_type: EntityType, data: Dict[str, Any], score: float) -> CandidateEntity:
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

        name = data.get("canonical_name", data.get("name", ""))
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
            match_source="dense_geographic",
            channels=["dense_geographic"],
        )


dense_retriever = DenseGeographicRetriever()
