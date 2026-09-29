"""Benchmark Dataset Generator for GeoVerify India.

Generates 1,000+ deterministic, reproducible, multi-category Indian test cases
with independent ground-truth annotations across Latin, Devanagari, and Mixed scripts.
"""

import os
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

from evaluation.schema import (
    BenchmarkDataset,
    BenchmarkRecord,
    GroundTruth,
    BenchmarkMetadata,
    SourceType,
    BenchmarkCategory,
    Language,
    Script,
    ExpectedStatus,
    CompletenessLevel,
)

# Base geographic entities for combinatorial generation
BASE_ENTITIES = [
    # Maharashtra
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Haveli", "locality": "Kharadi", "pincode": "411014", "lat": 18.5514, "lon": 73.9405, "aliases": ["Poona"], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "हवेली", "devanagari_locality": "खराडी"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Mulshi", "locality": "Hinjewadi", "pincode": "411057", "lat": 18.5913, "lon": 73.7389, "aliases": ["Hinjawadi"], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "मुळशी", "devanagari_locality": "हिंजवडी"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Haveli", "locality": "Baner", "pincode": "411045", "lat": 18.5590, "lon": 73.7868, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "हवेली", "devanagari_locality": "बाणेर"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Haveli", "locality": "Hadapsar", "pincode": "411028", "lat": 18.5089, "lon": 73.9260, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "हवेली", "devanagari_locality": "हडपसर"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Pune City", "locality": "Kothrud", "pincode": "411038", "lat": 18.5074, "lon": 73.8077, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "पुणे शहर", "devanagari_locality": "कोथरूड"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Pune", "subdistrict": "Haveli", "locality": "Viman Nagar", "pincode": "411014", "lat": 18.5679, "lon": 73.9143, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "पुणे", "devanagari_subdistrict": "हवेली", "devanagari_locality": "विमान नगर"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Mumbai Suburban", "subdistrict": "Andheri", "locality": "Andheri East", "pincode": "400069", "lat": 19.1136, "lon": 72.8697, "aliases": ["Bombay"], "devanagari_state": "महाराष्ट्र", "devanagari_district": "मुंबई उपनगर", "devanagari_subdistrict": "अंधेरी", "devanagari_locality": "अंधेरी पूर्व"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Mumbai Suburban", "subdistrict": "Andheri", "locality": "Powai", "pincode": "400076", "lat": 19.1176, "lon": 72.9060, "aliases": ["Bombay"], "devanagari_state": "महाराष्ट्र", "devanagari_district": "मुंबई उपनगर", "devanagari_subdistrict": "अंधेरी", "devanagari_locality": "पवई"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Mumbai Suburban", "subdistrict": "Andheri", "locality": "Bandra West", "pincode": "400050", "lat": 19.0596, "lon": 72.8295, "aliases": ["Bombay"], "devanagari_state": "महाराष्ट्र", "devanagari_district": "मुंबई उपनगर", "devanagari_subdistrict": "अंधेरी", "devanagari_locality": "वांद्रे पश्चिम"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Thane", "subdistrict": "Thane", "locality": "Thane West", "pincode": "400601", "lat": 19.2183, "lon": 72.9781, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "ठाणे", "devanagari_subdistrict": "ठाणे", "devanagari_locality": "ठाणे पश्चिम"},
    {"state": "Maharashtra", "state_code": "MH", "district": "Kolhapur", "subdistrict": "Karvir", "locality": "Rajarampuri", "pincode": "416008", "lat": 16.6913, "lon": 74.2449, "aliases": [], "devanagari_state": "महाराष्ट्र", "devanagari_district": "कोल्हापूर", "devanagari_subdistrict": "करवीर", "devanagari_locality": "राजारामपुरी"},

    # Karnataka
    {"state": "Karnataka", "state_code": "KA", "district": "Bengaluru Urban", "subdistrict": "Bengaluru East", "locality": "Whitefield", "pincode": "560066", "lat": 12.9698, "lon": 77.7500, "aliases": ["Bangalore"], "devanagari_state": "कर्नाटक", "devanagari_district": "बंगळुरू", "devanagari_subdistrict": "बंगळुरू पूर्व", "devanagari_locality": "व्हाइटफील्ड"},
    {"state": "Karnataka", "state_code": "KA", "district": "Bengaluru Urban", "subdistrict": "Bengaluru South", "locality": "Koramangala", "pincode": "560034", "lat": 12.9352, "lon": 77.6245, "aliases": ["Bangalore"], "devanagari_state": "कर्नाटक", "devanagari_district": "बंगळुरू", "devanagari_subdistrict": "बंगळुरू दक्षिण", "devanagari_locality": "कोरामंगला"},
    {"state": "Karnataka", "state_code": "KA", "district": "Bengaluru Urban", "subdistrict": "Bengaluru South", "locality": "HSR Layout", "pincode": "560102", "lat": 12.9121, "lon": 77.6446, "aliases": ["Bangalore"], "devanagari_state": "कर्नाटक", "devanagari_district": "बंगळुरू", "devanagari_subdistrict": "बंगळुरू दक्षिण", "devanagari_locality": "एचएसआर लेआउट"},
    {"state": "Karnataka", "state_code": "KA", "district": "Bengaluru Urban", "subdistrict": "Bengaluru East", "locality": "Indiranagar", "pincode": "560038", "lat": 12.9784, "lon": 77.6408, "aliases": ["Bangalore"], "devanagari_state": "कर्नाटक", "devanagari_district": "बंगळुरू", "devanagari_subdistrict": "बंगळुरू पूर्व", "devanagari_locality": "इंदिरानगर"},
    {"state": "Karnataka", "state_code": "KA", "district": "Bengaluru Urban", "subdistrict": "Bengaluru South", "locality": "Electronic City", "pincode": "560100", "lat": 12.8399, "lon": 77.6770, "aliases": ["Bangalore"], "devanagari_state": "कर्नाटक", "devanagari_district": "बंगळुरू", "devanagari_subdistrict": "बंगळुरू दक्षिण", "devanagari_locality": "इलेक्ट्रॉनिक सिटी"},
    {"state": "Karnataka", "state_code": "KA", "district": "Mysuru", "subdistrict": "Mysuru", "locality": "Gokulam", "pincode": "570002", "lat": 12.3270, "lon": 76.6260, "aliases": ["Mysore"], "devanagari_state": "कर्नाटक", "devanagari_district": "म्हैसूर", "devanagari_subdistrict": "म्हैसूर", "devanagari_locality": "गोकुलम"},

    # Delhi NCR
    {"state": "Delhi", "state_code": "DL", "district": "New Delhi", "subdistrict": "Chanakyapuri", "locality": "Connaught Place", "pincode": "110001", "lat": 28.6315, "lon": 77.2167, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "नई दिल्ली", "devanagari_subdistrict": "चाणक्यपुरी", "devanagari_locality": "कनॉट प्लेस"},
    {"state": "Delhi", "state_code": "DL", "district": "South Delhi", "subdistrict": "Hauz Khas", "locality": "Hauz Khas", "pincode": "110016", "lat": 28.5494, "lon": 77.2001, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "दक्षिण दिल्ली", "devanagari_subdistrict": "हौज खास", "devanagari_locality": "हौज खास"},
    {"state": "Delhi", "state_code": "DL", "district": "South Delhi", "subdistrict": "Saket", "locality": "Saket", "pincode": "110017", "lat": 28.5244, "lon": 77.2185, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "दक्षिण दिल्ली", "devanagari_subdistrict": "साकेत", "devanagari_locality": "साकेत"},
    {"state": "Delhi", "state_code": "DL", "district": "Central Delhi", "subdistrict": "Karol Bagh", "locality": "Karol Bagh", "pincode": "110005", "lat": 28.6517, "lon": 77.1906, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "मध्य दिल्ली", "devanagari_subdistrict": "करोल बाग", "devanagari_locality": "करोल बाग"},
    {"state": "Delhi", "state_code": "DL", "district": "South West Delhi", "subdistrict": "Dwarka", "locality": "Dwarka", "pincode": "110075", "lat": 28.5921, "lon": 77.0460, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "दक्षिण पश्चिम दिल्ली", "devanagari_subdistrict": "द्वारका", "devanagari_locality": "द्वारका"},
    {"state": "Delhi", "state_code": "DL", "district": "North West Delhi", "subdistrict": "Rohini", "locality": "Rohini", "pincode": "110085", "lat": 28.7495, "lon": 77.0565, "aliases": [], "devanagari_state": "दिल्ली", "devanagari_district": "उत्तर पश्चिम दिल्ली", "devanagari_subdistrict": "रोहिणी", "devanagari_locality": "रोहिणी"},

    # West Bengal
    {"state": "West Bengal", "state_code": "WB", "district": "Kolkata", "subdistrict": "Alipore", "locality": "Salt Lake", "pincode": "700091", "lat": 22.5867, "lon": 88.4178, "aliases": ["Calcutta"], "devanagari_state": "पश्चिम बंगाल", "devanagari_district": "कोलकाता", "devanagari_subdistrict": "अलिपूर", "devanagari_locality": "सॉल्ट लेक"},
    {"state": "West Bengal", "state_code": "WB", "district": "North 24 Parganas", "subdistrict": "Barasat", "locality": "Rajarhat", "pincode": "700135", "lat": 22.6231, "lon": 88.5134, "aliases": [], "devanagari_state": "पश्चिम बंगाल", "devanagari_district": "उत्तर 24 परगना", "devanagari_subdistrict": "बारासात", "devanagari_locality": "राजारहाट"},
    {"state": "West Bengal", "state_code": "WB", "district": "North 24 Parganas", "subdistrict": "Barasat", "locality": "New Town", "pincode": "700156", "lat": 22.5896, "lon": 88.4746, "aliases": [], "devanagari_state": "पश्चिम बंगाल", "devanagari_district": "उत्तर 24 परगना", "devanagari_subdistrict": "बारासात", "devanagari_locality": "न्यू टाउन"},

    # Tamil Nadu
    {"state": "Tamil Nadu", "state_code": "TN", "district": "Chennai", "subdistrict": "Mylapore", "locality": "T Nagar", "pincode": "600017", "lat": 13.0418, "lon": 80.2341, "aliases": ["Madras"], "devanagari_state": "तमिळनाडू", "devanagari_district": "चेन्नई", "devanagari_subdistrict": "मयिलापूर", "devanagari_locality": "टी नगर"},
    {"state": "Tamil Nadu", "state_code": "TN", "district": "Chennai", "subdistrict": "Guindy", "locality": "Adyar", "pincode": "600020", "lat": 13.0012, "lon": 80.2565, "aliases": ["Madras"], "devanagari_state": "तमिळनाडू", "devanagari_district": "चेन्नई", "devanagari_subdistrict": "गिंडी", "devanagari_locality": "अडयार"},

    # Telangana
    {"state": "Telangana", "state_code": "TG", "district": "Hyderabad", "subdistrict": "Shaikpet", "locality": "HITEC City", "pincode": "500081", "lat": 17.4435, "lon": 78.3772, "aliases": [], "devanagari_state": "तेलंगणा", "devanagari_district": "हैदराबाद", "devanagari_subdistrict": "शेखपेट", "devanagari_locality": "हायटेक सिटी"},
    {"state": "Telangana", "state_code": "TG", "district": "Hyderabad", "subdistrict": "Ameerpet", "locality": "Banjara Hills", "pincode": "500034", "lat": 17.4156, "lon": 78.4357, "aliases": [], "devanagari_state": "तेलंगणा", "devanagari_district": "हैदराबाद", "devanagari_subdistrict": "अमीरपेट", "devanagari_locality": "बंजारा हिल्स"},

    # Gujarat
    {"state": "Gujarat", "state_code": "GJ", "district": "Ahmedabad", "subdistrict": "Daskroi", "locality": "Navrangpura", "pincode": "380009", "lat": 23.0365, "lon": 72.5611, "aliases": ["Amdavad"], "devanagari_state": "गुजरात", "devanagari_district": "अहमदाबाद", "devanagari_subdistrict": "दशक्रोई", "devanagari_locality": "नवरंगपुरा"},
    {"state": "Gujarat", "state_code": "GJ", "district": "Surat", "subdistrict": "Chorasi", "locality": "Vesu", "pincode": "395007", "lat": 21.1418, "lon": 72.7709, "aliases": [], "devanagari_state": "गुजरात", "devanagari_district": "सुरत", "devanagari_subdistrict": "चौरासी", "devanagari_locality": "वेसू"},

    # Rajasthan
    {"state": "Rajasthan", "state_code": "RJ", "district": "Jaipur", "subdistrict": "Sanganer", "locality": "Malviya Nagar", "pincode": "302017", "lat": 26.8532, "lon": 75.8052, "aliases": [], "devanagari_state": "राजस्थान", "devanagari_district": "जयपुर", "devanagari_subdistrict": "सांगानेर", "devanagari_locality": "मालवीय नगर"},
    {"state": "Rajasthan", "state_code": "RJ", "district": "Jaipur", "subdistrict": "Jaipur", "locality": "Vaishali Nagar", "pincode": "302021", "lat": 26.9069, "lon": 75.7434, "aliases": [], "devanagari_state": "राजस्थान", "devanagari_district": "जयपुर", "devanagari_subdistrict": "जयपुर", "devanagari_locality": "वैशाली नगर"},

    # Uttar Pradesh
    {"state": "Uttar Pradesh", "state_code": "UP", "district": "Gautam Buddha Nagar", "subdistrict": "Dadri", "locality": "Sector 62", "pincode": "201309", "lat": 28.6258, "lon": 77.3653, "aliases": ["Noida"], "devanagari_state": "उत्तर प्रदेश", "devanagari_district": "गौतम बुद्ध नगर", "devanagari_subdistrict": "दादरी", "devanagari_locality": "सेक्टर 62"},
    {"state": "Uttar Pradesh", "state_code": "UP", "district": "Lucknow", "subdistrict": "Lucknow", "locality": "Gomti Nagar", "pincode": "226010", "lat": 26.8529, "lon": 80.9962, "aliases": [], "devanagari_state": "उत्तर प्रदेश", "devanagari_district": "लखनऊ", "devanagari_subdistrict": "लखनऊ", "devanagari_locality": "गोमती नगर"},
]

