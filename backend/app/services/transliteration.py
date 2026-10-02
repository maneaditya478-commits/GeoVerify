"""Indic script transliteration, phonetic expansion, and multilingual normalization service."""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from app.services.phonetic import phonetic_service

# Comprehensive Mapping of Indic scripts to English Latin canonicals
INDIC_TO_LATIN_MAPPINGS: Dict[str, str] = {
    # --- States & UTs (Devanagari, Tamil, Telugu, Kannada, Bengali, Gujarati, Odia, Punjabi, Malayalam) ---
    "महाराष्ट्र": "Maharashtra",
    "कर्नाटक": "Karnataka",
    "ಕರ್ನಾಟಕ": "Karnataka",
    "दिल्ली": "Delhi",
    "नवी दिल्ली": "New Delhi",
    "नई दिल्ली": "New Delhi",
    "തമിഴ്നാട്": "Tamil Nadu",
    "தமிழ்நாடு": "Tamil Nadu",
    "तमिळनाडू": "Tamil Nadu",
    "तमिलनाडु": "Tamil Nadu",
    "తెలంగాణ": "Telangana",
    "तेलंगणा": "Telangana",
    "तेलंगाना": "Telangana",
    "ગુજરાત": "Gujarat",
    "गुजरात": "Gujarat",
    "পশ্চিমবঙ্গ": "West Bengal",
    "পশ্চিম বঙ্গ": "West Bengal",
    "पश्चिम बंगाल": "West Bengal",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "राजस्थान": "Rajasthan",
    "കേരളം": "Kerala",
    "केरळ": "Kerala",
    "केरल": "Kerala",
    "मध्य प्रदेश": "Madhya Pradesh",
    "ఆంధ్ర ప్రదేశ్": "Andhra Pradesh",
    "ఆంధ్రప్రదేశ్": "Andhra Pradesh",
    "आंध्र प्रदेश": "Andhra Pradesh",
    "ਪੰਜਾਬ": "Punjab",
    "पंजाब": "Punjab",
    "हरियाणा": "Haryana",
    "बिहार": "Bihar",
    "ଓଡ଼ିଶା": "Odisha",
    "ओडिशा": "Odisha",
    "गोवा": "Goa",
    "অসম": "Assam",
    "আসাম": "Assam",
    "असम": "Assam",
    "हिमाचल प्रदेश": "Himachal Pradesh",
    "उत्तराखंड": "Uttarakhand",
    "झारखंड": "Jharkhand",
    "छत्तीसगढ़": "Chhattisgarh",
    "छत्तीसगड": "Chhattisgarh",
    "ত্রিপুরা": "Tripura",
    "त्रिपुरा": "Tripura",
    "पुदुचेरी": "Puducherry",
    "புதுச்சேரி": "Puducherry",
    "ಪಾಂಡಿಚೇರಿ": "Puducherry",
    "चंडीगढ़": "Chandigarh",
    "ਚੰਡੀਗੜ੍ਹ": "Chandigarh",
    "लद्दाख": "Ladakh",
    "जम्मू और कश्मीर": "Jammu and Kashmir",
    "दमन": "Daman",
    "દમણ": "Daman",
    "दीव": "Diu",

    # --- Districts & Major Cities (Pan-Indic) ---
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
    "अहमदनगर": "Ahmednagar",
    "अहिल्यानगर": "Ahmednagar",
    "सातारा": "Satara",
    "सतारा": "Satara",
    "रत्नागिरी": "Ratnagiri",

    # Karnataka
    "ಬೆಂಗಳೂರು": "Bengaluru Urban",
    "ಬೆಂಗಳೂರು ನಗರ": "Bengaluru Urban",
    "ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ": "Bengaluru Rural",
    "ಮೈಸೂರು": "Mysuru",
    "ಮಂಗಳೂರು": "Dakshina Kannada",
    "ಬೆಳಗಾವಿ": "Belagavi",
    "ಧಾರವಾಡ": "Dharwad",
    "ಹುಬ್ಬಳ್ಳಿ": "Dharwad",
    "ಬಳ್ಳಾರಿ": "Ballari",
    "ಕಲಬುರಗಿ": "Kalaburagi",
    "ಶಿವಮೊಗ್ಗ": "Shivamogga",
    "बंगळुरू": "Bengaluru Urban",
    "बेंगलुरु": "Bengaluru Urban",
    "बंगलोर": "Bengaluru Urban",
    "मैसूर": "Mysuru",
    "म्हैसूर": "Mysuru",

    # Tamil Nadu
    "சென்னை": "Chennai",
    "மதராஸ்": "Chennai",
    "கோயம்புத்தூர்": "Coimbatore",
    "கோவை": "Coimbatore",
    "மதுரை": "Madurai",
    "திருச்சிராப்பள்ளி": "Tiruchirappalli",
    "திருச்சி": "Tiruchirappalli",
    "சேலம்": "Salem",
    "காஞ்சிபுரம்": "Kanchipuram",
    "திருநெல்வேலி": "Tirunelveli",
    "चेन्नई": "Chennai",
    "मद्रास": "Chennai",
    "कोयंबटूर": "Coimbatore",
    "मदुरै": "Madurai",

    # Telangana & Andhra Pradesh
    "హైదరాబాద్": "Hyderabad",
    "సికింద్రాబాద్": "Medchal-Malkajgiri",
    "వరంగల్": "Warangal",
    "కరీంనగర్": "Karimnagar",
    "విశాఖపట్నం": "Visakhapatnam",
    "వైజాగ్": "Visakhapatnam",
    "విజయవాడ": "NTR",
    "గుంటూరు": "Guntur",
    "తిరుపతి": "Tirupati",
    "కర్నూలు": "Kurnool",
    "हैदराबाद": "Hyderabad",
    "वारंगल": "Warangal",
    "विशाखापट्टनम": "Visakhapatnam",
    "विजयवाड़ा": "NTR",
    "गुंटूर": "Guntur",

    # West Bengal & East
    "কলকাতা": "Kolkata",
    "হাওড়া": "Howrah",
    "দার্জিলিং": "Darjeeling",
    "উত্তর ২৪ পরগনা": "North 24 Parganas",
    "দক্ষিণ ২৪ পরগনা": "South 24 Parganas",
    "শিলিগুড়ি": "Darjeeling",
    "আসানসোল": "Paschim Bardhaman",
    "कोलकाता": "Kolkata",
    "कलकत्ता": "Kolkata",
    "हावड़ा": "Howrah",
    "दार्जिलिंग": "Darjeeling",
    "पटना": "Patna",
    "गया": "Gaya",
    "बोधगया": "Gaya",
    "रांची": "Ranchi",
    "जमशेदपुर": "East Singhbhum",
    "धनबाद": "Dhanbad",
    "भुवनेश्वर": "Khordha",
    "ଭୁବନେଶ୍ୱର": "Khordha",
    "କଟକ": "Cuttack",
    "କଟକ": "Cuttack",
    "कटक": "Cuttack",
    "पुरी": "Puri",
    "ପୁରୀ": "Puri",

    # Gujarat
    "અમદાવાદ": "Ahmedabad",
    "સુરત": "Surat",
    "વડોદરા": "Vadodara",
    "રાજકોટ": "Rajkot",
    "ગાંધીનગર": "Gandhinagar",
    "કચ્છ": "Kutch",
    "અહમદાબાદ": "Ahmedabad",
    "अहमदाबाद": "Ahmedabad",
    "सूरत": "Surat",
    "सुरत": "Surat",
    "वडोदरा": "Vadodara",
    "राजकोट": "Rajkot",

    # North & Central
    "जयपुर": "Jaipur",
    "जयपूर": "Jaipur",
    "जोधपुर": "Jodhpur",
    "उदयपुर": "Udaipur",
    "कोटा": "Kota",
    "सीकर": "Sikar",
    "गुरुग्राम": "Gurugram",
    "गुड़गांव": "Gurugram",
    "फरीदाबाद": "Faridabad",
    "लुधियाना": "Ludhiana",
    "ਲੁਧਿਆਣਾ": "Ludhiana",
    "ਅੰਮ੍ਰਿਤਸਰ": "Amritsar",
    "अमृतसर": "Amritsar",
    "ਜਲੰਧਰ": "Jalandhar",
    "जालंधर": "Jalandhar",
    "ਮੋਹਾਲੀ": "SAS Nagar",
    "मोहाली": "SAS Nagar",
    "पटियाला": "Patiala",
    "लखनऊ": "Lucknow",
    "लखनौ": "Lucknow",
    "कानपुर": "Kanpur Nagar",
    "वाराणसी": "Varanasi",
    "बनारस": "Varanasi",
    "काशी": "Varanasi",
    "प्रयागराज": "Prayagraj",
    "इलाहाबाद": "Prayagraj",
    "नोएडा": "Gautam Buddha Nagar",
    "ग्रेटर नोएडा": "Gautam Buddha Nagar",
    "गाजियाबाद": "Ghaziabad",
    "आगरा": "Agra",
    "रामपुर": "Rampur",
    "फतेहपुर": "Fatehpur",
    "चित्रकूट": "Chitrakoot",
    "देहरादून": "Dehradun",
    "हरिद्वार": "Haridwar",
    "नैनीताल": "Nainital",
    "शिमला": "Shimla",
    "बिलासपुर": "Bilaspur",
    "श्रीनगर": "Srinagar",
    "जम्मू": "Jammu",
    "लेह": "Leh",
    "कारगिल": "Kargil",
    "इंदौर": "Indore",
    "भोपाल": "Bhopal",
    "जबलपुर": "Jabalpur",
    "ग्वालियर": "Gwalior",
    "उज्जैन": "Ujjain",
    "रायपुर": "Raipur",
    "बस्तर": "Bastar",
    "जगदलपुर": "Bastar",

    # Northeast & Kerala
    "गुवाहाटी": "Kamrup Metropolitan",
    "গুৱাহাটী": "Kamrup Metropolitan",
    "দিছপুৰ": "Kamrup Metropolitan",
    "দিসপুর": "Kamrup Metropolitan",
    "शिलांग": "East Khasi Hills",
    "शिलाँग": "East Khasi Hills",
    "इम्फाल": "Imphal West",
    "कोहिमा": "Kohima",
    "दीमापुर": "Dimapur",
    "आइजोल": "Aizawl",
    "अगरतला": "West Tripura",
    "ত্রিপুরা": "West Tripura",
    "ईटानगर": "Papum Pare",
    "गंगटोक": "East Sikkim",
    "पोर्ट ब्लेयर": "South Andaman",
    "कवरत्ती": "Lakshadweep",
    "तिरुवनंतपुरम": "Thiruvananthapuram",
    "തിരുവനന്തപുരം": "Thiruvananthapuram",
    "एर्नाकुलम": "Ernakulam",
    "എറണാകുളം": "Ernakulam",
    "കൊച്ചി": "Ernakulam",
    "कोच्चि": "Ernakulam",
    "कोझिकोड": "Kozhikode",
    "त्रिशूर": "Thrissur",
    # --- Subdistricts, Talukas & Tehsils ---
    "हवेली": "Haveli",
    "हावेली": "Haveli",
    "मुळशी": "Mulshi",
    "मावळ": "Mawal",
    "शिरूर": "Shirur",
    "जुन्नर": "Junnar",
    "आंबेगाव": "Ambegaon",
    "बारामती": "Baramati",
    "दौंड": "Daund",
    "इंदापूर": "Indapur",
    "भोर": "Bhor",
    "वेल्हे": "Velhe",
    "पुरंदर": "Purandar",
    "खेड": "Khed",
    "कल्याण": "Kalyan",
    "कुर्ला": "Kurla",
    "अंधेरी": "Andheri",
    "बोरीवली": "Borivali",
    "सांगनेर": "Sanganer",
    "दादरी": "Dadri",
    "बिलासपुर सदर": "Bilaspur Sadar",

    # --- Localities & Neighborhoods (Pan-Indic) ---
    "खराडी": "Kharadi",
    "खराड़ी": "Kharadi",
    "हडपसर": "Hadapsar",
    "हड़पसर": "Hadapsar",
    "कोथरूड": "Kothrud",
    "कोथरुड": "Kothrud",
    "हिंजवडी": "Hinjawadi",
    "हिंजवाडी": "Hinjawadi",
    "विमान नगर": "Viman Nagar",
    "बाणेर": "Baner",
    "वांद्रे": "Bandra West",
    "बांद्रा": "Bandra West",
    "अंधेरी": "Andheri East",
    "नरिमन पॉइंट": "Nariman Point",
    "पंचवटी": "Panchavati",
    "कोरेगाव": "Koregaon",

    # South Localities
    "ವೈಟ್‌ಫೀಲ್ಡ್": "Whitefield",
    "ಇಂದಿರಾನಗರ": "Indiranagar",
    "ಕೋರಮಂಗಲ": "Koramangala",
    "ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಸಿಟಿ": "Electronic City",
    "ಮೈಲಾப்பூர்": "Mylapore",
    "மயிலாப்பூர்": "Mylapore",
    "காந்திபுரம்": "Gandhipuram",
    "சிம்மக்கல்": "Simmakkal",
    "அடையாறு": "Adyar",
    "தி நகர்": "T Nagar",
    "మాదాపూర్": "Madhapur",
    "హనుమకొండ": "Hanamkonda",
    "ఎంవిపి కాలనీ": "MVP Colony",
    "കാക്കനാട്": "Kakkanad",

    # North & East Localities
    "हौज़ खास": "Hauz Khas",
    "कनॉट प्लेस": "Connaught Place",
    "साकेत": "Saket",
    "करोल बाग": "Karol Bagh",
    "द्वारका": "Dwarka",
    "रोहिणी": "Rohini",
    "डीएलएफ": "DLF Phase 3",
    "मालवीय नगर": "Malviya Nagar",
    "अस्सी घाट": "Assi Ghat",
    "माल रोड": "Mall Road",
    "राजपुर रोड": "Rajpur Road",
    "लाल चौक": "Lal Chowk",
    "শিবপুর": "Shibpur",
    "সল্টলেক": "Salt Lake",
    "সরণি": "Sarani",
    "সহীদ ନଗର": "Saheed Nagar",
    "विजय नगर": "Vijay Nagar",
    "सिविल लाइन्स": "Civil Lines",
    "तेलीबांधा": "Telibandha",
    "জগদলপুর": "Jagdalpur",
    "диছপুৰ": "Dispur",
    "দিছপুর": "Dispur",
    "বনমালীপুর": "Banamalipur",
    "વરાછા": "Varachha",
    "નાની દમણ": "Nani Daman"
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
        r"(?:गा\.\s*|गाव|गाँव|ग्राम|கி\.\s*|கிராமம்|గ్రామం|ಗ್ರಾಮ|গ্রাম|ગામ|ਪਿੰਡ)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:area|locality|village)\s*[:\-]\s*([^,\n;]+)",
    ],
    "subdistrict": [
        r"(?:ता\.\s*|तालुका|तहसील|तहसिल|வட்\.\s*|வட்டம்|మండలం|ತಾಲೂಕು|থানা|মহকুমা|તાલુકો|ਤਹਿਸੀਲ)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:mandal|taluka|tehsil|subdivision)\s*[:\-]\s*([^,\n;]+)",
    ],
    "district": [
        r"(?:जि\.\s*|जिल्हा|जिला|மாவ\.\s*|மாவட்டம்|జిల్లా|ಜಿಲ್ಲೆ|জেলা|જિલ્લો|ਜ਼ਿਲ੍ਹਾ|ଜିଲ୍ଲା)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:district|dist|city)\s*[:\-]\s*([^,\n;]+)",
    ],
    "state": [
        r"(?:राज्य|प्रदेश|மாநிலம்|రాష్ట్రం|ರಾಜ್ಯ|রাজ্য|રાજ્ય|ਰਾਜ)\s*[:\-]?\s*([^,\n;]+)",
        r"\b(?:state|st)\s*[:\-]\s*([^,\n;]+)",
    ],
    "pincode": [
        r"(?:पिन\s*कोड|पिन|पिनकोड|தபால்\s*குறியீடு|పిన్‌కోడ్|ಪಿನ್‌ಕೋಡ್|পিন)\s*[:\-]?\s*([1-9][0-9]{5})",
        r"\b(?:pincode|pin|postal\s*code)\s*[:\-]?\s*([1-9][0-9]{5})",
    ],
}


