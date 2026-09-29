"""Indic script transliteration and multilingual normalization service for Indian addresses."""

import re
from typing import Dict, List, Optional, Tuple

# Mapping of common Indic (Devanagari) terms to English Latin canonicals
INDIC_TO_LATIN_MAPPINGS: Dict[str, str] = {
    # States
    "महाराष्ट्र": "Maharashtra",
    "कर्नाटक": "Karnataka",
    "दिल्ली": "Delhi",
    "नवी दिल्ली": "New Delhi",
    "तमिळनाडू": "Tamil Nadu",
    "तमिलनाडु": "Tamil Nadu",
    "तेलंगणा": "Telangana",
    "तेलंगाना": "Telangana",
    "गुजरात": "Gujarat",
    "पश्चिम बंगाल": "West Bengal",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "राजस्थान": "Rajasthan",
    "केरळ": "Kerala",
    "केरल": "Kerala",
    "मध्य प्रदेश": "Madhya Pradesh",
    "आंध्र प्रदेश": "Andhra Pradesh",
    "पंजाब": "Punjab",
    "हरियाणा": "Haryana",
    "बिहार": "Bihar",
    "ओडिशा": "Odisha",
    "गोवा": "Goa",
    "आसाम": "Assam",
    "असम": "Assam",

    # Districts & Major Cities
    "नवी दिल्ली": "New Delhi",
    "नई दिल्ली": "New Delhi",
    "दिल्ली": "Delhi",
    "पुणे": "Pune",
    "पुना": "Pune",
    "मुंबई": "Mumbai Suburban",
    "मुंबई उपनगर": "Mumbai Suburban",
    "मुंबई शहर": "Mumbai City",
    "ठाणे": "Thane",
    "नागपूर": "Nagpur",
    "नागपुर": "Nagpur",
    "नाशिक": "Nashik",
    "नासिक": "Nashik",
    "कोल्हापूर": "Kolhapur",
    "कोल्हापुर": "Kolhapur",
    "छत्रपती संभाजीनगर": "Chhatrapati Sambhajinagar",
    "औरंगाबाद": "Chhatrapati Sambhajinagar",
    "सोलापूर": "Solapur",
    "सोलापुर": "Solapur",
    "बंगळुरू": "Bengaluru Urban",
    "बेंगलुरु": "Bengaluru Urban",
    "बंगलोर": "Bengaluru Urban",
    "चेन्नई": "Chennai",
    "मद्रास": "Chennai",
    "हैदराबाद": "Hyderabad",
    "कोलकाता": "Kolkata",
    "कलकत्ता": "Kolkata",
    "अहमदाबाद": "Ahmedabad",
    "सुरत": "Surat",
    "जयपूर": "Jaipur",
    "जयपुर": "Jaipur",
    "लखनौ": "Lucknow",
    "लखनऊ": "Lucknow",
    "पाटणा": "Patna",
    "पटना": "Patna",

    # Sub-districts / Talukas
    "हवेली": "Haveli",
    "मुळशी": "Mulshi",
    "मुळशि": "Mulshi",
    "मावळ": "Maval",
    "पुणे शहर": "Pune City",
    "खेड": "Khed",
    "शिरूर": "Shirur",
    "बारामती": "Baramati",
    "अंधेरी": "Andheri",
    "कुर्ला": "Kurla",
    "बोरिवली": "Borivali",
    "चाणक्यपुरी": "Chanakyapuri",
    "अलिपूर": "Alipore",

    # Localities
    "खराडी": "Kharadi",
    "विमान नगर": "Viman Nagar",
    "हिंजवडी": "Hinjewadi",
    "हिंजवाडी": "Hinjewadi",
    "कोथरूड": "Kothrud",
    "कोथरूड": "Kothrud",
    "बाणेर": "Baner",
    "हडपसर": "Hadapsar",
    "औंध": "Aundh",
    "वाकड": "Wakad",
    "बावधन": "Bavdhan",
    "मगरपट्टा": "Magarpatta",
    "कल्याणी नगर": "Kalyani Nagar",
    "कोरेगाव पार्क": "Koregaon Park",
    "व्हाईटफील्ड": "Whitefield",
    "इंदिरानगर": "Indiranagar",
    "कोरमंगला": "Koramangala",
    "कनॉट प्लेस": "Connaught Place",
    "हौज खास": "Hauz Khas",
    "साकेत": "Saket",
    "द्वारका": "Dwarka",
    "रोहिणी": "Rohini",
    "राजापूर": "Rajapur",
    "रामपूर": "Rampur",
    "रामपुर": "Rampur"
}

