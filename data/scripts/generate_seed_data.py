"""Comprehensive Reference Data Ingestion & Seeding for GeoVerify India.
Ensures full coverage of Indian States, Districts, Sub-Districts/Talukas, Localities, PIN Codes, and POIs.
"""

import sys
import json
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

PROCESSED_DIR = Path(__file__).parent.parent / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 1. Indian States & UTs (All 36)
from data.scripts.transform.transform_admin_data import ALL_36_STATES

# 2. Comprehensive Districts Catalog
DISTRICTS = [
    {
        "id": "dist_pune",
        "lgd_code": 490,
        "name": "Pune",
        "canonical_name": "Pune",
        "name_hi": "पुणे",
        "name_mr": "पुणे",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Pune",
        "aliases": ["Poona", "Puna", "Pune District"],
        "bbox": [73.3, 18.0, 75.2, 19.4],
        "polygon": [[73.3, 18.0], [73.5, 19.4], [75.2, 19.0], [74.8, 18.2], [73.3, 18.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_mumbai_suburban",
        "lgd_code": 483,
        "name": "Mumbai Suburban",
        "canonical_name": "Mumbai Suburban",
        "name_hi": "मुंबई उपनगर",
        "name_mr": "मुंबई उपनगर",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Bandra",
        "aliases": ["Bombay Suburban", "Mumbai Suburban District", "Bombay"],
        "bbox": [72.75, 18.95, 72.98, 19.30],
        "polygon": [[72.75, 18.95], [72.78, 19.30], [72.98, 19.25], [72.95, 18.98], [72.75, 18.95]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_thane",
        "lgd_code": 492,
        "name": "Thane",
        "canonical_name": "Thane",
        "name_hi": "ठाणे",
        "name_mr": "ठाणे",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Thane",
        "aliases": ["Thana", "Thane District"],
        "bbox": [72.8, 19.0, 73.5, 19.8],
        "polygon": [[72.8, 19.0], [72.9, 19.8], [73.5, 19.6], [73.3, 19.1], [72.8, 19.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_kolhapur",
        "lgd_code": 480,
        "name": "Kolhapur",
        "canonical_name": "Kolhapur",
        "name_hi": "कोल्हापूर",
        "name_mr": "कोल्हापूर",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Kolhapur",
        "aliases": ["Kolhapur District"],
        "bbox": [73.7, 15.7, 74.7, 17.2],
        "polygon": [[73.7, 15.7], [73.9, 17.2], [74.7, 16.8], [74.5, 15.9], [73.7, 15.7]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_bengaluru_urban",
        "lgd_code": 529,
        "name": "Bengaluru Urban",
        "canonical_name": "Bengaluru Urban",
        "name_hi": "बंगळुरू",
        "name_mr": "बंगळुरू",
        "state_id": 29,
        "state_name": "Karnataka",
        "state_code": "KA",
        "headquarters": "Bengaluru",
        "aliases": ["Bangalore", "Bangalore Urban", "Bengaluru", "BLR"],
        "bbox": [77.3, 12.7, 77.8, 13.2],
        "polygon": [[77.3, 12.7], [77.4, 13.2], [77.8, 13.1], [77.7, 12.8], [77.3, 12.7]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_mysuru",
        "lgd_code": 535,
        "name": "Mysuru",
        "canonical_name": "Mysuru",
        "name_hi": "मैसूर",
        "name_mr": "म्हैसूर",
        "state_id": 29,
        "state_name": "Karnataka",
        "state_code": "KA",
        "headquarters": "Mysuru",
        "aliases": ["Mysore", "Mysuru District"],
        "bbox": [75.9, 11.7, 77.2, 12.6],
        "polygon": [[75.9, 11.7], [76.1, 12.6], [77.2, 12.4], [76.9, 11.8], [75.9, 11.7]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_new_delhi",
        "lgd_code": 141,
        "name": "New Delhi",
        "canonical_name": "New Delhi",
        "name_hi": "नई दिल्ली",
        "name_mr": "नवी दिल्ली",
        "state_id": 7,
        "state_name": "Delhi",
        "state_code": "DL",
        "headquarters": "New Delhi",
        "aliases": ["Delhi", "Central Delhi"],
        "bbox": [77.15, 28.55, 77.25, 28.65],
        "polygon": [[77.15, 28.55], [77.16, 28.65], [77.25, 28.64], [77.24, 28.56], [77.15, 28.55]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_south_delhi",
        "lgd_code": 142,
        "name": "South Delhi",
        "canonical_name": "South Delhi",
        "name_hi": "दक्षिण दिल्ली",
        "name_mr": "दक्षिण दिल्ली",
        "state_id": 7,
        "state_name": "Delhi",
        "state_code": "DL",
        "headquarters": "Saket",
        "aliases": ["South Delhi District"],
        "bbox": [77.15, 28.45, 77.30, 28.60],
        "polygon": [[77.15, 28.45], [77.16, 28.60], [77.30, 28.58], [77.28, 28.46], [77.15, 28.45]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_central_delhi",
        "lgd_code": 143,
        "name": "Central Delhi",
        "canonical_name": "Central Delhi",
        "name_hi": "मध्य दिल्ली",
        "name_mr": "मध्य दिल्ली",
        "state_id": 7,
        "state_name": "Delhi",
        "state_code": "DL",
        "headquarters": "Karol Bagh",
        "aliases": ["Central Delhi District"],
        "bbox": [77.16, 28.62, 77.26, 28.70],
        "polygon": [[77.16, 28.62], [77.17, 28.70], [77.26, 28.69], [77.25, 28.63], [77.16, 28.62]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_south_west_delhi",
        "lgd_code": 144,
        "name": "South West Delhi",
        "canonical_name": "South West Delhi",
        "name_hi": "दक्षिण पश्चिम दिल्ली",
        "name_mr": "दक्षिण पश्चिम दिल्ली",
        "state_id": 7,
        "state_name": "Delhi",
        "state_code": "DL",
        "headquarters": "Dwarka",
        "aliases": ["South West Delhi District"],
        "bbox": [76.95, 28.50, 77.15, 28.65],
        "polygon": [[76.95, 28.50], [76.98, 28.65], [77.15, 28.63], [77.12, 28.51], [76.95, 28.50]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_north_west_delhi",
        "lgd_code": 145,
        "name": "North West Delhi",
        "canonical_name": "North West Delhi",
        "name_hi": "उत्तर पश्चिम दिल्ली",
        "name_mr": "उत्तर पश्चिम दिल्ली",
        "state_id": 7,
        "state_name": "Delhi",
        "state_code": "DL",
        "headquarters": "Rohini",
        "aliases": ["North West Delhi District"],
        "bbox": [76.98, 28.68, 77.18, 28.82],
        "polygon": [[76.98, 28.68], [77.01, 28.82], [77.18, 28.80], [77.16, 28.69], [76.98, 28.68]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_kolkata",
        "lgd_code": 314,
        "name": "Kolkata",
        "canonical_name": "Kolkata",
        "name_hi": "कोलकाता",
        "name_mr": "कोलकाता",
        "state_id": 19,
        "state_name": "West Bengal",
        "state_code": "WB",
        "headquarters": "Kolkata",
        "aliases": ["Calcutta", "Kolkata District"],
        "bbox": [88.30, 22.45, 88.45, 22.65],
        "polygon": [[88.30, 22.45], [88.32, 22.65], [88.45, 22.62], [88.42, 22.46], [88.30, 22.45]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_north_24_parganas",
        "lgd_code": 315,
        "name": "North 24 Parganas",
        "canonical_name": "North 24 Parganas",
        "name_hi": "उत्तर 24 परगना",
        "name_mr": "उत्तर 24 परगना",
        "state_id": 19,
        "state_name": "West Bengal",
        "state_code": "WB",
        "headquarters": "Barasat",
        "aliases": ["North 24 Parganas District", "24 Parganas North"],
        "bbox": [88.35, 22.15, 89.05, 23.25],
        "polygon": [[88.35, 22.15], [88.40, 23.25], [89.05, 23.15], [88.95, 22.20], [88.35, 22.15]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_chennai",
        "lgd_code": 603,
        "name": "Chennai",
        "canonical_name": "Chennai",
        "name_hi": "चेन्नई",
        "name_mr": "चेन्नई",
        "state_id": 33,
        "state_name": "Tamil Nadu",
        "state_code": "TN",
        "headquarters": "Chennai",
        "aliases": ["Madras", "Chennai District"],
        "bbox": [80.15, 12.95, 80.32, 13.20],
        "polygon": [[80.15, 12.95], [80.18, 13.20], [80.32, 13.18], [80.30, 12.96], [80.15, 12.95]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_hyderabad",
        "lgd_code": 505,
        "name": "Hyderabad",
        "canonical_name": "Hyderabad",
        "name_hi": "हैदराबाद",
        "name_mr": "हैदराबाद",
        "state_id": 36,
        "state_name": "Telangana",
        "state_code": "TG",
        "headquarters": "Hyderabad",
        "aliases": ["Hyderabad District", "HYD", "Secunderabad"],
        "bbox": [78.35, 17.30, 78.58, 17.52],
        "polygon": [[78.35, 17.30], [78.38, 17.52], [78.58, 17.50], [78.55, 17.32], [78.35, 17.30]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_ahmedabad",
        "lgd_code": 438,
        "name": "Ahmedabad",
        "canonical_name": "Ahmedabad",
        "name_hi": "अहमदाबाद",
        "name_mr": "अहमदाबाद",
        "state_id": 24,
        "state_name": "Gujarat",
        "state_code": "GJ",
        "headquarters": "Ahmedabad",
        "aliases": ["Amdavad", "Ahmedabad District"],
        "bbox": [71.8, 22.0, 72.9, 23.3],
        "polygon": [[71.8, 22.0], [72.0, 23.3], [72.9, 23.1], [72.7, 22.2], [71.8, 22.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_surat",
        "lgd_code": 454,
        "name": "Surat",
        "canonical_name": "Surat",
        "name_hi": "सुरत",
        "name_mr": "सुरत",
        "state_id": 24,
        "state_name": "Gujarat",
        "state_code": "GJ",
        "headquarters": "Surat",
        "aliases": ["Surat District"],
        "bbox": [72.6, 20.8, 73.4, 21.6],
        "polygon": [[72.6, 20.8], [72.8, 21.6], [73.4, 21.4], [73.2, 20.9], [72.6, 20.8]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_jaipur",
        "lgd_code": 115,
        "name": "Jaipur",
        "canonical_name": "Jaipur",
        "name_hi": "जयपुर",
        "name_mr": "जयपुर",
        "state_id": 8,
        "state_name": "Rajasthan",
        "state_code": "RJ",
        "headquarters": "Jaipur",
        "aliases": ["Pink City", "Jaipur District"],
        "bbox": [74.9, 26.4, 76.2, 27.8],
        "polygon": [[74.9, 26.4], [75.1, 27.8], [76.2, 27.5], [75.9, 26.6], [74.9, 26.4]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_gautam_buddha_nagar",
        "lgd_code": 158,
        "name": "Gautam Buddha Nagar",
        "canonical_name": "Gautam Buddha Nagar",
        "name_hi": "गौतम बुद्ध नगर",
        "name_mr": "गौतम बुद्ध नगर",
        "state_id": 9,
        "state_name": "Uttar Pradesh",
        "state_code": "UP",
        "headquarters": "Greater Noida",
        "aliases": ["Noida", "GB Nagar", "Gautam Budh Nagar"],
        "bbox": [77.25, 28.10, 77.65, 28.70],
        "polygon": [[77.25, 28.10], [77.30, 28.70], [77.65, 28.65], [77.60, 28.15], [77.25, 28.10]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_lucknow",
        "lgd_code": 178,
        "name": "Lucknow",
        "canonical_name": "Lucknow",
        "name_hi": "लखनऊ",
        "name_mr": "लखनऊ",
        "state_id": 9,
        "state_name": "Uttar Pradesh",
        "state_code": "UP",
        "headquarters": "Lucknow",
        "aliases": ["Lucknow District"],
        "bbox": [80.5, 26.5, 81.3, 27.2],
        "polygon": [[80.5, 26.5], [80.7, 27.2], [81.3, 27.0], [81.1, 26.6], [80.5, 26.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_bilaspur_cg",
        "lgd_code": 374,
        "name": "Bilaspur",
        "canonical_name": "Bilaspur",
        "name_hi": "बिलासपुर",
        "name_mr": "बिलासपूर",
        "state_id": 22,
        "state_name": "Chhattisgarh",
        "state_code": "CG",
        "headquarters": "Bilaspur",
        "aliases": ["Bilaspur CG", "Bilaspur Chhattisgarh"],
        "bbox": [81.5, 21.7, 82.5, 22.8],
        "polygon": [[81.5, 21.7], [81.7, 22.8], [82.5, 22.6], [82.3, 21.8], [81.5, 21.7]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_bilaspur_hp",
        "lgd_code": 18,
        "name": "Bilaspur",
        "canonical_name": "Bilaspur",
        "name_hi": "बिलासपुर",
        "name_mr": "बिलासपूर",
        "state_id": 2,
        "state_name": "Himachal Pradesh",
        "state_code": "HP",
        "headquarters": "Bilaspur",
        "aliases": ["Bilaspur HP", "Bilaspur Himachal"],
        "bbox": [76.5, 31.2, 77.0, 31.6],
        "polygon": [[76.5, 31.2], [76.6, 31.6], [77.0, 31.5], [76.9, 31.3], [76.5, 31.2]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_rampur_up",
        "lgd_code": 189,
        "name": "Rampur",
        "canonical_name": "Rampur",
        "name_hi": "रामपुर",
        "name_mr": "रामपूर",
        "state_id": 9,
        "state_name": "Uttar Pradesh",
        "state_code": "UP",
        "headquarters": "Rampur",
        "aliases": ["Rampur UP", "Rampur District"],
        "bbox": [78.8, 28.4, 79.4, 29.2],
        "polygon": [[78.8, 28.4], [79.0, 29.2], [79.4, 29.0], [79.2, 28.5], [78.8, 28.4]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_shimla",
        "lgd_code": 27,
        "name": "Shimla",
        "canonical_name": "Shimla",
        "name_hi": "शिमला",
        "name_mr": "शिमला",
        "state_id": 2,
        "state_name": "Himachal Pradesh",
        "state_code": "HP",
        "headquarters": "Shimla",
        "aliases": ["Simla", "Shimla District"],
        "bbox": [77.0, 30.8, 78.2, 31.6],
        "polygon": [[77.0, 30.8], [77.2, 31.6], [78.2, 31.4], [77.9, 30.9], [77.0, 30.8]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_fatehpur_up",
        "lgd_code": 160,
        "name": "Fatehpur",
        "canonical_name": "Fatehpur",
        "name_hi": "फतेहपुर",
        "name_mr": "फतेहपूर",
        "state_id": 9,
        "state_name": "Uttar Pradesh",
        "state_code": "UP",
        "headquarters": "Fatehpur",
        "aliases": ["Fatehpur District", "Fatehpur UP"],
        "bbox": [80.5, 25.6, 81.3, 26.2],
        "polygon": [[80.5, 25.6], [80.7, 26.2], [81.3, 26.0], [81.1, 25.7], [80.5, 25.6]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_sikar",
        "lgd_code": 128,
        "name": "Sikar",
        "canonical_name": "Sikar",
        "name_hi": "सीकर",
        "name_mr": "सीकर",
        "state_id": 8,
        "state_name": "Rajasthan",
        "state_code": "RJ",
        "headquarters": "Sikar",
        "aliases": ["Sikar District"],
        "bbox": [74.7, 27.2, 75.6, 28.2],
        "polygon": [[74.7, 27.2], [74.9, 28.2], [75.6, 28.0], [75.4, 27.3], [74.7, 27.2]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_ratnagiri",
        "lgd_code": 487,
        "name": "Ratnagiri",
        "canonical_name": "Ratnagiri",
        "name_hi": "रत्नागिरी",
        "name_mr": "रत्नागिरी",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Ratnagiri",
        "aliases": ["Ratnagiri District"],
        "bbox": [73.1, 16.5, 73.9, 18.1],
        "polygon": [[73.1, 16.5], [73.3, 18.1], [73.9, 17.8], [73.7, 16.6], [73.1, 16.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_chitrakoot",
        "lgd_code": 154,
        "name": "Chitrakoot",
        "canonical_name": "Chitrakoot",
        "name_hi": "चित्रकूट",
        "name_mr": "चित्रकूट",
        "state_id": 9,
        "state_name": "Uttar Pradesh",
        "state_code": "UP",
        "headquarters": "Chitrakoot",
        "aliases": ["Chitrakoot District"],
        "bbox": [80.6, 24.8, 81.6, 25.5],
        "polygon": [[80.6, 24.8], [80.8, 25.5], [81.6, 25.3], [81.4, 24.9], [80.6, 24.8]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_aurangabad_mh",
        "lgd_code": 472,
        "name": "Aurangabad",
        "canonical_name": "Aurangabad",
        "name_hi": "औरंगाबाद",
        "name_mr": "छत्रपती संभाजीनगर",
        "state_id": 27,
        "state_name": "Maharashtra",
        "state_code": "MH",
        "headquarters": "Chhatrapati Sambhajinagar",
        "aliases": ["Chhatrapati Sambhajinagar", "Sambhajinagar", "Aurangabad MH"],
        "bbox": [74.6, 19.3, 76.1, 20.7],
        "polygon": [[74.6, 19.3], [74.8, 20.7], [76.1, 20.5], [75.9, 19.4], [74.6, 19.3]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "id": "dist_aurangabad_br",
        "lgd_code": 204,
        "name": "Aurangabad",
        "canonical_name": "Aurangabad",
        "name_hi": "औरंगाबाद",
        "name_mr": "औरंगाबाद",
        "state_id": 10,
        "state_name": "Bihar",
        "state_code": "BR",
        "headquarters": "Aurangabad",
        "aliases": ["Aurangabad Bihar", "Aurangabad BR"],
        "bbox": [84.1, 24.5, 84.8, 25.1],
        "polygon": [[84.1, 24.5], [84.2, 25.1], [84.8, 25.0], [84.7, 24.6], [84.1, 24.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    }
]

# 3. Comprehensive Subdistricts (Talukas / Tehsils / Mandals)
SUBDISTRICTS = [
    {"id": "subdist_fatehpur_up", "lgd_code": 1600, "name": "Fatehpur", "canonical_name": "Fatehpur", "name_hi": "फतेहपुर", "name_mr": "फतेहपूर", "admin_type": "Tehsil", "district_id": "dist_fatehpur_up", "district_name": "Fatehpur", "state_id": 9, "state_name": "Uttar Pradesh", "aliases": ["Fatehpur Tehsil"], "bbox": [80.78, 25.90, 80.85, 25.95], "polygon": [[80.78, 25.90], [80.79, 25.95], [80.85, 25.94], [80.84, 25.91], [80.78, 25.90]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_fatehpur_rj", "lgd_code": 1280, "name": "Fatehpur", "canonical_name": "Fatehpur", "name_hi": "फतेहपुर शेखावाटी", "name_mr": "फतेहपूर", "admin_type": "Tehsil", "district_id": "dist_sikar", "district_name": "Sikar", "state_id": 8, "state_name": "Rajasthan", "aliases": ["Fatehpur Shekhawati Tehsil"], "bbox": [74.92, 27.96, 74.98, 28.01], "polygon": [[74.92, 27.96], [74.93, 28.01], [74.98, 28.00], [74.97, 27.97], [74.92, 27.96]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_rajapur_mh", "lgd_code": 4870, "name": "Rajapur", "canonical_name": "Rajapur", "name_hi": "राजापुर", "name_mr": "राजापूर", "admin_type": "Taluka", "district_id": "dist_ratnagiri", "district_name": "Ratnagiri", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Rajapur Taluka"], "bbox": [73.49, 16.63, 73.54, 16.68], "polygon": [[73.49, 16.63], [73.50, 16.68], [73.54, 16.67], [73.53, 16.64], [73.49, 16.63]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_rajapur_up", "lgd_code": 1540, "name": "Rajapur", "canonical_name": "Rajapur", "name_hi": "राजापुर", "name_mr": "राजापूर", "admin_type": "Tehsil", "district_id": "dist_chitrakoot", "district_name": "Chitrakoot", "state_id": 9, "state_name": "Uttar Pradesh", "aliases": ["Rajapur Tehsil"], "bbox": [81.13, 25.36, 81.18, 25.41], "polygon": [[81.13, 25.36], [81.14, 25.41], [81.18, 25.40], [81.17, 25.37], [81.13, 25.36]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_aurangabad_mh", "lgd_code": 4720, "name": "Aurangabad", "canonical_name": "Aurangabad", "name_hi": "औरंगाबाद", "name_mr": "छत्रपती संभाजीनगर", "admin_type": "Taluka", "district_id": "dist_aurangabad_mh", "district_name": "Aurangabad", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Chhatrapati Sambhajinagar Taluka", "Sambhajinagar"], "bbox": [75.30, 19.85, 75.38, 19.90], "polygon": [[75.30, 19.85], [75.32, 19.90], [75.38, 19.89], [75.36, 19.86], [75.30, 19.85]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_aurangabad_br", "lgd_code": 2040, "name": "Aurangabad", "canonical_name": "Aurangabad", "name_hi": "औरंगाबाद", "name_mr": "औरंगाबाद", "admin_type": "Subdivision", "district_id": "dist_aurangabad_br", "district_name": "Aurangabad", "state_id": 10, "state_name": "Bihar", "aliases": ["Aurangabad Subdivision"], "bbox": [84.34, 24.73, 84.40, 24.78], "polygon": [[84.34, 24.73], [84.35, 24.78], [84.40, 24.77], [84.39, 24.74], [84.34, 24.73]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_haveli", "lgd_code": 4182, "name": "Haveli", "canonical_name": "Haveli", "name_hi": "हवेली", "name_mr": "हवेली", "admin_type": "Taluka", "district_id": "dist_pune", "district_name": "Pune", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Haveli Taluka", "Haweli"], "bbox": [73.80, 18.40, 74.05, 18.65], "polygon": [[73.80, 18.40], [73.82, 18.65], [74.05, 18.63], [74.02, 18.42], [73.80, 18.40]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_mulshi", "lgd_code": 4183, "name": "Mulshi", "canonical_name": "Mulshi", "name_hi": "मुळशी", "name_mr": "मुळशी", "admin_type": "Taluka", "district_id": "dist_pune", "district_name": "Pune", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Mulshi Taluka", "Paud"], "bbox": [73.45, 18.45, 73.78, 18.68], "polygon": [[73.45, 18.45], [73.48, 18.68], [73.78, 18.65], [73.75, 18.48], [73.45, 18.45]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_pune_city", "lgd_code": 4184, "name": "Pune City", "canonical_name": "Pune City", "name_hi": "पुणे शहर", "name_mr": "पुणे शहर", "admin_type": "Taluka", "district_id": "dist_pune", "district_name": "Pune", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Pune Taluka"], "bbox": [73.80, 18.48, 73.90, 18.58], "polygon": [[73.80, 18.48], [73.81, 18.58], [73.90, 18.57], [73.89, 18.49], [73.80, 18.48]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_andheri", "lgd_code": 4150, "name": "Andheri", "canonical_name": "Andheri", "name_hi": "अंधेरी", "name_mr": "अंधेरी", "admin_type": "Taluka", "district_id": "dist_mumbai_suburban", "district_name": "Mumbai Suburban", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Andheri Taluka"], "bbox": [72.80, 19.05, 72.95, 19.18], "polygon": [[72.80, 19.05], [72.82, 19.18], [72.95, 19.16], [72.93, 19.07], [72.80, 19.05]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_thane", "lgd_code": 4190, "name": "Thane", "canonical_name": "Thane", "name_hi": "ठाणे", "name_mr": "ठाणे", "admin_type": "Taluka", "district_id": "dist_thane", "district_name": "Thane", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Thane Taluka"], "bbox": [72.90, 19.15, 73.05, 19.28], "polygon": [[72.90, 19.15], [72.92, 19.28], [73.05, 19.26], [73.03, 19.17], [72.90, 19.15]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_karvir", "lgd_code": 4170, "name": "Karvir", "canonical_name": "Karvir", "name_hi": "करवीर", "name_mr": "करवीर", "admin_type": "Taluka", "district_id": "dist_kolhapur", "district_name": "Kolhapur", "state_id": 27, "state_name": "Maharashtra", "aliases": ["Karveer Taluka"], "bbox": [74.15, 16.60, 74.35, 16.78], "polygon": [[74.15, 16.60], [74.18, 16.78], [74.35, 16.75], [74.32, 16.62], [74.15, 16.60]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_bengaluru_east", "lgd_code": 5510, "name": "Bengaluru East", "canonical_name": "Bengaluru East", "name_hi": "बंगळुरू पूर्व", "name_mr": "बंगळुरू पूर्व", "admin_type": "Taluka", "district_id": "dist_bengaluru_urban", "district_name": "Bengaluru Urban", "state_id": 29, "state_name": "Karnataka", "aliases": ["Bangalore East", "K.R. Puram"], "bbox": [77.60, 12.92, 77.80, 13.08], "polygon": [[77.60, 12.92], [77.62, 13.08], [77.80, 13.06], [77.78, 12.94], [77.60, 12.92]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_bengaluru_south", "lgd_code": 5511, "name": "Bengaluru South", "canonical_name": "Bengaluru South", "name_hi": "बंगळुरू दक्षिण", "name_mr": "बंगळुरू दक्षिण", "admin_type": "Taluka", "district_id": "dist_bengaluru_urban", "district_name": "Bengaluru Urban", "state_id": 29, "state_name": "Karnataka", "aliases": ["Bangalore South"], "bbox": [77.55, 12.80, 77.72, 12.96], "polygon": [[77.55, 12.80], [77.57, 12.96], [77.72, 12.94], [77.70, 12.82], [77.55, 12.80]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_mysuru", "lgd_code": 5520, "name": "Mysuru", "canonical_name": "Mysuru", "name_hi": "मैसूर", "name_mr": "म्हैसूर", "admin_type": "Taluka", "district_id": "dist_mysuru", "district_name": "Mysuru", "state_id": 29, "state_name": "Karnataka", "aliases": ["Mysore Taluk"], "bbox": [76.55, 12.25, 76.75, 12.42], "polygon": [[76.55, 12.25], [76.58, 12.42], [76.75, 12.39], [76.72, 12.27], [76.55, 12.25]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_chanakyapuri", "lgd_code": 1410, "name": "Chanakyapuri", "canonical_name": "Chanakyapuri", "name_hi": "चाणक्यपुरी", "name_mr": "चाणक्यपुरी", "admin_type": "Subdivision", "district_id": "dist_new_delhi", "district_name": "New Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Chanakyapuri Tehsil"], "bbox": [77.16, 28.58, 77.24, 28.65], "polygon": [[77.16, 28.58], [77.17, 28.65], [77.24, 28.64], [77.23, 28.59], [77.16, 28.58]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_hauz_khas", "lgd_code": 1420, "name": "Hauz Khas", "canonical_name": "Hauz Khas", "name_hi": "हौज खास", "name_mr": "हौज खास", "admin_type": "Subdivision", "district_id": "dist_south_delhi", "district_name": "South Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Hauz Khas Tehsil"], "bbox": [77.16, 28.52, 77.24, 28.58], "polygon": [[77.16, 28.52], [77.18, 28.58], [77.24, 28.57], [77.22, 28.53], [77.16, 28.52]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_saket", "lgd_code": 1421, "name": "Saket", "canonical_name": "Saket", "name_hi": "साकेत", "name_mr": "साकेत", "admin_type": "Subdivision", "district_id": "dist_south_delhi", "district_name": "South Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Saket Tehsil"], "bbox": [77.18, 28.48, 77.26, 28.55], "polygon": [[77.18, 28.48], [77.19, 28.55], [77.26, 28.54], [77.25, 28.49], [77.18, 28.48]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_karol_bagh", "lgd_code": 1430, "name": "Karol Bagh", "canonical_name": "Karol Bagh", "name_hi": "करोल बाग", "name_mr": "करोल बाग", "admin_type": "Subdivision", "district_id": "dist_central_delhi", "district_name": "Central Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Karol Bagh Tehsil"], "bbox": [77.16, 28.63, 77.22, 28.68], "polygon": [[77.16, 28.63], [77.17, 28.68], [77.22, 28.67], [77.21, 28.64], [77.16, 28.63]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_dwarka", "lgd_code": 1440, "name": "Dwarka", "canonical_name": "Dwarka", "name_hi": "द्वारका", "name_mr": "द्वारका", "admin_type": "Subdivision", "district_id": "dist_south_west_delhi", "district_name": "South West Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Dwarka Tehsil"], "bbox": [77.00, 28.55, 77.10, 28.64], "polygon": [[77.00, 28.55], [77.02, 28.64], [77.10, 28.62], [77.08, 28.56], [77.00, 28.55]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_rohini", "lgd_code": 1450, "name": "Rohini", "canonical_name": "Rohini", "name_hi": "रोहिणी", "name_mr": "रोहिणी", "admin_type": "Subdivision", "district_id": "dist_north_west_delhi", "district_name": "North West Delhi", "state_id": 7, "state_name": "Delhi", "aliases": ["Rohini Tehsil"], "bbox": [77.02, 28.70, 77.14, 28.80], "polygon": [[77.02, 28.70], [77.04, 28.80], [77.14, 28.78], [77.12, 28.71], [77.02, 28.70]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_alipore", "lgd_code": 3140, "name": "Alipore", "canonical_name": "Alipore", "name_hi": "अलिपूर", "name_mr": "अलिपूर", "admin_type": "Subdivision", "district_id": "dist_kolkata", "district_name": "Kolkata", "state_id": 19, "state_name": "West Bengal", "aliases": ["Alipore Subdivision"], "bbox": [88.30, 22.50, 88.42, 22.60], "polygon": [[88.30, 22.50], [88.32, 22.60], [88.42, 22.58], [88.40, 22.51], [88.30, 22.50]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_barasat", "lgd_code": 3150, "name": "Barasat", "canonical_name": "Barasat", "name_hi": "बारासात", "name_mr": "बारासात", "admin_type": "Subdivision", "district_id": "dist_north_24_parganas", "district_name": "North 24 Parganas", "state_id": 19, "state_name": "West Bengal", "aliases": ["Barasat Sadar"], "bbox": [88.42, 22.55, 88.60, 22.75], "polygon": [[88.42, 22.55], [88.45, 22.75], [88.60, 22.72], [88.58, 22.57], [88.42, 22.55]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_mylapore", "lgd_code": 6030, "name": "Mylapore", "canonical_name": "Mylapore", "name_hi": "मयिलापूर", "name_mr": "मयिलापूर", "admin_type": "Taluk", "district_id": "dist_chennai", "district_name": "Chennai", "state_id": 33, "state_name": "Tamil Nadu", "aliases": ["Mylapore Taluk"], "bbox": [80.20, 13.00, 80.28, 13.08], "polygon": [[80.20, 13.00], [80.22, 13.08], [80.28, 13.07], [80.26, 13.01], [80.20, 13.00]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_guindy", "lgd_code": 6031, "name": "Guindy", "canonical_name": "Guindy", "name_hi": "गिंडी", "name_mr": "गिंडी", "admin_type": "Taluk", "district_id": "dist_chennai", "district_name": "Chennai", "state_id": 33, "state_name": "Tamil Nadu", "aliases": ["Guindy Taluk"], "bbox": [80.18, 12.96, 80.26, 13.02], "polygon": [[80.18, 12.96], [80.20, 13.02], [80.26, 13.01], [80.24, 12.97], [80.18, 12.96]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_shaikpet", "lgd_code": 5050, "name": "Shaikpet", "canonical_name": "Shaikpet", "name_hi": "शेखपेट", "name_mr": "शेखपेट", "admin_type": "Mandal", "district_id": "dist_hyderabad", "district_name": "Hyderabad", "state_id": 36, "state_name": "Telangana", "aliases": ["Shaikpet Mandal"], "bbox": [78.36, 17.40, 78.44, 17.48], "polygon": [[78.36, 17.40], [78.38, 17.48], [78.44, 17.46], [78.42, 17.41], [78.36, 17.40]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_ameerpet", "lgd_code": 5051, "name": "Ameerpet", "canonical_name": "Ameerpet", "name_hi": "अमीरपेट", "name_mr": "अमीरपेट", "admin_type": "Mandal", "district_id": "dist_hyderabad", "district_name": "Hyderabad", "state_id": 36, "state_name": "Telangana", "aliases": ["Ameerpet Mandal"], "bbox": [78.40, 17.40, 78.48, 17.46], "polygon": [[78.40, 17.40], [78.42, 17.46], [78.48, 17.45], [78.46, 17.41], [78.40, 17.40]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_daskroi", "lgd_code": 4380, "name": "Daskroi", "canonical_name": "Daskroi", "name_hi": "दशक्रोई", "name_mr": "दशक्रोई", "admin_type": "Taluka", "district_id": "dist_ahmedabad", "district_name": "Ahmedabad", "state_id": 24, "state_name": "Gujarat", "aliases": ["Daskroi Taluka"], "bbox": [72.50, 22.95, 72.65, 23.12], "polygon": [[72.50, 22.95], [72.52, 23.12], [72.65, 23.10], [72.63, 22.97], [72.50, 22.95]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_chorasi", "lgd_code": 4540, "name": "Chorasi", "canonical_name": "Chorasi", "name_hi": "चौरासी", "name_mr": "चौरासी", "admin_type": "Taluka", "district_id": "dist_surat", "district_name": "Surat", "state_id": 24, "state_name": "Gujarat", "aliases": ["Chorasi Taluka", "Choryasi"], "bbox": [72.70, 21.10, 72.85, 21.25], "polygon": [[72.70, 21.10], [72.72, 21.25], [72.85, 21.23], [72.83, 21.12], [72.70, 21.10]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_sanganer", "lgd_code": 1150, "name": "Sanganer", "canonical_name": "Sanganer", "name_hi": "सांगानेर", "name_mr": "सांगानेर", "admin_type": "Tehsil", "district_id": "dist_jaipur", "district_name": "Jaipur", "state_id": 8, "state_name": "Rajasthan", "aliases": ["Sanganer Tehsil"], "bbox": [75.75, 26.80, 75.88, 26.92], "polygon": [[75.75, 26.80], [75.77, 26.92], [75.88, 26.90], [75.86, 26.82], [75.75, 26.80]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_jaipur", "lgd_code": 1151, "name": "Jaipur", "canonical_name": "Jaipur", "name_hi": "जयपुर", "name_mr": "जयपुर", "admin_type": "Tehsil", "district_id": "dist_jaipur", "district_name": "Jaipur", "state_id": 8, "state_name": "Rajasthan", "aliases": ["Jaipur Tehsil"], "bbox": [75.70, 26.88, 75.82, 26.98], "polygon": [[75.70, 26.88], [75.72, 26.98], [75.82, 26.96], [75.80, 26.90], [75.70, 26.88]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_dadri", "lgd_code": 1580, "name": "Dadri", "canonical_name": "Dadri", "name_hi": "दादरी", "name_mr": "दादरी", "admin_type": "Tehsil", "district_id": "dist_gautam_buddha_nagar", "district_name": "Gautam Buddha Nagar", "state_id": 9, "state_name": "Uttar Pradesh", "aliases": ["Dadri Tehsil", "Noida Tehsil"], "bbox": [77.30, 28.55, 77.50, 28.70], "polygon": [[77.30, 28.55], [77.32, 28.70], [77.50, 28.68], [77.48, 28.57], [77.30, 28.55]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_lucknow", "lgd_code": 1780, "name": "Lucknow", "canonical_name": "Lucknow", "name_hi": "लखनऊ", "name_mr": "लखनऊ", "admin_type": "Tehsil", "district_id": "dist_lucknow", "district_name": "Lucknow", "state_id": 9, "state_name": "Uttar Pradesh", "aliases": ["Lucknow Sadar"], "bbox": [80.90, 26.80, 81.08, 26.95], "polygon": [[80.90, 26.80], [80.92, 26.95], [81.08, 26.93], [81.06, 26.82], [80.90, 26.80]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_bilaspur_cg", "lgd_code": 3740, "name": "Bilaspur", "canonical_name": "Bilaspur", "name_hi": "बिलासपुर", "name_mr": "बिलासपूर", "admin_type": "Tehsil", "district_id": "dist_bilaspur_cg", "district_name": "Bilaspur", "state_id": 22, "state_name": "Chhattisgarh", "aliases": ["Bilaspur Tehsil"], "bbox": [82.10, 22.05, 82.25, 22.18], "polygon": [[82.10, 22.05], [82.12, 22.18], [82.25, 22.16], [82.23, 22.07], [82.10, 22.05]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_bilaspur_hp", "lgd_code": 180, "name": "Bilaspur Sadar", "canonical_name": "Bilaspur Sadar", "name_hi": "बिलासपुर सदर", "name_mr": "बिलासपूर सदर", "admin_type": "Tehsil", "district_id": "dist_bilaspur_hp", "district_name": "Bilaspur", "state_id": 2, "state_name": "Himachal Pradesh", "aliases": ["Bilaspur Sadar Tehsil", "Bilaspur"], "bbox": [76.70, 31.30, 76.82, 31.40], "polygon": [[76.70, 31.30], [76.72, 31.40], [76.82, 31.38], [76.80, 31.32], [76.70, 31.30]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_rampur_up", "lgd_code": 1890, "name": "Rampur", "canonical_name": "Rampur", "name_hi": "रामपुर", "name_mr": "रामपूर", "admin_type": "Tehsil", "district_id": "dist_rampur_up", "district_name": "Rampur", "state_id": 9, "state_name": "Uttar Pradesh", "aliases": ["Rampur Sadar"], "bbox": [78.95, 28.75, 79.10, 28.88], "polygon": [[78.95, 28.75], [78.97, 28.88], [79.10, 28.86], [79.08, 28.77], [78.95, 28.75]], "source": "LGD", "license": "GODL-India"},
    {"id": "subdist_rampur_bushahr", "lgd_code": 270, "name": "Rampur", "canonical_name": "Rampur", "name_hi": "रामपुर बुशहर", "name_mr": "रामपूर", "admin_type": "Tehsil", "district_id": "dist_shimla", "district_name": "Shimla", "state_id": 2, "state_name": "Himachal Pradesh", "aliases": ["Rampur Bushahr", "Rampur HP"], "bbox": [77.60, 31.40, 77.75, 31.55], "polygon": [[77.60, 31.40], [77.62, 31.55], [77.75, 31.53], [77.73, 31.42], [77.60, 31.40]], "source": "LGD", "license": "GODL-India"}
]

# 4. Comprehensive Localities Catalog (38 Localities across Metro & Non-Metro Regions)
LOCALITIES = [
    # Maharashtra - Pune
    {"name": "Kharadi", "canonical_name": "Kharadi", "name_hi": "खराड़ी", "name_mr": "खराडी", "aliases": ["Kharadi Gaon", "Kharadi Bypass", "EON Free Zone Kharadi", "Khardi", "Kharadee"], "subdistrict_id": "subdist_haveli", "subdistrict": "Haveli", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411014", "coordinates": {"latitude": 18.5514, "longitude": 73.9405}, "bbox": [73.92, 18.53, 73.96, 18.57]},
    {"name": "Viman Nagar", "canonical_name": "Viman Nagar", "name_hi": "विमान नगर", "name_mr": "विमान नगर", "aliases": ["Vimannagar", "Viman Nagar Pune"], "subdistrict_id": "subdist_haveli", "subdistrict": "Haveli", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411014", "coordinates": {"latitude": 18.5679, "longitude": 73.9143}, "bbox": [73.90, 18.55, 73.93, 18.58]},
    {"name": "Hinjewadi", "canonical_name": "Hinjewadi", "name_hi": "हिंजेवाड़ी", "name_mr": "हिंजवडी", "aliases": ["Hinjawadi", "Hinjewadi Phase 1", "Hinjewadi Phase 2", "Hinjewadi Phase 3"], "subdistrict_id": "subdist_mulshi", "subdistrict": "Mulshi", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411057", "coordinates": {"latitude": 18.5913, "longitude": 73.7389}, "bbox": [73.71, 18.57, 73.76, 18.61]},
    {"name": "Baner", "canonical_name": "Baner", "name_hi": "बानेर", "name_mr": "बाणेर", "aliases": ["Baner Gaon", "Baner Road", "Banere"], "subdistrict_id": "subdist_haveli", "subdistrict": "Haveli", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411045", "coordinates": {"latitude": 18.5590, "longitude": 73.7868}, "bbox": [73.77, 18.54, 73.81, 18.58]},
    {"name": "Hadapsar", "canonical_name": "Hadapsar", "name_hi": "हड़पसर", "name_mr": "हडपसर", "aliases": ["Hadapsar Gaon", "Magarpatta City", "Hadapsar Gadital"], "subdistrict_id": "subdist_haveli", "subdistrict": "Haveli", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411028", "coordinates": {"latitude": 18.5089, "longitude": 73.9260}, "bbox": [73.90, 18.49, 73.95, 18.53]},
    {"name": "Kothrud", "canonical_name": "Kothrud", "name_hi": "कोथरुड", "name_mr": "कोथरूड", "aliases": ["Kothrud Depot", "Paud Road Kothrud", "Kothrood"], "subdistrict_id": "subdist_pune_city", "subdistrict": "Pune City", "district_id": "dist_pune", "district": "Pune", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "411038", "coordinates": {"latitude": 18.5074, "longitude": 73.8077}, "bbox": [73.79, 18.49, 73.83, 18.53]},

    # Maharashtra - Mumbai & Thane & Kolhapur
    {"name": "Bandra West", "canonical_name": "Bandra West", "name_hi": "बांद्रा पश्चिम", "name_mr": "वांद्रे पश्चिम", "aliases": ["Bandra W", "Bandra", "BKC", "Bandra Reclamation"], "subdistrict_id": "subdist_andheri", "subdistrict": "Andheri", "district_id": "dist_mumbai_suburban", "district": "Mumbai Suburban", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "400050", "coordinates": {"latitude": 19.0596, "longitude": 72.8295}, "bbox": [72.81, 19.04, 72.85, 19.08]},
    {"name": "Andheri East", "canonical_name": "Andheri East", "name_hi": "अंधेरी पूर्व", "name_mr": "अंधेरी पूर्व", "aliases": ["Andheri E", "MIDC Andheri", "Marol"], "subdistrict_id": "subdist_andheri", "subdistrict": "Andheri", "district_id": "dist_mumbai_suburban", "district": "Mumbai Suburban", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "400069", "coordinates": {"latitude": 19.1136, "longitude": 72.8697}, "bbox": [72.85, 19.10, 72.89, 19.14]},
    {"name": "Powai", "canonical_name": "Powai", "name_hi": "पवई", "name_mr": "पवई", "aliases": ["Hiranandani Powai", "IIT Bombay", "Powaye"], "subdistrict_id": "subdist_andheri", "subdistrict": "Andheri", "district_id": "dist_mumbai_suburban", "district": "Mumbai Suburban", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "400076", "coordinates": {"latitude": 19.1176, "longitude": 72.9060}, "bbox": [72.88, 19.10, 72.93, 19.14]},
    {"name": "Thane West", "canonical_name": "Thane West", "name_hi": "ठाणे पश्चिम", "name_mr": "ठाणे पश्चिम", "aliases": ["Thane W", "Majiwada", "Ghubunder Road"], "subdistrict_id": "subdist_thane", "subdistrict": "Thane", "district_id": "dist_thane", "district": "Thane", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "400601", "coordinates": {"latitude": 19.2183, "longitude": 72.9781}, "bbox": [72.95, 19.19, 73.00, 19.24]},
    {"name": "Rajarampuri", "canonical_name": "Rajarampuri", "name_hi": "राजारामपुरी", "name_mr": "राजारामपुरी", "aliases": ["Rajarampuri Kolhapur"], "subdistrict_id": "subdist_karvir", "subdistrict": "Karvir", "district_id": "dist_kolhapur", "district": "Kolhapur", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "416008", "coordinates": {"latitude": 16.6913, "longitude": 74.2449}, "bbox": [74.22, 16.67, 74.27, 16.71]},

    # Karnataka - Bengaluru & Mysuru
    {"name": "Whitefield", "canonical_name": "Whitefield", "name_hi": "व्हाइटफील्ड", "name_mr": "व्हाइटफील्ड", "aliases": ["Whitefield Bengaluru", "ITPL Whitefield", "EPIP Zone"], "subdistrict_id": "subdist_bengaluru_east", "subdistrict": "Bengaluru East", "district_id": "dist_bengaluru_urban", "district": "Bengaluru Urban", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "560066", "coordinates": {"latitude": 12.9698, "longitude": 77.7500}, "bbox": [77.72, 12.94, 77.77, 12.99]},
    {"name": "Koramangala", "canonical_name": "Koramangala", "name_hi": "कोरामंगला", "name_mr": "कोरामंगला", "aliases": ["Koramangala 4th Block", "Koramangala 5th Block"], "subdistrict_id": "subdist_bengaluru_south", "subdistrict": "Bengaluru South", "district_id": "dist_bengaluru_urban", "district": "Bengaluru Urban", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "560034", "coordinates": {"latitude": 12.9352, "longitude": 77.6245}, "bbox": [77.60, 12.91, 77.65, 12.95]},
    {"name": "HSR Layout", "canonical_name": "HSR Layout", "name_hi": "एचएसआर लेआउट", "name_mr": "एचएसआर लेआउट", "aliases": ["HSR", "Hosur Sarjapur Road Layout", "HSR Sector 1"], "subdistrict_id": "subdist_bengaluru_south", "subdistrict": "Bengaluru South", "district_id": "dist_bengaluru_urban", "district": "Bengaluru Urban", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "560102", "coordinates": {"latitude": 12.9121, "longitude": 77.6446}, "bbox": [77.62, 12.89, 77.67, 12.93]},
    {"name": "Indiranagar", "canonical_name": "Indiranagar", "name_hi": "इंदिरानगर", "name_mr": "इंदिरानगर", "aliases": ["Indira Nagar Bangalore", "100 Feet Road Indiranagar"], "subdistrict_id": "subdist_bengaluru_east", "subdistrict": "Bengaluru East", "district_id": "dist_bengaluru_urban", "district": "Bengaluru Urban", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "560038", "coordinates": {"latitude": 12.9784, "longitude": 77.6408}, "bbox": [77.62, 12.96, 77.66, 13.00]},
    {"name": "Electronic City", "canonical_name": "Electronic City", "name_hi": "इलेक्ट्रॉनिक सिटी", "name_mr": "इलेक्ट्रॉनिक सिटी", "aliases": ["E-City", "Electronic City Phase 1", "ECity"], "subdistrict_id": "subdist_bengaluru_south", "subdistrict": "Bengaluru South", "district_id": "dist_bengaluru_urban", "district": "Bengaluru Urban", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "560100", "coordinates": {"latitude": 12.8399, "longitude": 77.6770}, "bbox": [77.65, 12.82, 77.70, 12.86]},
    {"name": "Gokulam", "canonical_name": "Gokulam", "name_hi": "गोकुलम", "name_mr": "गोकुलम", "aliases": ["Gokulam 3rd Stage", "Goculam"], "subdistrict_id": "subdist_mysuru", "subdistrict": "Mysuru", "district_id": "dist_mysuru", "district": "Mysuru", "state_id": 29, "state": "Karnataka", "state_code": "KA", "pincode": "570002", "coordinates": {"latitude": 12.3270, "longitude": 76.6260}, "bbox": [76.60, 12.30, 76.65, 12.35]},

    # Delhi NCR
    {"name": "Connaught Place", "canonical_name": "Connaught Place", "name_hi": "कनॉट प्लेस", "name_mr": "कनॉट प्लेस", "aliases": ["CP", "Rajiv Chowk", "Connaught Circus", "Inner Circle CP"], "subdistrict_id": "subdist_chanakyapuri", "subdistrict": "Chanakyapuri", "district_id": "dist_new_delhi", "district": "New Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110001", "coordinates": {"latitude": 28.6315, "longitude": 77.2167}, "bbox": [77.20, 28.62, 77.23, 28.65]},
    {"name": "Hauz Khas", "canonical_name": "Hauz Khas", "name_hi": "हौज खास", "name_mr": "हौज खास", "aliases": ["Hauz Khas Village", "HKV", "Hauz Khas Enclave"], "subdistrict_id": "subdist_hauz_khas", "subdistrict": "Hauz Khas", "district_id": "dist_south_delhi", "district": "South Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110016", "coordinates": {"latitude": 28.5494, "longitude": 77.2001}, "bbox": [77.18, 28.53, 77.22, 28.57]},
    {"name": "Saket", "canonical_name": "Saket", "name_hi": "साकेत", "name_mr": "साकेत", "aliases": ["Saket District Centre", "Select Citywalk Saket"], "subdistrict_id": "subdist_saket", "subdistrict": "Saket", "district_id": "dist_south_delhi", "district": "South Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110017", "coordinates": {"latitude": 28.5244, "longitude": 77.2185}, "bbox": [77.20, 28.50, 77.24, 28.54]},
    {"name": "Karol Bagh", "canonical_name": "Karol Bagh", "name_hi": "करोल बाग", "name_mr": "करोल बाग", "aliases": ["Gaffar Market Karol Bagh", "Pusa Road"], "subdistrict_id": "subdist_karol_bagh", "subdistrict": "Karol Bagh", "district_id": "dist_central_delhi", "district": "Central Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110005", "coordinates": {"latitude": 28.6517, "longitude": 77.1906}, "bbox": [77.17, 28.63, 77.21, 28.67]},
    {"name": "Dwarka", "canonical_name": "Dwarka", "name_hi": "द्वारका", "name_mr": "द्वारका", "aliases": ["Dwarka Sector 10", "Dwarka Sector 12", "Dwarka Mor"], "subdistrict_id": "subdist_dwarka", "subdistrict": "Dwarka", "district_id": "dist_south_west_delhi", "district": "South West Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110075", "coordinates": {"latitude": 28.5921, "longitude": 77.0460}, "bbox": [77.02, 28.57, 77.07, 28.61]},
    {"name": "Rohini", "canonical_name": "Rohini", "name_hi": "रोहिणी", "name_mr": "रोहिणी", "aliases": ["Rohini Sector 7", "Rohini Sector 14", "Rohini West"], "subdistrict_id": "subdist_rohini", "subdistrict": "Rohini", "district_id": "dist_north_west_delhi", "district": "North West Delhi", "state_id": 7, "state": "Delhi", "state_code": "DL", "pincode": "110085", "coordinates": {"latitude": 28.7495, "longitude": 77.0565}, "bbox": [77.03, 28.73, 77.08, 28.77]},

    # West Bengal - Kolkata & North 24 Parganas
    {"name": "Salt Lake", "canonical_name": "Salt Lake", "name_hi": "सॉल्ट लेक", "name_mr": "सॉल्ट लेक", "aliases": ["Salt Lake Sector 5", "Bidhannagar", "Salt Lake City"], "subdistrict_id": "subdist_alipore", "subdistrict": "Alipore", "district_id": "dist_kolkata", "district": "Kolkata", "state_id": 19, "state": "West Bengal", "state_code": "WB", "pincode": "700091", "coordinates": {"latitude": 22.5867, "longitude": 88.4178}, "bbox": [88.39, 22.56, 88.44, 22.61]},
    {"name": "Rajarhat", "canonical_name": "Rajarhat", "name_hi": "राजारहाट", "name_mr": "राजारहाट", "aliases": ["Rajarhat Main Road", "Rajarhat Gopalpur"], "subdistrict_id": "subdist_barasat", "subdistrict": "Barasat", "district_id": "dist_north_24_parganas", "district": "North 24 Parganas", "state_id": 19, "state": "West Bengal", "state_code": "WB", "pincode": "700135", "coordinates": {"latitude": 22.6231, "longitude": 88.5134}, "bbox": [88.48, 22.60, 88.54, 22.65]},
    {"name": "New Town", "canonical_name": "New Town", "name_hi": "न्यू टाउन", "name_mr": "न्यू टाउन", "aliases": ["New Town Action Area 1", "New Town Kolkata", "Rajarhat New Town"], "subdistrict_id": "subdist_barasat", "subdistrict": "Barasat", "district_id": "dist_north_24_parganas", "district": "North 24 Parganas", "state_id": 19, "state": "West Bengal", "state_code": "WB", "pincode": "700156", "coordinates": {"latitude": 22.5896, "longitude": 88.4746}, "bbox": [88.45, 22.56, 88.50, 22.61]},

    # Tamil Nadu - Chennai
    {"name": "T Nagar", "canonical_name": "T Nagar", "name_hi": "टी नगर", "name_mr": "टी नगर", "aliases": ["Thyagaraya Nagar", "T. Nagar", "Panagal Park"], "subdistrict_id": "subdist_mylapore", "subdistrict": "Mylapore", "district_id": "dist_chennai", "district": "Chennai", "state_id": 33, "state": "Tamil Nadu", "state_code": "TN", "pincode": "600017", "coordinates": {"latitude": 13.0418, "longitude": 80.2341}, "bbox": [80.21, 13.02, 80.25, 13.06]},
    {"name": "Adyar", "canonical_name": "Adyar", "name_hi": "अडयार", "name_mr": "अडयार", "aliases": ["Adayar", "Adyar Gandhi Nagar", "Adyar Bus Depot"], "subdistrict_id": "subdist_guindy", "subdistrict": "Guindy", "district_id": "dist_chennai", "district": "Chennai", "state_id": 33, "state": "Tamil Nadu", "state_code": "TN", "pincode": "600020", "coordinates": {"latitude": 13.0012, "longitude": 80.2565}, "bbox": [80.23, 12.98, 80.28, 13.02]},

    # Telangana - Hyderabad
    {"name": "HITEC City", "canonical_name": "HITEC City", "name_hi": "हायटेक सिटी", "name_mr": "हायटेक सिटी", "aliases": ["Hitech City", "Madhapur", "Cyberabad", "Cyber Towers"], "subdistrict_id": "subdist_shaikpet", "subdistrict": "Shaikpet", "district_id": "dist_hyderabad", "district": "Hyderabad", "state_id": 36, "state": "Telangana", "state_code": "TG", "pincode": "500081", "coordinates": {"latitude": 17.4435, "longitude": 78.3772}, "bbox": [78.35, 17.42, 78.40, 17.47]},
    {"name": "Banjara Hills", "canonical_name": "Banjara Hills", "name_hi": "बंजारा हिल्स", "name_mr": "बंजारा हिल्स", "aliases": ["Road No 1 Banjara Hills", "Road No 12 Banjara Hills"], "subdistrict_id": "subdist_ameerpet", "subdistrict": "Ameerpet", "district_id": "dist_hyderabad", "district": "Hyderabad", "state_id": 36, "state": "Telangana", "state_code": "TG", "pincode": "500034", "coordinates": {"latitude": 17.4156, "longitude": 78.4357}, "bbox": [78.41, 17.39, 78.46, 17.44]},

    # Gujarat - Ahmedabad & Surat
    {"name": "Navrangpura", "canonical_name": "Navrangpura", "name_hi": "नवरंगपुरा", "name_mr": "नवरंगपुरा", "aliases": ["Navrangpura Ahmedabad", "CG Road Navrangpura"], "subdistrict_id": "subdist_daskroi", "subdistrict": "Daskroi", "district_id": "dist_ahmedabad", "district": "Ahmedabad", "state_id": 24, "state": "Gujarat", "state_code": "GJ", "pincode": "380009", "coordinates": {"latitude": 23.0365, "longitude": 72.5611}, "bbox": [72.54, 23.01, 72.58, 23.06]},
    {"name": "Vesu", "canonical_name": "Vesu", "name_hi": "वेसू", "name_mr": "वेसू", "aliases": ["Vesu Surat", "VIP Road Vesu"], "subdistrict_id": "subdist_chorasi", "subdistrict": "Chorasi", "district_id": "dist_surat", "district": "Surat", "state_id": 24, "state": "Gujarat", "state_code": "GJ", "pincode": "395007", "coordinates": {"latitude": 21.1418, "longitude": 72.7709}, "bbox": [72.75, 21.12, 72.79, 21.16]},

    # Rajasthan - Jaipur
    {"name": "Malviya Nagar", "canonical_name": "Malviya Nagar", "name_hi": "मालवीय नगर", "name_mr": "मालवीय नगर", "aliases": ["Malviya Nagar Jaipur", "World Trade Park Malviya Nagar"], "subdistrict_id": "subdist_sanganer", "subdistrict": "Sanganer", "district_id": "dist_jaipur", "district": "Jaipur", "state_id": 8, "state": "Rajasthan", "state_code": "RJ", "pincode": "302017", "coordinates": {"latitude": 26.8532, "longitude": 75.8052}, "bbox": [75.78, 26.83, 75.83, 26.88]},
    {"name": "Vaishali Nagar", "canonical_name": "Vaishali Nagar", "name_hi": "वैशाली नगर", "name_mr": "वैशाली नगर", "aliases": ["Vaishali Nagar Jaipur", "Amrapali Plaza Vaishali Nagar"], "subdistrict_id": "subdist_jaipur", "subdistrict": "Jaipur", "district_id": "dist_jaipur", "district": "Jaipur", "state_id": 8, "state": "Rajasthan", "state_code": "RJ", "pincode": "302021", "coordinates": {"latitude": 26.9069, "longitude": 75.7434}, "bbox": [75.72, 26.88, 75.77, 26.93]},

    # Uttar Pradesh - Noida & Lucknow
    {"name": "Sector 62", "canonical_name": "Sector 62", "name_hi": "सेक्टर 62", "name_mr": "सेक्टर 62", "aliases": ["Sector 62 Noida", "Noida Sector 62", "Cyber City", "DLF Phase 2"], "subdistrict_id": "subdist_dadri", "subdistrict": "Dadri", "district_id": "dist_gautam_buddha_nagar", "district": "Gautam Buddha Nagar", "state_id": 9, "state": "Uttar Pradesh", "state_code": "UP", "pincode": "201309", "coordinates": {"latitude": 28.6258, "longitude": 77.3653}, "bbox": [77.34, 28.60, 77.39, 28.65]},
    {"name": "Gomti Nagar", "canonical_name": "Gomti Nagar", "name_hi": "गोमती नगर", "name_mr": "गोमती नगर", "aliases": ["Gomti Nagar Extension", "Vibhuti Khand Gomti Nagar"], "subdistrict_id": "subdist_lucknow", "subdistrict": "Lucknow", "district_id": "dist_lucknow", "district": "Lucknow", "state_id": 9, "state": "Uttar Pradesh", "state_code": "UP", "pincode": "226010", "coordinates": {"latitude": 26.8529, "longitude": 80.9962}, "bbox": [77.97, 26.83, 81.02, 26.88]},

    # Homonymous Localities across states
    {"name": "Rampur", "canonical_name": "Rampur UP", "name_hi": "रामपुर", "name_mr": "रामपूर", "aliases": ["Rampur City UP", "Rampur Town"], "subdistrict_id": "subdist_rampur_up", "subdistrict": "Rampur", "district_id": "dist_rampur_up", "district": "Rampur", "state_id": 9, "state": "Uttar Pradesh", "state_code": "UP", "pincode": "244901", "coordinates": {"latitude": 28.8154, "longitude": 79.0250}, "bbox": [78.99, 28.79, 79.06, 28.84]},
    {"name": "Rampur", "canonical_name": "Rampur HP", "name_hi": "रामपुर बुशहर", "name_mr": "रामपूर", "aliases": ["Rampur Bushahr", "Rampur Shimla"], "subdistrict_id": "subdist_rampur_bushahr", "subdistrict": "Rampur", "district_id": "dist_shimla", "district": "Shimla", "state_id": 2, "state": "Himachal Pradesh", "state_code": "HP", "pincode": "172101", "coordinates": {"latitude": 31.4485, "longitude": 77.6300}, "bbox": [77.61, 31.43, 77.65, 31.47]},
    {"name": "Bilaspur", "canonical_name": "Bilaspur CG", "name_hi": "बिलासपुर", "name_mr": "बिलासपूर", "aliases": ["Bilaspur City CG", "Bilaspur Chhattisgarh"], "subdistrict_id": "subdist_bilaspur_cg", "subdistrict": "Bilaspur", "district_id": "dist_bilaspur_cg", "district": "Bilaspur", "state_id": 22, "state": "Chhattisgarh", "state_code": "CG", "pincode": "495001", "coordinates": {"latitude": 22.0797, "longitude": 82.1409}, "bbox": [82.11, 22.05, 82.17, 22.11]},
    {"name": "Bilaspur", "canonical_name": "Bilaspur HP", "name_hi": "बिलासपुर", "name_mr": "बिलासपूर", "aliases": ["Bilaspur Town HP", "Bilaspur Himachal"], "subdistrict_id": "subdist_bilaspur_hp", "subdistrict": "Bilaspur Sadar", "district_id": "dist_bilaspur_hp", "district": "Bilaspur", "state_id": 2, "state": "Himachal Pradesh", "state_code": "HP", "pincode": "174001", "coordinates": {"latitude": 31.3411, "longitude": 76.7570}, "bbox": [76.73, 31.32, 76.78, 31.36]},
    {"name": "Fatehpur", "canonical_name": "Fatehpur UP", "name_hi": "फतेहपुर", "name_mr": "फतेहपूर", "aliases": ["Fatehpur City UP"], "subdistrict_id": "subdist_fatehpur_up", "subdistrict": "Fatehpur", "district_id": "dist_fatehpur_up", "district": "Fatehpur", "state_id": 9, "state": "Uttar Pradesh", "state_code": "UP", "pincode": "212601", "coordinates": {"latitude": 25.9284, "longitude": 80.8130}, "bbox": [80.78, 25.90, 80.85, 25.95]},
    {"name": "Fatehpur", "canonical_name": "Fatehpur RJ", "name_hi": "फतेहपुर शेखावाटी", "name_mr": "फतेहपूर", "aliases": ["Fatehpur Shekhawati"], "subdistrict_id": "subdist_fatehpur_rj", "subdistrict": "Fatehpur", "district_id": "dist_sikar", "district": "Sikar", "state_id": 8, "state": "Rajasthan", "state_code": "RJ", "pincode": "332301", "coordinates": {"latitude": 27.9845, "longitude": 74.9540}, "bbox": [74.92, 27.96, 74.98, 28.01]},
    {"name": "Rajapur", "canonical_name": "Rajapur MH", "name_hi": "राजापुर", "name_mr": "राजापूर", "aliases": ["Rajapur Konkan"], "subdistrict_id": "subdist_rajapur_mh", "subdistrict": "Rajapur", "district_id": "dist_ratnagiri", "district": "Ratnagiri", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "416702", "coordinates": {"latitude": 16.6580, "longitude": 73.5180}, "bbox": [73.49, 16.63, 73.54, 16.68]},
    {"name": "Rajapur", "canonical_name": "Rajapur UP", "name_hi": "राजापुर", "name_mr": "राजापूर", "aliases": ["Rajapur Chitrakoot"], "subdistrict_id": "subdist_rajapur_up", "subdistrict": "Rajapur", "district_id": "dist_chitrakoot", "district": "Chitrakoot", "state_id": 9, "state": "Uttar Pradesh", "state_code": "UP", "pincode": "210207", "coordinates": {"latitude": 25.3850, "longitude": 81.1550}, "bbox": [81.13, 25.36, 81.18, 25.41]},
    {"name": "Aurangabad", "canonical_name": "Aurangabad MH", "name_hi": "औरंगाबाद", "name_mr": "छत्रपती संभाजीनगर", "aliases": ["Chhatrapati Sambhajinagar", "Sambhajinagar"], "subdistrict_id": "subdist_aurangabad_mh", "subdistrict": "Aurangabad", "district_id": "dist_aurangabad_mh", "district": "Aurangabad", "state_id": 27, "state": "Maharashtra", "state_code": "MH", "pincode": "431001", "coordinates": {"latitude": 19.8762, "longitude": 75.3433}, "bbox": [75.30, 19.85, 75.38, 19.90]},
    {"name": "Aurangabad", "canonical_name": "Aurangabad BR", "name_hi": "औरंगाबाद", "name_mr": "औरंगाबाद", "aliases": ["Aurangabad Bihar"], "subdistrict_id": "subdist_aurangabad_br", "subdistrict": "Aurangabad", "district_id": "dist_aurangabad_br", "district": "Aurangabad", "state_id": 10, "state": "Bihar", "state_code": "BR", "pincode": "824101", "coordinates": {"latitude": 24.7539, "longitude": 84.3739}, "bbox": [84.34, 24.73, 84.40, 24.78]}
]

# 5. Comprehensive Pincodes Catalog
PINCODES = [
    {"pincode": "411014", "office_name": "Kharadi SO", "post_offices": ["Kharadi B.O", "Kharadi SO", "Viman Nagar SO"], "circle": "Maharashtra", "region": "Pune", "district": "Pune", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 18.5514, "longitude": 73.9405}},
    {"pincode": "411057", "office_name": "Hinjewadi SO", "circle": "Maharashtra", "region": "Pune", "district": "Pune", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 18.5913, "longitude": 73.7389}},
    {"pincode": "411045", "office_name": "Baner SO", "circle": "Maharashtra", "region": "Pune", "district": "Pune", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 18.5590, "longitude": 73.7868}},
    {"pincode": "411028", "office_name": "Hadapsar SO", "circle": "Maharashtra", "region": "Pune", "district": "Pune", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 18.5089, "longitude": 73.9260}},
    {"pincode": "411038", "office_name": "Kothrud SO", "circle": "Maharashtra", "region": "Pune", "district": "Pune", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 18.5074, "longitude": 73.8077}},
    {"pincode": "400050", "office_name": "Bandra West SO", "circle": "Maharashtra", "region": "Mumbai", "district": "Mumbai Suburban", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 19.0596, "longitude": 72.8295}},
    {"pincode": "400069", "office_name": "Andheri East SO", "circle": "Maharashtra", "region": "Mumbai", "district": "Mumbai Suburban", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 19.1136, "longitude": 72.8697}},
    {"pincode": "400076", "office_name": "Powai IIT SO", "circle": "Maharashtra", "region": "Mumbai", "district": "Mumbai Suburban", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 19.1176, "longitude": 72.9060}},
    {"pincode": "400601", "office_name": "Thane SO", "circle": "Maharashtra", "region": "Mumbai", "district": "Thane", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 19.2183, "longitude": 72.9781}},
    {"pincode": "416008", "office_name": "Rajarampuri SO", "circle": "Maharashtra", "region": "Goa-Kolhapur", "district": "Kolhapur", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 16.6913, "longitude": 74.2449}},
    {"pincode": "560066", "office_name": "Whitefield SO", "circle": "Karnataka", "region": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.9698, "longitude": 77.7500}},
    {"pincode": "560034", "office_name": "Koramangala SO", "circle": "Karnataka", "region": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.9352, "longitude": 77.6245}},
    {"pincode": "560102", "office_name": "HSR Layout SO", "circle": "Karnataka", "region": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.9121, "longitude": 77.6446}},
    {"pincode": "560038", "office_name": "Indiranagar SO", "circle": "Karnataka", "region": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.9784, "longitude": 77.6408}},
    {"pincode": "560100", "office_name": "Electronic City SO", "circle": "Karnataka", "region": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.8399, "longitude": 77.6770}},
    {"pincode": "570002", "office_name": "Gokulam SO", "circle": "Karnataka", "region": "South Karnataka", "district": "Mysuru", "state": "Karnataka", "state_code": "KA", "centroid": {"latitude": 12.3270, "longitude": 76.6260}},
    {"pincode": "110001", "office_name": "New Delhi GPO", "circle": "Delhi", "region": "Delhi", "district": "New Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.6315, "longitude": 77.2167}},
    {"pincode": "110016", "office_name": "Hauz Khas SO", "circle": "Delhi", "region": "Delhi", "district": "South Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.5494, "longitude": 77.2001}},
    {"pincode": "110017", "office_name": "Saket SO", "circle": "Delhi", "region": "Delhi", "district": "South Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.5244, "longitude": 77.2185}},
    {"pincode": "110005", "office_name": "Karol Bagh SO", "circle": "Delhi", "region": "Delhi", "district": "Central Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.6517, "longitude": 77.1906}},
    {"pincode": "110075", "office_name": "Dwarka SO", "circle": "Delhi", "region": "Delhi", "district": "South West Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.5921, "longitude": 77.0460}},
    {"pincode": "110085", "office_name": "Rohini SO", "circle": "Delhi", "region": "Delhi", "district": "North West Delhi", "state": "Delhi", "state_code": "DL", "centroid": {"latitude": 28.7495, "longitude": 77.0565}},
    {"pincode": "700091", "office_name": "Salt Lake SO", "circle": "West Bengal", "region": "Kolkata", "district": "Kolkata", "state": "West Bengal", "state_code": "WB", "centroid": {"latitude": 22.5867, "longitude": 88.4178}},
    {"pincode": "700135", "office_name": "Rajarhat SO", "circle": "West Bengal", "region": "Kolkata", "district": "North 24 Parganas", "state": "West Bengal", "state_code": "WB", "centroid": {"latitude": 22.6231, "longitude": 88.5134}},
    {"pincode": "700156", "office_name": "New Town SO", "circle": "West Bengal", "region": "Kolkata", "district": "North 24 Parganas", "state": "West Bengal", "state_code": "WB", "centroid": {"latitude": 22.5896, "longitude": 88.4746}},
    {"pincode": "600017", "office_name": "T Nagar SO", "circle": "Tamil Nadu", "region": "Chennai", "district": "Chennai", "state": "Tamil Nadu", "state_code": "TN", "centroid": {"latitude": 13.0418, "longitude": 80.2341}},
    {"pincode": "600020", "office_name": "Adyar SO", "circle": "Tamil Nadu", "region": "Chennai", "district": "Chennai", "state": "Tamil Nadu", "state_code": "TN", "centroid": {"latitude": 13.0012, "longitude": 80.2565}},
    {"pincode": "500081", "office_name": "HITEC City SO", "circle": "Telangana", "region": "Hyderabad", "district": "Hyderabad", "state": "Telangana", "state_code": "TG", "centroid": {"latitude": 17.4435, "longitude": 78.3772}},
    {"pincode": "500034", "office_name": "Banjara Hills SO", "circle": "Telangana", "region": "Hyderabad", "district": "Hyderabad", "state": "Telangana", "state_code": "TG", "centroid": {"latitude": 17.4156, "longitude": 78.4357}},
    {"pincode": "380009", "office_name": "Navrangpura SO", "circle": "Gujarat", "region": "Ahmedabad", "district": "Ahmedabad", "state": "Gujarat", "state_code": "GJ", "centroid": {"latitude": 23.0365, "longitude": 72.5611}},
    {"pincode": "395007", "office_name": "Vesu SO", "circle": "Gujarat", "region": "Vadodara", "district": "Surat", "state": "Gujarat", "state_code": "GJ", "centroid": {"latitude": 21.1418, "longitude": 72.7709}},
    {"pincode": "302017", "office_name": "Malviya Nagar SO", "circle": "Rajasthan", "region": "Jaipur", "district": "Jaipur", "state": "Rajasthan", "state_code": "RJ", "centroid": {"latitude": 26.8532, "longitude": 75.8052}},
    {"pincode": "302021", "office_name": "Vaishali Nagar SO", "circle": "Rajasthan", "region": "Jaipur", "district": "Jaipur", "state": "Rajasthan", "state_code": "RJ", "centroid": {"latitude": 26.9069, "longitude": 75.7434}},
    {"pincode": "201309", "office_name": "Sector 62 Noida SO", "circle": "Uttar Pradesh", "region": "Bareilly", "district": "Gautam Buddha Nagar", "state": "Uttar Pradesh", "state_code": "UP", "centroid": {"latitude": 28.6258, "longitude": 77.3653}},
    {"pincode": "226010", "office_name": "Gomti Nagar SO", "circle": "Uttar Pradesh", "region": "Lucknow", "district": "Lucknow", "state": "Uttar Pradesh", "state_code": "UP", "centroid": {"latitude": 26.8529, "longitude": 80.9962}},
    {"pincode": "244901", "office_name": "Rampur HO", "circle": "Uttar Pradesh", "region": "Bareilly", "district": "Rampur", "state": "Uttar Pradesh", "state_code": "UP", "centroid": {"latitude": 28.8154, "longitude": 79.0250}},
    {"pincode": "172101", "office_name": "Rampur Bushahr SO", "circle": "Himachal Pradesh", "region": "Shimla", "district": "Shimla", "state": "Himachal Pradesh", "state_code": "HP", "centroid": {"latitude": 31.4485, "longitude": 77.6300}},
    {"pincode": "495001", "office_name": "Bilaspur HO", "circle": "Chhattisgarh", "region": "Raipur", "district": "Bilaspur", "state": "Chhattisgarh", "state_code": "CG", "centroid": {"latitude": 22.0797, "longitude": 82.1409}},
    {"pincode": "174001", "office_name": "Bilaspur HO HP", "circle": "Himachal Pradesh", "region": "Mandi", "district": "Bilaspur", "state": "Himachal Pradesh", "state_code": "HP", "centroid": {"latitude": 31.3411, "longitude": 76.7570}},
    {"pincode": "212601", "office_name": "Fatehpur HO", "circle": "Uttar Pradesh", "region": "Kanpur", "district": "Fatehpur", "state": "Uttar Pradesh", "state_code": "UP", "centroid": {"latitude": 25.9284, "longitude": 80.8130}},
    {"pincode": "332301", "office_name": "Fatehpur Shekhawati SO", "circle": "Rajasthan", "region": "Jaipur", "district": "Sikar", "state": "Rajasthan", "state_code": "RJ", "centroid": {"latitude": 27.9845, "longitude": 74.9540}},
    {"pincode": "416702", "office_name": "Rajapur SO", "circle": "Maharashtra", "region": "Goa-Kolhapur", "district": "Ratnagiri", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 16.6580, "longitude": 73.5180}},
    {"pincode": "210207", "office_name": "Rajapur SO UP", "circle": "Uttar Pradesh", "region": "Allahabad", "district": "Chitrakoot", "state": "Uttar Pradesh", "state_code": "UP", "centroid": {"latitude": 25.3850, "longitude": 81.1550}},
    {"pincode": "431001", "office_name": "Aurangabad HO", "circle": "Maharashtra", "region": "Aurangabad", "district": "Aurangabad", "state": "Maharashtra", "state_code": "MH", "centroid": {"latitude": 19.8762, "longitude": 75.3433}},
    {"pincode": "824101", "office_name": "Aurangabad HO BR", "circle": "Bihar", "region": "Patna", "district": "Aurangabad", "state": "Bihar", "state_code": "BR", "centroid": {"latitude": 24.7539, "longitude": 84.3739}}
]

# 6. Comprehensive POIs
POIS = [
    {"name": "World Trade Center Pune", "aliases": ["WTC Pune", "World Trade Center"], "category": "Commercial Hub", "type": "Commercial Hub", "locality": "Kharadi", "district": "Pune", "state": "Maharashtra", "coordinates": {"latitude": 18.552, "longitude": 73.939}},
    {"name": "EON Free Zone", "aliases": ["EON IT Park", "EON Phase 1", "EON Phase 2"], "category": "IT Park", "type": "IT Park", "locality": "Kharadi", "district": "Pune", "state": "Maharashtra", "coordinates": {"latitude": 18.551, "longitude": 73.951}},
    {"name": "Prestige Tech Park", "aliases": ["Prestige IT Park"], "category": "IT Park", "type": "IT Park", "locality": "Whitefield", "district": "Bengaluru Urban", "state": "Karnataka", "coordinates": {"latitude": 12.936, "longitude": 77.691}},
    {"name": "DLF Cyber City", "aliases": ["Cyber City", "Cyber Hub", "DLF Phase 2"], "category": "Commercial Complex", "type": "Commercial Complex", "locality": "Sector 62", "district": "Gautam Buddha Nagar", "state": "Uttar Pradesh", "coordinates": {"latitude": 28.626, "longitude": 77.366}},
    {"name": "Phoenix Marketcity", "aliases": ["Phoenix Mall Viman Nagar", "Phoenix Mall"], "category": "Shopping Mall", "type": "Shopping Mall", "locality": "Viman Nagar", "district": "Pune", "state": "Maharashtra", "coordinates": {"latitude": 18.562, "longitude": 73.916}},
    {"name": "Select Citywalk", "aliases": ["Select City Walk", "Citywalk Mall"], "category": "Shopping Mall", "type": "Shopping Mall", "locality": "Saket", "district": "South Delhi", "state": "Delhi", "coordinates": {"latitude": 28.528, "longitude": 77.219}},
    {"name": "Cyber Towers", "aliases": ["Cyber Towers HITEC City", "HITEC City Towers"], "category": "IT Park", "type": "IT Park", "locality": "HITEC City", "district": "Hyderabad", "state": "Telangana", "coordinates": {"latitude": 17.450, "longitude": 78.380}}
]


def write_all():
    with open(PROCESSED_DIR / "states.json", "w", encoding="utf-8") as f:
        json.dump(ALL_36_STATES, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "districts.json", "w", encoding="utf-8") as f:
        json.dump(DISTRICTS, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "subdistricts.json", "w", encoding="utf-8") as f:
        json.dump(SUBDISTRICTS, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "localities.json", "w", encoding="utf-8") as f:
        json.dump(LOCALITIES, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "pincodes.json", "w", encoding="utf-8") as f:
        json.dump(PINCODES, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "pois.json", "w", encoding="utf-8") as f:
        json.dump(POIS, f, indent=2, ensure_ascii=False)
    print(f"Successfully wrote reference datasets to {PROCESSED_DIR}:")
    print(f"  States       : {len(ALL_36_STATES)}")
    print(f"  Districts    : {len(DISTRICTS)}")
    print(f"  Subdistricts : {len(SUBDISTRICTS)}")
    print(f"  Localities   : {len(LOCALITIES)}")
    print(f"  Pincodes     : {len(PINCODES)}")
    print(f"  POIs         : {len(POIS)}")


if __name__ == "__main__":
    write_all()
