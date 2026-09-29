"""Address field extractor for segmented document address regions.

Extracts:
- PIN code (with character repair validation)
- State (with alias matching)
- District (with canonical resolution)
- Sub-District / Taluka / Tehsil (with prefix matching)
- Locality / Village (with landmark separation)
- Premise / Street / Road / Marg
- Landmark (near, opp, behind, etc.)
"""

import re
from typing import Dict, Optional, List, Tuple, Any
from app.document.models import (
    AddressRegion,
    ExtractedAddressField,
    BoundingBox,
    ExtractionMethod,
)
from app.services.address_parser import AddressParser
from app.services.normalizer import AddressNormalizer
from app.document.address.ocr_normalizer import OCRNormalizer


def _extract_str(val: Any) -> Optional[str]:
    """Extracts first element if val is a tuple, or string directly."""
    if val is None:
        return None
    if isinstance(val, tuple):
        return str(val[0]) if val[0] else None
    return str(val).strip()


class AddressFieldExtractor:
    """Extracts structured address fields from OCR address regions."""

    def __init__(self):
        self.ocr_normalizer = OCRNormalizer()
        self.address_parser = AddressParser()

    def extract_fields(self, region: AddressRegion) -> Dict[str, ExtractedAddressField]:
        """Extract structured address fields from an AddressRegion."""
        fields: Dict[str, ExtractedAddressField] = {}
        
        # 1. Normalize full region text
        raw_text = region.full_region_text
        normalized_text = self.ocr_normalizer.normalize_text(raw_text)

        # 2. Extract PIN code
        pincode_field = self._extract_pincode(normalized_text, raw_text, region.page_num, region.bbox)
        if pincode_field:
            fields["pincode"] = pincode_field

        # 3. Use parsed components from AddressParser
        parsed = self.address_parser.parse(normalized_text)

        state_val = getattr(parsed, "state", None)
        if state_val:
            norm_state = _extract_str(AddressNormalizer.normalize_state(state_val)) or state_val
            fields["state"] = ExtractedAddressField(
                field_name="state",
                raw_value=state_val,
                normalized_value=norm_state,
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        dist_val = getattr(parsed, "district", None) or getattr(parsed, "city", None)
        if dist_val:
            norm_dist = _extract_str(AddressNormalizer.normalize_district(dist_val)) or dist_val
            fields["district"] = ExtractedAddressField(
                field_name="district",
                raw_value=dist_val,
                normalized_value=norm_dist,
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        subdist_val = getattr(parsed, "subdistrict", None)
        if subdist_val:
            fields["subdistrict"] = ExtractedAddressField(
                field_name="subdistrict",
                raw_value=subdist_val,
                normalized_value=subdist_val.strip(),
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        loc_val = getattr(parsed, "locality", None)
        if loc_val:
            fields["locality"] = ExtractedAddressField(
                field_name="locality",
                raw_value=loc_val,
                normalized_value=loc_val.strip(),
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        premise_val = getattr(parsed, "premise", None)
        if premise_val:
            fields["premise"] = ExtractedAddressField(
                field_name="premise",
                raw_value=premise_val,
                normalized_value=premise_val.strip(),
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        landmarks_val = getattr(parsed, "landmarks", [])
        if landmarks_val:
            lm_str = ", ".join(landmarks_val)
            fields["landmark"] = ExtractedAddressField(
                field_name="landmark",
                raw_value=lm_str,
                normalized_value=lm_str.strip(),
                confidence=region.confidence,
                page_num=region.page_num,
                bbox=region.bbox,
                source_text=normalized_text,
            )

        return fields

    def _extract_pincode(
        self,
        normalized_text: str,
        raw_text: str,
        page_num: int,
        bbox: Optional[BoundingBox],
    ) -> Optional[ExtractedAddressField]:
        """Detect and validate 6-digit Indian PIN code."""
        pin_matches = re.findall(r"\b([1-9][0-9]{5})\b", normalized_text)
        if pin_matches:
            pin = pin_matches[-1]
            is_repaired = pin not in raw_text
            return ExtractedAddressField(
                field_name="pincode",
                raw_value=pin,
                normalized_value=pin,
                confidence=0.98 if not is_repaired else 0.88,
                extraction_method=ExtractionMethod.EXPLICIT if not is_repaired else ExtractionMethod.OCR_REPAIRED,
                page_num=page_num,
                bbox=bbox,
                source_text=raw_text,
                correction_reason=None if not is_repaired else "Repaired OCR character substitution in text",
            )

        pin_repaired = self.ocr_normalizer.repair_pincodes_in_text(raw_text)
        repaired_matches = re.findall(r"\b([1-9][0-9]{5})\b", pin_repaired)
        if repaired_matches:
            pin = repaired_matches[-1]
            return ExtractedAddressField(
                field_name="pincode",
                raw_value=pin,
                normalized_value=pin,
                confidence=0.85,
                extraction_method=ExtractionMethod.OCR_REPAIRED,
                page_num=page_num,
                bbox=bbox,
                source_text=raw_text,
                correction_reason="Repaired OCR digit substitution",
            )

        return None
