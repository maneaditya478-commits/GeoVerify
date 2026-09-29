"""Indic script transliteration, phonetic expansion, and multilingual normalization service."""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from app.services.phonetic import phonetic_service

# Comprehensive Mapping of Indic (Devanagari) terms to English Latin canonicals
INDIC_TO_LATIN_MAPPINGS: Dict[str, str] = {
    # States
    "महाराष्ट्र": "Maharashtra",
    "कर्नाटक": "Karnataka",
    "दिल्ली": "Delhi",
    "नवी दिल्ली": "New Delhi",
    "नई दिल्ली": "New Delhi",
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
    "हिमाचल प्रदेश": "Himachal Pradesh",
    "उत्तराखंड": "Uttarakhand",
    "झारखंड": "Jharkhand",
    "छत्तीसगढ़": "Chhattisgarh",
    "छत्तीसगड": "Chhattisgarh",

    # Districts & Major Cities
    "पुणे": "Pune",
    "पुना": "Pune",
    "मुंबई": "Mumbai",
    "मुंबई उपनगर": "Mumbai Suburban",
    "मुंबई शहर": "Mumbai City",
    "ठाणे": "Thane",
    "कोल्हापूर": "Kolhapur",
    "कोल्हापुर": "Kolhapur",
    "नागपूर": "Nagpur",
    "नागपुर": "Nagpur",
    "नाशिक": "Nashik",
    "नासिक": "Nashik",
    "छत्रपती संभाजीनगर": "Aurangabad",
    "औरंगाबाद": "Aurangabad",
    "सोलापूर": "Solapur",
    "सोलापुर": "Solapur",
    "अहमदनगर": "Ahmednagar",
    "अहिल्यानगर": "Ahmednagar",
    "बंगळुरू": "Bengaluru Urban",
    "बेंगलुरु": "Bengaluru Urban",
    "बंगलोर": "Bengaluru Urban",
    "म्हैसूर": "Mysuru",
    "मैसूर": "Mysuru",
    "चेन्नई": "Chennai",
    "मद्रास": "Chennai",
    "हैदराबाद": "Hyderabad",
    "कोलकाता": "Kolkata",
    "कलकत्ता": "Kolkata",
    "उत्तर २४ परगना": "North 24 Parganas",
    "उत्तर 24 परगना": "North 24 Parganas",
    "अहमदाबाद": "Ahmedabad",
    "सुरत": "Surat",
    "सूरत": "Surat",
    "जयपूर": "Jaipur",
    "जयपुर": "Jaipur",
    "गौतम बुद्ध नगर": "Gautam Buddha Nagar",
    "नोएडा": "Gautam Buddha Nagar",
    "लखनौ": "Lucknow",
    "लखनऊ": "Lucknow",
    "बिलासपुर": "Bilaspur",
    "बिलासपूर": "Bilaspur",
    "रामपुर": "Rampur",
    "रामपूर": "Rampur",
    "शिमला": "Shimla",
    "वाराणसी": "Varanasi",
    "इंदौर": "Indore",
    "इन्दौर": "Indore",
    "पटना": "Patna",
    "रायपुर": "Raipur",
    "आगरा": "Agra",
    "रांची": "Ranchi",
    "राँची": "Ranchi",
    "भोपाल": "Bhopal",
    "गुरुग्राम": "Gurugram",
    "गुड़गांव": "Gurugram",
    "गुड़गांव": "Gurugram",
    "एर्नाकुलम": "Ernakulam",
    "कोच्चि": "Ernakulam",

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
    "करवीर": "Karvir",
    "बंगळुरू पूर्व": "Bengaluru East",
    "बंगळुरू दक्षिण": "Bengaluru South",
    "चाणक्यपुरी": "Chanakyapuri",
    "हौज खास": "Hauz Khas",
    "साकेत": "Saket",
    "करोल बाग": "Karol Bagh",
    "द्वारका": "Dwarka",
    "रोहिणी": "Rohini",
    "अलिपूर": "Alipore",
    "बारासात": "Barasat",
    "मयिलापूर": "Mylapore",
    "गिंडी": "Guindy",
    "शेखपेट": "Shaikpet",
    "अमीरपेट": "Ameerpet",
    "दशक्रोई": "Daskroi",
    "चौरासी": "Chorasi",
    "सांगानेर": "Sanganer",
    "दादरी": "Dadri",
    "रामपुर बुशहर": "Rampur",
    "बिलासपुर सदर": "Bilaspur",

    # Localities
    "खराडी": "Kharadi",
    "खराड़ी": "Kharadi",
    "विमान नगर": "Viman Nagar",
    "हिंजवडी": "Hinjewadi",
    "हिंजवाडी": "Hinjewadi",
    "हिंजेवाड़ी": "Hinjewadi",
    "कोथरूड": "Kothrud",
    "कोथरुड": "Kothrud",
    "बाणेर": "Baner",
    "बानेर": "Baner",
    "हडपसर": "Hadapsar",
    "हड़पसर": "Hadapsar",
    "वांद्रे पश्चिम": "Bandra West",
    "बांद्रा पश्चिम": "Bandra West",
    "अंधेरी पूर्व": "Andheri East",
    "पवई": "Powai",
    "ठाणे पश्चिम": "Thane West",
    "राजारामपुरी": "Rajarampuri",
    "व्हाइटफील्ड": "Whitefield",
    "व्हाईटफील्ड": "Whitefield",
    "कोरामंगला": "Koramangala",
    "कोरमंगला": "Koramangala",
    "एचएसआर लेआउट": "HSR Layout",
    "इंदिरानगर": "Indiranagar",
    "इलेक्ट्रॉनिक सिटी": "Electronic City",
    "गोकुलम": "Gokulam",
    "कनॉट प्लेस": "Connaught Place",
    "सॉल्ट लेक": "Salt Lake",
    "राजारहाट": "Rajarhat",
    "न्यू टाउन": "New Town",
    "टी नगर": "T Nagar",
    "अडयार": "Adyar",
    "हायटेक सिटी": "HITEC City",
    "बंजारा हिल्स": "Banjara Hills",
    "नवरंगपुरा": "Navrangpura",
    "वेसू": "Vesu",
    "मालवीय नगर": "Malviya Nagar",
    "वैशाली नगर": "Vaishali Nagar",
    "सेक्टर 62": "Sector 62",
    "गोमती नगर": "Gomti Nagar"
}

