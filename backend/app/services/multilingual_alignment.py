"""Advanced Multilingual Alignment, Mixed-Script Parsing, and Indian Geographic Abbreviations."""

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


# Indian Administrative and Geographic Abbreviation Mapping
ABBREVIATIONS_DICT: List[Dict[str, Any]] = [
    # District abbreviations
    {
        "patterns": [r"\bजि\.\s*", r"\bजि:\s*", r"\bजि\s+", r"\bDist\.\s*", r"\bDt\.\s*", r"\bDist\s+"],
        "category": "DISTRICT",
        "expansion": "District ",
        "language": "mar+hin+eng"
    },
    # Taluka / Tehsil abbreviations
    {
        "patterns": [r"\bता\.\s*", r"\bता:\s*", r"\bता\s+", r"\bतह\.\s*", r"\bतह:\s*", r"\bTal\.\s*", r"\bTeh\.\s*", r"\bTaluka\s+", r"\bTehsil\s+"],
        "category": "TALUKA",
        "expansion": "Taluka ",
        "language": "mar+hin+eng"
    },
    # Village / Locality abbreviations
    {
        "patterns": [r"\bमु\.पो\.\s*", r"\bमु\.\s*", r"\bमु:\s*", r"\bगा\.\s*", r"\bVill\.\s*", r"\bVlg\.\s*"],
        "category": "VILLAGE",
        "expansion": "Village ",
        "language": "mar+hin+eng"
    },
    # Post Office abbreviations
    {
        "patterns": [r"\bपो\.\s*", r"\bपो:\s*", r"\bपो\.बॉ\.\s*", r"\bP\.O\.\s*", r"\bPO\s+"],
        "category": "POST_OFFICE",
        "expansion": "Post Office ",
        "language": "mar+hin+eng"
    },
    # Municipal Corporation / Council
    {
        "patterns": [r"\bम\.न\.पा\.\s*", r"\bमनपा\b", r"\bन\.प\.\s*", r"\bCorp\.\s*", r"\bMunc\.\s*"],
        "category": "MUNICIPALITY",
        "expansion": "Municipal Corporation ",
        "language": "mar+hin+eng"
    },
    # Road / Marg
    {
        "patterns": [r"\bर\.\s*", r"\bमार्ग\b", r"\bरोड\b", r"\bRd\.\s*", r"\bMarg\s*"],
        "category": "ROAD",
        "expansion": "Road ",
        "language": "mar+hin+eng"
    },
    # Chowk / Junction
    {
        "patterns": [r"\bचौ\.\s*", r"\bचौक\b", r"\bChowk\b", r"\bSq\.\s*"],
        "category": "CHOWK",
        "expansion": "Chowk ",
        "language": "mar+hin+eng"
    },
]


class MultilingualAlignmentEngine:
    """Detects scripts, handles mixed-script code-switching, and expands administrative abbreviations."""

    @classmethod
    def detect_scripts(cls, text: str) -> Tuple[str, List[str], bool]:
        """Detects scripts in the text (Devanagari, Latin, Bengali, Tamil, Telugu, Kannada, etc.)."""
        scripts = set()
        for ch in text:
            code = ord(ch)
            if 0x0900 <= code <= 0x097F:
                scripts.add("Devanagari")
            elif 0x0041 <= code <= 0x007A:
                scripts.add("Latin")
            elif 0x0980 <= code <= 0x09FF:
                scripts.add("Bengali")
            elif 0x0B80 <= code <= 0x0BFF:
                scripts.add("Tamil")
            elif 0x0C00 <= code <= 0x0C7F:
                scripts.add("Telugu")
            elif 0x0C80 <= code <= 0x0CFF:
                scripts.add("Kannada")

        detected = list(scripts)
        is_mixed = len(detected) > 1
        primary = detected[0] if len(detected) == 1 else ("Mixed" if is_mixed else "Latin")
        return primary, detected, is_mixed

    @classmethod
    def align_and_expand(cls, raw_address: str) -> ScriptAlignmentResult:
        """Expands administrative abbreviations and extracts structural entity hints."""
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

        # Regex search for administrative structures
        # e.g. "जि. पुणे" or "Dist. Pune"
        dist_match = re.search(r"(?:जि\.|जि:|Dist\.|Dt\.|जिला)\s*([A-Za-z\u0900-\u097F]+)", raw_address, re.IGNORECASE)
        if dist_match:
            dist_hint = dist_match.group(1).strip()

        # e.g. "ता. हवेली" or "Tal. Haveli"
        tal_match = re.search(r"(?:ता\.|ता:|Tal\.|Teh\.|तालुका|तहसील)\s*([A-Za-z\u0900-\u097F]+)", raw_address, re.IGNORECASE)
        if tal_match:
            tal_hint = tal_match.group(1).strip()

        # e.g. "मु.पो. कोथरूड" or "Vill. Kothrud"
        loc_match = re.search(r"(?:मु\.पो\.|मु\.|गा\.|Vill\.)\s*([A-Za-z\u0900-\u097F]+)", raw_address, re.IGNORECASE)
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
