"""Advanced Multilingual Alignment, Mixed-Script Parsing, and Pan-Indic Geographic Abbreviations."""

import re
from typing import Optional, List, Dict, Tuple, Any
from pydantic import BaseModel, Field


class ExpandedToken(BaseModel):
    original_token: str
    expanded_token: str
    category: str
    language: str
    applied: bool = False


class ScriptAlignmentResult(BaseModel):
    primary_script: str
    is_mixed_script: bool
    detected_scripts: List[str] = Field(default_factory=list)
    expanded_address: str
    expanded_tokens: List[ExpandedToken] = Field(default_factory=list)
    extracted_district_hint: Optional[str] = None
    extracted_taluka_hint: Optional[str] = None
    extracted_locality_hint: Optional[str] = None


# Pan-Indic Administrative and Geographic Abbreviation Mapping
ABBREVIATIONS_DICT: List[Dict[str, Any]] = [
    # District abbreviations (Hindi, Marathi, Tamil, Telugu, Kannada, Bengali, Gujarati, Punjabi, Odia, English)
    {
        "patterns": [
            r"\bजि\.\s*", r"\bजि:\s*", r"\bजि\s+", r"\bDist\.\s*", r"\bDt\.\s*", r"\bDist\s+", r"\bजिला\b", r"\bजिल्हा\b",
            r"மாவ\.\s*", r"மாவட்டம்\s*", r"జిల్లా\s*", r"ಜಿಲ್ಲೆ\s*", r"জেলা\s*", r"જિલ્લો\s*", r"ਜ਼ਿਲ੍ਹਾ\s*", r"ଜିଲ୍ଲା\s*"
        ],
        "category": "DISTRICT",
        "expansion": "District ",
        "language": "pan_indic+eng"
    },
    # Taluka / Tehsil / Mandal abbreviations
    {
        "patterns": [
            r"\bता\.\s*", r"\bता:\s*", r"\bता\s+", r"\bतह\.\s*", r"\bतह:\s*", r"\bTal\.\s*", r"\bTeh\.\s*", r"\bTaluka\s+", r"\bTehsil\s+",
            r"\bतालुका\b", r"\bतहसील\b", r"வட்\.\s*", r"வட்டம்\s*", r"మండలం\s*", r"తಾಲೂಕು\s*", r"থানা\s*", r"মহকুমা\s*", r"તાલુકો\s*", r"ਤਹਿਸੀਲ\s*"
        ],
        "category": "TALUKA",
        "expansion": "Taluka ",
        "language": "pan_indic+eng"
    },
    # Village / Locality abbreviations
    {
        "patterns": [
            r"\bमु\.पो\.\s*", r"\bमु\.\s*", r"\bमु:\s*", r"\bगा\.\s*", r"\bVill\.\s*", r"\bVlg\.\s*", r"\bगाँव\b", r"\bगाव\b",
            r"கி\.\s*", r"கிராமம்\s*", r"గ్రామం\s*", r"ಗ್ರಾಮ\s*", r"গ্রাম\s*", r"ગામ\s*", r"ਪਿੰਡ\s*"
        ],
        "category": "VILLAGE",
        "expansion": "Village ",
        "language": "pan_indic+eng"
    },
    # Post Office abbreviations
    {
        "patterns": [
            r"\bपो\.\s*", r"\bपो:\s*", r"\bपो\.बॉ\.\s*", r"\bP\.O\.\s*", r"\bPO\s+", r"\bपोस्ट\b", r"தபால்\s*", r"പോസ്റ്റ്\s*"
        ],
        "category": "POST_OFFICE",
        "expansion": "Post Office ",
        "language": "pan_indic+eng"
    },
    # Municipal Corporation / Council
    {
        "patterns": [
            r"\bम\.न\.पा\.\s*", r"\bमनपा\b", r"\bन\.प\.\s*", r"\bCorp\.\s*", r"\bMunc\.\s*", r"மாநகராட்சி\s*", r"నగరపాలక\s*", r"ಮಹಾನಗರ\s*", r"পৌরসভা\s*"
        ],
        "category": "MUNICIPALITY",
        "expansion": "Municipal Corporation ",
        "language": "pan_indic+eng"
    },
    # Road / Marg / Street
    {
        "patterns": [
            r"\bर\.\s*", r"\bमार्ग\b", r"\bरोड\b", r"\bRd\.\s*", r"\bMarg\s*", r"தெரு\s*", r"சாலை\s*", r"వీధి\s*", r"రಸ್ತೆ\s*", r"ਸੜਕ\s*", r"রাস্তা\s*", r"সরণি\s*"
        ],
        "category": "ROAD",
        "expansion": "Road ",
        "language": "pan_indic+eng"
    },
    # Chowk / Junction / Circle
    {
        "patterns": [
            r"\bचौ\.\s*", r"\bचौक\b", r"\bChowk\b", r"\bSq\.\s*", r"சந்திப்பு\s*", r"కూడలి\s*", r"ವೃತ್ತ\s*", r"মোড়\s*"
        ],
        "category": "CHOWK",
        "expansion": "Chowk ",
        "language": "pan_indic+eng"
    },
]


