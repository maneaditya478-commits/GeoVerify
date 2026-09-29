"""Address normalization pipeline for Indian addresses."""

import re
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
from app.schemas.address import NormalizedAddress, TransformationStep

# Canonical States & Union Territories mapping (Canonical -> [Aliases, Code])
STATE_MAPPINGS = {
    "Maharashtra": {
        "code": "MH",
        "aliases": ["maharashtra", "maharastra", "maharashthra", "mh", "maha", "maharashtra state", "महाराष्ट्र", "महा"]
    },
    "Karnataka": {
        "code": "KA",
        "aliases": ["karnataka", "karnatak", "ka", "mysore", "mysore state", "karnataka state", "कर्नाटक", "ಕರ್ನಾಟಕ"]
    },
    "Delhi": {
        "code": "DL",
        "aliases": ["delhi", "new delhi", "nct of delhi", "national capital territory of delhi", "dl", "dilli", "दिल्ली", "दिली"]
    },
    "Tamil Nadu": {
        "code": "TN",
        "aliases": ["tamil nadu", "tamilnadu", "tn", "madras state", "tamil nadu state", "तमिलनाडु", "தமிழ்நாடு"]
    },
    "Telangana": {
        "code": "TG",
        "aliases": ["telangana", "telengana", "tg", "ts", "तेलंगाना", "తెలంగాణ"]
    },
    "Gujarat": {
        "code": "GJ",
        "aliases": ["gujarat", "gujrat", "gj", "gujarat state", "गुजरात", "ગુજરાત"]
    },
    "West Bengal": {
        "code": "WB",
        "aliases": ["west bengal", "westbengal", "wb", "paschim banga", "bengal", "पश्चिम बंगाल", "পশ্চিমবঙ্গ"]
    },
    "Uttar Pradesh": {
        "code": "UP",
        "aliases": ["uttar pradesh", "uttarpradesh", "up", "u.p.", "उत्तर प्रदेश"]
    },
    "Rajasthan": {
        "code": "RJ",
        "aliases": ["rajasthan", "rajsthan", "rj", "rajputana", "राजस्थान"]
    },
    "Kerala": {
        "code": "KL",
        "aliases": ["kerala", "keralam", "kl", "केरल", "केरलम", "കേരളം"]
    },
    "Madhya Pradesh": {
        "code": "MP",
        "aliases": ["madhya pradesh", "mp", "m.p.", "मध्य प्रदेश"]
    },
    "Andhra Pradesh": {
        "code": "AP",
        "aliases": ["andhra pradesh", "ap", "a.p.", "आंध्र प्रदेश", "ఆంధ్ర ప్రదేశ్"]
    },
    "Punjab": {
        "code": "PB",
        "aliases": ["punjab", "pb", "पंजाब", "ਪੰਜਾਬ"]
    },
    "Haryana": {
        "code": "HR",
        "aliases": ["haryana", "hr", "हरियाणा"]
    },
    "Bihar": {
        "code": "BR",
        "aliases": ["bihar", "br", "बिहार"]
    },
    "Odisha": {
        "code": "OD",
        "aliases": ["odisha", "orissa", "od", "ओडिशा", "উড়িষ্যা", "ଓଡ଼ିଶା"]
    }
}

# City/District canonical normalization dictionary
DISTRICT_ALIASES = {
    "pune": "Pune",
    "poona": "Pune",
    "puna": "Pune",
    "mumbai": "Mumbai Suburban",
    "bombay": "Mumbai Suburban",
    "mumbai city": "Mumbai City",
    "mumbai suburban": "Mumbai Suburban",
    "bangalore": "Bengaluru Urban",
    "bengaluru": "Bengaluru Urban",
    "bangalore urban": "Bengaluru Urban",
    "blr": "Bengaluru Urban",
    "kolhapur": "Kolhapur",
    "nagpur": "Nagpur",
    "new delhi": "New Delhi",
    "delhi": "New Delhi",
    "chennai": "Chennai",
    "madras": "Chennai",
    "hyderabad": "Hyderabad",
    "secunderabad": "Hyderabad",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "ahmedabad": "Ahmedabad",
    "jaipur": "Jaipur",
    "lucknow": "Lucknow"
}

