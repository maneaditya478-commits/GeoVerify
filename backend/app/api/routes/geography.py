"""Geographic directory search and inspection API routes."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from rapidfuzz import fuzz

router = APIRouter(prefix="/geography", tags=["Geographic Directory"])

DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed"


def _load_json(filename: str) -> List[Dict[str, Any]]:
    filepath = DATA_DIR / filename
    if filepath.exists():
        return json.loads(filepath.read_text(encoding="utf-8"))
    return []


@router.get("/states")
async def get_states():
    """Retrieve all 36 Indian States and Union Territories with official LGD codes and metadata."""
    states = _load_json("states.json")
    return [
        {
            "lgd_code": s.get("lgd_code"),
            "code": s["code"],
            "name": s["name"],
            "canonical_name": s["canonical_name"],
            "name_hi": s.get("name_hi"),
            "name_mr": s.get("name_mr"),
            "type": s.get("type", "State"),
            "capital": s.get("capital"),
            "bbox": s.get("bbox")
        }
        for s in states
    ]


@router.get("/districts")
async def get_districts(
    state_code: Optional[str] = Query(None, description="Filter by State code (e.g., 'MH', 'KA', 'DL')")
):
    """Retrieve Indian districts, optionally filtered by state code."""
    districts = _load_json("districts.json")
    if state_code:
        districts = [d for d in districts if d.get("state_code", "").lower() == state_code.lower()]
    return [
        {
            "id": d["id"],
            "lgd_code": d.get("lgd_code"),
            "name": d["name"],
            "canonical_name": d["canonical_name"],
            "name_hi": d.get("name_hi"),
            "name_mr": d.get("name_mr"),
            "state_code": d.get("state_code"),
            "state_name": d["state_name"],
            "headquarters": d.get("headquarters"),
            "bbox": d.get("bbox")
        }
        for d in districts
    ]


@router.get("/subdistricts")
async def get_subdistricts(
    district_id: Optional[str] = Query(None, description="Filter by District ID (e.g., 'dist_pune')")
):
    """Retrieve sub-districts / talukas / tehsils / mandals."""
    subdistricts = _load_json("subdistricts.json")
    if district_id:
        subdistricts = [sd for sd in subdistricts if sd.get("district_id", "").lower() == district_id.lower()]
    return subdistricts


@router.get("/search")
async def search_geography(
    q: str = Query(..., min_length=2, description="Search query string")
):
    """Search across states, districts, subdistricts, and localities in English or native script."""
    query = q.strip().lower()
    results = []

    states = _load_json("states.json")
    for s in states:
        names = [s["name"].lower(), s["canonical_name"].lower()]
        if s.get("name_hi"):
            names.append(s["name_hi"].lower())
        if s.get("name_mr"):
            names.append(s["name_mr"].lower())
        names.extend([a.lower() for a in s.get("aliases", [])])

        if any(query in n or fuzz.ratio(query, n) >= 80 for n in names):
            results.append({
                "type": "state",
                "name": s["name"],
                "canonical_name": s["canonical_name"],
                "code": s["code"],
                "capital": s.get("capital")
            })

    districts = _load_json("districts.json")
    for d in districts:
        names = [d["name"].lower(), d["canonical_name"].lower()]
        if d.get("name_hi"):
            names.append(d["name_hi"].lower())
        if d.get("name_mr"):
            names.append(d["name_mr"].lower())
        names.extend([a.lower() for a in d.get("aliases", [])])

        if any(query in n or fuzz.ratio(query, n) >= 80 for n in names):
            results.append({
                "type": "district",
                "name": d["name"],
                "canonical_name": d["canonical_name"],
                "state_name": d["state_name"],
                "state_code": d.get("state_code")
            })

    localities = _load_json("localities.json")
    for loc in localities:
        names = [loc["name"].lower(), loc.get("canonical_name", "").lower()]
        if loc.get("name_hi"):
            names.append(loc["name_hi"].lower())
        if loc.get("name_mr"):
            names.append(loc["name_mr"].lower())
        names.extend([a.lower() for a in loc.get("aliases", [])])

        if any(query in n or fuzz.ratio(query, n) >= 80 for n in names):
            results.append({
                "type": "locality",
                "name": loc["name"],
                "district": loc["district"],
                "state": loc["state"],
                "pincode": loc.get("pincode")
            })

    return {"query": q, "total_matches": len(results), "results": results}


@router.get("/pincode/{pincode}")
async def get_pincode_details(pincode: str):
    """Lookup authoritative PIN code details including circle, district, state, and centroid."""
    pincodes = _load_json("pincodes.json")
    for pin in pincodes:
        if pin.get("pincode") == pincode:
            return pin
    raise HTTPException(status_code=404, detail=f"PIN code {pincode} not found in directory")

