"""Administrative hierarchy validation for Indian administrative levels."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from app.schemas.hierarchy import AdministrativeHierarchyResult, HierarchyNode


class HierarchyValidator:
    """Validates child-parent relationships in Indian administrative structure."""

    def __init__(self):
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
        self.states = []
        self.districts = []
        self.localities = []

        if (data_dir / "states.json").exists():
            with open(data_dir / "states.json", "r", encoding="utf-8") as f:
                self.states = json.load(f)

        if (data_dir / "districts.json").exists():
            with open(data_dir / "districts.json", "r", encoding="utf-8") as f:
                self.districts = json.load(f)

        if (data_dir / "localities.json").exists():
            with open(data_dir / "localities.json", "r", encoding="utf-8") as f:
                self.localities = json.load(f)

    def validate_hierarchy(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        subdistrict: Optional[str] = None,
        locality: Optional[str] = None
    ) -> AdministrativeHierarchyResult:
        mismatches: List[str] = []
        chain: List[HierarchyNode] = [
            HierarchyNode(level="country", name="India", canonical_name="India", matched=True, evidence="Sovereign nation")
        ]

        state_matched = False
        matched_state_name = None
        matched_state_code = None

        # 1. State Validation
        if state:
            for s in self.states:
                if s["canonical_name"].lower() == state.lower() or state.lower() in [a.lower() for a in s.get("aliases", [])]:
                    state_matched = True
                    matched_state_name = s["canonical_name"]
                    matched_state_code = s["code"]
                    chain.append(HierarchyNode(
                        level="state",
                        name=state,
                        canonical_name=matched_state_name,
                        level_code=matched_state_code,
                        matched=True,
                        evidence=f"Recognized Indian State ({matched_state_code})"
                    ))
                    break

            if not state_matched:
                chain.append(HierarchyNode(
                    level="state",
                    name=state,
                    canonical_name=None,
                    matched=False,
                    evidence=f"State '{state}' not recognized in standard Indian state registry"
                ))
                mismatches.append(f"Unrecognized state '{state}'.")

        # 2. District Validation & Parent State Consistency
        district_matched = False
        matched_dist_obj = None

        if district:
            for d in self.districts:
                if d["canonical_name"].lower() == district.lower() or district.lower() in [a.lower() for a in d.get("aliases", [])]:
                    district_matched = True
                    matched_dist_obj = d
                    # Check if district belongs to the asserted state
                    if matched_state_name and d["state_name"].lower() != matched_state_name.lower():
                        chain.append(HierarchyNode(
                            level="district",
                            name=district,
                            canonical_name=d["canonical_name"],
                            matched=False,
                            evidence=f"District '{d['canonical_name']}' belongs to '{d['state_name']}', not '{matched_state_name}'"
                        ))
                        mismatches.append(f"District '{district}' belongs to {d['state_name']}, but state was given as {matched_state_name}.")
                    else:
                        chain.append(HierarchyNode(
                            level="district",
                            name=district,
                            canonical_name=d["canonical_name"],
                            matched=True,
                            evidence=f"District verified under state '{d['state_name']}'"
                        ))
                    break

            if not district_matched:
                chain.append(HierarchyNode(
                    level="district",
                    name=district,
                    canonical_name=None,
                    matched=False,
                    evidence=f"District '{district}' not found in administrative records"
                ))
                mismatches.append(f"District '{district}' could not be validated.")

        # 3. Locality Validation & Parent District Consistency
        if locality:
            loc_found = None
            for loc in self.localities:
                if loc["name"].lower() == locality.lower() or locality.lower() in [a.lower() for a in loc.get("aliases", [])]:
                    loc_found = loc
                    break

            if loc_found:
                # Check district consistency
                if district and loc_found["district"].lower() != district.lower():
                    chain.append(HierarchyNode(
                        level="locality",
                        name=locality,
                        canonical_name=loc_found["name"],
                        matched=False,
                        evidence=f"Locality '{loc_found['name']}' is situated in district '{loc_found['district']}', but '{district}' was supplied"
                    ))
                    mismatches.append(f"Locality '{locality}' belongs to district '{loc_found['district']}', not '{district}'.")
                else:
                    chain.append(HierarchyNode(
                        level="locality",
                        name=locality,
                        canonical_name=loc_found["name"],
                        matched=True,
                        evidence=f"Locality situated in {loc_found.get('subdistrict', 'subdistrict')}, {loc_found['district']}, {loc_found['state']}"
                    ))
            else:
                chain.append(HierarchyNode(
                    level="locality",
                    name=locality,
                    canonical_name=None,
                    matched=True,  # Locality can be custom/granular
                    evidence="Granular locality / neighborhood"
                ))

        is_consistent = len(mismatches) == 0

        return AdministrativeHierarchyResult(
            country="India",
            state=matched_state_name or state,
            state_code=matched_state_code,
            district=matched_dist_obj["canonical_name"] if matched_dist_obj else district,
            subdistrict=subdistrict,
            locality=locality,
            is_consistent=is_consistent,
            hierarchy_chain=chain,
            mismatch_details=mismatches
        )


hierarchy_validator = HierarchyValidator()
