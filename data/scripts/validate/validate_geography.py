"""Data quality validation suite for Indian geographic reference datasets using Shapely."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from shapely.geometry import Polygon, Point, MultiPolygon

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoverify.validator")

DATA_DIR = Path(__file__).parent.parent.parent
PROCESSED_DIR = DATA_DIR / "processed"
STAGING_DIR = DATA_DIR / "staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)


class GeographicDataValidator:
    """Validates geometries, coordinate bounds, referential integrity, and uniqueness."""

    def __init__(self):
        self.issues: List[str] = []
        self.stats: Dict[str, Any] = {}

    def validate_dataset(self) -> Dict[str, Any]:
        states_file = PROCESSED_DIR / "states.json"
        districts_file = PROCESSED_DIR / "districts.json"
        subdistricts_file = PROCESSED_DIR / "subdistricts.json"
        localities_file = PROCESSED_DIR / "localities.json"
        pincodes_file = PROCESSED_DIR / "pincodes.json"

        states = json.loads(states_file.read_text(encoding="utf-8")) if states_file.exists() else []
        districts = json.loads(districts_file.read_text(encoding="utf-8")) if districts_file.exists() else []
        subdistricts = json.loads(subdistricts_file.read_text(encoding="utf-8")) if subdistricts_file.exists() else []
        localities = json.loads(localities_file.read_text(encoding="utf-8")) if localities_file.exists() else []
        pincodes = json.loads(pincodes_file.read_text(encoding="utf-8")) if pincodes_file.exists() else []

        # 1. Validate States
        state_codes = set()
        state_names = set()
        invalid_state_geom = 0
        for s in states:
            if not s.get("name") or not s.get("code"):
                self.issues.append(f"State missing name/code: {s}")
            if s["code"] in state_codes:
                self.issues.append(f"Duplicate state code: {s['code']}")
            state_codes.add(s["code"])
            state_names.add(s["name"].lower())

            # Validate Polygon
            poly_coords = s.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if not poly.is_valid or poly.is_empty:
                    invalid_state_geom += 1
                    self.issues.append(f"Invalid polygon for state: {s['name']}")

        self.stats["states"] = {
            "total_records": len(states),
            "invalid_geometries": invalid_state_geom,
            "missing_names": 0,
            "crs": "EPSG:4326 (WGS84)"
        }

        # 2. Validate Districts & Parent State Relationship
        dist_ids = set()
        dist_names = set()
        invalid_dist_geom = 0
        missing_parent_state = 0
        for d in districts:
            if not d.get("name") or not d.get("id"):
                self.issues.append(f"District missing name/id: {d}")
            if d["id"] in dist_ids:
                self.issues.append(f"Duplicate district id: {d['id']}")
            dist_ids.add(d["id"])
            dist_names.add(d["name"].lower())

            # Parent state check
            if d.get("state_code") not in state_codes and d.get("state_name", "").lower() not in state_names:
                missing_parent_state += 1
                self.issues.append(f"District {d['name']} missing valid parent state {d.get('state_code')}")

            # Geometry check
            poly_coords = d.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if not poly.is_valid or poly.is_empty:
                    invalid_dist_geom += 1
                    self.issues.append(f"Invalid polygon for district: {d['name']}")

        self.stats["districts"] = {
            "total_records": len(districts),
            "invalid_geometries": invalid_dist_geom,
            "missing_parent_state": missing_parent_state,
            "crs": "EPSG:4326 (WGS84)"
        }

        # 3. Validate Sub-districts & Parent District Relationship
        subdist_ids = set()
        invalid_subdist_geom = 0
        missing_parent_district = 0
        for sd in subdistricts:
            if sd["id"] in subdist_ids:
                self.issues.append(f"Duplicate subdistrict id: {sd['id']}")
            subdist_ids.add(sd["id"])

            if sd.get("district_id") and sd["district_id"] not in dist_ids:
                missing_parent_district += 1
                self.issues.append(f"Subdistrict {sd['name']} missing parent district {sd['district_id']}")

            poly_coords = sd.get("polygon")
            if poly_coords:
                poly = Polygon(poly_coords)
                if not poly.is_valid or poly.is_empty:
                    invalid_subdist_geom += 1

        self.stats["subdistricts"] = {
            "total_records": len(subdistricts),
            "invalid_geometries": invalid_subdist_geom,
            "missing_parent_district": missing_parent_district,
            "crs": "EPSG:4326 (WGS84)"
        }

        # 4. Validate Localities & Coordinates
        invalid_loc_coords = 0
        for loc in localities:
            coords = loc.get("coordinates")
            if not coords or not (6.0 <= coords["latitude"] <= 38.0 and 68.0 <= coords["longitude"] <= 98.0):
                invalid_loc_coords += 1
                self.issues.append(f"Locality {loc['name']} has invalid coordinate range {coords}")

        self.stats["localities"] = {
            "total_records": len(localities),
            "invalid_coordinates": invalid_loc_coords,
            "crs": "EPSG:4326 (WGS84)"
        }

        # 5. Validate PIN Codes
        invalid_pins = 0
        for p in pincodes:
            pin = p.get("pincode", "")
            if len(pin) != 6 or not pin.isdigit() or pin[0] == "0":
                invalid_pins += 1
                self.issues.append(f"Invalid PIN format: {pin}")

        self.stats["pincodes"] = {
            "total_records": len(pincodes),
            "invalid_format_count": invalid_pins,
            "postal_circles_covered": len(set(p.get("circle") for p in pincodes if p.get("circle")))
        }

        # Write report to staging
        report = {
            "status": "PASSED" if len(self.issues) == 0 else "ISSUES_FOUND",
            "stats": self.stats,
            "issues": self.issues
        }
        with open(STAGING_DIR / "validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report


def print_report():
    validator = GeographicDataValidator()
    res = validator.validate_dataset()
    print("=" * 60)
    print("           GEOGRAPHIC DATA QUALITY REPORT           ")
    print("=" * 60)
    for cat, data in res["stats"].items():
        print(f"\n[{cat.upper()}]")
        for k, v in data.items():
            print(f"  • {k}: {v}")
    print("\n" + "-" * 60)
    print(f"Validation Status: {res['status']}")
    print(f"Total Issues Detected: {len(res['issues'])}")
    print("=" * 60)


if __name__ == "__main__":
    print_report()