class TransliterationService:
    """Provides Indic script detection, transliteration, multi-form expansion, and semantic token normalization."""

    @staticmethod
    def detect_script(text: str) -> str:
        """Detect primary script family across Latin, Devanagari, and Pan-Indic Unicode blocks."""
        if not text:
            return "Unknown"
        
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        has_tamil = bool(re.search(r"[\u0B80-\u0BFF]", text))
        has_telugu = bool(re.search(r"[\u0C00-\u0C7F]", text))
        has_kannada = bool(re.search(r"[\u0C80-\u0CFF]", text))
        has_bengali = bool(re.search(r"[\u0980-\u09FF]", text))
        has_gujarati = bool(re.search(r"[\u0A80-\u0AFF]", text))
        has_gurmukhi = bool(re.search(r"[\u0A00-\u0A7F]", text))
        has_odia = bool(re.search(r"[\u0B00-\u0B7F]", text))
        has_malayalam = bool(re.search(r"[\u0D00-\u0D7F]", text))

        has_indic = has_devanagari or has_tamil or has_telugu or has_kannada or has_bengali or has_gujarati or has_gurmukhi or has_odia or has_malayalam
        has_latin = bool(re.search(r"[a-zA-Z]", text))

        if has_indic and has_latin:
            return "Mixed"
        elif has_devanagari and not (has_tamil or has_telugu or has_kannada or has_bengali or has_gujarati or has_gurmukhi or has_odia or has_malayalam):
            return "Devanagari"
        elif has_tamil:
            return "Tamil"
        elif has_telugu:
            return "Telugu"
        elif has_kannada:
            return "Kannada"
        elif has_bengali:
            return "Bengali"
        elif has_gujarati:
            return "Gujarati"
        elif has_gurmukhi:
            return "Gurmukhi"
        elif has_odia:
            return "Odia"
        elif has_malayalam:
            return "Malayalam"
        elif has_indic:
            return "Indic"
        elif has_latin:
            return "Latin"
        return "Unknown"

    @classmethod
    def transliterate_to_latin(cls, text: str) -> Tuple[str, List[str]]:
        """
        Transliterates Pan-Indic words/phrases into canonical English equivalents.
        Returns: (transliterated_text, list_of_transformations)
        """
        if not text:
            return "", []

        transformations = []
        result = unicodedata.normalize("NFKC", text)

        # 1. Match known multi-word & single-word gazetteer phrases first across all Indic scripts
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
                    continue
                else:
                    chars.append(ch)
            fallback_res = "".join(chars).strip()
            if fallback_res != result:
                transformations.append(f"Devanagari char transliteration: '{result}' → '{fallback_res}'")
                result = fallback_res

        return result, transformations

    @classmethod
    def generate_normalized_forms(cls, text: str) -> Dict[str, str]:
        """Generates 4 distinct normalized variations for comprehensive multi-strategy retrieval."""
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
        """Extracts address components marked with formal Indic or English prefixes."""
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
