"""Structured rule-and-dictionary based address parser for Indian addresses."""

import re
from typing import Optional, List, Dict, Any, Tuple
from rapidfuzz import fuzz, process
from app.schemas.address import ParsedAddress
from app.services.normalizer import STATE_MAPPINGS, DISTRICT_ALIASES, AddressNormalizer

# Common Indian landmark indicator prefixes
LANDMARK_PREFIXES = [
    r"\bnear\s+([^,]+)",
    r"\bopposite\s+([^,]+)",
    r"\bopp\.\s*([^,]+)",
    r"\bbehind\s+([^,]+)",
    r"\bbeside\s+([^,]+)",
    r"\bnext\s+to\s+([^,]+)",
    r"\badjacent\s+to\s+([^,]+)",
]

# Common premise / flat / building regex patterns
PREMISE_PATTERNS = [
    r"(flat\s*(?:no\.?|#)?\s*[0-9a-zA-Z\-/]+)",
    r"(shop\s*(?:no\.?|#)?\s*[0-9a-zA-Z\-/]+)",
    r"(plot\s*(?:no\.?|#)?\s*[0-9a-zA-Z\-/]+)",
    r"(house\s*(?:no\.?|#)?\s*[0-9a-zA-Z\-/]+)",
    r"(building\s*(?:no\.?|#)?\s*[0-9a-zA-Z\-/]+)",
    r"(tower\s*[0-9a-zA-Z\-/]+)",
    r"(sector\s*[0-9a-zA-Z\-/]+)",
    r"(\b[0-9]{1,4}[a-zA-Z]?(?:/[0-9]{1,4})?\b)"
]

# Known localities for direct detection
KNOWN_LOCALITIES = [
    "Kharadi", "Viman Nagar", "Hinjewadi", "Hinjawadi", "Kothrud", "Baner", "Hadapsar",
    "Aundh", "Wakad", "Bavdhan", "Magarpatta", "Kalyani Nagar", "Koregaon Park",
    "Whitefield", "Indiranagar", "Koramangala", "HSR Layout", "Electronic City",
    "Bandra West", "Bandra East", "Andheri East", "Andheri West", "Powai", "Juhu",
    "Connaught Place", "Hauz Khas", "Saket", "Karol Bagh", "Dwarka", "Rohini",
    "Rajarhat", "Salt Lake", "New Town", "Rampur"
]


class AddressParser:
    """Parses free-form Indian address strings into structured administrative components."""

    @classmethod
    def parse(cls, raw_address: str) -> ParsedAddress:
        if not raw_address or not raw_address.strip():
            return ParsedAddress(parse_confidence=0.0)

        # 1. Clean input text
        cleaned_text, _ = AddressNormalizer.clean_text(raw_address)
        remaining_text = cleaned_text

        # 2. Extract PIN code
        pincode = None
        pin_match = re.search(r"\b([1-9][0-9]{5})\b", remaining_text)
        if pin_match:
            pincode = pin_match.group(1)
            remaining_text = re.sub(r"\b" + pincode + r"\b", "", remaining_text).strip()

        # 3. Extract Landmarks
        landmarks = []
        for l_prefix in LANDMARK_PREFIXES:
            for match in re.finditer(l_prefix, remaining_text, re.IGNORECASE):
                landmark_text = match.group(0).strip()
                landmarks.append(landmark_text)
                remaining_text = remaining_text.replace(landmark_text, " ").strip()

        # 4. Extract State
        state = None
        state_code = None
        # Check by reverse scanning tokens or alias matches
        for canonical, data in STATE_MAPPINGS.items():
            for alias in [canonical.lower()] + data["aliases"]:
                pattern = r"\b" + re.escape(alias) + r"\b"
                if re.search(pattern, remaining_text, re.IGNORECASE):
                    state = canonical
                    state_code = data["code"]
                    remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                    break
            if state:
                break

        # 5. Extract District / City
        district = None
        city = None
        for alias, canonical in DISTRICT_ALIASES.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, remaining_text, re.IGNORECASE):
                district = canonical
                city = canonical
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                break

        # 6. Extract Locality
        locality = None
        # Check against known localities
        for loc in KNOWN_LOCALITIES:
            pattern = r"\b" + re.escape(loc) + r"\b"
            if re.search(pattern, remaining_text, re.IGNORECASE):
                locality = loc
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                break

        # If locality not found by exact catalog, split remaining comma-separated or space tokens
        tokens = [t.strip() for t in re.split(r"[,;]+", remaining_text) if t.strip()]
        premise = None
        unparsed = []

        for token in tokens:
            # Check if token looks like a premise
            is_premise = any(re.search(p, token, re.IGNORECASE) for p in PREMISE_PATTERNS)
            if is_premise and not premise:
                premise = token
            elif not locality and len(token.split()) <= 3 and not is_premise:
                locality = token.title()
            else:
                unparsed.append(token)

        # 7. Calculate parse confidence score
        confidence = 0.0
        if state:
            confidence += 0.25
        if district or city:
            confidence += 0.25
        if locality:
            confidence += 0.25
        if pincode:
            confidence += 0.25

        return ParsedAddress(
            premise=premise,
            locality=locality,
            subdistrict=None,
            city=city,
            district=district,
            state=state,
            state_code=state_code,
            pincode=pincode,
            landmarks=landmarks,
            unparsed_tokens=unparsed,
            parse_confidence=round(confidence, 2)
        )