PREMISE_TEMPLATES = [
    "Flat {num}, {bldg}",
    "Shop {num}, {market}",
    "Plot {num}, Sector {sec}",
    "House No. {num}, {society}",
    "Tower {t_num}, {complex}",
    "Building {bldg}",
    "Suite {num}, {bldg}",
    "{bldg}, 3rd Floor",
]

BUILDINGS = [
    "Ganga Carnation", "EON Free Zone", "World Trade Center", "Kumar Primavera",
    "Prestige Tech Park", "Cyber City", "Pheonix Marketcity", "Infinity Tower",
    "Gokul Dham", "Shanti Niketan", "Vasundhara Complex", "Surya Enclave",
    "Marvel Cerise", "Godrej Woods", "Sobha Dream Acres", "Brigade Gateway"
]

ROADS = [
    "Main Road", "MG Road", "Ring Road", "Bypass Highway", "Station Road",
    "Airport Road", "Link Road", "DP Road", "Outer Ring Road", "Park Street"
]

LANDMARKS = [
    "Near Metro Station", "Opposite City Mall", "Behind Police Station",
    "Near Bus Stand", "Beside Apollo Hospital", "Near Tech Park",
    "Opposite Railway Station", "Near Central Bank", "Behind HP Petrol Pump"
]

AMBIGUOUS_ENTITIES = [
    {
        "name": "Bilaspur",
        "loc1": {"state": "Chhattisgarh", "district": "Bilaspur", "pincode": "495001"},
        "loc2": {"state": "Himachal Pradesh", "district": "Bilaspur", "pincode": "174001"}
    },
    {
        "name": "Rampur",
        "loc1": {"state": "Uttar Pradesh", "district": "Rampur", "pincode": "244901"},
        "loc2": {"state": "Bihar", "district": "Gaya", "pincode": "823001"}
    },
    {
        "name": "Rajapur",
        "loc1": {"state": "Maharashtra", "district": "Ratnagiri", "pincode": "416702"},
        "loc2": {"state": "Uttar Pradesh", "district": "Chitrakoot", "pincode": "210207"}
    },
    {
        "name": "Aurangabad",
        "loc1": {"state": "Maharashtra", "district": "Chhatrapati Sambhajinagar", "pincode": "431001"},
        "loc2": {"state": "Bihar", "district": "Aurangabad", "pincode": "824101"}
    },
    {
        "name": "Fatehpur",
        "loc1": {"state": "Uttar Pradesh", "district": "Fatehpur", "pincode": "212601"},
        "loc2": {"state": "Rajasthan", "district": "Sikar", "pincode": "332301"}
    }
]