class MultilingualAlignmentEngine:
    """Detects scripts, handles mixed-script code-switching, and expands administrative abbreviations."""

    @classmethod
    def detect_scripts(cls, text: str) -> Tuple[str, List[str], bool]:
        """Detects scripts across all Indian language Unicode blocks."""
        scripts = set()
        for ch in text:
            code = ord(ch)
            if 0x0900 <= code <= 0x097F:
                scripts.add("Devanagari")
            elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                scripts.add("Latin")
            elif 0x0980 <= code <= 0x09FF:
                scripts.add("Bengali")
            elif 0x0A00 <= code <= 0x0A7F:
                scripts.add("Gurmukhi")
            elif 0x0A80 <= code <= 0x0AFF:
                scripts.add("Gujarati")
            elif 0x0B00 <= code <= 0x0B7F:
                scripts.add("Odia")
            elif 0x0B80 <= code <= 0x0BFF:
                scripts.add("Tamil")
            elif 0x0C00 <= code <= 0x0C7F:
                scripts.add("Telugu")
            elif 0x0C80 <= code <= 0x0CFF:
                scripts.add("Kannada")
            elif 0x0D00 <= code <= 0x0D7F:
                scripts.add("Malayalam")

        detected = list(scripts)
        is_mixed = len(detected) > 1
        primary = detected[0] if len(detected) == 1 else ("Mixed" if is_mixed else "Latin")
        return primary, detected, is_mixed

    @classmethod
    def align_and_expand(cls, raw_address: str) -> ScriptAlignmentResult:
        """Expands administrative abbreviations and extracts structural entity hints across scripts."""
        if not raw_address:
            return ScriptAlignmentResult(
                primary_script="Latin",
                is_mixed_script=False,
                detected_scripts=["Latin"],
                expanded_address="",
                expanded_tokens=[]
            )

        primary_script, detected_scripts, is_mixed = cls.detect_scripts(raw_address)
        expanded_text = raw_address
        applied_expansions: List[ExpandedToken] = []

        dist_hint: Optional[str] = None
        tal_hint: Optional[str] = None
        loc_hint: Optional[str] = None

        # Regex search for administrative structures across all Indic unicode ranges
        # e.g. "जि. पुणे", "மாவட்டம் சென்னை", "Dist. Pune"
        dist_match = re.search(r"(?:जि\.|जि:|Dist\.|Dt\.|जिला|जिल्हा|மாவ\.|மாவட்டம்|జిల్లా|ಜಿಲ್ಲೆ|জেলা|જિલ્લો|ਜ਼ਿਲ੍ਹਾ|ଜିଲ୍ଲା)\s*([\w\u0900-\u0D7F]+)", raw_address, re.IGNORECASE)
        if dist_match:
            dist_hint = dist_match.group(1).strip()

        # e.g. "ता. हवेली", "வட்டம் மைலாப்பூர்", "Tal. Haveli"
        tal_match = re.search(r"(?:ता\.|ता:|Tal\.|Teh\.|तालुका|तहसील|வட்\.|வட்டம்|మండలం|ತಾಲೂಕು|থানা|মহকুমা|તાલુકો|ਤਹਿਸੀਲ)\s*([\w\u0900-\u0D7F]+)", raw_address, re.IGNORECASE)
        if tal_match:
            tal_hint = tal_match.group(1).strip()

        # e.g. "मु.पो. कोथरूड", "கிராமம்", "Vill. Kothrud"
        loc_match = re.search(r"(?:मु\.पो\.|मु\.|गा\.|Vill\.|கி\.|கிராமம்|గ్రామం|ಗ್ರಾಮ|গ্রাম|ગામ|ਪਿੰਡ)\s*([\w\u0900-\u0D7F]+)", raw_address, re.IGNORECASE)
        if loc_match:
            loc_hint = loc_match.group(1).strip()

        # Apply dictionary replacements
        for item in ABBREVIATIONS_DICT:
            for pattern in item["patterns"]:
                matches = list(re.finditer(pattern, expanded_text, flags=re.IGNORECASE))
                if matches:
                    for m in matches:
                        applied_expansions.append(ExpandedToken(
                            original_token=m.group(0).strip(),
                            expanded_token=item["expansion"].strip(),
                            category=item["category"],
                            language=item["language"],
                            applied=True
                        ))
                    expanded_text = re.sub(pattern, item["expansion"], expanded_text, flags=re.IGNORECASE)

        # Normalize extra spaces
        expanded_text = re.sub(r"\s+", " ", expanded_text).strip()

        return ScriptAlignmentResult(
            primary_script=primary_script,
            is_mixed_script=is_mixed,
            detected_scripts=detected_scripts,
            expanded_address=expanded_text,
            expanded_tokens=applied_expansions,
            extracted_district_hint=dist_hint,
            extracted_taluka_hint=tal_hint,
            extracted_locality_hint=loc_hint
        )


# Global singleton instance
multilingual_alignment_engine = MultilingualAlignmentEngine()
