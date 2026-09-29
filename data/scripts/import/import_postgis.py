"""Database import script for GeoVerify India.
Loads validated reference geographic data into SQLite / PostGIS tables.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to sys.path
backend_dir = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.database import engine, SessionLocal, Base
from app.models.entities import (
    StateEntity,
    DistrictEntity,
    SubDistrictEntity,
    LocalityEntity,
    PostalCode,
    PointOfInterest,
    DatasetProvenance
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoverify.importer")

DATA_DIR = Path(__file__).parent.parent.parent / "processed"


def import_all():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # 1. Import States
        states_file = DATA_DIR / "states.json"
        if states_file.exists():
            states = json.loads(states_file.read_text(encoding="utf-8"))
            for s in states:
                state_id = f"state_{s['code'].lower()}"
                existing = session.query(StateEntity).filter_by(id=state_id).first()
                if not existing:
                    session.add(StateEntity(
                        id=state_id,
                        lgd_code=s.get("lgd_code"),
                        code=s["code"],
                        name=s["name"],
                        canonical_name=s["canonical_name"],
                        name_hi=s.get("name_hi"),
                        name_mr=s.get("name_mr"),
                        type=s.get("type", "State"),
                        capital=s.get("capital"),
                        aliases=s.get("aliases", []),
                        bbox=s.get("bbox"),
                        geometry_geojson={"type": "Polygon", "coordinates": [s.get("polygon", [])]},
                        source=s.get("source", "LGD / Survey of India"),
                        license=s.get("license", "GODL-India")
                    ))
            logger.info(f"Imported {len(states)} states into database.")

        # 2. Import Districts
        districts_file = DATA_DIR / "districts.json"
        if districts_file.exists():
            districts = json.loads(districts_file.read_text(encoding="utf-8"))
            for d in districts:
                existing = session.query(DistrictEntity).filter_by(id=d["id"]).first()
                if not existing:
                    session.add(DistrictEntity(
                        id=d["id"],
                        lgd_code=d.get("lgd_code"),
                        state_id=f"state_{d['state_code'].lower()}",
                        state_lgd_code=d.get("state_lgd_code"),
                        state_code=d.get("state_code"),
                        state_name=d["state_name"],
                        name=d["name"],
                        canonical_name=d["canonical_name"],
                        name_hi=d.get("name_hi"),
                        name_mr=d.get("name_mr"),
                        aliases=d.get("aliases", []),
                        headquarters=d.get("headquarters"),
                        bbox=d.get("bbox"),
                        geometry_geojson={"type": "Polygon", "coordinates": [d.get("polygon", [])]},
                        source=d.get("source", "LGD / Survey of India"),
                        license=d.get("license", "GODL-India")
                    ))
            logger.info(f"Imported {len(districts)} districts into database.")

        # 3. Import Sub-Districts
        subdistricts_file = DATA_DIR / "subdistricts.json"
        if subdistricts_file.exists():
            subdistricts = json.loads(subdistricts_file.read_text(encoding="utf-8"))
            for sd in subdistricts:
                existing = session.query(SubDistrictEntity).filter_by(id=sd["id"]).first()
                if not existing:
                    session.add(SubDistrictEntity(
                        id=sd["id"],
                        lgd_code=sd.get("lgd_code"),
                        district_id=sd.get("district_id"),
                        district_name=sd["district_name"],
                        state_name=sd["state_name"],
                        name=sd["name"],
                        canonical_name=sd["canonical_name"],
                        admin_type=sd.get("admin_type", "Taluka"),
                        bbox=sd.get("bbox"),
                        geometry_geojson={"type": "Polygon", "coordinates": [sd.get("polygon", [])]},
                        source=sd.get("source", "LGD")
                    ))
            logger.info(f"Imported {len(subdistricts)} subdistricts into database.")

        # 4. Import Localities
        localities_file = DATA_DIR / "localities.json"
        if localities_file.exists():
            localities = json.loads(localities_file.read_text(encoding="utf-8"))
            for loc in localities:
                loc_id = f"loc_{loc['name'].lower().replace(' ', '_')}"
                existing = session.query(LocalityEntity).filter_by(id=loc_id).first()
                if not existing:
                    session.add(LocalityEntity(
                        id=loc_id,
                        name=loc["name"],
                        canonical_name=loc.get("canonical_name", loc["name"]),
                        name_hi=loc.get("name_hi"),
                        name_mr=loc.get("name_mr"),
                        aliases=loc.get("aliases", []),
                        subdistrict_id=loc.get("subdistrict_id"),
                        subdistrict=loc.get("subdistrict"),
                        district_id=loc.get("district_id"),
                        district=loc["district"],
                        state=loc["state"],
                        state_code=loc.get("state_code"),
                        pincode=loc.get("pincode"),
                        latitude=loc["coordinates"]["latitude"] if "coordinates" in loc else None,
                        longitude=loc["coordinates"]["longitude"] if "coordinates" in loc else None,
                        bbox=loc.get("bbox"),
                        geometry_geojson={"type": "Polygon", "coordinates": [loc.get("polygon", [])]} if loc.get("polygon") else None,
                        source=loc.get("source", "Verified Gazetteer")
                    ))
            logger.info(f"Imported {len(localities)} localities into database.")

        # 5. Import PIN Codes
        pincodes_file = DATA_DIR / "pincodes.json"
        if pincodes_file.exists():
            pincodes = json.loads(pincodes_file.read_text(encoding="utf-8"))
            for p in pincodes:
                existing = session.query(PostalCode).filter_by(pincode=p["pincode"]).first()
                if not existing:
                    session.add(PostalCode(
                        pincode=p["pincode"],
                        circle=p.get("circle"),
                        region=p.get("region"),
                        division=p.get("division"),
                        office_type=p.get("office_type", "S.O"),
                        delivery_status=p.get("delivery_status", "Delivery"),
                        post_offices=p.get("post_offices", []),
                        district=p.get("district"),
                        state=p.get("state"),
                        state_code=p.get("state_code"),
                        centroid_lat=p["centroid"]["latitude"] if "centroid" in p and p["centroid"] else None,
                        centroid_lon=p["centroid"]["longitude"] if "centroid" in p and p["centroid"] else None,
                        source=p.get("source", "India Post")
                    ))
            logger.info(f"Imported {len(pincodes)} PIN codes into database.")

        # 6. Import POIs
        pois_file = DATA_DIR / "pois.json"
        if pois_file.exists():
            pois = json.loads(pois_file.read_text(encoding="utf-8"))
            for poi in pois:
                existing = session.query(PointOfInterest).filter_by(name=poi["name"]).first()
                if not existing:
                    session.add(PointOfInterest(
                        name=poi["name"],
                        category=poi["category"],
                        subtype=poi.get("subtype"),
                        latitude=poi["coordinates"]["latitude"],
                        longitude=poi["coordinates"]["longitude"],
                        address=poi.get("address"),
                        district=poi.get("district"),
                        state=poi.get("state"),
                        source=poi.get("source", "OpenStreetMap")
                    ))
            logger.info(f"Imported {len(pois)} POIs into database.")

        # 7. Record Provenance
        provenances = [
            DatasetProvenance(
                id="prov_lgd_admin",
                dataset_name="Local Government Directory (LGD) Administrative Boundaries",
                record_count=len(states) + len(districts) + len(subdistricts),
                crs="EPSG:4326 (WGS84)",
                license="GODL-India",
                source_url="https://lgdirectory.gov.in/",
                version="2026.1"
            ),
            DatasetProvenance(
                id="prov_india_post",
                dataset_name="All India Pincode Directory",
                record_count=len(pincodes),
                crs="EPSG:4326 (WGS84)",
                license="GODL-India",
                source_url="https://data.gov.in/resource/all-india-pincode-directory",
                version="2026.1"
            )
        ]
        for prov in provenances:
            existing = session.query(DatasetProvenance).filter_by(id=prov.id).first()
            if not existing:
                session.add(prov)

        session.commit()
        logger.info("Database import completed successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error during database import: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_all()
