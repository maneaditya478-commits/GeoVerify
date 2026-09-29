"""Address assembler for transforming extracted regions and fields into verification-ready candidates."""

import uuid
from typing import List, Dict, Any, Optional

from app.document.models import (
    AddressRegion,
    ExtractedAddressField,
    ExtractedAddressCandidate,
    AddressExtractionStatus,
    DocumentAddressType,
)
from app.document.address.field_extractor import AddressFieldExtractor
from app.document.address.pin_recovery import PINFirstRecoveryService


class AddressCandidateAssembler:
    """Assembles segmented regions and extracted fields into standardized candidate address structures."""

    def __init__(self):
        self.field_extractor = AddressFieldExtractor()
        self.pin_recovery = PINFirstRecoveryService()

    def assemble_candidates(self, regions: List[AddressRegion]) -> List[ExtractedAddressCandidate]:
        """Convert a list of detected address regions into verified/structured address candidates."""
        candidates: List[ExtractedAddressCandidate] = []

        for idx, region in enumerate(regions):
            fields = self.field_extractor.extract_fields(region)
            
            # Form structured components dictionary
            structured_components: Dict[str, Optional[str]] = {
                "premise": fields["premise"].normalized_value if "premise" in fields else None,
                "street": fields["street"].normalized_value if "street" in fields else None,
                "locality": fields["locality"].normalized_value if "locality" in fields else None,
                "subdistrict": fields["subdistrict"].normalized_value if "subdistrict" in fields else None,
                "district": fields["district"].normalized_value if "district" in fields else None,
                "state": fields["state"].normalized_value if "state" in fields else None,
                "pincode": fields["pincode"].normalized_value if "pincode" in fields else None,
            }

            # Build assembled single-line string
            comp_vals = [v for v in structured_components.values() if v]
            assembled_str = ", ".join(comp_vals) if comp_vals else region.full_region_text

            # Compute overall extraction confidence
            field_confs = [f.confidence for f in fields.values()]
            mean_field_conf = sum(field_confs) / len(field_confs) if field_confs else region.confidence
            overall_conf = round(0.4 * region.confidence + 0.6 * mean_field_conf, 2)

            # Determine extraction status
            has_geo_anchor = bool(structured_components.get("locality") or structured_components.get("district") or structured_components.get("pincode"))
            if not fields:
                status = AddressExtractionStatus.FAILED
            elif has_geo_anchor:
                status = AddressExtractionStatus.EXTRACTED
            else:
                status = AddressExtractionStatus.PARTIALLY_EXTRACTED

            candidate = ExtractedAddressCandidate(
                candidate_id=f"addr_cand_{idx + 1}_{uuid.uuid4().hex[:6]}",
                address_type=region.address_type,
                raw_address_text=region.full_region_text,
                assembled_address=assembled_str,
                fields=fields,
                structured_components=structured_components,
                extraction_confidence=overall_conf,
                extraction_status=status,
                page_num=region.page_num,
                region_bbox=region.bbox,
                provenance={
                    "detection_method": region.region_id,
                    "header_detected": region.header_keyword_detected,
                    "region_confidence": region.confidence,
                },
                pin_recovered=False,
            )

            # Attempt PIN-First recovery
            candidate = self.pin_recovery.recover_candidate(candidate)
            candidates.append(candidate)

        return candidates
