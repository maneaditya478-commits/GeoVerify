"""Data models for the Geographic Relationship Graph."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GeographicNodeType(str, Enum):
    COUNTRY = "COUNTRY"
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    TALUKA = "TALUKA"
    LOCALITY = "LOCALITY"
    CITY = "CITY"
    POSTAL_CODE = "POSTAL_CODE"
    LANDMARK = "LANDMARK"


class GeographicEdgeType(str, Enum):
    CONTAINS = "CONTAINS"
    PART_OF = "PART_OF"
    SERVED_BY = "SERVED_BY"
    COVERS_PIN = "COVERS_PIN"
    NEAR = "NEAR"
    ADJACENT_TO = "ADJACENT_TO"
    FORMERLY_KNOWN_AS = "FORMERLY_KNOWN_AS"
    RENAMED_TO = "RENAMED_TO"
    SAME_AS = "SAME_AS"
    ALIAS_OF = "ALIAS_OF"


class GeographicEntityNode(BaseModel):
    id: str
    name: str
    node_type: GeographicNodeType
    canonical_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    aliases: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeographicRelationshipEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    edge_type: GeographicEdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphTraversalStep(BaseModel):
    from_node: GeographicEntityNode
    to_node: GeographicEntityNode
    edge_type: GeographicEdgeType
    description: str


class EvidencePath(BaseModel):
    source_id: str
    target_id: str
    steps: List[GraphTraversalStep] = Field(default_factory=list)
    total_depth: int = 0
    is_valid_hierarchical_path: bool = True
    narrative: str = ""


class SubgraphEvidence(BaseModel):
    nodes: List[GeographicEntityNode] = Field(default_factory=list)
    edges: List[GeographicRelationshipEdge] = Field(default_factory=list)
    paths: List[EvidencePath] = Field(default_factory=list)
    summary: str = ""
    is_consistent: bool = True
