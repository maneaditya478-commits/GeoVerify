"""Script & Language Detection for Document OCR (Phase 7).

Detects character distribution across:
- English / Latin
- Hindi / Devanagari
- Marathi / Devanagari
- Mixed Multilingual
"""

import re
import unicodedata
from typing import Dict, Any, Tuple


class LanguageDetector:
    """Detects primary and secondary languages in OCR text strings and pages."""

    # Common Marathi marker words vs Hindi marker words
    MARATHI_MARKERS = ["पत्ता", "गाव", "तालुका", "जिल्हा", "महाराष्ट्र", "रस्ता", "नगर", "महानगरपालिका", "ग्रामपंचायत", "ता.", "जि."]
    HINDI_MARKERS = ["पता", "गाँव", "तहसील", "जिला", "मार्ग", "सड़क", "नगर", "मकान", "वार्ड"]

    @classmethod
    def detect_languages(cls, text: str) -> Dict[str, float]:
        """
        Returns normalized language/script distribution percentages (e.g. {'eng': 0.6, 'hin': 0.4}).
        """
        if not text or not text.strip():
            return {"eng": 1.0}

        latin_count = 0
        devanagari_count = 0
        digit_count = 0
        other_count = 0

        for char in text:
            if char.isspace():
                continue
            name = unicodedata.name(char, "")
            if "LATIN" in name:
                latin_count += 1
            elif "DEVANAGARI" in name:
                devanagari_count += 1
            elif "DIGIT" in name:
                digit_count += 1
            else:
                other_count += 1

        total = float(latin_count + devanagari_count + digit_count + other_count)
        if total == 0:
            return {"eng": 1.0}

        latin_pct = round(latin_count / total, 3)
        deva_pct = round(devanagari_count / total, 3)

        res: Dict[str, float] = {}
        if latin_pct > 0.05:
            res["eng"] = latin_pct

        if deva_pct > 0.05:
            # Differentiate Hindi vs Marathi via lexical markers
            marathi_hits = sum(1 for m in cls.MARATHI_MARKERS if m in text)
            hindi_hits = sum(1 for h in cls.HINDI_MARKERS if h in text)

            if marathi_hits > hindi_hits:
                res["mar"] = deva_pct
            elif hindi_hits > marathi_hits:
                res["hin"] = deva_pct
            else:
                # Default Devanagari split or generic Devanagari
                res["hin"] = round(deva_pct * 0.5, 3)
                res["mar"] = round(deva_pct * 0.5, 3)

        return res or {"eng": 1.0}


language_detector = LanguageDetector()
detect_language_scripts = LanguageDetector.detect_languages