# Common Indian address abbreviations
ABBREVIATIONS = {
    r"\brd\b\.?": "Road",
    r"\bst\b\.?": "Street",
    r"\bapt\b\.?": "Apartment",
    r"\bflt\b\.?": "Flat",
    r"\bnrg\b\.?": "Nagar",
    r"\bmrg\b\.?": "Marg",
    r"\bchw\b\.?": "Chowk",
    r"\bopp\b\.?": "Opposite",
    r"\bnr\b\.?": "Near",
    r"\bbhd\b\.?": "Behind",
    r"\bsec\b\.?": "Sector",
    r"\bph\b\.?": "Phase",
    r"\bdist\b\.?": "District",
    r"\btal\b\.?": "Taluka",
    r"\bpo\b\.?": "Post Office",
    r"\bso\b\.?": "Sub Office",
    r"\bbo\b\.?": "Branch Office",
    r"\bho\b\.?": "Head Office",
    r"\bpin\b[:\s]*": "",
}


class AddressNormalizer:
    """Normalizes Indian address components with an audit trail of transformations."""

    @staticmethod
    def clean_text(raw_text: str) -> Tuple[str, List[TransformationStep]]:
        transformations = []
        if not raw_text:
            return "", transformations

        text = raw_text.strip()
        
        # 1. Normalize extra whitespace
        cleaned_whitespace = re.sub(r"\s+", " ", text)
        if cleaned_whitespace != text:
            transformations.append(TransformationStep(
                field="general",
                original_value=text,
                transformed_value=cleaned_whitespace,
                rule_applied="Collapsed redundant whitespace"
            ))
            text = cleaned_whitespace

        # 2. Expand common abbreviations
        for pattern, replacement in ABBREVIATIONS.items():
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                transformations.append(TransformationStep(
                    field="general",
                    original_value=text,
                    transformed_value=new_text,
                    rule_applied=f"Standardized abbreviation: {pattern} -> {replacement}"
                ))
                text = new_text

        # 3. Clean trailing / duplicate commas
        cleaned_commas = re.sub(r",\s*,+", ",", text)
        cleaned_commas = re.sub(r"^\s*,\s*|\s*,\s*$", "", cleaned_commas).strip()
        if cleaned_commas != text:
            transformations.append(TransformationStep(
                field="punctuation",
                original_value=text,
                transformed_value=cleaned_commas,
                rule_applied="Cleaned repeated / trailing commas"
            ))
            text = cleaned_commas

        return text, transformations

    @classmethod
    def normalize_state(cls, raw_state: Optional[str]) -> Tuple[Optional[str], Optional[str], List[TransformationStep]]:
        """Normalize Indian State name and return (Canonical Name, State Code, Transformations)."""
        transformations = []
        if not raw_state:
            return None, None, transformations

        cleaned = raw_state.strip()
        lowered = cleaned.lower()

        # Direct match or alias lookup
        for canonical, data in STATE_MAPPINGS.items():
            if lowered in data["aliases"] or lowered == canonical.lower():
                if cleaned != canonical:
                    transformations.append(TransformationStep(
                        field="state",
                        original_value=raw_state,
                        transformed_value=canonical,
                        rule_applied="Mapped state name / alias to canonical standard"
                    ))
                return canonical, data["code"], transformations

        # Fuzzy match for typos (e.g. "Maharastra" -> "Maharashtra")
        all_aliases = []
        alias_to_canonical = {}
        for canonical, data in STATE_MAPPINGS.items():
            for alias in data["aliases"] + [canonical.lower()]:
                all_aliases.append(alias)
                alias_to_canonical[alias] = (canonical, data["code"])

        match = process.extractOne(lowered, all_aliases, scorer=fuzz.ratio)
        if match and match[1] >= 80:
            canonical, code = alias_to_canonical[match[0]]
            transformations.append(TransformationStep(
                field="state",
                original_value=raw_state,
                transformed_value=canonical,
                rule_applied=f"Fuzzy matched state name '{raw_state}' -> '{canonical}' (similarity {match[1]}%)"
            ))
            return canonical, code, transformations

        return raw_state.strip().title(), None, transformations

    @classmethod
    def normalize_district(cls, raw_district: Optional[str]) -> Tuple[Optional[str], List[TransformationStep]]:
        """Normalize district name to canonical spelling."""
        transformations = []
        if not raw_district:
            return None, transformations

        cleaned = raw_district.strip()
        lowered = cleaned.lower()

        # Check direct lookup table
        if lowered in DISTRICT_ALIASES:
            canonical = DISTRICT_ALIASES[lowered]
            if cleaned != canonical:
                transformations.append(TransformationStep(
                    field="district",
                    original_value=raw_district,
                    transformed_value=canonical,
                    rule_applied="Standardized district name from alias dictionary"
                ))
            return canonical, transformations

        # Fuzzy match across known district aliases
        match = process.extractOne(lowered, list(DISTRICT_ALIASES.keys()), scorer=fuzz.ratio)
        if match and match[1] >= 82:
            canonical = DISTRICT_ALIASES[match[0]]
            transformations.append(TransformationStep(
                field="district",
                original_value=raw_district,
                transformed_value=canonical,
                rule_applied=f"Fuzzy matched district '{raw_district}' -> '{canonical}' (score {match[1]}%)"
            ))
            return canonical, transformations

        return cleaned.title(), transformations

    @classmethod
    def normalize_pincode(cls, raw_pincode: Optional[str]) -> Tuple[Optional[str], List[TransformationStep]]:
        """Extract and format 6-digit Indian PIN code."""
        transformations = []
        if not raw_pincode:
            return None, transformations

        # Remove spaces, hyphens, prefixes
        cleaned = re.sub(r"[^\d]", "", raw_pincode)
        if len(cleaned) == 6 and cleaned[0] in "123456789":
            if raw_pincode != cleaned:
                transformations.append(TransformationStep(
                    field="pincode",
                    original_value=raw_pincode,
                    transformed_value=cleaned,
                    rule_applied="Cleaned 6-digit PIN code format"
                ))
            return cleaned, transformations

        return None, transformations

    @classmethod
    def normalize_address(
        cls,
        address_text: Optional[str] = None,
        locality: Optional[str] = None,
        subdistrict: Optional[str] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> NormalizedAddress:
        """Full normalization pipeline across all fields."""
        all_transformations: List[TransformationStep] = []
        original_input = address_text or f"{locality or ''} {city or ''} {district or ''} {state or ''} {pincode or ''}".strip()

        # 1. Clean full text
        normalized_text, text_transformations = cls.clean_text(original_input)
        all_transformations.extend(text_transformations)

        # 2. Extract PIN code from text if not provided
        if not pincode and normalized_text:
            pin_match = re.search(r"\b([1-9][0-9]{5})\b", normalized_text)
            if pin_match:
                pincode = pin_match.group(1)

        norm_pincode, pin_trans = cls.normalize_pincode(pincode)
        all_transformations.extend(pin_trans)

        # 3. State normalization
        norm_state, state_code, state_trans = cls.normalize_state(state)
        all_transformations.extend(state_trans)

        # 4. District normalization
        norm_district, dist_trans = cls.normalize_district(district or city)
        all_transformations.extend(dist_trans)

        # 5. Locality normalization
        norm_locality = locality.strip().title() if locality else None

        return NormalizedAddress(
            original_input=original_input,
            normalized_text=normalized_text,
            locality=norm_locality,
            subdistrict=subdistrict.strip().title() if subdistrict else None,
            city=city.strip().title() if city else (norm_district if norm_district else None),
            district=norm_district,
            state=norm_state,
            state_code=state_code,
            pincode=norm_pincode,
            transformations=all_transformations
        )