# Devanagari character to Latin phonetic transliteration table for unlisted words
DEV_CHAR_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'ळ': 'l',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n',
    'अ': 'a', 'आ': 'a', 'इ': 'i', 'ई': 'i', 'उ': 'u', 'ऊ': 'u',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au'
}

# Common Indic address prefix patterns
INDIC_PREFIX_PATTERNS = {
    "locality": [
        r"(?:गा\.\s*|गाव|गाँव|ग्राम|वस्ती|मोहल्ला|परिसर|इलाका)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:area|locality|village)\s*[:\-]\s*([^,\n;]+)",
    ],
    "subdistrict": [
        r"(?:ता\.\s*|तालुका|तहसील|तहसिल|मंडळ)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:mandal|taluka|tehsil|subdivision)\s*[:\-]\s*([^,\n;]+)",
    ],
    "district": [
        r"(?:जि\.\s*|जिल्हा|जिला|शहर)\s*[:\-]?\s*([^,\n;]+)",
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
    """Provides Indic script detection, transliteration, multi-form expansion, and semantic token normalization."""

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

    @classmethod
    def transliterate_to_latin(cls, text: str) -> Tuple[str, List[str]]:
        """
        Transliterates Devanagari words/phrases into canonical English equivalents.
        Returns: (transliterated_text, list_of_transformations)
        """
        if not text:
            return "", []

        transformations = []
        result = unicodedata.normalize("NFKC", text)

        # 1. Match known multi-word & single-word gazetteer phrases first
        sorted_indic_keys = sorted(INDIC_TO_LATIN_MAPPINGS.keys(), key=lambda x: len(x), reverse=True)
        for indic_term in sorted_indic_keys:
            if indic_term in result:
                latin_canonical = INDIC_TO_LATIN_MAPPINGS[indic_term]
                result = re.sub(re.escape(indic_term), latin_canonical, result)
                transformations.append(f"Transliterated '{indic_term}' → '{latin_canonical}'")

        # 2. Character-level fallback for remaining unmapped Devanagari sequences
        if re.search(r"[\u0900-\u097F]", result):
            chars = []
            for ch in result:
                if ch in DEV_CHAR_MAP:
                    chars.append(DEV_CHAR_MAP[ch])
                elif '\u0900' <= ch <= '\u097F':
                    continue  # skip unmapped diacritics
                else:
                    chars.append(ch)
            fallback_res = "".join(chars).strip()
            if fallback_res != result:
                transformations.append(f"Devanagari char transliteration: '{result}' → '{fallback_res}'")
                result = fallback_res

        return result, transformations

    @classmethod
    def generate_normalized_forms(cls, text: str) -> Dict[str, str]:
        """
        Generates 4 distinct normalized variations for comprehensive multi-strategy retrieval:
        1. canonical_form: Standardized, lowercase, trimmed string.
        2. transliterated_form: Romanized Latin equivalent.
        3. phonetic_form: Indian place-name phonetic representation.
        4. simplified_phonetic_form: Simplified consonant-skeleton form.
        """
        if not text:
            return {
                "canonical_form": "",
                "transliterated_form": "",
                "phonetic_form": "",
                "simplified_phonetic_form": ""
            }

        clean = unicodedata.normalize("NFKC", text).strip()
        translit, _ = cls.transliterate_to_latin(clean)
        translit_clean = translit.lower().strip()
        phon = phonetic_service.simplify_phonetic(translit_clean)
        keys = phonetic_service.get_phonetic_keys(translit_clean)
        simp_phon = keys[1] if len(keys) > 1 else phon

        return {
            "canonical_form": clean.lower(),
            "transliterated_form": translit_clean,
            "phonetic_form": phon,
            "simplified_phonetic_form": simp_phon
        }

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
                    clean_val = re.sub(r"^[,\-:\s]+|[,\-:\s]+$", "", raw_val)
                    if clean_val and field not in extracted:
                        latin_val, _ = cls.transliterate_to_latin(clean_val)
                        extracted[field] = latin_val.strip()

        return extracted


transliteration_service = TransliterationService()
