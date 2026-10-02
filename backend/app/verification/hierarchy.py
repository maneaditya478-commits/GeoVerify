"""Administrative hierarchy validation for Indian administrative levels with sub-districts and multilingual names."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.schemas.hierarchy import AdministrativeHierarchyResult, HierarchyNode


class HierarchyValidator:
    """Validates child-parent relationships in Indian administrative structure."""

    def __init__(self):
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
        self.states = []
        self.districts = []
        self.subdistricts = []
        self.localities = []

        if (data_dir / "states.json").exists():
            with open(data_dir / "states.json", "r", encoding="utf-8") as f:
                self.states = json.load(f)

        if (data_dir / "districts.json").exists():
            with open(data_dir / "districts.json", "r", encoding="utf-8") as f:
                self.districts = json.load(f)

        if (data_dir / "subdistricts.json").exists():
            with open(data_dir / "subdistricts.json", "r", encoding="utf-8") as f:
                self.subdistricts = json.load(f)

        if (data_dir / "localities.json").exists():
            with open(data_dir / "localities.json", "r", encoding="utf-8") as f:
                self.localities = json.load(f)

        self._build_indices()

    def _build_indices(self):
        """Builds in-memory dictionary indexes for O(1) state, district, and subdistrict resolution."""
        self._state_index: Dict[str, dict] = {}
        for s in self.states:
            for key in [s["name"].lower(), s["canonical_name"].lower(), s["code"].lower()]:
                self._state_index[key] = s
            if s.get("name_hi"):
                self._state_index[s["name_hi"].lower()] = s
            if s.get("name_mr"):
                self._state_index[s["name_mr"].lower()] = s
            for a in s.get("aliases", []):
                self._state_index[a.lower()] = s

        self._district_index: Dict[str, dict] = {}
        for d in self.districts:
            for key in [d["name"].lower(), d["canonical_name"].lower()]:
                self._district_index[key] = d
            if d.get("name_hi"):
                self._district_index[d["name_hi"].lower()] = d
            if d.get("name_mr"):
                self._district_index[d["name_mr"].lower()] = d
            for a in d.get("aliases", []):
                self._district_index[a.lower()] = d

        self._subdistrict_index: Dict[str, dict] = {}
        for sd in self.subdistricts:
            for key in [sd["name"].lower(), sd["canonical_name"].lower()]:
                self._subdistrict_index[key] = sd

    def _match_state_entity(self, name_to_check: str) -> Optional[dict]:
        """Match state by canonical name, code, multilingual names, or aliases."""
        target = name_to_check.strip().lower()
        if target in self._state_index:
            return self._state_index[target]
        for k, v in self._state_index.items():
            if target in k or k in target:
                return v
        return None

    def _match_district_entity(self, name_to_check: str) -> Optional[dict]:
        """Match district by canonical name, multilingual names, or aliases."""
        target = name_to_check.strip().lower()
        if target in self._district_index:
            return self._district_index[target]
        for k, v in self._district_index.items():
            if target in k or k in target:
                return v
        return None

    def _match_subdistrict_entity(self, name_to_check: str) -> Optional[dict]:
        """Match subdistrict by canonical name or aliases."""
        target = name_to_check.strip().lower()
        if target in self._subdistrict_index:
            return self._subdistrict_index[target]
        for k, v in self._subdistrict_index.items():
            if target in k or k in target:
                return v
        return None

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

        matched_state_obj = None
        matched_state_name = None
        matched_state_code = None

        # 1. State Validation
        if state:
            matched_state_obj = self._match_state_entity(state)
            if matched_state_obj:
                matched_state_name = matched_state_obj["canonical_name"]
                matched_state_code = matched_state_obj["code"]
                chain.append(HierarchyNode(
                    level="state",
                    name=state,
                    canonical_name=matched_state_name,
                    level_code=matched_state_code,
                    matched=True,
                    evidence=f"Recognized Indian {matched_state_obj.get('type', 'State')} ({matched_state_code})"
                ))
            else:
                chain.append(HierarchyNode(
                    level="state",
                    name=state,
                    canonical_name=None,
                    matched=False,
                    evidence=f"State '{state}' not recognized in official LGD registry"
                ))
                mismatches.append(f"Unrecognized state '{state}'.")

        # 2. District Validation & Parent State Consistency
        matched_dist_obj = None
        if district:
            matched_dist_obj = self._match_district_entity(district)
            if matched_dist_obj:
                if matched_state_name and matched_dist_obj["state_name"].lower() != matched_state_name.lower():
                    chain.append(HierarchyNode(
                        level="district",
                        name=district,
                        canonical_name=matched_dist_obj["canonical_name"],
                        matched=False,
                        evidence=f"District '{matched_dist_obj['canonical_name']}' belongs to '{matched_dist_obj['state_name']}', not '{matched_state_name}'"
                    ))
                    mismatches.append(f"District '{district}' belongs to {matched_dist_obj['state_name']}, but state was given as {matched_state_name}.")
                else:
                    chain.append(HierarchyNode(
                        level="district",
                        name=district,
                        canonical_name=matched_dist_obj["canonical_name"],
                        matched=True,
                        evidence=f"District verified under state '{matched_dist_obj['state_name']}'"
                    ))
            else:
                chain.append(HierarchyNode(
                    level="district",
                    name=district,
                    canonical_name=None,
                    matched=False,
                    evidence=f"District '{district}' not found in administrative records"
                ))
                mismatches.append(f"District '{district}' could not be validated.")

        # 3. Sub-District / Taluka / Tehsil Validation
        if subdistrict:
            matched_subdist_obj = self._match_subdistrict_entity(subdistrict)
            if matched_subdist_obj:
                admin_type = matched_subdist_obj.get("admin_type", "Taluka")
                if matched_dist_obj and matched_subdist_obj["district_name"].lower() != matched_dist_obj["canonical_name"].lower():
                    chain.append(HierarchyNode(
                        level="subdistrict",
                        name=subdistrict,
                        canonical_name=matched_subdist_obj["canonical_name"],
                        matched=False,
                        evidence=f"{admin_type} '{matched_subdist_obj['canonical_name']}' belongs to district '{matched_subdist_obj['district_name']}', not '{matched_dist_obj['canonical_name']}'"
                    ))
                    mismatches.append(f"{admin_type} '{subdistrict}' belongs to district '{matched_subdist_obj['district_name']}'.")
                else:
                    chain.append(HierarchyNode(
                        level="subdistrict",
                        name=subdistrict,
                        canonical_name=matched_subdist_obj["canonical_name"],
                        matched=True,
                        evidence=f"{admin_type} verified under district '{matched_subdist_obj['district_name']}'"
                    ))
            else:
                chain.append(HierarchyNode(
                    level="subdistrict",
                    name=subdistrict,
                    canonical_name=None,
                    matched=True,
                    evidence="Sub-district entity provided"
                ))

        # 4. Locality Validation & Parent District Consistency
        if locality:
            loc_found = None
            loc_target = locality.strip().lower()
            for loc in self.localities:
                names = [loc["name"].lower(), loc.get("canonical_name", "").lower()]
                if loc.get("name_hi"):
                    names.append(loc["name_hi"].lower())
                if loc.get("name_mr"):
                    names.append(loc["name_mr"].lower())
                names.extend([a.lower() for a in loc.get("aliases", [])])

                if loc_target in names:
                    loc_found = loc
                    break

            if loc_found:
                eff_district = matched_dist_obj["canonical_name"].lower() if matched_dist_obj else (district.strip().lower() if district else "")
                if eff_district and loc_found["district"].lower() != eff_district and loc_found["district"].lower() not in eff_district:
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
                        evidence=f"Locality situated in {loc_found.get('subdistrict', 'subdistrict')}, {loc_found.get('district', '')}, {loc_found.get('state_name', loc_found.get('state', ''))}"
                    ))
            else:
                chain.append(HierarchyNode(
                    level="locality",
                    name=locality,
                    canonical_name=None,
                    matched=True,
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
