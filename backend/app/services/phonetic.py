"""Indian Geographic & Place-Name Phonetic Matching Engine.

Provides phonetic encoding, Indic phonetic simplification, and phonetic similarity
tailored for Indian administrative entities and spelling variations.
"""

import re
from typing import List, Set, Tuple
from rapidfuzz import fuzz


class IndianPhoneticEncoder:
    """Phonetic transformations and canonical hash generation for Indian place names."""

    # Consonant equivalence mappings for Indian English / Romanized Indic words
    CONSONANT_MAP = [
        (r"ksh", "x"),
        (r"sh", "s"),
        (r"zh", "z"),
        (r"ph", "f"),
        (r"bh", "b"),
        (r"dh", "d"),
        (r"th", "t"),
        (r"kh", "k"),
        (r"gh", "g"),
        (r"ch", "c"),
        (r"jh", "j"),
        (r"wh", "w"),
        (r"v", "w"),
        (r"c(?=[eiy])", "s"),
        (r"c", "k"),
        (r"q", "k"),
        (r"z", "j"),
    ]

    # Vowel combinations and long vowel normalizations
    VOWEL_MAP = [
        (r"ee", "i"),
        (r"oo", "u"),
        (r"ou", "au"),
        (r"ai", "ay"),
        (r"ei", "ay"),
        (r"aa", "a"),
        (r"ii", "i"),
        (r"uu", "u"),
        (r"oa", "o"),
    ]

    @classmethod
    def simplify_phonetic(cls, text: str) -> str:
        """
        Produces a simplified phonetic signature for Indian place names.
        Examples:
          'Kharadi' -> 'karadi'
          'Khardi'  -> 'kardi'
          'Nashik'  -> 'nasik'
          'Puna'    -> 'pune'
          'Maharastra' -> 'maharastra'
        """
        if not text:
            return ""

        s = text.lower().strip()
        # Remove non-alphanumeric except space
        s = re.sub(r"[^a-z0-9\s]", "", s)

        # Apply consonant mappings
        for pattern, replacement in cls.CONSONANT_MAP:
            s = re.sub(pattern, replacement, s)

        # Apply vowel mappings
        for pattern, replacement in cls.VOWEL_MAP:
            s = re.sub(pattern, replacement, s)

        # Deduplicate consecutive identical characters (e.g. 'kolkata' -> 'kolkata', 'hadapsar' -> 'hadapsar', 'kothrood' -> 'kotrud')
        s = re.sub(r"(.)\1+", r"\1", s)

        # Normalize terminal vowels (schwa variation e.g. Puna -> Pune, Thana -> Thane, Hadapsara -> Hadapsare)
        if len(s) >= 3 and s.endswith("a"):
            s = s[:-1] + "e"

        return s

    @classmethod
    def get_phonetic_keys(cls, text: str) -> List[str]:
        """Returns a set of plausible phonetic variants for indexing and retrieval."""
        if not text:
            return []

        base = text.lower().strip()
        simplified = cls.simplify_phonetic(base)
        
        # Consonant-skeleton (removing all vowels except leading vowel)
        consonant_skeleton = base[0] if base else ""
        for char in base[1:]:
            if char not in "aeiou \t\n":
                consonant_skeleton += char
            elif consonant_skeleton and consonant_skeleton[-1] != "_":
                consonant_skeleton += "_"

        keys = {base, simplified, consonant_skeleton.replace("_", "")}
        
        # Also include soundex-style code
        soundex_code = cls.compute_indic_soundex(base)
        if soundex_code:
            keys.add(soundex_code)

        return [k for k in keys if k]

    @classmethod
    def compute_indic_soundex(cls, text: str) -> str:
        """Computes a 4-character phonetic soundex code adapted for Indian place names."""
        if not text:
            return ""

        clean = re.sub(r"[^a-zA-Z]", "", text).upper()
        if not clean:
            return ""

        first_char = clean[0]
        # Mapping: 1: B,F,P,V; 2: C,G,J,K,Q,S,X,Z; 3: D,T; 4: L; 5: M,N; 6: R
        mapping = {
            "B": "1", "F": "1", "P": "1", "V": "1", "W": "1",
            "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
            "D": "3", "T": "3",
            "L": "4",
            "M": "5", "N": "5",
            "R": "6"
        }

        coded = [first_char]
        prev_code = mapping.get(first_char, "0")

        for char in clean[1:]:
            code = mapping.get(char, "0")
            if code != "0" and code != prev_code:
                coded.append(code)
            prev_code = code

        # Pad or truncate to length 4
        digits = "".join(coded[1:])
        return (first_char + digits + "000")[:4]

    @classmethod
    def compute_phonetic_similarity(cls, query: str, candidate: str) -> float:
        """
        Computes phonetic similarity between query and candidate string (0.0 to 1.0).
        """
        if not query or not candidate:
            return 0.0

        q_clean = query.lower().strip()
        c_clean = candidate.lower().strip()

        if q_clean == c_clean:
            return 1.0

        q_phon = cls.simplify_phonetic(q_clean)
        c_phon = cls.simplify_phonetic(c_clean)

        if q_phon == c_phon:
            return 0.98

        # RapidFuzz similarity on phonetic signatures
        ratio_phon = fuzz.ratio(q_phon, c_phon) / 100.0
        partial_phon = fuzz.partial_ratio(q_phon, c_phon) / 100.0
        token_sort = fuzz.token_sort_ratio(q_phon, c_phon) / 100.0

        # Soundex match bonus
        q_soundex = cls.compute_indic_soundex(q_clean)
        c_soundex = cls.compute_indic_soundex(c_clean)
        soundex_match = (q_soundex == c_soundex and len(q_soundex) >= 4)

        score = max(ratio_phon, partial_phon * 0.92, token_sort)
        if soundex_match and score > 0.60:
            score = min(0.96, score + 0.10)

        return round(score, 3)


phonetic_service = IndianPhoneticEncoder()
