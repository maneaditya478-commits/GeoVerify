"""Data models for Landmark-Aware Spatial Reasoning."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LandmarkCategory(str, Enum):
    TRANSIT = "TRANSIT"                # Railway Station, Metro, Airport, Bus Station
    EDUCATION = "EDUCATION"            # University, IIT, College, School
    HEALTHCARE = "HEALTHCARE"          # Hospital, Medical College
    HERITAGE = "HERITAGE"              # Fort, Monument, Palace, Museum
    COMMERCIAL = "COMMERCIAL"          # Mall, Market, IT Park, SEZ
    TECH_PARK = "TECH_PARK"            # Infotech Park, Cyber Hub
    ADMINISTRATIVE = "ADMINISTRATIVE"  # High Court, Collectorate, Municipal Corp
    WORSHIP = "WORSHIP"                # Temple, Mosque, Gurudwara, Church
    POSTAL = "POSTAL"                  # Head Post Office, GPO


class DistanceBucket(str, Enum):
    WITHIN_500M = "<500m"
    FROM_500M_TO_1KM = "500m-1km"
    FROM_1KM_TO_5KM = "1km-5km"
    FROM_5KM_TO_15KM = "5km-15km"
    BEYOND_15KM = ">15km"


class LandmarkEntity(BaseModel):
    id: str
    name: str
    category: LandmarkCategory
    locality: str
    taluka: Optional[str] = None
    district: str
    state: str
    pincode: Optional[str] = None
    latitude: float
    longitude: float
    aliases: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class LandmarkEvidence(BaseModel):
    landmark_id: str
    landmark_name: str
    category: LandmarkCategory
    extracted_mention: str
    target_locality: Optional[str] = None
    distance_km: Optional[float] = None
    distance_bucket: DistanceBucket
    spatial_consistency_score: float = Field(..., ge=0.0, le=1.0)
    is_consistent: bool = True
    explanation: str