# Reverse mapping for Latin to Devanagari representation
LATIN_TO_INDIC_MAPPINGS: Dict[str, str] = {v: k for k, v in INDIC_TO_LATIN_MAPPINGS.items()}

# Common Indic address prefix patterns
INDIC_PREFIX_PATTERNS = {
    "locality": [
        r"(?:गाव|गाँव|ग्राम|वस्ती|मोहल्ला|परिसर|इलाका)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:area|locality|village)\s*[:\-]\s*([^,\n;]+)",
    ],
    "subdistrict": [
        r"(?:तालुका|तहसील|तहसिल|मंडळ)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:mandal|taluka|tehsil|subdivision)\s*[:\-]\s*([^,\n;]+)",
    ],
    "district": [
        r"(?:जिल्हा|जिला|शहर)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:district|dist|city)\s*[:\-]\s*([^,\n;]+)",
    ],
    "state": [
        r"(?:राज्य|प्रदेश)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:state|st)\s*[:\-]\s*([^,\n;]+)",
    ],
    "pincode": [
        r"(?:पिन\s*कोड|पिन|पिनकोड)\s*[:\-]?\s*([1-9][0-9]{5})",
        r"\b(?:pincode|pin|postal\s*code)\s*[:\-]?\s*([1-9][0-9]{5})",
    ],
    "landmark": [
        r"(?:जवळ|शेजारी|जवळपास|समोर|मागे)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:landmark|near|opp|behind|opposite)\s*[:\-]\s*([^,\n;]+)",
    ]
}


class TransliterationService:
    """Provides Indic script detection, transliteration, and semantic token normalization."""

    @staticmethod
    def detect_script(text: str) -> str:
        """Detect primary script (Devanagari, Latin, Mixed, or Unknown)."""
        if not text:
            return "Unknown"
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        has_latin = bool(re.search(r"[a-zA-Z]", text))

        if has_devanagari and has_latin:
            return "Mixed"
        elif has_devanagari:
            return "Devanagari"
        elif has_latin:
            return "Latin"
        return "Unknown"

    @staticmethod
    def transliterate_to_latin(text: str) -> Tuple[str, List[str]]:
        """
        Transliterates Devanagari words/phrases into canonical English equivalents.
        Returns: (transliterated_text, list_of_transformations)
        """
        if not text:
            return "", []

        transformations = []
        result = text

        # Sort keys by length descending to match multi-word phrases first (e.g., 'नवी दिल्ली' before 'दिल्ली')
        sorted_indic_keys = sorted(INDIC_TO_LATIN_MAPPINGS.keys(), key=lambda x: len(x), reverse=True)

        for indic_term in sorted_indic_keys:
            if indic_term in result:
                latin_canonical = INDIC_TO_LATIN_MAPPINGS[indic_term]
                result = re.sub(re.escape(indic_term), latin_canonical, result)
                transformations.append(f"Transliterated '{indic_term}' → '{latin_canonical}'")

        return result, transformations

    @classmethod
    def extract_indic_prefixed_fields(cls, text: str) -> Dict[str, str]:
        """
        Extracts address components marked with formal Indic or English prefixes
        (e.g., 'गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, राज्य: महाराष्ट्र, पिन: 411014').
        """
        extracted: Dict[str, str] = {}
        if not text:
            return extracted

        for field, patterns in INDIC_PREFIX_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    raw_val = match.group(1).strip()
                    # Clean punctuation
                    clean_val = re.sub(r"^[,\-:\s]+|[,\-:\s]+$", "", raw_val)
                    if clean_val and field not in extracted:
                        # Transliterate value to Latin if in Devanagari
                        latin_val, _ = cls.transliterate_to_latin(clean_val)
                        extracted[field] = latin_val.strip()

        return extracted


transliteration_service = TransliterationService()
