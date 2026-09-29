"""Data source downloader and catalog synchronizer for GeoVerify India.
Downloads or prepares raw authoritative Indian geographic datasets from LGD, SOI, and India Post.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoverify.downloader")

DATA_DIR = Path(__file__).parent.parent.parent
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
RAW_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)

SOURCES_CATALOG = {
    "lgd_states": {
        "title": "Local Government Directory - States and Union Territories",
        "source_url": "https://lgdirectory.gov.in/services/getStateList",
        "publisher": "Ministry of Panchayati Raj, Government of India",
        "license": "Government Open Data License - India (GODL)",
        "version": "2026.1",
        "format": "JSON",
        "target_file": "raw_states.json"
    },
    "lgd_districts": {
        "title": "Local Government Directory - District Directory",
        "source_url": "https://lgdirectory.gov.in/services/getDistrictList",
        "publisher": "Ministry of Panchayati Raj, Government of India",
        "license": "Government Open Data License - India (GODL)",
        "version": "2026.1",
        "format": "JSON",
        "target_file": "raw_districts.json"
    },
    "lgd_subdistricts": {
        "title": "Local Government Directory - Sub-District / Taluka Directory",
        "source_url": "https://lgdirectory.gov.in/services/getSubDistrictList",
        "publisher": "Ministry of Panchayati Raj, Government of India",
        "license": "Government Open Data License - India (GODL)",
        "version": "2026.1",
        "format": "JSON",
        "target_file": "raw_subdistricts.json"
    },
    "india_post_pincodes": {
        "title": "All India Pincode Directory",
        "source_url": "https://data.gov.in/resource/all-india-pincode-directory",
        "publisher": "Department of Posts, Ministry of Communications, Government of India",
        "license": "Government Open Data License - India (GODL)",
        "version": "2026.1",
        "format": "JSON",
        "target_file": "raw_pincodes.json"
    }
}


def create_manifest() -> Path:
    """Create a download manifest tracking provenance, license, timestamp, and status."""
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_STAGING",
        "crs": "EPSG:4326 (WGS84)",
        "sources": SOURCES_CATALOG
    }
    manifest_path = RAW_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Created data source manifest at {manifest_path}")
    return manifest_path


if __name__ == "__main__":
    create_manifest()
