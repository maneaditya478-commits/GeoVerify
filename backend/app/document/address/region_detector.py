"""Address region detector for isolating address blocks from document OCR results.

Detects address regions using:
1. Explicit header triggers (English, Hindi, Marathi).
2. Spatial clustering and density of address tokens / PIN patterns.
3. Keyword density markers (Taluka, Dist, Tehsil, Road, Flat, Nagar, etc.).
"""

import re
from typing import List, Optional, Tuple
from app.document.models import (
    OCRResult,
    OCRPage,
    OCRBlock,
    OCRLine,
    OCRWord,
    BoundingBox,
    AddressRegion,
    DocumentAddressType,
)

# Address header patterns in English, Hindi, Devanagari Marathi
ADDRESS_HEADER_PATTERNS = [
    # English
    r"(?i)\b(?:current|present|permanent|residence|residential|communication|office|registered|billing|shipping|delivery)?\s*(?:address|addr)\b[:\s\-\.]*",
    # Hindi / Marathi Devanagari
    r"(?:पत्ता|पता|कायमचा पत्ता|सध्याचा पत्ता|वर्तमान पता|स्थायी पता|घर का पता|रहिवासी पत्ता|निवासाचा पत्ता)\s*[:\s\-\.]*",
]

# Secondary keywords indicating address context
ADDRESS_KEYWORD_PATTERNS = [
    # English keywords
    r"\b(?:flat|room|plot|survey|s\.no|h\.no|house|bldg|building|apt|apartment|floor|wing|tower|block|sector|phase|pocket)\b",
    r"\b(?:road|rd|street|st|marg|cross|lane|avenue|ave|bypass|highway|chowk|circle|corner|opp|opposite|near|nr|behind|b/h|beside|next to|above)\b",
    r"\b(?:nagar|colony|layout|enclave|vihar|society|soc|heights|residency|park|wadi|basti|pada|puram|pura|gram|gaon|village)\b",
    r"\b(?:taluka|tal|tehsil|tahsil|mandal|dist|district|post|po|p\.o\.|pin|pincode|pin code)\b",
    r"\b(?:state|maharashtra|karnataka|delhi|uttar pradesh|tamil nadu|gujarat|rajasthan|madhya pradesh|kerala|andhra pradesh|telangana|west bengal|punjab|bihar|haryana)\b",
    # Devanagari keywords
    r"(?:फ्लॅट|प्लॉट|सर्व्हे|घर क्र|गट क्र|इमारत|मजला|विंग|रस्ता|मार्ग|चौक|जवळ|समोर|मागे|शेजारी|नगर|कॉलनी|सोसायटी|पार्क|वाडी|पाडा|गाव|ग्राम|तालुका|ता\.|जि\.|जिल्हा|पिन|पिनकोड|महाराष्ट्र|कर्नाटक|दिल्ली)",
]

PINCODE_REGEX = re.compile(r"\b[1-9][0-9]{2}\s?[0-9]{3}\b")


