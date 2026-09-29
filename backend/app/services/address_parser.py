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

# Common road / street / highway indicators
ROAD_PATTERNS = [
    r"\b(?:road|rd\.?|marg|street|st\.?|highway|nh\s*\d*|expressway|ring\s*road|bypass|lane|gali|path|avenue|rasta|chowk)\b"
]

# Known localities for direct detection
KNOWN_LOCALITIES = [
    "Kharadi", "Viman Nagar", "Hinjewadi", "Hinjawadi", "Kothrud", "Baner", "Hadapsar",
    "Aundh", "Wakad", "Bavdhan", "Magarpatta", "Kalyani Nagar", "Koregaon Park",
    "Whitefield", "Indiranagar", "Koramangala", "HSR Layout", "Electronic City",
    "Bandra West", "Bandra East", "Andheri East", "Andheri West", "Powai", "Juhu",
    "Connaught Place", "Hauz Khas", "Saket", "Karol Bagh", "Dwarka", "Rohini", "Dilshad Garden",
    "Rajarhat", "Salt Lake", "New Town", "Rampur",
    "DLF Cyber City", "DLF Phase 3", "Jubilee Hills", "Anna Nagar", "Navrangpura", "Vaishali Nagar",
    "Gomti Nagar", "Sector 35B", "Sector 62", "Sector 132", "Vijay Nagar", "Naupada",
    "MP Nagar", "Sitabuldi", "Pandri", "Navi Peth", "Sanjay Place", "Samarth Nagar", "Hinoo",
    "Panampilly Nagar", "Kankarbagh", "Rajarampuri",
    "खराडी", "हिंजवडी", "कोथरूड", "बाणेर", "हडपसर", "राजारामपुरी", "नौपाडा"
]


# Known sub-districts / talukas for direct detection
KNOWN_SUBDISTRICTS = [
    "Haveli", "Mulshi", "Maval", "Pune City", "Khed", "Shirur", "Baramati",
    "Chanakyapuri", "Alipore", "Bengaluru South", "Bengaluru North", "Bengaluru East",
    "Andheri", "Kurla", "Borivali", "Thane", "Kalyan"
]


class AddressParser:
    """Parses free-form and prefix-labeled Indian address strings into structured administrative components."""

    @classmethod
    def parse(cls, raw_address: str) -> ParsedAddress:
        from app.services.transliteration import transliteration_service
        if not raw_address or not raw_address.strip():
            return ParsedAddress(parse_confidence=0.0)

        detected_script = transliteration_service.detect_script(raw_address)

        # 0. Check for explicit Indic/English field prefixes (e.g. 'गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे')
        prefixed = transliteration_service.extract_indic_prefixed_fields(raw_address)
        if len(prefixed) >= 2:
            norm_state, state_code, _ = AddressNormalizer.normalize_state(prefixed.get("state"))
            norm_dist, _ = AddressNormalizer.normalize_district(prefixed.get("district"))
            pincode = prefixed.get("pincode")
            locality = prefixed.get("locality")
            subdistrict = prefixed.get("subdistrict")
            landmarks = [prefixed["landmark"]] if "landmark" in prefixed else []

            conf = 0.0
            if norm_state: conf += 0.25
            if norm_dist: conf += 0.25
            if locality: conf += 0.25
            if pincode: conf += 0.25

            return ParsedAddress(
                premise=None,
                locality=locality.title() if locality else None,
                subdistrict=subdistrict.title() if subdistrict else None,
                city=norm_dist,
                district=norm_dist,
                state=norm_state,
                state_code=state_code,
                pincode=pincode,
                landmarks=landmarks,
                unparsed_tokens=[],
                detected_script=detected_script,
                parse_confidence=round(conf, 2)
            )

        # 1. Clean input text & transliterate Indic script to Latin
        cleaned_text, _ = AddressNormalizer.clean_text(raw_address)
        transliterated_text, _ = transliteration_service.transliterate_to_latin(cleaned_text)
        remaining_text = transliterated_text

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

        # 4. Extract District / City (sorted by alias length descending so "New Delhi" matches before "Delhi")
        district = None
        city = None
        sorted_district_aliases = sorted(DISTRICT_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, canonical in sorted_district_aliases:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, remaining_text, re.IGNORECASE):
                district = canonical
                city = canonical
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                break

        # 5. Extract State
        state = None
        state_code = None
        all_state_aliases = []
        for canonical, data in STATE_MAPPINGS.items():
            for alias in [canonical.lower()] + data["aliases"]:
                all_state_aliases.append((alias, canonical, data["code"]))
        all_state_aliases.sort(key=lambda x: len(x[0]), reverse=True)

        for alias, canonical, code in all_state_aliases:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, remaining_text, re.IGNORECASE):
                state = canonical
                state_code = code
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                break

        # If state is Delhi and district not found, set district to New Delhi (and vice-versa)
        if state == "Delhi" and not district:
            district = "New Delhi"
            city = "New Delhi"
        elif (district == "New Delhi" or city == "New Delhi") and not state:
            state = "Delhi"
            state_code = "DL"

        # 6. Extract Sub-District / Taluka
        subdistrict = None
        sorted_subdistricts = sorted(KNOWN_SUBDISTRICTS, key=lambda x: len(x), reverse=True)
        for sd in sorted_subdistricts:
            pattern = r"\b" + re.escape(sd) + r"\b"
            if re.search(pattern, remaining_text, re.IGNORECASE):
                subdistrict = sd
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                break

        # 7. Extract Locality
        locality = None
        sorted_known_localities = sorted(KNOWN_LOCALITIES, key=lambda x: len(x), reverse=True)
        for loc in sorted_known_localities:
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
            # Check if token looks like a premise or road
            is_premise = any(re.search(p, token, re.IGNORECASE) for p in PREMISE_PATTERNS)
            is_road = any(re.search(p, token, re.IGNORECASE) for p in ROAD_PATTERNS)
            if (is_premise or is_road) and not premise:
                premise = token
            elif not locality and len(token.split()) <= 3 and not is_premise and not is_road:
                locality = token.title()
            else:
                unparsed.append(token)

        # 8. Calculate parse confidence score
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
            subdistrict=subdistrict,
            city=city,
            district=district,
            state=state,
            state_code=state_code,
            pincode=pincode,
            landmarks=landmarks,
            unparsed_tokens=unparsed,
            detected_script=detected_script,
            parse_confidence=round(confidence, 2)
        )
