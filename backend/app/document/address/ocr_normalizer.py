"""OCR text normalizer for Indian address domains.

Fixes common optical character recognition misrecognitions:
- Digit / Letter confusion in PIN codes (e.g. 'O' -> '0', 'l'/'I' -> '1', 'S' -> '5', 'B' -> '8')
- Devanagari numerals to standard Arabic numerals (०-९ -> 0-9)
- Common Indian administrative token OCR errors (e.g. 'Tal:' vs 'Ta1:', 'D1st' vs 'Dist')
- Spacing, hyphenation, and noise character cleanup
"""

import re
from typing import Tuple, Optional

# Devanagari to standard Arabic digit translation table
DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

# Character confusion maps specifically for numeric PIN code sequences
PIN_CONFUSION_MAP = {
    "O": "0", "o": "0", "D": "0", "Q": "0",
    "I": "1", "l": "1", "i": "1", "|": "1", "!": "1",
    "Z": "2", "z": "2",
    "E": "3",
    "A": "4",
    "S": "5", "s": "5", "$": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8", "&": "8",
    "g": "9", "q": "9",
}

# Common OCR administrative keyword fixes
ADMIN_KEYWORD_REPLACEMENTS = [
    (r"(?i)\bTa[1l!|]uk[a@]?[.:]?(?=[^a-zA-Z0-9]|$)", "Taluka"),
    (r"(?i)\bTa[1l!|][.:](?=[^a-zA-Z0-9]|$)", "Taluka"),
    (r"(?i)\bD[1il!|]st[.:]?(?=[^a-zA-Z0-9]|$)", "District"),
    (r"(?i)\bD[1il!|]str[1il!|]ct\b", "District"),
    (r"(?i)\bP[1il!|]n\s*c[o0]de\b", "Pincode"),
    (r"(?i)\bP[1il!|]n[.:]?(?=[^a-zA-Z0-9]|$)", "PIN"),
    (r"(?i)\bP[o0]st[.:]?(?=[^a-zA-Z0-9]|$)", "Post"),
    (r"(?i)\bP[o0]\b[.:]?", "PO"),
    (r"(?i)\bM[a@]h[a@]r[a@]shtr[a@]+(?=[^a-zA-Z0-9]|$)", "Maharashtra"),
    (r"(?i)\bK[a@]rn[a@]t[a@]k[a@]+(?=[^a-zA-Z0-9]|$)", "Karnataka"),
    (r"(?i)\bTehs[1il!|][1il!|]?(?=[^a-zA-Z0-9]|$)", "Tehsil"),
    (r"(?i)\bSo[c0][1il!|]ety\b", "Society"),
    (r"(?i)\bBu[1il!|]d[1il!|]ng\b", "Building"),
    (r"(?i)\bF[1il!|][a@]t(?=[^a-zA-Z0-9]|$)", "Flat"),
    (r"(?i)\bN[a@]g[a@]r(?=[^a-zA-Z0-9]|$)", "Nagar"),
]


class OCRNormalizer:
    """Specialized normalizer to correct OCR artifacts in Indian address text."""

    def __init__(self):
        self.admin_replacements = [(re.compile(pattern), repl) for pattern, repl in ADMIN_KEYWORD_REPLACEMENTS]

    def normalize_text(self, text: str) -> str:
        """Run complete normalization pipeline on raw OCR address text."""
        if not text:
            return ""

        # Step 1: Normalize Devanagari digits to standard digits
        text = text.translate(DEVANAGARI_DIGITS)

        # Step 2: Replace known administrative keyword OCR errors
        for pattern, replacement in self.admin_replacements:
            text = pattern.sub(replacement, text)

        # Step 3: Normalize whitespace and remove rogue OCR noise symbols
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        text = re.sub(r"[~`^_*=+|]", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)

        # Step 4: Repair corrupted PIN codes in text
        text = self.repair_pincodes_in_text(text)

        return text.strip()

    def repair_pincodes_in_text(self, text: str) -> str:
        """Find candidate 6-character PIN code tokens near PIN keywords and repair letter substitutions."""
        # Find explicit PIN markers: 'PIN: 411014' or 'PIN 411 O14' or 'PIN-411O14' or 'PIN: 411O1A'
        pin_prefix_regex = re.compile(
            r"(?i)\b(?:PIN(?:CODE)?|PIN\s*NO|P\.O\.|POSTAL\s*CODE)[-:\s.]*([A-Za-z0-9\s]{6,8})\b"
        )

        def fix_prefix_match(match: re.Match) -> str:
            raw_val = match.group(1)
            repaired = self.repair_pincode_candidate(raw_val)
            if repaired:
                return f"PIN: {repaired}"
            return match.group(0)

        text = pin_prefix_regex.sub(fix_prefix_match, text)

        # Also search for standalone 6-character tokens with standard Indian PIN leading digit (1-9)
        # e.g. "411O14", "560OO1"
        standalone_regex = re.compile(r"\b([1-9][A-Za-z0-9]{5})\b")

        def fix_standalone(match: re.Match) -> str:
            candidate = match.group(1)
            # Only attempt if it has letters
            if any(c.isalpha() for c in candidate):
                repaired = self.repair_pincode_candidate(candidate)
                if repaired:
                    return repaired
            return candidate

        text = standalone_regex.sub(fix_standalone, text)

        return text

    def repair_pincode_candidate(self, token: str) -> Optional[str]:
        """Attempt to repair a potential 6-character PIN code candidate string."""
        clean_token = token.replace(" ", "").replace("-", "")
        if len(clean_token) != 6:
            return None

        # First char in Indian PIN code is 1-9
        first_char = clean_token[0]
        if first_char in PIN_CONFUSION_MAP:
            first_char = PIN_CONFUSION_MAP[first_char]
        if not (first_char.isdigit() and "1" <= first_char <= "9"):
            return None

        repaired_digits = [first_char]
        for c in clean_token[1:]:
            if c.isdigit():
                repaired_digits.append(c)
            elif c in PIN_CONFUSION_MAP:
                repaired_digits.append(PIN_CONFUSION_MAP[c])
            else:
                return None  # Unrepairable character

        repaired_pin = "".join(repaired_digits)
        # Check standard 6 digit validity
        if len(repaired_pin) == 6 and repaired_pin.isdigit() and repaired_pin[0] != "0":
            return repaired_pin
        return None
