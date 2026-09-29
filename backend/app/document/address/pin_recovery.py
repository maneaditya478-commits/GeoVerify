"""PIN-First & Geographic Hierarchy Recovery for OCR Address candidates.

When OCR produces degraded locality or subdistrict tokens (e.g. 'Kharadl' instead of 'Kharadi'),
a valid 6-digit PIN code or District anchor restricts the search space so candidate resolution
can reliably recover the ground-truth geographic entity without hallucinatory drift.
"""

from typing import Dict, Any, Optional, List, Tuple
from rapidfuzz import fuzz

from app.document.models import ExtractedAddressCandidate, ExtractedAddressField
from app.entity_resolution.candidates import MultiStageCandidateGenerator
from app.services.pin_validator import PinValidator


class PINFirstRecoveryService:
    """Recovers corrupted address tokens using PIN code and geographic hierarchy constraints."""

    def __init__(self, candidate_generator: Optional[MultiStageCandidateGenerator] = None):
        self.candidate_generator = candidate_generator or MultiStageCandidateGenerator()
        self.pin_validator = PinValidator()

    def recover_candidate(self, candidate: ExtractedAddressCandidate) -> ExtractedAddressCandidate:
        """Attempt to enrich and recover missing or noisy fields using PIN index and entity lookups."""
        pincode_field = candidate.fields.get("pincode")
        pincode = pincode_field.normalized_value if pincode_field else None

        if not pincode or len(pincode) != 6:
            return candidate

        # Look up PIN metadata from PIN validator database
        pin_record = self.pin_validator.pincode_db.get(pincode)
        if not pin_record:
            return candidate

        recovered_any = False
        pin_state = pin_record.get("state")
        pin_dist = pin_record.get("district")
        pin_localities = pin_record.get("localities") or [pin_record.get("locality")] if pin_record.get("locality") else []

        # If state is missing, fill from PIN metadata
        if "state" not in candidate.fields and pin_state:
            candidate.fields["state"] = ExtractedAddressField(
                field_name="state",
                raw_value=pin_state,
                normalized_value=pin_state,
                confidence=0.92,
                page_num=candidate.page_num,
                bbox=candidate.region_bbox,
                source_text=f"PIN {pincode} postal mapping",
                correction_reason="PIN-first administrative inference",
            )
            candidate.structured_components["state"] = pin_state
            recovered_any = True

        # If district is missing, fill from PIN metadata
        if "district" not in candidate.fields and pin_dist:
            candidate.fields["district"] = ExtractedAddressField(
                field_name="district",
                raw_value=pin_dist,
                normalized_value=pin_dist,
                confidence=0.90,
                page_num=candidate.page_num,
                bbox=candidate.region_bbox,
                source_text=f"PIN {pincode} postal mapping",
                correction_reason="PIN-first administrative inference",
            )
            candidate.structured_components["district"] = pin_dist
            recovered_any = True

        # If locality is noisy or missing, check if any token in raw text matches PIN localities
        if pin_localities:
            raw_text = candidate.raw_address_text
            best_match_loc = None
            best_score = 0.0

            for ref_loc in pin_localities:
                if not ref_loc:
                    continue
                # Fuzzy partial token match
                score = fuzz.partial_ratio(ref_loc.lower(), raw_text.lower())
                if score > best_score:
                    best_score = score
                    best_match_loc = ref_loc

            if best_match_loc and best_score >= 70:
                current_loc_field = candidate.fields.get("locality")
                if not current_loc_field or current_loc_field.normalized_value != best_match_loc:
                    candidate.fields["locality"] = ExtractedAddressField(
                        field_name="locality",
                        raw_value=current_loc_field.raw_value if current_loc_field else best_match_loc,
                        normalized_value=best_match_loc,
                        confidence=round(best_score / 100.0, 2),
                        page_num=candidate.page_num,
                        bbox=candidate.region_bbox,
                        source_text=raw_text,
                        correction_reason=f"PIN {pincode} locality fuzzy match ({best_score:.0f}%)",
                    )
                    candidate.structured_components["locality"] = best_match_loc
                    recovered_any = True

        if recovered_any:
            candidate.pin_recovered = True
            parts = []
            for k in ["premise", "street", "locality", "subdistrict", "district", "state", "pincode"]:
                if k in candidate.fields and candidate.fields[k].normalized_value:
                    parts.append(candidate.fields[k].normalized_value)
            if parts:
                candidate.assembled_address = ", ".join(parts)

        return candidate