class AddressRegionDetector:
    """Detects and segments address candidate regions in OCR document pages."""

    def __init__(self):
        self.header_regexes = [re.compile(p, re.IGNORECASE) for p in ADDRESS_HEADER_PATTERNS]
        self.keyword_regexes = [re.compile(p, re.IGNORECASE) for p in ADDRESS_KEYWORD_PATTERNS]

    def detect_regions(self, ocr_result: OCRResult) -> List[AddressRegion]:
        """Detect all plausible address regions across all pages of an OCR result."""
        regions: List[AddressRegion] = []
        region_counter = 1

        for page in ocr_result.pages:
            # Step 1: Detect header-anchored address regions
            header_regions = self._detect_header_anchored_regions(page, region_counter)
            regions.extend(header_regions)
            region_counter += len(header_regions)

            # Step 2: Detect dense address clusters / blocks if no header regions or as additional candidates
            if not header_regions:
                cluster_regions = self._detect_spatial_cluster_regions(page, region_counter)
                regions.extend(cluster_regions)
                region_counter += len(cluster_regions)

        # Step 3: Fallback - if no specific address region was detected, only fallback if address tokens present
        if not regions:
            for page in ocr_result.pages:
                if page.text.strip() and self._compute_address_density_score(page.text) >= 1:
                    bbox = BoundingBox(x_min=0, y_min=0, x_max=page.width or 1000, y_max=page.height or 1000)
                    lines = [l.text for l in page.lines] if page.lines else page.text.splitlines()
                    regions.append(
                        AddressRegion(
                            region_id=f"region_{region_counter}",
                            address_type=DocumentAddressType.PRIMARY,
                            page_num=page.page_num,
                            bbox=bbox,
                            raw_lines=lines,
                            full_region_text=page.text.strip(),
                            header_keyword_detected="fallback",
                            confidence=0.5,
                        )
                    )
                    region_counter += 1

        return regions

    def _detect_header_anchored_regions(self, page: OCRPage, start_id: int) -> List[AddressRegion]:
        """Find lines that contain an address header keyword, and collect subsequent lines."""
        regions: List[AddressRegion] = []
        current_id = start_id

        # Scan blocks and lines
        for block_idx, block in enumerate(page.blocks):
            for line_idx, line in enumerate(block.lines):
                line_text = line.text.strip()
                address_type, matched_kw = self._classify_header(line_text)
                if address_type is not None:
                    # Found header in this line!
                    collected_lines: List[OCRLine] = []
                    
                    cleaned_header_line = self._strip_header(line_text)
                    if cleaned_header_line:
                        collected_lines.append(line)
                    
                    # Gather remaining lines in current block
                    for next_line in block.lines[line_idx + 1:]:
                        if self._is_non_address_section_header(next_line.text):
                            break
                        collected_lines.append(next_line)

                    # Also check if next adjacent block is immediately below and part of address
                    if block_idx + 1 < len(page.blocks):
                        next_block = page.blocks[block_idx + 1]
                        if self._is_continuation_block(block, next_block):
                            for next_line in next_block.lines:
                                if self._is_non_address_section_header(next_line.text):
                                    break
                                collected_lines.append(next_line)

                    if collected_lines:
                        line_texts = [l.text for l in collected_lines]
                        merged_text = "\n".join(line_texts).strip()
                        merged_bbox = self._merge_bounding_boxes([l.bbox for l in collected_lines if l.bbox])
                        avg_conf = sum(l.confidence for l in collected_lines) / len(collected_lines)

                        regions.append(
                            AddressRegion(
                                region_id=f"region_{current_id}",
                                address_type=address_type,
                                page_num=page.page_num,
                                bbox=merged_bbox,
                                raw_lines=line_texts,
                                full_region_text=merged_text,
                                header_keyword_detected=matched_kw,
                                confidence=min(1.0, avg_conf + 0.1),
                            )
                        )
                        current_id += 1

        return regions

    def _detect_spatial_cluster_regions(self, page: OCRPage, start_id: int) -> List[AddressRegion]:
        """Find blocks with high address keyword and PIN code density."""
        regions: List[AddressRegion] = []
        current_id = start_id

        for block in page.blocks:
            block_text = block.text.strip()
            if not block_text:
                continue

            score = self._compute_address_density_score(block_text)
            has_pin = bool(PINCODE_REGEX.search(block_text))

            if (score >= 2) or (has_pin and score >= 1):
                line_texts = [l.text for l in block.lines] if block.lines else block_text.splitlines()
                regions.append(
                    AddressRegion(
                        region_id=f"region_{current_id}",
                        address_type=DocumentAddressType.PRIMARY,
                        page_num=page.page_num,
                        bbox=block.bbox,
                        raw_lines=line_texts,
                        full_region_text=block_text,
                        header_keyword_detected=None,
                        confidence=block.confidence,
                    )
                )
                current_id += 1

        return regions

    def _classify_header(self, text: str) -> Tuple[Optional[DocumentAddressType], Optional[str]]:
        """Check if text contains an address header and classify its type."""
        for pattern in self.header_regexes:
            match = pattern.search(text)
            if match:
                matched_str = match.group(0).lower()
                kw = match.group(0).strip()
                if "perm" in matched_str or "कायम" in matched_str or "स्थायी" in matched_str:
                    return DocumentAddressType.PERMANENT, kw
                elif "curr" in matched_str or "pres" in matched_str or "सध्या" in matched_str or "वर्तमान" in matched_str:
                    return DocumentAddressType.CURRENT, kw
                elif "bill" in matched_str:
                    return DocumentAddressType.BILLING, kw
                elif "ship" in matched_str or "deliv" in matched_str:
                    return DocumentAddressType.SHIPPING, kw
                elif "off" in matched_str or "reg" in matched_str:
                    return DocumentAddressType.OFFICE, kw
                return DocumentAddressType.PRIMARY, kw
        return None, None

    def _strip_header(self, text: str) -> str:
        """Strip header labels like 'Address:' or 'पत्ता:' from the beginning of line text."""
        for pattern in self.header_regexes:
            text = pattern.sub("", text)
        return text.strip()

    def _is_non_address_section_header(self, text: str) -> bool:
        """Check if line starts a non-address section (e.g. 'Father's Name:', 'Date of Birth:')."""
        non_addr_patterns = [
            r"(?i)\b(?:father|mother|husband|guardian|dob|date of birth|gender|mobile|phone|email|pan|aadhaar|voter|signature|issued)\b[:\s]",
            r"(?:वडिलांचे नाव|जन्म तारीख|लिंग|मोबाईल|ईमेल|स्वाक्षरी)",
        ]
        return any(re.search(p, text) for p in non_addr_patterns)

    def _is_continuation_block(self, prev_block: OCRBlock, next_block: OCRBlock) -> bool:
        """Check if next_block is vertically proximate and aligned with prev_block."""
        if not prev_block.bbox or not next_block.bbox:
            return False
        gap = next_block.bbox.y_min - prev_block.bbox.y_max
        if 0 <= gap <= 40:
            x_overlap = min(prev_block.bbox.x_max, next_block.bbox.x_max) - max(prev_block.bbox.x_min, next_block.bbox.x_min)
            if x_overlap > 0:
                return True
        return False

    def _compute_address_density_score(self, text: str) -> int:
        """Count distinct address keyword matches in text."""
        score = 0
        for pattern in self.keyword_regexes:
            matches = pattern.findall(text)
            score += len(matches)
        if PINCODE_REGEX.search(text):
            score += 2
        return score

    def _merge_bounding_boxes(self, boxes: List[BoundingBox]) -> Optional[BoundingBox]:
        """Calculate the enclosing bounding box for a list of boxes."""
        valid_boxes = [b for b in boxes if b is not None]
        if not valid_boxes:
            return None
        return BoundingBox(
            x_min=min(b.x_min for b in valid_boxes),
            y_min=min(b.y_min for b in valid_boxes),
            x_max=max(b.x_max for b in valid_boxes),
            y_max=max(b.y_max for b in valid_boxes),
        )
