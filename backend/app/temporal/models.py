"""Data models for Temporal Geography reasoning and historical administrative entities."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TemporalRelationshipType(str, Enum):
    RENAMED_TO = "RENAMED_TO"
    FORMERLY_KNOWN_AS = "FORMERLY_KNOWN_AS"
    SPLIT_FROM = "SPLIT_FROM"
    BIFURCATED_INTO = "BIFURCATED_INTO"
    MERGED_INTO = "MERGED_INTO"
    ADMINISTERED_BY = "ADMINISTERED_BY"
    HISTORICAL_SPELLING = "HISTORICAL_SPELLING"


class TemporalEntityType(str, Enum):
    COUNTRY = "COUNTRY"
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    TALUKA = "TALUKA"
    LOCALITY = "LOCALITY"
    CITY = "CITY"


class TemporalStatus(str, Enum):
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    VALID_FOR_DATE = "VALID_FOR_DATE"
    OUTSIDE_DATE_RANGE = "OUTSIDE_DATE_RANGE"
    UNKNOWN = "UNKNOWN"


class HistoricalNameRecord(BaseModel):
    current_name: str
    historical_name: str
    relationship: TemporalRelationshipType = TemporalRelationshipType.RENAMED_TO
    entity_type: TemporalEntityType = TemporalEntityType.CITY
    effective_year: Optional[int] = None
    effective_date: Optional[str] = None  # ISO format "YYYY-MM-DD"
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    authority_note: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)


class TemporalEvidence(BaseModel):
    status: TemporalStatus
    detected_name: str
    canonical_current_name: str
    relationship: TemporalRelationshipType
    entity_type: TemporalEntityType
    reference_date: Optional[str] = None
    effective_date: Optional[str] = None
    is_valid_for_reference_date: bool = True
    authority_note: Optional[str] = None
    explanation: str
