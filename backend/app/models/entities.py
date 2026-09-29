"""SQLAlchemy models for Indian administrative boundaries, postal codes, and verification records."""

import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class AdministrativeEntity(Base):
    """Represents an administrative unit in the Indian hierarchy (State, District, SubDistrict, Locality)."""
    __tablename__ = "administrative_entities"

    id = Column(String(100), primary_key=True)
    level = Column(String(50), nullable=False, index=True)  # 'state', 'district', 'subdistrict', 'locality'
    name = Column(String(200), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    level_code = Column(String(20), nullable=True, index=True)  # e.g., 'MH', 'KA'
    parent_id = Column(String(100), ForeignKey("administrative_entities.id"), nullable=True)
    
    # Aliases stored as JSON array of strings
    aliases = Column(JSON, default=list)
    
    # Centroid / Default Coordinate
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Bounding Box: [min_lon, min_lat, max_lon, max_lat]
    bbox = Column(JSON, nullable=True)
    
    # GeoJSON Polygon/MultiPolygon Coordinates
    geometry_geojson = Column(JSON, nullable=True)
    
    source = Column(String(200), default="Survey of India / Local Govt Directory")
    source_date = Column(String(50), default="2026")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    children = relationship("AdministrativeEntity", backref="parent", remote_side=[id])


class PostalCode(Base):
    """Represents a 6-digit Indian PIN Code with postal circle, division, post offices and centroid."""
    __tablename__ = "postal_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pincode = Column(String(6), nullable=False, unique=True, index=True)
    circle = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    division = Column(String(100), nullable=True)
    post_offices = Column(JSON, default=list)  # List of post office names
    district = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    state_code = Column(String(10), nullable=True)
    centroid_lat = Column(Float, nullable=True)
    centroid_lon = Column(Float, nullable=True)
    source = Column(String(100), default="India Post")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PointOfInterest(Base):
    """Represents nearby points of interest for consistency verification and context."""
    __tablename__ = "points_of_interest"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # transit, hospital, education, commercial, landmark, police, post_office
    subtype = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(500), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    source = Column(String(100), default="OpenStreetMap / Verified Directory")


class VerificationLog(Base):
    """Audit log of verification checks conducted."""
    __tablename__ = "verification_logs"

    id = Column(String(100), primary_key=True)
    request_address = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, index=True)  # VERIFIED, CONSISTENT, NEEDS_REVIEW, etc.
    score = Column(Integer, nullable=False)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    locality = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    evidence_json = Column(JSON, default=list)
    warnings_json = Column(JSON, default=list)
    score_breakdown_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
