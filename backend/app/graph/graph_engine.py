"""Geographic Relationship Graph Engine with indexing, traversals, and subgraph extraction."""

import re
from typing import Optional, List, Dict, Set, Tuple
from collections import deque

from app.graph.models import (
    GeographicNodeType,
    GeographicEdgeType,
    GeographicEntityNode,
    GeographicRelationshipEdge,
    GraphTraversalStep,
    EvidencePath,
    SubgraphEvidence,
)
from app.temporal.catalog import HISTORICAL_RECORDS
from app.landmarks.catalog import LANDMARK_CATALOG
from app.verification.hierarchy import HierarchyValidator


class GeographicGraph:
    """In-memory indexed graph representing Indian multi-level geographic entities,

    hierarchies, postal routing, historical transformations, and spatial landmarks.
    """

    def __init__(self):
        self.nodes: Dict[str, GeographicEntityNode] = {}
        self.edges: List[GeographicRelationshipEdge] = []
        self._adj: Dict[str, List[Tuple[str, GeographicRelationshipEdge]]] = {}
        self._rev_adj: Dict[str, List[Tuple[str, GeographicRelationshipEdge]]] = {}
        self._name_index: Dict[str, List[str]] = {}
        self._pincode_index: Dict[str, List[str]] = {}

        self._initialize_graph()

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text.strip().lower())

    def add_node(self, node: GeographicEntityNode):
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self._adj[node.id] = []
            self._rev_adj[node.id] = []

            # Index by primary name
            norm_name = self._normalize(node.name)
            self._name_index.setdefault(norm_name, []).append(node.id)

            # Index by aliases
            for alias in node.aliases:
                norm_alias = self._normalize(alias)
                self._name_index.setdefault(norm_alias, []).append(node.id)

            # Index by pincode
            if node.pincode:
                self._pincode_index.setdefault(node.pincode.strip(), []).append(node.id)

    def add_edge(self, edge: GeographicRelationshipEdge):
        if edge.source_id in self.nodes and edge.target_id in self.nodes:
            self.edges.append(edge)
            self._adj[edge.source_id].append((edge.target_id, edge))
            self._rev_adj[edge.target_id].append((edge.source_id, edge))

    def _initialize_graph(self):
        # 1. Country Node
        india_id = "country_india"
        self.add_node(GeographicEntityNode(
            id=india_id,
            name="India",
            node_type=GeographicNodeType.COUNTRY,
            canonical_name="Republic of India",
            aliases=["Bharat", "IN", "IND"]
        ))

        # 2. Ingest hierarchy data
        hierarchy_validator = HierarchyValidator()
        state_id_map = {}

        for state in hierarchy_validator.states:
            s_name = state["name"]
            s_id = f"state_{self._normalize(s_name).replace(' ', '_')}"
            state_id_map[s_name.lower()] = s_id
            self.add_node(GeographicEntityNode(
                id=s_id,
                name=s_name,
                node_type=GeographicNodeType.STATE,
                canonical_name=state.get("canonical_name", s_name),
                state=s_name,
                aliases=state.get("aliases", []) + ([state["name_hi"]] if state.get("name_hi") else []) + ([state["name_mr"]] if state.get("name_mr") else []),
                properties={"code": state.get("code", "")}
            ))
            # Edge: State -> Country
            self.add_edge(GeographicRelationshipEdge(
                id=f"edge_{s_id}_{india_id}",
                source_id=s_id,
                target_id=india_id,
                edge_type=GeographicEdgeType.PART_OF
            ))
            self.add_edge(GeographicRelationshipEdge(
                id=f"edge_{india_id}_{s_id}",
                source_id=india_id,
                target_id=s_id,
                edge_type=GeographicEdgeType.CONTAINS
            ))

        district_id_map = {}
        for dist in hierarchy_validator.districts:
            d_name = dist["name"]
            d_state = dist.get("state_name") or dist.get("state", "")
            d_id = f"dist_{self._normalize(d_name).replace(' ', '_')}_{self._normalize(d_state).replace(' ', '_')}"
            district_id_map[(d_name.lower(), d_state.lower())] = d_id
            district_id_map[d_name.lower()] = d_id
            self.add_node(GeographicEntityNode(
                id=d_id,
                name=d_name,
                node_type=GeographicNodeType.DISTRICT,
                canonical_name=dist.get("canonical_name", d_name),
                state=d_state,
                district=d_name,
                aliases=dist.get("aliases", []) + ([dist["name_hi"]] if dist.get("name_hi") else []) + ([dist["name_mr"]] if dist.get("name_mr") else [])
            ))

            # Edge: District -> State
            s_id = state_id_map.get(d_state.lower())
            if s_id:
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{d_id}_{s_id}",
                    source_id=d_id,
                    target_id=s_id,
                    edge_type=GeographicEdgeType.PART_OF
                ))
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{s_id}_{d_id}",
                    source_id=s_id,
                    target_id=d_id,
                    edge_type=GeographicEdgeType.CONTAINS
                ))

        for subdist in hierarchy_validator.subdistricts:
            sd_name = subdist["name"]
            sd_dist = subdist.get("district", "")
            sd_state = subdist.get("state_name") or subdist.get("state", "")
            sd_id = f"taluka_{self._normalize(sd_name).replace(' ', '_')}_{self._normalize(sd_dist).replace(' ', '_')}"
            self.add_node(GeographicEntityNode(
                id=sd_id,
                name=sd_name,
                node_type=GeographicNodeType.TALUKA,
                canonical_name=subdist.get("canonical_name", sd_name),
                state=sd_state,
                district=sd_dist,
                subdistrict=sd_name
            ))
            # Edge: Taluka -> District
            d_id = district_id_map.get((sd_dist.lower(), sd_state.lower())) or district_id_map.get(sd_dist.lower())
            if d_id:
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{sd_id}_{d_id}",
                    source_id=sd_id,
                    target_id=d_id,
                    edge_type=GeographicEdgeType.PART_OF
                ))
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{d_id}_{sd_id}",
                    source_id=d_id,
                    target_id=sd_id,
                    edge_type=GeographicEdgeType.CONTAINS
                ))

        for loc in hierarchy_validator.localities:
            l_name = loc["name"]
            l_dist = loc.get("district", "")
            l_state = loc.get("state_name") or loc.get("state", "")
            l_pin = str(loc.get("pincode", ""))
            l_id = f"loc_{self._normalize(l_name).replace(' ', '_')}_{self._normalize(l_dist).replace(' ', '_')}"
            self.add_node(GeographicEntityNode(
                id=l_id,
                name=l_name,
                node_type=GeographicNodeType.LOCALITY,
                canonical_name=loc.get("canonical_name", l_name),
                state=l_state,
                district=l_dist,
                subdistrict=loc.get("subdistrict"),
                pincode=l_pin,
                latitude=loc.get("latitude"),
                longitude=loc.get("longitude"),
                aliases=loc.get("aliases", [])
            ))

            # Edge: Locality -> District
            d_id = district_id_map.get((l_dist.lower(), l_state.lower())) or district_id_map.get(l_dist.lower())
            if d_id:
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{l_id}_{d_id}",
                    source_id=l_id,
                    target_id=d_id,
                    edge_type=GeographicEdgeType.PART_OF
                ))
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{d_id}_{l_id}",
                    source_id=d_id,
                    target_id=l_id,
                    edge_type=GeographicEdgeType.CONTAINS
                ))

            # Postal code node & edge
            if l_pin:
                pin_id = f"pin_{l_pin}"
                if pin_id not in self.nodes:
                    self.add_node(GeographicEntityNode(
                        id=pin_id,
                        name=f"PIN {l_pin}",
                        node_type=GeographicNodeType.POSTAL_CODE,
                        pincode=l_pin,
                        state=l_state,
                        district=l_dist
                    ))
                    if d_id:
                        self.add_edge(GeographicRelationshipEdge(
                            id=f"edge_{pin_id}_{d_id}",
                            source_id=pin_id,
                            target_id=d_id,
                            edge_type=GeographicEdgeType.PART_OF
                        ))
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{l_id}_{pin_id}",
                    source_id=l_id,
                    target_id=pin_id,
                    edge_type=GeographicEdgeType.SERVED_BY
                ))

        # 3. Ingest Historical Transformations
        for rec in HISTORICAL_RECORDS:
            hist_id = f"hist_{self._normalize(rec.historical_name).replace(' ', '_')}"
            self.add_node(GeographicEntityNode(
                id=hist_id,
                name=rec.historical_name,
                node_type=GeographicNodeType(rec.entity_type.value),
                canonical_name=rec.current_name,
                state=rec.state,
                district=rec.district,
                properties={"effective_year": rec.effective_year, "status": "HISTORICAL"}
            ))

            curr_ids = self.find_nodes_by_name(rec.current_name)
            for curr_id in curr_ids:
                if curr_id != hist_id:
                    self.add_edge(GeographicRelationshipEdge(
                        id=f"edge_{hist_id}_{curr_id}",
                        source_id=hist_id,
                        target_id=curr_id,
                        edge_type=GeographicEdgeType.RENAMED_TO,
                        properties={"year": rec.effective_year}
                    ))
                    self.add_edge(GeographicRelationshipEdge(
                        id=f"edge_{curr_id}_{hist_id}",
                        source_id=curr_id,
                        target_id=hist_id,
                        edge_type=GeographicEdgeType.FORMERLY_KNOWN_AS,
                        properties={"year": rec.effective_year}
                    ))

        # 4. Ingest Landmarks
        for lm in LANDMARK_CATALOG:
            lm_id = lm.id
            self.add_node(GeographicEntityNode(
                id=lm_id,
                name=lm.name,
                node_type=GeographicNodeType.LANDMARK,
                state=lm.state,
                district=lm.district,
                subdistrict=lm.taluka,
                pincode=lm.pincode,
                latitude=lm.latitude,
                longitude=lm.longitude,
                aliases=lm.aliases,
                properties={"category": lm.category.value}
            ))

            loc_ids = self.find_nodes_by_name(lm.locality)
            for loc_id in loc_ids:
                self.add_edge(GeographicRelationshipEdge(
                    id=f"edge_{lm_id}_{loc_id}",
                    source_id=lm_id,
                    target_id=loc_id,
                    edge_type=GeographicEdgeType.NEAR,
                    properties={"category": lm.category.value}
                ))

    def find_nodes_by_name(self, name: str, node_type: Optional[GeographicNodeType] = None) -> List[str]:
        """Looks up node IDs matching a name or alias."""
        norm = self._normalize(name)
        matched_ids = self._name_index.get(norm, [])
        if not matched_ids:
            # Substring scan
            for k, v in self._name_index.items():
                if norm == k or norm in k or k in norm:
                    matched_ids.extend(v)
        unique_ids = list(dict.fromkeys(matched_ids))
        if node_type:
            unique_ids = [nid for nid in unique_ids if self.nodes[nid].node_type == node_type]
        return unique_ids

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 4,
        max_nodes: int = 100
    ) -> Optional[EvidencePath]:
        """Finds shortest path between two nodes using BFS with bounded depth and node exploration."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        if source_id == target_id:
            src_node = self.nodes[source_id]
            return EvidencePath(
                source_id=source_id,
                target_id=target_id,
                steps=[],
                total_depth=0,
                is_valid_hierarchical_path=True,
                narrative=f"{src_node.name} is the identical entity."
            )

        queue = deque([(source_id, [])])
        visited: Set[str] = {source_id}
        explored_count = 0

        while queue and explored_count < max_nodes:
            curr_id, path = queue.popleft()
            explored_count += 1

            if len(path) >= max_depth:
                continue

            for next_id, edge in self._adj.get(curr_id, []):
                new_path = path + [edge]
                if next_id == target_id:
                    # Construct steps
                    steps = []
                    for step_edge in new_path:
                        u = self.nodes[step_edge.source_id]
                        v = self.nodes[step_edge.target_id]
                        steps.append(GraphTraversalStep(
                            from_node=u,
                            to_node=v,
                            edge_type=step_edge.edge_type,
                            description=f"{u.name} ({u.node_type.value}) -> [{step_edge.edge_type.value}] -> {v.name} ({v.node_type.value})"
                        ))
                    return EvidencePath(
                        source_id=source_id,
                        target_id=target_id,
                        steps=steps,
                        total_depth=len(steps),
                        is_valid_hierarchical_path=True,
                        narrative=" -> ".join([s.description for s in steps])
                    )

                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, new_path))

        return None

    def extract_evidence_subgraph(
        self,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        landmark: Optional[str] = None
    ) -> SubgraphEvidence:
        """Extracts the minimal connected evidence subgraph connecting extracted address entities."""
        matched_node_ids: List[str] = []

        if locality:
            matched_node_ids.extend(self.find_nodes_by_name(locality, GeographicNodeType.LOCALITY))
        if district:
            matched_node_ids.extend(self.find_nodes_by_name(district, GeographicNodeType.DISTRICT))
        if state:
            matched_node_ids.extend(self.find_nodes_by_name(state, GeographicNodeType.STATE))
        if pincode:
            matched_node_ids.extend(self._pincode_index.get(pincode.strip(), []))
        if landmark:
            matched_node_ids.extend(self.find_nodes_by_name(landmark, GeographicNodeType.LANDMARK))

        unique_node_ids = list(dict.fromkeys(matched_node_ids))
        sub_nodes = [self.nodes[nid] for nid in unique_node_ids if nid in self.nodes]

        # Extract paths between consecutive hierarchy levels
        paths: List[EvidencePath] = []
        is_consistent = True

        # Locality -> District path
        if locality and district:
            loc_ids = self.find_nodes_by_name(locality, GeographicNodeType.LOCALITY)
            dist_ids = self.find_nodes_by_name(district, GeographicNodeType.DISTRICT)
            found = False
            for lid in loc_ids:
                for did in dist_ids:
                    p = self.find_path(lid, did, max_depth=3)
                    if p:
                        paths.append(p)
                        found = True
                        break
                if found:
                    break
            if not found and loc_ids and dist_ids:
                is_consistent = False

        # District -> State path
        if district and state:
            dist_ids = self.find_nodes_by_name(district, GeographicNodeType.DISTRICT)
            st_ids = self.find_nodes_by_name(state, GeographicNodeType.STATE)
            found = False
            for did in dist_ids:
                for sid in st_ids:
                    p = self.find_path(did, sid, max_depth=2)
                    if p:
                        paths.append(p)
                        found = True
                        break
                if found:
                    break
            if not found and dist_ids and st_ids:
                is_consistent = False

        # Build edge subset
        sub_node_set = {n.id for n in sub_nodes}
        sub_edges = [e for e in self.edges if e.source_id in sub_node_set and e.target_id in sub_node_set]

        summary = (
            f"Geographic subgraph contains {len(sub_nodes)} entities with {len(paths)} verified traversal path(s). "
            f"Consistency status: {'CONSISTENT' if is_consistent else 'HIERARCHICAL_MISMATCH'}."
        )

        return SubgraphEvidence(
            nodes=sub_nodes,
            edges=sub_edges,
            paths=paths,
            summary=summary,
            is_consistent=is_consistent
        )


# Global singleton graph instance
geographic_graph = GeographicGraph()
