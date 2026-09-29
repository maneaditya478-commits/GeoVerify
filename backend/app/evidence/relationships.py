"""Evidence Graph Relationship and Edge definitions."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    LOCATED_IN = "located_in"
    INSIDE_POLYGON = "inside_polygon"
    POSTAL_AREA_OF = "postal_area_of"
    IN_VICINITY_OF = "in_vicinity_of"
    ADMINISTRATIVE_PARENT = "administrative_parent"
    MISMATCH_WITH = "mismatch_with"


class EdgeSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CONFLICT = "CONFLICT"


class EvidenceEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: RelationshipType = Field(..., description="Semantic relationship type")
    label: str = Field(..., description="Human-readable edge label (e.g. 'located in', 'inside polygon')")
    severity: EdgeSeverity = Field(EdgeSeverity.INFO, description="INFO, WARNING, CONFLICT")
    passed: bool = Field(True, description="Whether the relationship check passed")
    evidence_text: Optional[str] = Field(None, description="Detailed explanatory text")
