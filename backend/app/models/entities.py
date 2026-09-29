"""SQLAlchemy models for Indian administrative boundaries, postal codes, and verification records."""

import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class StateEntity(Base):
    """Represents an authoritative Indian State or Union Territory."""
    __tablename__ = "states"

    id = Column(String(50), primary_key=True)  # e.g., 'state_mh' or 'MH'
    lgd_code = Column(Integer, unique=True, index=True, nullable=True)  # Official LGD State Code
    code = Column(String(10), unique=True, index=True, nullable=False)  # e.g., 'MH', 'DL'
    name = Column(String(200), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    name_hi = Column(String(200), nullable=True)
    name_mr = Column(String(200), nullable=True)
    type = Column(String(50), default="State")  # State or Union Territory
    capital = Column(String(100), nullable=True)
    aliases = Column(JSON, default=list)
    bbox = Column(JSON, nullable=True)
    geometry_geojson = Column(JSON, nullable=True)
    source = Column(String(200), default="Local Government Directory / Survey of India")
    license = Column(String(100), default="GODL-India")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    districts = relationship("DistrictEntity", back_populates="state_ref", cascade="all, delete-orphan")


class DistrictEntity(Base):
    """Represents an Indian District under a parent State."""
    __tablename__ = "districts"

    id = Column(String(100), primary_key=True)  # e.g., 'dist_pune'
    lgd_code = Column(Integer, unique=True, index=True, nullable=True)  # Official LGD District Code
    state_id = Column(String(50), ForeignKey("states.id"), nullable=True, index=True)
    state_lgd_code = Column(Integer, nullable=True)
    state_code = Column(String(10), index=True, nullable=True)
    state_name = Column(String(200), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    name_hi = Column(String(200), nullable=True)
    name_mr = Column(String(200), nullable=True)
    aliases = Column(JSON, default=list)
    headquarters = Column(String(100), nullable=True)
    bbox = Column(JSON, nullable=True)
    geometry_geojson = Column(JSON, nullable=True)
    source = Column(String(200), default="Local Government Directory / Survey of India")
    license = Column(String(100), default="GODL-India")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    state_ref = relationship("StateEntity", back_populates="districts")
    subdistricts = relationship("SubDistrictEntity", back_populates="district_ref", cascade="all, delete-orphan")


class SubDistrictEntity(Base):
    """Represents Sub-Districts / Talukas / Tehsils / Mandals / Subdivisions / Blocks."""
    __tablename__ = "subdistricts"

    id = Column(String(100), primary_key=True)  # e.g., 'subdist_haveli'
    lgd_code = Column(Integer, unique=True, index=True, nullable=True)  # Official LGD Sub-District Code
    district_id = Column(String(100), ForeignKey("districts.id"), nullable=True, index=True)
    district_name = Column(String(200), nullable=False, index=True)
    state_name = Column(String(200), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    name_hi = Column(String(200), nullable=True)
    name_mr = Column(String(200), nullable=True)
    admin_type = Column(String(50), default="Taluka")  # Taluka, Tehsil, Mandal, Subdivision, Block
    aliases = Column(JSON, default=list)
    bbox = Column(JSON, nullable=True)
    geometry_geojson = Column(JSON, nullable=True)
    source = Column(String(200), default="Local Government Directory")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    district_ref = relationship("DistrictEntity", back_populates="subdistricts")
    localities = relationship("LocalityEntity", back_populates="subdistrict_ref", cascade="all, delete-orphan")


class LocalityEntity(Base):
    """Represents a Locality, Village, Town, or Municipal Ward."""
    __tablename__ = "localities"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    name_hi = Column(String(200), nullable=True)
    name_mr = Column(String(200), nullable=True)
    aliases = Column(JSON, default=list)
    subdistrict_id = Column(String(100), ForeignKey("subdistricts.id"), nullable=True, index=True)
    subdistrict = Column(String(200), nullable=True)
    district_id = Column(String(100), ForeignKey("districts.id"), nullable=True, index=True)
    district = Column(String(200), nullable=False, index=True)
    state = Column(String(200), nullable=False, index=True)
    state_code = Column(String(10), nullable=True)
    pincode = Column(String(10), nullable=True, index=True)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    bbox = Column(JSON, nullable=True)
    geometry_geojson = Column(JSON, nullable=True)
    source = Column(String(200), default="Verified Gazetteers / OpenStreetMap")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    subdistrict_ref = relationship("SubDistrictEntity", back_populates="localities")


# Legacy alias for backward compatibility
AdministrativeEntity = StateEntity


class PostalCode(Base):
    """Represents a 6-digit Indian PIN Code with postal circle, division, post offices and centroid."""
    __tablename__ = "postal_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pincode = Column(String(6), nullable=False, unique=True, index=True)
    circle = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    division = Column(String(100), nullable=True)
    office_type = Column(String(50), nullable=True)  # H.O, S.O, B.O
    delivery_status = Column(String(50), default="Delivery")
    post_offices = Column(JSON, default=list)
    district = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    state_code = Column(String(10), nullable=True)
    centroid_lat = Column(Float, nullable=True)
    centroid_lon = Column(Float, nullable=True)
    source = Column(String(100), default="India Post (Department of Posts)")
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


class DatasetProvenance(Base):
    """Metadata and lineage for authoritative datasets ingested into GeoVerify."""
    __tablename__ = "dataset_provenance"

    id = Column(String(100), primary_key=True)
    dataset_name = Column(String(200), nullable=False)
    record_count = Column(Integer, nullable=False)
    crs = Column(String(50), default="EPSG:4326 (WGS84)")
    license = Column(String(100), default="GODL-India")
    source_url = Column(String(500), nullable=True)
    version = Column(String(50), default="2026.1")
    last_imported = Column(DateTime, default=datetime.datetime.utcnow)


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


# Indexing definitions for fast lookup
Index("idx_district_state_code", DistrictEntity.state_code)
Index("idx_locality_district_name", LocalityEntity.district)
Index("idx_subdistrict_district_name", SubDistrictEntity.district_name)
