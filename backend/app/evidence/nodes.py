"""Evidence Graph Node definitions and schemas for GeoVerify India."""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    COUNTRY = "country"
    STATE = "state"
    DISTRICT = "district"
    SUBDISTRICT = "subdistrict"
    LOCALITY = "locality"
    PINCODE = "pincode"
    COORDINATES = "coordinates"
    POI = "poi"
    LANDMARK = "landmark"


class NodeStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONSISTENT = "CONSISTENT"
    WARNING = "WARNING"
    CONFLICT = "CONFLICT"
    UNVERIFIED = "UNVERIFIED"


class EvidenceNode(BaseModel):
    id: str = Field(..., description="Unique node ID in graph, e.g., 'state_maharashtra'")
    label: str = Field(..., description="Display label for node")
    node_type: NodeType = Field(..., description="Classification level")
    level: str = Field(..., description="Human-readable level description")
    status: NodeStatus = Field(NodeStatus.CONSISTENT, description="Verification status of this node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata / codes")