class BenchmarkGenerator:
    """Generates balanced, deterministic benchmark test suites for GeoVerify India."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.case_counter = 1

    def _next_id(self) -> str:
        cid = f"GV-{self.case_counter:06d}"
        self.case_counter += 1
        return cid

    def generate(self, target_size: int = 1000) -> BenchmarkDataset:
        cases: List[BenchmarkRecord] = []

        # Target distribution across 19 categories
        # Aim for at least ~40-80 cases per category to reach target_size
        per_cat_target = max(25, target_size // 19)

        # 1. COMPLETE_VALID (Complete 5-tier addresses)
        for i in range(per_cat_target + 20):
            ent = random.choice(BASE_ENTITIES)
            p_tpl = random.choice(PREMISE_TEMPLATES)
            premise = p_tpl.format(
                num=random.randint(101, 909),
                bldg=random.choice(BUILDINGS),
                market=random.choice(BUILDINGS),
                sec=random.randint(1, 45),
                society=random.choice(BUILDINGS),
                t_num=random.choice(["A", "B", "C", "T1", "T2"]),
                complex=random.choice(BUILDINGS)
            )
            lm = random.choice(LANDMARKS)
            addr = f"{premise}, {lm}, {ent['locality']}, {ent['subdistrict']}, {ent['district']}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], subdistrict=ent["subdistrict"],
                    locality=ent["locality"], pincode=ent["pincode"],
                    latitude=ent["lat"], longitude=ent["lon"]
                ),
                category=BenchmarkCategory.COMPLETE_VALID,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.COMPLETE, ambiguity=False)
            ))

        # 2. PARTIAL_VALID (Valid without PIN or subdistrict -> CONSISTENT status)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            addr = f"{ent['locality']}, {ent['district']}, {ent['state']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    latitude=ent["lat"], longitude=ent["lon"]
                ),
                category=BenchmarkCategory.PARTIAL_VALID,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.CONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False)
            ))

        # 3. INFORMAL_SLANG (Colloquial formatting without PIN -> CONSISTENT status)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            prefix = random.choice(["near", "opp", "opposite to", "behind", "adjacent", "just after"])
            suffix = random.choice(["side", "area", "chowk", "circle", "post"])
            addr = f"{prefix} {ent['locality']} {suffix}, {ent['district']}, {ent['state']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"]
                ),
                category=BenchmarkCategory.INFORMAL_SLANG,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.CONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False)
            ))

        # 4. DEVANAGARI_HINDI (Hindi Devanagari addresses)
        hindi_entities = [e for e in BASE_ENTITIES if e.get("devanagari_state")]
        for i in range(per_cat_target):
            ent = random.choice(hindi_entities)
            addr = f"{ent['devanagari_locality']}, {ent['devanagari_district']}, {ent['devanagari_state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.DEVANAGARI_HINDI,
                language=Language.HI,
                script=Script.DEVANAGARI,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False)
            ))

        # 5. DEVANAGARI_MARATHI (Marathi Devanagari with prefixes)
        mh_entities = [e for e in BASE_ENTITIES if e["state"] == "Maharashtra"]
        for i in range(per_cat_target):
            ent = random.choice(mh_entities)
            addr = f"गाव: {ent['devanagari_locality']}, तालुका: {ent['devanagari_subdistrict']}, जिल्हा: {ent['devanagari_district']}, राज्य: {ent['devanagari_state']}, पिन: {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], subdistrict=ent["subdistrict"],
                    locality=ent["locality"], pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.DEVANAGARI_MARATHI,
                language=Language.MR,
                script=Script.DEVANAGARI,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.COMPLETE, ambiguity=False)
            ))

        # 6. MIXED_LANGUAGE (Mixed Latin and Devanagari tokens)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            addr = f"{ent['locality']}, {ent.get('devanagari_district', ent['district'])}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.MIXED_LANGUAGE,
                language=Language.MIXED_MR_EN if ent["state"] == "Maharashtra" else Language.MIXED_HI_EN,
                script=Script.MIXED,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False)
            ))

        # 7. TYPO (Controlled 1-2 char typo)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            loc_typo = ent["locality"] + ("i" if not ent["locality"].endswith("i") else "a")
            addr = f"{loc_typo}, {ent['district']}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.TYPO,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="char_typo")
            ))

        # 8. MISSPELLING (Phonetic common misspellings)
        misspelling_map = {
            "Maharashtra": "Maharastra",
            "Bengaluru Urban": "Bengalru",
            "Ahmedabad": "Ahamdabad",
            "Kolkata": "Kolkatta",
            "Pune": "Poone"
        }
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            st_miss = misspelling_map.get(ent["state"], ent["state"])
            dist_miss = misspelling_map.get(ent["district"], ent["district"])
            addr = f"{ent['locality']}, {dist_miss}, {st_miss} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.MISSPELLING,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="phonetic_misspelling")
            ))

        # 9. HISTORICAL_ALIAS (Poona, Bombay, Calcutta, Madras, Bangalore)
        alias_entities = [e for e in BASE_ENTITIES if e.get("aliases")]
        for i in range(per_cat_target):
            ent = random.choice(alias_entities)
            alias = ent["aliases"][0]
            addr = f"{ent['locality']}, {alias}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], state_code=ent["state_code"],
                    district=ent["district"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.HISTORICAL_ALIAS,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.VERIFIED,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="historical_alias")
            ))

        # 10. AMBIGUOUS_LOCALITY (Homonymous town/district names)
        for i in range(per_cat_target):
            amb = random.choice(AMBIGUOUS_ENTITIES)
            addr = amb["name"]
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(locality=amb["name"]),
                category=BenchmarkCategory.AMBIGUOUS_LOCALITY,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.AMBIGUOUS,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.MINIMAL, ambiguity=True)
            ))

        # 11. DISTRICT_MISMATCH (Locality placed in wrong district in same state)
        for i in range(per_cat_target):
            ent1 = random.choice(BASE_ENTITIES)
            # Find another entity in same state but different district
            same_state = [e for e in BASE_ENTITIES if e["state"] == ent1["state"] and e["district"] != ent1["district"]]
            if not same_state:
                wrong_dist = "Kolhapur" if ent1["district"] != "Kolhapur" else "Nashik"
            else:
                wrong_dist = random.choice(same_state)["district"]

            addr = f"{ent1['locality']}, {wrong_dist}, {ent1['state']} {ent1['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent1["state"], state_code=ent1["state_code"],
                    district=ent1["district"], locality=ent1["locality"],
                    pincode=ent1["pincode"]
                ),
                category=BenchmarkCategory.DISTRICT_MISMATCH,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.INCONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="district_mismatch")
            ))

        # 12. STATE_MISMATCH (District placed in wrong state)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            wrong_state = "Karnataka" if ent["state"] != "Karnataka" else "Maharashtra"
            addr = f"{ent['district']}, {wrong_state} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"], pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.STATE_MISMATCH,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.INCONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.PARTIAL, ambiguity=False, perturbation_type="state_mismatch")
            ))

        # 13. SUBDISTRICT_MISMATCH (Locality paired with wrong subdistrict)
        for i in range(per_cat_target):
            ent = random.choice([e for e in BASE_ENTITIES if e["state"] == "Maharashtra"])
            wrong_sub = "Mulshi" if ent["subdistrict"] != "Mulshi" else "Haveli"
            addr = f"{ent['locality']}, {wrong_sub}, {ent['district']}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"],
                    subdistrict=ent["subdistrict"], locality=ent["locality"],
                    pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.SUBDISTRICT_MISMATCH,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.CONSISTENT,  # Sub-district warning or soft inconsistency
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.COMPLETE, ambiguity=False, perturbation_type="subdistrict_mismatch")
            ))

        # 14. LOCALITY_MISMATCH (Cross-state locality conflict)
        for i in range(per_cat_target):
            ent1 = random.choice([e for e in BASE_ENTITIES if e["state"] == "Maharashtra"])
            ent2 = random.choice([e for e in BASE_ENTITIES if e["state"] == "Karnataka"])
            addr = f"{ent1['locality']}, {ent2['district']}, {ent2['state']} {ent2['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent1["state"], district=ent1["district"], locality=ent1["locality"]
                ),
                category=BenchmarkCategory.LOCALITY_MISMATCH,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.INCONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="cross_state_locality_mismatch")
            ))

        # 15. PIN_MISMATCH (PIN circle conflicts with state)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            # Incompatible PIN (Circle 5 for MH, Circle 4 for KA, Circle 1 for South)
            wrong_pin = "560066" if ent["state_code"] == "MH" else "411014"
            addr = f"{ent['locality']}, {ent['district']}, {ent['state']} {wrong_pin}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"],
                    locality=ent["locality"], pincode=wrong_pin
                ),
                category=BenchmarkCategory.PIN_MISMATCH,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.NEEDS_REVIEW,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False, perturbation_type="pin_circle_mismatch")
            ))

        # 16. INVALID_PIN (Format violations)
        invalid_pins = ["12345", "011014", "41101A", "9999999", "PIN-CODE"]
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            inv_pin = random.choice(invalid_pins)
            addr = f"{ent['locality']}, {ent['district']}, {ent['state']} {inv_pin}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"], locality=ent["locality"]
                ),
                category=BenchmarkCategory.INVALID_PIN,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.NEEDS_REVIEW,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.PARTIAL, ambiguity=False, perturbation_type="invalid_pin_format")
            ))

        # 17. INCOMPLETE (Lacking state/district tokens)
        incomplete_inputs = [
            "Near Metro Station, Ring Road",
            "Near Bus Stand, Main Market",
            "Shop 12, MG Road",
            "Flat 402, Sunshine Apartments",
            "Near City Hospital",
            "Maharashtra"
        ]
        for i in range(per_cat_target):
            inp = random.choice(incomplete_inputs)
            exp_status = ExpectedStatus.NEEDS_REVIEW if inp == "Maharashtra" else ExpectedStatus.UNABLE_TO_VERIFY
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=inp,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(state="Maharashtra" if inp == "Maharashtra" else None),
                category=BenchmarkCategory.INCOMPLETE,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=exp_status,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.MINIMAL, ambiguity=False)
            ))

        # 18. WRONG_ADMIN_HIERARCHY (Inverted hierarchical levels)
        for i in range(per_cat_target):
            ent = random.choice(BASE_ENTITIES)
            addr = f"{ent['state']}, {ent['locality']}, {ent['district']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"], locality=ent["locality"]
                ),
                category=BenchmarkCategory.WRONG_ADMIN_HIERARCHY,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.CONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.PARTIAL, ambiguity=False, perturbation_type="inverted_hierarchy")
            ))

        # 19. NEARBY_BUT_WRONG_LOCALITY (Adjacent locality with wrong PIN)
        for i in range(per_cat_target):
            ent = random.choice([e for e in BASE_ENTITIES if e["state"] == "Maharashtra"])
            adj_loc = "Viman Nagar" if ent["locality"] == "Kharadi" else "Kharadi"
            addr = f"Near EON IT Park, {adj_loc}, {ent['district']}, {ent['state']} {ent['pincode']}"
            cases.append(BenchmarkRecord(
                id=self._next_id(),
                address=addr,
                source_type=SourceType.SYNTHETIC,
                ground_truth=GroundTruth(
                    state=ent["state"], district=ent["district"], locality=adj_loc, pincode=ent["pincode"]
                ),
                category=BenchmarkCategory.NEARBY_BUT_WRONG_LOCALITY,
                language=Language.EN,
                script=Script.LATIN,
                expected_status=ExpectedStatus.CONSISTENT,
                metadata=BenchmarkMetadata(completeness=CompletenessLevel.ADEQUATE, ambiguity=False)
            ))

        # Shuffle deterministically
        random.shuffle(cases)

        return BenchmarkDataset(
            version="1.0.0",
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_cases=len(cases),
            cases=cases
        )


def export_dataset(dataset: BenchmarkDataset, output_dir: Path):
    """Exports dataset to JSON and CSV formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / "benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset.model_dump(), f, indent=2, ensure_ascii=False)
    
    csv_path = output_dir / "benchmark.csv"
    import pandas as pd
    rows = []
    for c in dataset.cases:
        rows.append({
            "id": c.id,
            "address": c.address,
            "source_type": c.source_type.value,
            "category": c.category.value,
            "language": c.language.value,
            "script": c.script.value,
            "expected_status": c.expected_status.value,
            "expected_state": c.ground_truth.state,
            "expected_district": c.ground_truth.district,
            "expected_subdistrict": c.ground_truth.subdistrict,
            "expected_locality": c.ground_truth.locality,
            "expected_pincode": c.ground_truth.pincode,
            "completeness": c.metadata.completeness.value,
            "ambiguity": c.metadata.ambiguity,
            "perturbation_type": c.metadata.perturbation_type or ""
        })
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Generated {len(dataset.cases)} benchmark cases -> {json_path} & {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate GeoVerify India Benchmark Dataset")
    parser.add_argument("--size", type=int, default=1050, help="Target total benchmark test cases (default: 1050)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument("--output", type=str, default="evaluation/datasets", help="Output directory path")
    args = parser.parse_args()

    gen = BenchmarkGenerator(seed=args.seed)
    ds = gen.generate(target_size=args.size)
    export_dataset(ds, Path(args.output))


if __name__ == "__main__":
    main()
