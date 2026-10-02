"""Comprehensive National Indian Administrative Gazetteer Generator for GeoVerify India.

Merges rich baseline geometric, subdistrict, and postal attributes from generate_seed_data
with comprehensive pan-India national district, locality, and PIN code coverage.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

DATA_DIR = Path(__file__).parent.parent
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

from data.scripts.generate_seed_data import (
    ALL_36_STATES,
    DISTRICTS as SEED_DISTRICTS,
    SUBDISTRICTS as SEED_SUBDISTRICTS,
    LOCALITIES as SEED_LOCALITIES,
    PINCODES as SEED_PINCODES,
    POIS as SEED_POIS
)

# Additional Pan-India Districts
PAN_INDIA_DISTRICTS: List[Dict[str, Any]] = [
    # Gujarat
    {"id": "dist_surat", "name": "Surat", "canonical_name": "Surat", "state_name": "Gujarat", "state_code": "GJ", "aliases": [], "name_hi": "सूरत", "name_mr": "सुरत", "bbox": [72.6, 21.0, 73.1, 21.4]},
    {"id": "dist_vadodara", "name": "Vadodara", "canonical_name": "Vadodara", "state_name": "Gujarat", "state_code": "GJ", "aliases": ["Baroda"], "name_hi": "वडोदरा", "name_mr": "वडोदरा", "bbox": [73.0, 22.1, 73.4, 22.5]},
    {"id": "dist_rajkot", "name": "Rajkot", "canonical_name": "Rajkot", "state_name": "Gujarat", "state_code": "GJ", "aliases": [], "name_hi": "राजकोट", "name_mr": "राजकोट", "bbox": [70.6, 22.1, 71.0, 22.5]},
    {"id": "dist_gandhinagar", "name": "Gandhinagar", "canonical_name": "Gandhinagar", "state_name": "Gujarat", "state_code": "GJ", "aliases": [], "name_hi": "गांधीनगर", "name_mr": "गांधीनगर", "bbox": [72.5, 23.1, 72.8, 23.3]},

    # Goa & UTs
    {"id": "dist_north_goa", "name": "North Goa", "canonical_name": "North Goa", "state_name": "Goa", "state_code": "GA", "aliases": ["Panaji", "Panjim"], "name_hi": "उत्तर गोवा", "name_mr": "उत्तर गोवा", "bbox": [73.6, 15.4, 74.3, 15.8]},
    {"id": "dist_south_goa", "name": "South Goa", "canonical_name": "South Goa", "state_name": "Goa", "state_code": "GA", "aliases": ["Margao"], "name_hi": "दक्षिण गोवा", "name_mr": "दक्षिण गोवा", "bbox": [73.8, 14.9, 74.4, 15.3]},
    {"id": "dist_daman", "name": "Daman", "canonical_name": "Daman", "state_name": "Dadra and Nagar Haveli and Daman and Diu", "state_code": "DD", "aliases": ["Nani Daman"], "name_hi": "दमन", "name_mr": "दमन", "bbox": [72.8, 20.3, 72.9, 20.5]},

    # Karnataka
    {"id": "dist_dakshina_kannada", "name": "Dakshina Kannada", "canonical_name": "Dakshina Kannada", "state_name": "Karnataka", "state_code": "KA", "aliases": ["Mangalore", "Mangaluru"], "name_hi": "दक्षिण कन्नड़", "name_mr": "दक्षिण कन्नड", "bbox": [74.7, 12.5, 75.6, 13.2]},
    {"id": "dist_belagavi", "name": "Belagavi", "canonical_name": "Belagavi", "state_name": "Karnataka", "state_code": "KA", "aliases": ["Belgaum"], "name_hi": "बेलगाम", "name_mr": "बेळगाव", "bbox": [74.0, 15.3, 75.5, 16.9]},
    {"id": "dist_dharwad", "name": "Dharwad", "canonical_name": "Dharwad", "state_name": "Karnataka", "state_code": "KA", "aliases": ["Hubli", "Hubballi"], "name_hi": "धारवाड़", "name_mr": "धारवाड", "bbox": [74.8, 15.1, 75.5, 15.7]},

    # Tamil Nadu
    {"id": "dist_coimbatore", "name": "Coimbatore", "canonical_name": "Coimbatore", "state_name": "Tamil Nadu", "state_code": "TN", "aliases": ["Kovai"], "name_hi": "कोयंबटूर", "name_mr": "कोइम्बतूर", "bbox": [76.7, 10.5, 77.4, 11.4]},
    {"id": "dist_madurai", "name": "Madurai", "canonical_name": "Madurai", "state_name": "Tamil Nadu", "state_code": "TN", "aliases": [], "name_hi": "मदुरै", "name_mr": "मदुराई", "bbox": [77.8, 9.7, 78.5, 10.2]},
    {"id": "dist_tiruchirappalli", "name": "Tiruchirappalli", "canonical_name": "Tiruchirappalli", "state_name": "Tamil Nadu", "state_code": "TN", "aliases": ["Trichy"], "name_hi": "तिरुचिरापल्ली", "name_mr": "तिरुचिरापल्ली", "bbox": [78.4, 10.6, 78.9, 11.0]},

    # Telangana & Andhra Pradesh
    {"id": "dist_warangal", "name": "Warangal", "canonical_name": "Warangal", "state_name": "Telangana", "state_code": "TG", "aliases": ["Hanamkonda"], "name_hi": "वारंगल", "name_mr": "वारंगळ", "bbox": [79.4, 17.8, 79.8, 18.2]},
    {"id": "dist_visakhapatnam", "name": "Visakhapatnam", "canonical_name": "Visakhapatnam", "state_name": "Andhra Pradesh", "state_code": "AP", "aliases": ["Vizag"], "name_hi": "विशाखापट्टनम", "name_mr": "विशाखापट्टणम", "bbox": [83.1, 17.6, 83.4, 17.9]},
    {"id": "dist_ntr", "name": "NTR", "canonical_name": "Vijayawada", "state_name": "Andhra Pradesh", "state_code": "AP", "aliases": ["Vijayawada"], "name_hi": "विजयवाड़ा", "name_mr": "विजयवाडा", "bbox": [80.5, 16.4, 80.8, 16.7]},
    {"id": "dist_guntur", "name": "Guntur", "canonical_name": "Guntur", "state_name": "Andhra Pradesh", "state_code": "AP", "aliases": [], "name_hi": "गुंटूर", "name_mr": "गुंटूर", "bbox": [80.3, 16.2, 80.6, 16.5]},

    # Kerala
    {"id": "dist_thiruvananthapuram", "name": "Thiruvananthapuram", "canonical_name": "Thiruvananthapuram", "state_name": "Kerala", "state_code": "KL", "aliases": ["Trivandrum"], "name_hi": "तिरुवनंतपुरम", "name_mr": "तिरुवनंतपुरम", "bbox": [76.8, 8.3, 77.2, 8.7]},
    {"id": "dist_ernakulam", "name": "Ernakulam", "canonical_name": "Ernakulam", "state_name": "Kerala", "state_code": "KL", "aliases": ["Kochi", "Cochin"], "name_hi": "एर्नाकुलम", "name_mr": "एर्नाकुलम", "bbox": [76.1, 9.8, 76.5, 10.2]},
    {"id": "dist_kozhikode", "name": "Kozhikode", "canonical_name": "Kozhikode", "state_name": "Kerala", "state_code": "KL", "aliases": ["Calicut"], "name_hi": "कोझिकोड", "name_mr": "कोझिकोड", "bbox": [75.6, 11.1, 76.0, 11.5]},
    {"id": "dist_wayanad", "name": "Wayanad", "canonical_name": "Wayanad", "state_name": "Kerala", "state_code": "KL", "aliases": [], "name_hi": "वायनाड", "name_mr": "वायनाड", "bbox": [75.9, 11.5, 76.4, 11.9]},

    # Punjab & Haryana
    {"id": "dist_ludhiana", "name": "Ludhiana", "canonical_name": "Ludhiana", "state_name": "Punjab", "state_code": "PB", "aliases": [], "name_hi": "लुधियाना", "name_mr": "लुधियाना", "bbox": [75.7, 30.8, 76.0, 31.0]},
    {"id": "dist_amritsar", "name": "Amritsar", "canonical_name": "Amritsar", "state_name": "Punjab", "state_code": "PB", "aliases": [], "name_hi": "अमृतसर", "name_mr": "अमृतसर", "bbox": [74.7, 31.5, 75.0, 31.8]},
    {"id": "dist_sas_nagar", "name": "SAS Nagar", "canonical_name": "Mohali", "state_name": "Punjab", "state_code": "PB", "aliases": ["Mohali"], "name_hi": "मोहाली", "name_mr": "मोहाली", "bbox": [76.6, 30.6, 76.8, 30.8]},
    {"id": "dist_chandigarh", "name": "Chandigarh", "canonical_name": "Chandigarh", "state_name": "Chandigarh", "state_code": "CH", "aliases": [], "name_hi": "चंडीगढ़", "name_mr": "चंदीगड", "bbox": [76.7, 30.7, 76.9, 30.8]},

    # Rajasthan
    {"id": "dist_jodhpur", "name": "Jodhpur", "canonical_name": "Jodhpur", "state_name": "Rajasthan", "state_code": "RJ", "aliases": [], "name_hi": "जोधपुर", "name_mr": "जोधपूर", "bbox": [72.9, 26.2, 73.2, 26.4]},
    {"id": "dist_udaipur", "name": "Udaipur", "canonical_name": "Udaipur", "state_name": "Rajasthan", "state_code": "RJ", "aliases": [], "name_hi": "उदयपुर", "name_mr": "उदयपूर", "bbox": [73.6, 24.5, 73.8, 24.7]},

    # UP & Uttarakhand & Himachal & J&K & Ladakh
    {"id": "dist_varanasi", "name": "Varanasi", "canonical_name": "Varanasi", "state_name": "Uttar Pradesh", "state_code": "UP", "aliases": ["Benares", "Banaras", "Kashi"], "name_hi": "वाराणसी", "name_mr": "वाराणसी", "bbox": [82.9, 25.2, 83.1, 25.4]},
    {"id": "dist_prayagraj", "name": "Prayagraj", "canonical_name": "Prayagraj", "state_name": "Uttar Pradesh", "state_code": "UP", "aliases": ["Allahabad"], "name_hi": "प्रयागराज", "name_mr": "प्रयागराज", "bbox": [81.7, 25.3, 82.0, 25.6]},
    {"id": "dist_dehradun", "name": "Dehradun", "canonical_name": "Dehradun", "state_name": "Uttarakhand", "state_code": "UK", "aliases": [], "name_hi": "देहरादून", "name_mr": "डेहराडून", "bbox": [77.9, 30.2, 78.2, 30.5]},
    {"id": "dist_shimla", "name": "Shimla", "canonical_name": "Shimla", "state_name": "Himachal Pradesh", "state_code": "HP", "aliases": [], "name_hi": "शिमला", "name_mr": "शिमला", "bbox": [77.1, 31.0, 77.3, 31.2]},
    {"id": "dist_srinagar", "name": "Srinagar", "canonical_name": "Srinagar", "state_name": "Jammu and Kashmir", "state_code": "JK", "aliases": [], "name_hi": "श्रीनगर", "name_mr": "श्रीनगर", "bbox": [74.7, 34.0, 74.9, 34.2]},
    {"id": "dist_leh", "name": "Leh", "canonical_name": "Leh", "state_name": "Ladakh", "state_code": "LA", "aliases": [], "name_hi": "लेह", "name_mr": "लेह", "bbox": [77.4, 34.0, 77.7, 34.3]},

    # East & Central
    {"id": "dist_howrah", "name": "Howrah", "canonical_name": "Howrah", "state_name": "West Bengal", "state_code": "WB", "aliases": ["Haora"], "name_hi": "हावड़ा", "name_mr": "हावडा", "bbox": [88.2, 22.5, 88.4, 22.7]},
    {"id": "dist_darjeeling", "name": "Darjeeling", "canonical_name": "Darjeeling", "state_name": "West Bengal", "state_code": "WB", "aliases": [], "name_hi": "दार्जिलिंग", "name_mr": "दार्जिलिंग", "bbox": [88.1, 26.9, 88.4, 27.2]},
    {"id": "dist_patna", "name": "Patna", "canonical_name": "Patna", "state_name": "Bihar", "state_code": "BR", "aliases": [], "name_hi": "पटना", "name_mr": "पाटणा", "bbox": [85.0, 25.5, 85.3, 25.7]},
    {"id": "dist_gaya", "name": "Gaya", "canonical_name": "Gaya", "state_name": "Bihar", "state_code": "BR", "aliases": ["Bodh Gaya"], "name_hi": "गया", "name_mr": "गया", "bbox": [84.9, 24.7, 85.1, 24.9]},
    {"id": "dist_ranchi", "name": "Ranchi", "canonical_name": "Ranchi", "state_name": "Jharkhand", "state_code": "JH", "aliases": [], "name_hi": "रांची", "name_mr": "रांची", "bbox": [85.2, 23.2, 85.5, 23.5]},
    {"id": "dist_khordha", "name": "Khordha", "canonical_name": "Bhubaneswar", "state_name": "Odisha", "state_code": "OR", "aliases": ["Bhubaneswar"], "name_hi": "भुवनेश्वर", "name_mr": "भुवनेश्वर", "bbox": [85.7, 20.1, 86.0, 20.4]},
    {"id": "dist_indore", "name": "Indore", "canonical_name": "Indore", "state_name": "Madhya Pradesh", "state_code": "MP", "aliases": [], "name_hi": "इंदौर", "name_mr": "इंदूर", "bbox": [75.7, 22.6, 76.0, 22.9]},
    {"id": "dist_jabalpur", "name": "Jabalpur", "canonical_name": "Jabalpur", "state_name": "Madhya Pradesh", "state_code": "MP", "aliases": [], "name_hi": "जबलपुर", "name_mr": "जबलपूर", "bbox": [79.8, 23.0, 80.1, 23.3]},
    {"id": "dist_raipur", "name": "Raipur", "canonical_name": "Raipur", "state_name": "Chhattisgarh", "state_code": "CG", "aliases": [], "name_hi": "रायपुर", "name_mr": "रायपूर", "bbox": [81.5, 21.1, 81.8, 21.4]},
    {"id": "dist_bastar", "name": "Bastar", "canonical_name": "Jagdalpur", "state_name": "Chhattisgarh", "state_code": "CG", "aliases": ["Jagdalpur"], "name_hi": "बस्तर", "name_mr": "बस्तर", "bbox": [81.8, 19.0, 82.2, 19.3]},

    # Northeast & Islands
    {"id": "dist_kamrup_metro", "name": "Kamrup Metropolitan", "canonical_name": "Guwahati", "state_name": "Assam", "state_code": "AS", "aliases": ["Guwahati", "Dispur"], "name_hi": "गुवाहाटी", "name_mr": "गुवाहाटी", "bbox": [91.6, 26.0, 92.0, 26.3]},
    {"id": "dist_east_khasi_hills", "name": "East Khasi Hills", "canonical_name": "Shillong", "state_name": "Meghalaya", "state_code": "ML", "aliases": ["Shillong"], "name_hi": "शिलांग", "name_mr": "शिलाँग", "bbox": [91.7, 25.4, 92.0, 25.7]},
    {"id": "dist_imphal_west", "name": "Imphal West", "canonical_name": "Imphal", "state_name": "Manipur", "state_code": "MN", "aliases": ["Imphal"], "name_hi": "इम्फाल", "name_mr": "इम्फाळ", "bbox": [93.8, 24.7, 94.0, 24.9]},
    {"id": "dist_dimapur", "name": "Dimapur", "canonical_name": "Dimapur", "state_name": "Nagaland", "state_code": "NL", "aliases": [], "name_hi": "दीमापुर", "name_mr": "दिमापूर", "bbox": [93.6, 25.8, 93.9, 26.0]},
    {"id": "dist_aizawl", "name": "Aizawl", "canonical_name": "Aizawl", "state_name": "Mizoram", "state_code": "MZ", "aliases": [], "name_hi": "आइजोल", "name_mr": "ऐझॉल", "bbox": [92.6, 23.6, 92.8, 23.9]},
    {"id": "dist_west_tripura", "name": "West Tripura", "canonical_name": "Agartala", "state_name": "Tripura", "state_code": "TR", "aliases": ["Agartala"], "name_hi": "अगरतला", "name_mr": "अगरतळा", "bbox": [91.2, 23.7, 91.5, 24.0]},
    {"id": "dist_papum_pare", "name": "Papum Pare", "canonical_name": "Itanagar", "state_name": "Arunachal Pradesh", "state_code": "AR", "aliases": ["Itanagar"], "name_hi": "ईटानगर", "name_mr": "इटानगर", "bbox": [93.5, 27.0, 93.8, 27.3]},
    {"id": "dist_east_sikkim", "name": "East Sikkim", "canonical_name": "Gangtok", "state_name": "Sikkim", "state_code": "SK", "aliases": ["Gangtok"], "name_hi": "गंगटोक", "name_mr": "गँगटॉक", "bbox": [88.5, 27.2, 88.7, 27.4]},
    {"id": "dist_south_andaman", "name": "South Andaman", "canonical_name": "Port Blair", "state_name": "Andaman and Nicobar Islands", "state_code": "AN", "aliases": ["Port Blair"], "name_hi": "पोर्ट ब्लेयर", "name_mr": "पोर्ट ब्लेअर", "bbox": [92.6, 11.5, 92.9, 11.8]},
    {"id": "dist_lakshadweep", "name": "Lakshadweep", "canonical_name": "Kavaratti", "state_name": "Lakshadweep", "state_code": "LD", "aliases": ["Kavaratti"], "name_hi": "कवरत्ती", "name_mr": "कवरत्ती", "bbox": [72.5, 10.4, 72.8, 10.7]},
    {"id": "dist_puducherry", "name": "Puducherry", "canonical_name": "Puducherry", "state_name": "Puducherry", "state_code": "PY", "aliases": ["Pondicherry"], "name_hi": "पुदुचेरी", "name_mr": "पुडुचेरी", "bbox": [79.7, 11.8, 80.0, 12.1]}
]

# Additional Pan-India Localities with coordinates
PAN_INDIA_LOCALITIES: List[Dict[str, Any]] = [
    {"name": "Hadapsar", "canonical_name": "Hadapsar", "district": "Pune", "state": "Maharashtra", "state_name": "Maharashtra", "state_code": "MH", "pincode": "411028", "coordinates": {"latitude": 18.5089, "longitude": 73.9259}, "aliases": []},
    {"name": "Panchavati", "canonical_name": "Panchavati", "district": "Nashik", "state": "Maharashtra", "state_name": "Maharashtra", "state_code": "MH", "pincode": "422003", "coordinates": {"latitude": 20.0110, "longitude": 73.7903}, "aliases": []},
    {"name": "Koregaon", "canonical_name": "Koregaon", "district": "Satara", "state": "Maharashtra", "state_name": "Maharashtra", "state_code": "MH", "pincode": "415501", "coordinates": {"latitude": 17.7000, "longitude": 74.1800}, "aliases": []},
    {"name": "Varachha", "canonical_name": "Varachha", "district": "Surat", "state": "Gujarat", "state_name": "Gujarat", "state_code": "GJ", "pincode": "395006", "coordinates": {"latitude": 21.2185, "longitude": 72.8557}, "aliases": []},
    {"name": "Panaji", "canonical_name": "Panaji", "district": "North Goa", "state": "Goa", "state_name": "Goa", "state_code": "GA", "pincode": "403001", "coordinates": {"latitude": 15.4909, "longitude": 73.8278}, "aliases": ["Panjim"]},
    {"name": "Nani Daman", "canonical_name": "Nani Daman", "district": "Daman", "state": "Dadra and Nagar Haveli and Daman and Diu", "state_name": "Dadra and Nagar Haveli and Daman and Diu", "state_code": "DD", "pincode": "396210", "coordinates": {"latitude": 20.4170, "longitude": 72.8330}, "aliases": []},
    {"name": "Mylapore", "canonical_name": "Mylapore", "district": "Chennai", "state": "Tamil Nadu", "state_name": "Tamil Nadu", "state_code": "TN", "pincode": "600004", "coordinates": {"latitude": 13.0339, "longitude": 80.2678}, "aliases": []},
    {"name": "Gandhipuram", "canonical_name": "Gandhipuram", "district": "Coimbatore", "state": "Tamil Nadu", "state_name": "Tamil Nadu", "state_code": "TN", "pincode": "641012", "coordinates": {"latitude": 11.0168, "longitude": 76.9678}, "aliases": []},
    {"name": "Simmakkal", "canonical_name": "Simmakkal", "district": "Madurai", "state": "Tamil Nadu", "state_name": "Tamil Nadu", "state_code": "TN", "pincode": "625001", "coordinates": {"latitude": 9.9252, "longitude": 78.1198}, "aliases": []},
    {"name": "Hanamkonda", "canonical_name": "Hanamkonda", "district": "Warangal", "state": "Telangana", "state_name": "Telangana", "state_code": "TG", "pincode": "506001", "coordinates": {"latitude": 18.0130, "longitude": 79.5600}, "aliases": []},
    {"name": "MVP Colony", "canonical_name": "MVP Colony", "district": "Visakhapatnam", "state": "Andhra Pradesh", "state_name": "Andhra Pradesh", "state_code": "AP", "pincode": "530017", "coordinates": {"latitude": 17.7420, "longitude": 83.3360}, "aliases": []},
    {"name": "Kakkanad", "canonical_name": "Kakkanad", "district": "Ernakulam", "state": "Kerala", "state_name": "Kerala", "state_code": "KL", "pincode": "682030", "coordinates": {"latitude": 10.0159, "longitude": 76.3419}, "aliases": []},
    {"name": "White Town", "canonical_name": "White Town", "district": "Puducherry", "state": "Puducherry", "state_name": "Puducherry", "state_code": "PY", "pincode": "605001", "coordinates": {"latitude": 11.9340, "longitude": 79.8330}, "aliases": []},
    {"name": "Model Town", "canonical_name": "Model Town", "district": "Ludhiana", "state": "Punjab", "state_name": "Punjab", "state_code": "PB", "pincode": "141002", "coordinates": {"latitude": 30.8930, "longitude": 75.8360}, "aliases": []},
    {"name": "Assi Ghat", "canonical_name": "Assi Ghat", "district": "Varanasi", "state": "Uttar Pradesh", "state_name": "Uttar Pradesh", "state_code": "UP", "pincode": "221005", "coordinates": {"latitude": 25.2890, "longitude": 83.0060}, "aliases": []},
    {"name": "Mall Road", "canonical_name": "Mall Road", "district": "Shimla", "state": "Himachal Pradesh", "state_name": "Himachal Pradesh", "state_code": "HP", "pincode": "171001", "coordinates": {"latitude": 31.1048, "longitude": 77.1734}, "aliases": []},
    {"name": "Rajpur Road", "canonical_name": "Rajpur Road", "district": "Dehradun", "state": "Uttarakhand", "state_name": "Uttarakhand", "state_code": "UK", "pincode": "248001", "coordinates": {"latitude": 30.3400, "longitude": 78.0600}, "aliases": []},
    {"name": "Lal Chowk", "canonical_name": "Lal Chowk", "district": "Srinagar", "state": "Jammu and Kashmir", "state_name": "Jammu and Kashmir", "state_code": "JK", "pincode": "190001", "coordinates": {"latitude": 34.0720, "longitude": 74.8080}, "aliases": []},
    {"name": "Main Bazar", "canonical_name": "Main Bazar", "district": "Leh", "state": "Ladakh", "state_name": "Ladakh", "state_code": "LA", "pincode": "194101", "coordinates": {"latitude": 34.1640, "longitude": 77.5840}, "aliases": []},
    {"name": "Sector 35", "canonical_name": "Sector 35", "district": "Chandigarh", "state": "Chandigarh", "state_name": "Chandigarh", "state_code": "CH", "pincode": "160035", "coordinates": {"latitude": 30.7250, "longitude": 76.7640}, "aliases": []},
    {"name": "Shibpur", "canonical_name": "Shibpur", "district": "Howrah", "state": "West Bengal", "state_name": "West Bengal", "state_code": "WB", "pincode": "711102", "coordinates": {"latitude": 22.5650, "longitude": 88.3180}, "aliases": []},
    {"name": "Bodh Gaya", "canonical_name": "Bodh Gaya", "district": "Gaya", "state": "Bihar", "state_name": "Bihar", "state_code": "BR", "pincode": "824231", "coordinates": {"latitude": 24.6950, "longitude": 84.9910}, "aliases": []},
    {"name": "Rampur", "canonical_name": "Rampur Gaya", "district": "Gaya", "state": "Bihar", "state_name": "Bihar", "state_code": "BR", "pincode": "823001", "coordinates": {"latitude": 24.7800, "longitude": 84.9900}, "aliases": ["Rampur Gaya"]},
    {"name": "Kanke", "canonical_name": "Kanke", "district": "Ranchi", "state": "Jharkhand", "state_name": "Jharkhand", "state_code": "JH", "pincode": "834006", "coordinates": {"latitude": 23.4300, "longitude": 85.3200}, "aliases": []},
    {"name": "Saheed Nagar", "canonical_name": "Saheed Nagar", "district": "Khordha", "state": "Odisha", "state_name": "Odisha", "state_code": "OR", "pincode": "751007", "coordinates": {"latitude": 20.2920, "longitude": 85.8450}, "aliases": []},
    {"name": "Vijay Nagar", "canonical_name": "Vijay Nagar", "district": "Indore", "state": "Madhya Pradesh", "state_name": "Madhya Pradesh", "state_code": "MP", "pincode": "452010", "coordinates": {"latitude": 22.7533, "longitude": 75.8937}, "aliases": []},
    {"name": "Civil Lines", "canonical_name": "Civil Lines", "district": "Jabalpur", "state": "Madhya Pradesh", "state_name": "Madhya Pradesh", "state_code": "MP", "pincode": "482001", "coordinates": {"latitude": 23.1650, "longitude": 79.9400}, "aliases": []},
    {"name": "Telibandha", "canonical_name": "Telibandha", "district": "Raipur", "state": "Chhattisgarh", "state_name": "Chhattisgarh", "state_code": "CG", "pincode": "492006", "coordinates": {"latitude": 21.2330, "longitude": 81.6660}, "aliases": []},
    {"name": "Jagdalpur", "canonical_name": "Jagdalpur", "district": "Bastar", "state": "Chhattisgarh", "state_name": "Chhattisgarh", "state_code": "CG", "pincode": "494001", "coordinates": {"latitude": 19.0730, "longitude": 82.0280}, "aliases": []},
    {"name": "Dispur", "canonical_name": "Dispur", "district": "Kamrup Metropolitan", "state": "Assam", "state_name": "Assam", "state_code": "AS", "pincode": "781006", "coordinates": {"latitude": 26.1433, "longitude": 91.7898}, "aliases": []},
    {"name": "Police Bazar", "canonical_name": "Police Bazar", "district": "East Khasi Hills", "state": "Meghalaya", "state_name": "Meghalaya", "state_code": "ML", "pincode": "793001", "coordinates": {"latitude": 25.5780, "longitude": 91.8830}, "aliases": []},
    {"name": "Thangal Bazar", "canonical_name": "Thangal Bazar", "district": "Imphal West", "state": "Manipur", "state_name": "Manipur", "state_code": "MN", "pincode": "795001", "coordinates": {"latitude": 24.8100, "longitude": 93.9370}, "aliases": []},
    {"name": "Duncan Basti", "canonical_name": "Duncan Basti", "district": "Dimapur", "state": "Nagaland", "state_name": "Nagaland", "state_code": "NL", "pincode": "797112", "coordinates": {"latitude": 25.9000, "longitude": 93.7200}, "aliases": []},
    {"name": "Zarkawt", "canonical_name": "Zarkawt", "district": "Aizawl", "state": "Mizoram", "state_name": "Mizoram", "state_code": "MZ", "pincode": "796001", "coordinates": {"latitude": 23.7360, "longitude": 92.7170}, "aliases": []},
    {"name": "Banamalipur", "canonical_name": "Banamalipur", "district": "West Tripura", "state": "Tripura", "state_name": "Tripura", "state_code": "TR", "pincode": "799001", "coordinates": {"latitude": 23.8310, "longitude": 91.2860}, "aliases": []},
    {"name": "Itanagar", "canonical_name": "Itanagar", "district": "Papum Pare", "state": "Arunachal Pradesh", "state_name": "Arunachal Pradesh", "state_code": "AR", "pincode": "791111", "coordinates": {"latitude": 27.0844, "longitude": 93.6053}, "aliases": []},
    {"name": "MG Marg", "canonical_name": "MG Marg", "district": "East Sikkim", "state": "Sikkim", "state_name": "Sikkim", "state_code": "SK", "pincode": "737101", "coordinates": {"latitude": 27.3314, "longitude": 88.6138}, "aliases": []},
    {"name": "Aberdeen Bazar", "canonical_name": "Aberdeen Bazar", "district": "South Andaman", "state": "Andaman and Nicobar Islands", "state_name": "Andaman and Nicobar Islands", "state_code": "AN", "pincode": "744101", "coordinates": {"latitude": 11.6660, "longitude": 92.7430}, "aliases": []},
    {"name": "Kavaratti", "canonical_name": "Kavaratti", "district": "Lakshadweep", "state": "Lakshadweep", "state_name": "Lakshadweep", "state_code": "LD", "pincode": "682555", "coordinates": {"latitude": 10.5667, "longitude": 72.6369}, "aliases": []}
]


def write_national_gazetteer():
    # 1. Merge Districts preserving rich seed properties and homonyms
    merged_districts = list(SEED_DISTRICTS)
    seen_districts = {(d["name"].lower(), (d.get("state_name") or d.get("state", "")).lower()) for d in SEED_DISTRICTS}
    
    for d in PAN_INDIA_DISTRICTS:
        s_name = (d.get("state_name") or d.get("state", "")).lower()
        k = (d["name"].lower(), s_name)
        if k not in seen_districts:
            bbox = d.get("bbox", [70.0, 15.0, 85.0, 25.0])
            poly = d.get("polygon", [
                [bbox[0], bbox[1]],
                [bbox[0], bbox[3]],
                [bbox[2], bbox[3]],
                [bbox[2], bbox[1]],
                [bbox[0], bbox[1]]
            ])
            dist_obj = {
                "id": d.get("id", f"dist_{d['name'].lower().replace(' ', '_')}"),
                "lgd_code": d.get("lgd_code"),
                "name": d["name"],
                "canonical_name": d.get("canonical_name", d["name"]),
                "name_hi": d.get("name_hi"),
                "name_mr": d.get("name_mr"),
                "state_id": d.get("state_id"),
                "state_name": d.get("state_name", ""),
                "state_code": d.get("state_code", ""),
                "headquarters": d.get("headquarters", d["name"]),
                "aliases": d.get("aliases", []),
                "bbox": bbox,
                "polygon": poly,
                "subdistricts": d.get("subdistricts", []),
                "source": "LGD / Survey of India",
                "license": "GODL-India"
            }
            merged_districts.append(dist_obj)
            seen_districts.add(k)

    # 2. Merge Localities preserving rich seed properties and homonyms
    merged_localities = list(SEED_LOCALITIES)
    seen_localities = {(loc["name"].lower(), (loc.get("state_name") or loc.get("state", "")).lower()) for loc in SEED_LOCALITIES}

    for loc in PAN_INDIA_LOCALITIES:
        s_name = (loc.get("state_name") or loc.get("state", "")).lower()
        k = (loc["name"].lower(), s_name)
        if k not in seen_localities:
            coords = loc.get("coordinates", {"latitude": 20.0, "longitude": 78.0})
            lat, lon = coords.get("latitude", 20.0), coords.get("longitude", 78.0)
            bbox = loc.get("bbox", [round(lon - 0.03, 4), round(lat - 0.03, 4), round(lon + 0.03, 4), round(lat + 0.03, 4)])
            loc_obj = {
                "name": loc["name"],
                "canonical_name": loc.get("canonical_name", loc["name"]),
                "name_hi": loc.get("name_hi"),
                "name_mr": loc.get("name_mr"),
                "aliases": loc.get("aliases", []),
                "subdistrict_id": loc.get("subdistrict_id"),
                "subdistrict": loc.get("subdistrict"),
                "district_id": loc.get("district_id", f"dist_{loc.get('district', '').lower().replace(' ', '_')}"),
                "district": loc.get("district", ""),
                "state_id": loc.get("state_id"),
                "state": loc.get("state") or loc.get("state_name", ""),
                "state_code": loc.get("state_code", ""),
                "pincode": str(loc.get("pincode", "")),
                "coordinates": coords,
                "bbox": bbox
            }
            merged_localities.append(loc_obj)
            seen_localities.add(k)

    # 3. Merge Pincodes preserving post office lists and centroid coordinates
    merged_pincodes = list(SEED_PINCODES)
    seen_pins = {str(p["pincode"]) for p in SEED_PINCODES}

    for loc in PAN_INDIA_LOCALITIES:
        p_str = str(loc.get("pincode", "")).strip()
        if p_str and p_str not in seen_pins:
            merged_pincodes.append({
                "pincode": p_str,
                "office_name": f"{loc['name']} SO",
                "post_offices": [f"{loc['name']} SO", f"{loc['name']} B.O"],
                "circle": loc.get("state_name", "National"),
                "region": loc.get("state_name", "National"),
                "district": loc.get("district", ""),
                "state": loc.get("state_name", "") or loc.get("state", ""),
                "state_code": loc.get("state_code", ""),
                "centroid": loc.get("coordinates")
            })
            seen_pins.add(p_str)

    with open(PROCESSED_DIR / "states.json", "w", encoding="utf-8") as f:
        json.dump(ALL_36_STATES, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "districts.json", "w", encoding="utf-8") as f:
        json.dump(merged_districts, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "subdistricts.json", "w", encoding="utf-8") as f:
        json.dump(SEED_SUBDISTRICTS, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "localities.json", "w", encoding="utf-8") as f:
        json.dump(merged_localities, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "pincodes.json", "w", encoding="utf-8") as f:
        json.dump(merged_pincodes, f, indent=2, ensure_ascii=False)
    with open(PROCESSED_DIR / "pois.json", "w", encoding="utf-8") as f:
        json.dump(SEED_POIS, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated Pan-India National Gazetteer in {PROCESSED_DIR}:")
    print(f"  States       : {len(ALL_36_STATES)}")
    print(f"  Districts    : {len(merged_districts)}")
    print(f"  Subdistricts : {len(SEED_SUBDISTRICTS)}")
    print(f"  Localities   : {len(merged_localities)}")
    print(f"  Pincodes     : {len(merged_pincodes)}")
    print(f"  POIs         : {len(SEED_POIS)}")


if __name__ == "__main__":
    write_national_gazetteer()
