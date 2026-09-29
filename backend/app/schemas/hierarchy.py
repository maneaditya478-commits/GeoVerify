"""Schemas for administrative hierarchy representations."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HierarchyNode(BaseModel):
    level: str = Field(..., json_schema_extra={"example": "district"})
    name: str = Field(..., json_schema_extra={"example": "Pune"})
    canonical_name: Optional[str] = None
    level_code: Optional[str] = None
    matched: bool = True
    evidence: Optional[str] = None


class AdministrativeHierarchyResult(BaseModel):
    country: str = "India"
    state: Optional[str] = None
    state_code: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    locality: Optional[str] = None
    is_consistent: bool = True
    hierarchy_chain: List[HierarchyNode] = []
    mismatch_details: List[str] = []
