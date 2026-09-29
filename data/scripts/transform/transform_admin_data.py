"""Transform and structure raw geographic records into standardized GeoVerify format."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoverify.transform")

DATA_DIR = Path(__file__).parent.parent.parent
PROCESSED_DIR = DATA_DIR / "processed"
STAGING_DIR = DATA_DIR / "staging"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)

# 1. All 36 Indian States & Union Territories with LGD codes & Multilingual metadata
ALL_36_STATES = [
    {
        "lgd_code": 27,
        "code": "MH",
        "name": "Maharashtra",
        "canonical_name": "Maharashtra",
        "name_hi": "महाराष्ट्र",
        "name_mr": "महाराष्ट्र",
        "type": "State",
        "capital": "Mumbai",
        "aliases": ["Maharastra", "Maharashthra", "MH", "Maharashtra State", "Maha"],
        "bbox": [72.6, 15.6, 80.9, 22.0],
        "polygon": [
            [72.6, 18.9], [72.8, 20.0], [74.5, 21.9], [78.5, 21.8],
            [80.9, 19.5], [80.0, 18.0], [77.5, 15.6], [73.5, 15.8], [72.6, 18.9]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 29,
        "code": "KA",
        "name": "Karnataka",
        "canonical_name": "Karnataka",
        "name_hi": "कर्नाटक",
        "name_mr": "कर्नाटक",
        "type": "State",
        "capital": "Bengaluru",
        "aliases": ["Karnatak", "KA", "Karnataka State", "Mysore State"],
        "bbox": [74.0, 11.5, 78.5, 18.5],
        "polygon": [
            [74.0, 14.5], [74.5, 17.5], [77.5, 18.5], [78.5, 15.0],
            [77.8, 12.0], [76.0, 11.5], [74.5, 12.5], [74.0, 14.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 7,
        "code": "DL",
        "name": "Delhi",
        "canonical_name": "Delhi",
        "name_hi": "दिल्ली",
        "name_mr": "दिल्ली",
        "type": "Union Territory",
        "capital": "New Delhi",
        "aliases": ["NCT of Delhi", "National Capital Territory of Delhi", "DL", "New Delhi", "Dilli"],
        "bbox": [76.8, 28.4, 77.4, 28.9],
        "polygon": [
            [76.8, 28.5], [76.9, 28.8], [77.2, 28.9], [77.4, 28.7],
            [77.3, 28.4], [77.0, 28.4], [76.8, 28.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 33,
        "code": "TN",
        "name": "Tamil Nadu",
        "canonical_name": "Tamil Nadu",
        "name_hi": "तमिलनाडु",
        "name_mr": "तमिळनाडू",
        "type": "State",
        "capital": "Chennai",
        "aliases": ["Tamilnadu", "TN", "Madras State", "Tamil Nadu State"],
        "bbox": [76.2, 8.0, 80.4, 13.5],
        "polygon": [
            [76.2, 10.5], [77.0, 12.5], [80.3, 13.5], [80.0, 10.0],
            [78.0, 8.0], [77.2, 8.3], [76.8, 9.5], [76.2, 10.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 36,
        "code": "TG",
        "name": "Telangana",
        "canonical_name": "Telangana",
        "name_hi": "तेलंगाना",
        "name_mr": "तेलंगणा",
        "type": "State",
        "capital": "Hyderabad",
        "aliases": ["Telengana", "TG", "TS"],
        "bbox": [77.2, 15.8, 81.8, 19.9],
        "polygon": [
            [77.2, 17.0], [78.0, 19.5], [80.5, 19.9], [81.8, 17.5],
            [79.8, 16.0], [78.2, 15.8], [77.2, 17.0]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 24,
        "code": "GJ",
        "name": "Gujarat",
        "canonical_name": "Gujarat",
        "name_hi": "गुजरात",
        "name_mr": "गुजरात",
        "type": "State",
        "capital": "Gandhinagar",
        "aliases": ["Gujrat", "GJ", "Gujarat State"],
        "bbox": [68.1, 20.1, 74.5, 24.7],
        "polygon": [
            [68.1, 23.5], [70.0, 24.7], [74.5, 24.0], [73.5, 20.1],
            [72.5, 20.8], [69.0, 22.0], [68.1, 23.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 19,
        "code": "WB",
        "name": "West Bengal",
        "canonical_name": "West Bengal",
        "name_hi": "पश्चिम बंगाल",
        "name_mr": "पश्चिम बंगाल",
        "type": "State",
        "capital": "Kolkata",
        "aliases": ["Westbengal", "WB", "Paschim Banga", "Bengal"],
        "bbox": [85.8, 21.5, 89.9, 27.2],
        "polygon": [
            [85.8, 23.5], [87.5, 27.2], [89.9, 26.5], [88.5, 22.0],
            [87.5, 21.5], [86.5, 22.5], [85.8, 23.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 9,
        "code": "UP",
        "name": "Uttar Pradesh",
        "canonical_name": "Uttar Pradesh",
        "name_hi": "उत्तर प्रदेश",
        "name_mr": "उत्तर प्रदेश",
        "type": "State",
        "capital": "Lucknow",
        "aliases": ["UP", "Uttarpradesh", "U.P."],
        "bbox": [77.0, 23.8, 84.6, 30.4],
        "polygon": [
            [77.0, 28.5], [78.0, 30.4], [84.6, 27.5], [83.5, 24.0],
            [81.0, 23.8], [78.5, 25.5], [77.0, 28.5]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 8,
        "code": "RJ",
        "name": "Rajasthan",
        "canonical_name": "Rajasthan",
        "name_hi": "राजस्थान",
        "name_mr": "राजस्थान",
        "type": "State",
        "capital": "Jaipur",
        "aliases": ["RJ", "Rajsthan", "Rajputana"],
        "bbox": [69.5, 23.0, 78.2, 30.2],
        "polygon": [
            [69.5, 27.0], [72.0, 30.2], [77.0, 29.0], [78.2, 26.5],
            [76.0, 23.5], [73.0, 23.0], [69.5, 27.0]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 32,
        "code": "KL",
        "name": "Kerala",
        "canonical_name": "Kerala",
        "name_hi": "केरल",
        "name_mr": "केरळ",
        "type": "State",
        "capital": "Thiruvananthapuram",
        "aliases": ["KL", "Keralam"],
        "bbox": [74.8, 8.2, 77.5, 12.8],
        "polygon": [
            [74.8, 12.8], [76.0, 12.0], [77.5, 10.0], [77.3, 8.3],
            [76.8, 8.2], [75.8, 10.5], [74.8, 12.8]
        ],
        "source": "Local Government Directory (LGD) / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 23,
        "code": "MP",
        "name": "Madhya Pradesh",
        "canonical_name": "Madhya Pradesh",
        "name_hi": "मध्य प्रदेश",
        "name_mr": "मध्य प्रदेश",
        "type": "State",
        "capital": "Bhopal",
        "aliases": ["MP", "Madhya Bharat"],
        "bbox": [74.0, 21.1, 82.8, 26.9],
        "polygon": [[74.0, 21.5], [75.0, 26.9], [82.0, 24.5], [82.8, 22.0], [78.0, 21.1], [74.0, 21.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 28,
        "code": "AP",
        "name": "Andhra Pradesh",
        "canonical_name": "Andhra Pradesh",
        "name_hi": "आंध्र प्रदेश",
        "name_mr": "आंध्र प्रदेश",
        "type": "State",
        "capital": "Amaravati",
        "aliases": ["AP", "Andhra"],
        "bbox": [76.7, 12.6, 84.8, 19.1],
        "polygon": [[76.7, 14.0], [79.0, 19.1], [84.8, 18.5], [80.5, 13.5], [76.7, 12.6], [76.7, 14.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 3,
        "code": "PB",
        "name": "Punjab",
        "canonical_name": "Punjab",
        "name_hi": "पंजाब",
        "name_mr": "पंजाब",
        "type": "State",
        "capital": "Chandigarh",
        "aliases": ["PB"],
        "bbox": [73.8, 29.5, 76.9, 32.5],
        "polygon": [[73.8, 30.0], [74.5, 32.5], [76.9, 31.5], [76.0, 29.5], [73.8, 30.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 6,
        "code": "HR",
        "name": "Haryana",
        "canonical_name": "Haryana",
        "name_hi": "हरियाणा",
        "name_mr": "हरियाणा",
        "type": "State",
        "capital": "Chandigarh",
        "aliases": ["HR"],
        "bbox": [74.4, 27.6, 77.6, 30.9],
        "polygon": [[74.4, 28.5], [76.0, 30.9], [77.6, 29.5], [76.5, 27.6], [74.4, 28.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 10,
        "code": "BR",
        "name": "Bihar",
        "canonical_name": "Bihar",
        "name_hi": "बिहार",
        "name_mr": "बिहार",
        "type": "State",
        "capital": "Patna",
        "aliases": ["BR"],
        "bbox": [83.3, 24.3, 88.3, 27.5],
        "polygon": [[83.3, 25.0], [84.5, 27.5], [88.3, 26.5], [87.5, 24.3], [83.3, 25.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 21,
        "code": "OD",
        "name": "Odisha",
        "canonical_name": "Odisha",
        "name_hi": "ओडिशा",
        "name_mr": "ओडिशा",
        "type": "State",
        "capital": "Bhubaneswar",
        "aliases": ["OD", "Orissa"],
        "bbox": [81.4, 17.8, 87.5, 22.6],
        "polygon": [[81.4, 18.5], [83.5, 22.6], [87.5, 21.5], [85.0, 19.0], [81.4, 17.8], [81.4, 18.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 22,
        "code": "CG",
        "name": "Chhattisgarh",
        "canonical_name": "Chhattisgarh",
        "name_hi": "छत्तीसगढ़",
        "name_mr": "छत्तीसगड",
        "type": "State",
        "capital": "Raipur",
        "aliases": ["CG", "Chattisgarh"],
        "bbox": [80.2, 17.8, 84.4, 24.1],
        "polygon": [[80.2, 19.0], [82.5, 24.1], [84.4, 23.0], [81.5, 17.8], [80.2, 19.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 20,
        "code": "JH",
        "name": "Jharkhand",
        "canonical_name": "Jharkhand",
        "name_hi": "झारखंड",
        "name_mr": "झारखंड",
        "type": "State",
        "capital": "Ranchi",
        "aliases": ["JH"],
        "bbox": [83.3, 21.9, 87.9, 25.3],
        "polygon": [[83.3, 23.5], [85.5, 25.3], [87.9, 24.5], [86.0, 21.9], [83.3, 23.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 18,
        "code": "AS",
        "name": "Assam",
        "canonical_name": "Assam",
        "name_hi": "असम",
        "name_mr": "आसाम",
        "type": "State",
        "capital": "Dispur",
        "aliases": ["AS", "Asom"],
        "bbox": [89.7, 24.1, 96.0, 28.0],
        "polygon": [[89.7, 26.0], [93.0, 28.0], [96.0, 27.5], [92.5, 24.1], [89.7, 26.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 5,
        "code": "UK",
        "name": "Uttarakhand",
        "canonical_name": "Uttarakhand",
        "name_hi": "उत्तराखंड",
        "name_mr": "उत्तराखंड",
        "type": "State",
        "capital": "Dehradun",
        "aliases": ["UK", "UA", "Uttaranchal"],
        "bbox": [77.6, 28.7, 81.0, 31.5],
        "polygon": [[77.6, 30.0], [79.0, 31.5], [81.0, 30.5], [79.5, 28.7], [77.6, 30.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 2,
        "code": "HP",
        "name": "Himachal Pradesh",
        "canonical_name": "Himachal Pradesh",
        "name_hi": "हिमाचल प्रदेश",
        "name_mr": "हिमाचल प्रदेश",
        "type": "State",
        "capital": "Shimla",
        "aliases": ["HP"],
        "bbox": [75.6, 30.4, 79.0, 33.2],
        "polygon": [[75.6, 31.5], [77.0, 33.2], [79.0, 32.0], [77.5, 30.4], [75.6, 31.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 30,
        "code": "GA",
        "name": "Goa",
        "canonical_name": "Goa",
        "name_hi": "गोवा",
        "name_mr": "गोवा",
        "type": "State",
        "capital": "Panaji",
        "aliases": ["GA"],
        "bbox": [73.6, 14.9, 74.3, 15.8],
        "polygon": [[73.6, 15.5], [74.0, 15.8], [74.3, 15.2], [73.9, 14.9], [73.6, 15.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 11,
        "code": "SK",
        "name": "Sikkim",
        "canonical_name": "Sikkim",
        "name_hi": "सिक्किम",
        "name_mr": "सिक्कीम",
        "type": "State",
        "capital": "Gangtok",
        "aliases": ["SK"],
        "bbox": [88.0, 27.1, 88.9, 28.1],
        "polygon": [[88.0, 27.5], [88.5, 28.1], [88.9, 27.8], [88.6, 27.1], [88.0, 27.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 12,
        "code": "AR",
        "name": "Arunachal Pradesh",
        "canonical_name": "Arunachal Pradesh",
        "name_hi": "अरुणाचल प्रदेश",
        "name_mr": "अरुणाचल प्रदेश",
        "type": "State",
        "capital": "Itanagar",
        "aliases": ["AR"],
        "bbox": [91.5, 26.6, 97.4, 29.5],
        "polygon": [[91.5, 27.5], [94.5, 29.5], [97.4, 28.2], [93.5, 26.6], [91.5, 27.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 14,
        "code": "MN",
        "name": "Manipur",
        "canonical_name": "Manipur",
        "name_hi": "मणिपुर",
        "name_mr": "मणिपूर",
        "type": "State",
        "capital": "Imphal",
        "aliases": ["MN"],
        "bbox": [93.0, 23.8, 94.8, 25.7],
        "polygon": [[93.0, 24.5], [94.0, 25.7], [94.8, 24.8], [93.8, 23.8], [93.0, 24.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 17,
        "code": "ME",
        "name": "Meghalaya",
        "canonical_name": "Meghalaya",
        "name_hi": "मेघालय",
        "name_mr": "मेघालय",
        "type": "State",
        "capital": "Shillong",
        "aliases": ["ML", "ME"],
        "bbox": [89.8, 25.0, 92.8, 26.1],
        "polygon": [[89.8, 25.5], [91.5, 26.1], [92.8, 25.8], [91.0, 25.0], [89.8, 25.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 15,
        "code": "MZ",
        "name": "Mizoram",
        "canonical_name": "Mizoram",
        "name_hi": "मिज़ोरम",
        "name_mr": "मिझोरम",
        "type": "State",
        "capital": "Aizawl",
        "aliases": ["MZ"],
        "bbox": [92.2, 21.9, 93.4, 24.5],
        "polygon": [[92.2, 23.0], [93.0, 24.5], [93.4, 23.2], [92.8, 21.9], [92.2, 23.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 13,
        "code": "NL",
        "name": "Nagaland",
        "canonical_name": "Nagaland",
        "name_hi": "नागालैंड",
        "name_mr": "नागालँड",
        "type": "State",
        "capital": "Kohima",
        "aliases": ["NL"],
        "bbox": [93.3, 25.1, 95.3, 27.0],
        "polygon": [[93.3, 25.8], [94.5, 27.0], [95.3, 26.5], [94.0, 25.1], [93.3, 25.8]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 16,
        "code": "TR",
        "name": "Tripura",
        "canonical_name": "Tripura",
        "name_hi": "त्रिपुरा",
        "name_mr": "त्रिपुरा",
        "type": "State",
        "capital": "Agartala",
        "aliases": ["TR"],
        "bbox": [91.1, 22.9, 92.4, 24.5],
        "polygon": [[91.1, 23.5], [92.0, 24.5], [92.4, 23.8], [91.8, 22.9], [91.1, 23.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 1,
        "code": "JK",
        "name": "Jammu and Kashmir",
        "canonical_name": "Jammu and Kashmir",
        "name_hi": "जम्मू और कश्मीर",
        "name_mr": "जम्मू आणि काश्मीर",
        "type": "Union Territory",
        "capital": "Srinagar / Jammu",
        "aliases": ["JK", "J&K"],
        "bbox": [73.5, 32.2, 77.8, 37.1],
        "polygon": [[73.5, 33.5], [75.0, 37.1], [77.8, 35.0], [75.5, 32.2], [73.5, 33.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 37,
        "code": "LA",
        "name": "Ladakh",
        "canonical_name": "Ladakh",
        "name_hi": "लद्दाख",
        "name_mr": "लडाख",
        "type": "Union Territory",
        "capital": "Leh",
        "aliases": ["LA"],
        "bbox": [75.5, 32.5, 80.5, 36.0],
        "polygon": [[75.5, 34.0], [77.5, 36.0], [80.5, 34.5], [78.0, 32.5], [75.5, 34.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 34,
        "code": "PY",
        "name": "Puducherry",
        "canonical_name": "Puducherry",
        "name_hi": "पुदुच्चेरी",
        "name_mr": "पुडुचेरी",
        "type": "Union Territory",
        "capital": "Puducherry",
        "aliases": ["PY", "Pondicherry"],
        "bbox": [79.6, 11.8, 80.0, 12.1],
        "polygon": [[79.6, 11.9], [79.8, 12.1], [80.0, 12.0], [79.8, 11.8], [79.6, 11.9]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 4,
        "code": "CH",
        "name": "Chandigarh",
        "canonical_name": "Chandigarh",
        "name_hi": "चंडीगढ़",
        "name_mr": "चंदीगड",
        "type": "Union Territory",
        "capital": "Chandigarh",
        "aliases": ["CH"],
        "bbox": [76.7, 30.6, 76.9, 30.8],
        "polygon": [[76.7, 30.7], [76.8, 30.8], [76.9, 30.75], [76.8, 30.6], [76.7, 30.7]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 35,
        "code": "AN",
        "name": "Andaman and Nicobar Islands",
        "canonical_name": "Andaman and Nicobar Islands",
        "name_hi": "अंडमान और निकोबार द्वीप समूह",
        "name_mr": "अंदमान आणि निकोबार",
        "type": "Union Territory",
        "capital": "Port Blair",
        "aliases": ["AN", "Andaman and Nicobar"],
        "bbox": [92.2, 6.7, 94.0, 13.7],
        "polygon": [[92.2, 9.0], [93.0, 13.7], [94.0, 12.5], [93.5, 6.7], [92.2, 9.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 26,
        "code": "DN",
        "name": "Dadra and Nagar Haveli and Daman and Diu",
        "canonical_name": "Dadra and Nagar Haveli and Daman and Diu",
        "name_hi": "दादरा और नगर हवेली और दमन और दीव",
        "name_mr": "दादरा आणि नगर हवेली आणि दमण आणि दीव",
        "type": "Union Territory",
        "capital": "Daman",
        "aliases": ["DN", "DD", "DNH", "Daman and Diu"],
        "bbox": [70.8, 20.0, 73.2, 20.9],
        "polygon": [[70.8, 20.5], [72.5, 20.9], [73.2, 20.2], [71.5, 20.0], [70.8, 20.5]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    },
    {
        "lgd_code": 31,
        "code": "LD",
        "name": "Lakshadweep",
        "canonical_name": "Lakshadweep",
        "name_hi": "लक्षद्वीप",
        "name_mr": "लक्षद्वीप",
        "type": "Union Territory",
        "capital": "Kavaratti",
        "aliases": ["LD", "Laccadive"],
        "bbox": [71.5, 8.2, 74.0, 12.5],
        "polygon": [[71.5, 10.0], [72.5, 12.5], [74.0, 11.5], [73.0, 8.2], [71.5, 10.0]],
        "source": "LGD / Survey of India",
        "license": "GODL-India"
    }
]

# 2. Comprehensive Districts with LGD Codes, parent states, multilingual names & geometry
DISTRICTS = [
    # Maharashtra Districts
    {
        "id": "dist_pune",
        "lgd_code": 490,
        "name": "Pune",
        "canonical_name": "Pune",
        "name_hi": "पुणे",
        "name_mr": "पुणे",
        "aliases": ["Poona", "Pune District", "Puna"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Pune",
        "bbox": [73.3, 17.9, 75.1, 19.4],
        "polygon": [
            [73.3, 18.5], [73.6, 19.3], [74.5, 19.4], [75.1, 18.6],
            [74.8, 17.9], [73.8, 18.0], [73.3, 18.5]
        ]
    },
    {
        "id": "dist_mumbai_suburban",
        "lgd_code": 489,
        "name": "Mumbai Suburban",
        "canonical_name": "Mumbai Suburban",
        "name_hi": "मुंबई उपनगर",
        "name_mr": "मुंबई उपनगर",
        "aliases": ["Mumbai", "Bombay", "Mumbai Suburban District", "Bandra"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Bandra",
        "bbox": [72.7, 18.9, 73.0, 19.3],
        "polygon": [
            [72.7, 19.0], [72.8, 19.3], [73.0, 19.2], [72.9, 18.9], [72.7, 19.0]
        ]
    },
    {
        "id": "dist_mumbai_city",
        "lgd_code": 488,
        "name": "Mumbai City",
        "canonical_name": "Mumbai City",
        "name_hi": "मुंबई शहर",
        "name_mr": "मुंबई शहर",
        "aliases": ["South Mumbai", "Town"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Mumbai",
        "bbox": [72.8, 18.88, 72.86, 19.02],
        "polygon": [[72.8, 18.9], [72.82, 19.02], [72.86, 19.0], [72.84, 18.88], [72.8, 18.9]]
    },
    {
        "id": "dist_thane",
        "lgd_code": 501,
        "name": "Thane",
        "canonical_name": "Thane",
        "name_hi": "ठाणे",
        "name_mr": "ठाणे",
        "aliases": ["Thana"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Thane",
        "bbox": [72.9, 19.1, 73.5, 19.6],
        "polygon": [[72.9, 19.2], [73.1, 19.6], [73.5, 19.4], [73.3, 19.1], [72.9, 19.2]]
    },
    {
        "id": "dist_kolhapur",
        "lgd_code": 482,
        "name": "Kolhapur",
        "canonical_name": "Kolhapur",
        "name_hi": "कोल्हापुर",
        "name_mr": "कोल्हापूर",
        "aliases": ["Kolhapur District"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Kolhapur",
        "bbox": [73.7, 15.7, 74.7, 17.2],
        "polygon": [
            [73.7, 16.5], [74.0, 17.2], [74.7, 16.8], [74.5, 15.7], [73.7, 16.5]
        ]
    },
    {
        "id": "dist_nagpur",
        "lgd_code": 485,
        "name": "Nagpur",
        "canonical_name": "Nagpur",
        "name_hi": "नागपुर",
        "name_mr": "नागपूर",
        "aliases": ["Nagpur District"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Nagpur",
        "bbox": [78.5, 20.5, 79.6, 21.8],
        "polygon": [
            [78.5, 21.0], [78.8, 21.8], [79.6, 21.5], [79.4, 20.5], [78.5, 21.0]
        ]
    },
    {
        "id": "dist_nashik",
        "lgd_code": 487,
        "name": "Nashik",
        "canonical_name": "Nashik",
        "name_hi": "नासिक",
        "name_mr": "नाशिक",
        "aliases": ["Nasik"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Nashik",
        "bbox": [73.3, 19.5, 74.9, 20.9],
        "polygon": [[73.3, 20.0], [74.0, 20.9], [74.9, 20.5], [74.5, 19.5], [73.3, 20.0]]
    },
    {
        "id": "dist_aurangabad_mh",
        "lgd_code": 470,
        "name": "Chhatrapati Sambhajinagar",
        "canonical_name": "Chhatrapati Sambhajinagar",
        "name_hi": "छत्रपति संभाजीनगर",
        "name_mr": "छत्रपती संभाजीनगर",
        "aliases": ["Aurangabad", "Aurangabad Maharashtra", "Sambhajinagar"],
        "state_lgd_code": 27,
        "state_code": "MH",
        "state_name": "Maharashtra",
        "headquarters": "Chhatrapati Sambhajinagar",
        "bbox": [74.7, 19.3, 76.0, 20.7],
        "polygon": [[74.7, 19.8], [75.2, 20.7], [76.0, 20.2], [75.5, 19.3], [74.7, 19.8]]
    },
    # Karnataka Districts
    {
        "id": "dist_bengaluru_urban",
        "lgd_code": 529,
        "name": "Bengaluru Urban",
        "canonical_name": "Bengaluru Urban",
        "name_hi": "बेंगलुरु शहरी",
        "name_mr": "बंगळूर शहरी",
        "aliases": ["Bangalore", "Bengaluru", "Bangalore Urban", "BLR"],
        "state_lgd_code": 29,
        "state_code": "KA",
        "state_name": "Karnataka",
        "headquarters": "Bengaluru",
        "bbox": [77.4, 12.7, 77.8, 13.2],
        "polygon": [
            [77.4, 12.9], [77.5, 13.2], [77.8, 13.1], [77.8, 12.8],
            [77.5, 12.7], [77.4, 12.9]
        ]
    },
    {
        "id": "dist_mysuru",
        "lgd_code": 544,
        "name": "Mysuru",
        "canonical_name": "Mysuru",
        "name_hi": "मैसूर",
        "name_mr": "म्हैसूर",
        "aliases": ["Mysore"],
        "state_lgd_code": 29,
        "state_code": "KA",
        "state_name": "Karnataka",
        "headquarters": "Mysuru",
        "bbox": [75.9, 11.7, 77.1, 12.6],
        "polygon": [[75.9, 12.2], [76.5, 12.6], [77.1, 12.0], [76.6, 11.7], [75.9, 12.2]]
    },
    # Delhi Districts
    {
        "id": "dist_new_delhi",
        "lgd_code": 88,
        "name": "New Delhi",
        "canonical_name": "New Delhi",
        "name_hi": "नई दिल्ली",
        "name_mr": "नवी दिल्ली",
        "aliases": ["Central Delhi", "Delhi Central", "NDLS"],
        "state_lgd_code": 7,
        "state_code": "DL",
        "state_name": "Delhi",
        "headquarters": "Connaught Place",
        "bbox": [77.1, 28.5, 77.3, 28.7],
        "polygon": [
            [77.1, 28.6], [77.2, 28.7], [77.3, 28.6], [77.2, 28.5], [77.1, 28.6]
        ]
    },
    {
        "id": "dist_south_delhi",
        "lgd_code": 91,
        "name": "South Delhi",
        "canonical_name": "South Delhi",
        "name_hi": "दक्षिण दिल्ली",
        "name_mr": "दक्षिण दिल्ली",
        "aliases": ["South Delhi District"],
        "state_lgd_code": 7,
        "state_code": "DL",
        "state_name": "Delhi",
        "headquarters": "Saket",
        "bbox": [77.15, 28.45, 77.3, 28.58],
        "polygon": [[77.15, 28.5], [77.25, 28.58], [77.3, 28.52], [77.2, 28.45], [77.15, 28.5]]
    },
    # Tamil Nadu Districts
    {
        "id": "dist_chennai",
        "lgd_code": 565,
        "name": "Chennai",
        "canonical_name": "Chennai",
        "name_hi": "चेन्नई",
        "name_mr": "चेन्नई",
        "aliases": ["Madras", "Chennai District"],
        "state_lgd_code": 33,
        "state_code": "TN",
        "state_name": "Tamil Nadu",
        "headquarters": "Chennai",
        "bbox": [80.1, 12.9, 80.35, 13.2],
        "polygon": [
            [80.1, 13.0], [80.2, 13.2], [80.35, 13.1], [80.3, 12.9], [80.1, 13.0]
        ]
    },
    # Telangana Districts
    {
        "id": "dist_hyderabad",
        "lgd_code": 505,
        "name": "Hyderabad",
        "canonical_name": "Hyderabad",
        "name_hi": "हैदराबाद",
        "name_mr": "हैदराबाद",
        "aliases": ["Hyderabad District", "HYD", "Secunderabad"],
        "state_lgd_code": 36,
        "state_code": "TG",
        "state_name": "Telangana",
        "headquarters": "Hyderabad",
        "bbox": [78.3, 17.2, 78.6, 17.55],
        "polygon": [
            [78.3, 17.4], [78.4, 17.55], [78.6, 17.45], [78.5, 17.2], [78.3, 17.4]
        ]
    },
    # Uttar Pradesh Districts
    {
        "id": "dist_lucknow",
        "lgd_code": 160,
        "name": "Lucknow",
        "canonical_name": "Lucknow",
        "name_hi": "लखनऊ",
        "name_mr": "लखनौ",
        "aliases": ["LKO"],
        "state_lgd_code": 9,
        "state_code": "UP",
        "state_name": "Uttar Pradesh",
        "headquarters": "Lucknow",
        "bbox": [80.6, 26.5, 81.2, 27.2],
        "polygon": [[80.6, 26.8], [80.9, 27.2], [81.2, 26.9], [80.9, 26.5], [80.6, 26.8]]
    },
    {
        "id": "dist_rampur",
        "lgd_code": 178,
        "name": "Rampur",
        "canonical_name": "Rampur",
        "name_hi": "रामपुर",
        "name_mr": "रामपूर",
        "aliases": ["Rampur District"],
        "state_lgd_code": 9,
        "state_code": "UP",
        "state_name": "Uttar Pradesh",
        "headquarters": "Rampur",
        "bbox": [78.9, 28.6, 79.3, 29.1],
        "polygon": [[78.9, 28.8], [79.1, 29.1], [79.3, 28.9], [79.1, 28.6], [78.9, 28.8]]
    },
    # West Bengal Districts
    {
        "id": "dist_north_24_parganas",
        "lgd_code": 310,
        "name": "North 24 Parganas",
        "canonical_name": "North 24 Parganas",
        "name_hi": "उत्तर 24 परगना",
        "name_mr": "उत्तर २४ परगणा",
        "aliases": ["24 Parganas North", "Rajarhat Area"],
        "state_lgd_code": 19,
        "state_code": "WB",
        "state_name": "West Bengal",
        "headquarters": "Barasat",
        "bbox": [88.3, 22.2, 89.1, 23.2],
        "polygon": [[88.3, 22.6], [88.7, 23.2], [89.1, 22.8], [88.8, 22.2], [88.3, 22.6]]
    }
]

# 3. Sub-Districts / Talukas / Tehsils / Mandals
SUBDISTRICTS = [
    {
        "id": "subdist_haveli",
        "lgd_code": 4150,
        "name": "Haveli",
        "canonical_name": "Haveli",
        "admin_type": "Taluka",
        "district_id": "dist_pune",
        "district_name": "Pune",
        "state_name": "Maharashtra",
        "bbox": [73.7, 18.4, 74.1, 18.7],
        "polygon": [[73.7, 18.5], [73.9, 18.7], [74.1, 18.6], [73.9, 18.4], [73.7, 18.5]]
    },
    {
        "id": "subdist_pune_city",
        "lgd_code": 4151,
        "name": "Pune City",
        "canonical_name": "Pune City",
        "admin_type": "Taluka",
        "district_id": "dist_pune",
        "district_name": "Pune",
        "state_name": "Maharashtra",
        "bbox": [73.8, 18.48, 73.92, 18.56],
        "polygon": [[73.8, 18.5], [73.86, 18.56], [73.92, 18.52], [73.88, 18.48], [73.8, 18.5]]
    },
    {
        "id": "subdist_mulshi",
        "lgd_code": 4152,
        "name": "Mulshi",
        "canonical_name": "Mulshi",
        "admin_type": "Taluka",
        "district_id": "dist_pune",
        "district_name": "Pune",
        "state_name": "Maharashtra",
        "bbox": [73.5, 18.45, 73.78, 18.65],
        "polygon": [[73.5, 18.55], [73.7, 18.65], [73.78, 18.58], [73.65, 18.45], [73.5, 18.55]]
    },
    {
        "id": "subdist_andheri",
        "lgd_code": 4140,
        "name": "Andheri",
        "canonical_name": "Andheri",
        "admin_type": "Taluka",
        "district_id": "dist_mumbai_suburban",
        "district_name": "Mumbai Suburban",
        "state_name": "Maharashtra",
        "bbox": [72.8, 19.04, 72.9, 19.16],
        "polygon": [[72.8, 19.08], [72.84, 19.16], [72.9, 19.12], [72.86, 19.04], [72.8, 19.08]]
    },
    {
        "id": "subdist_bengaluru_east",
        "lgd_code": 5501,
        "name": "Bengaluru East",
        "canonical_name": "Bengaluru East",
        "admin_type": "Taluka",
        "district_id": "dist_bengaluru_urban",
        "district_name": "Bengaluru Urban",
        "state_name": "Karnataka",
        "bbox": [77.6, 12.92, 77.8, 13.05],
        "polygon": [[77.6, 12.95], [77.7, 13.05], [77.8, 12.98], [77.72, 12.92], [77.6, 12.95]]
    },
    {
        "id": "subdist_chanakyapuri",
        "lgd_code": 881,
        "name": "Chanakyapuri",
        "canonical_name": "Chanakyapuri",
        "admin_type": "Subdivision",
        "district_id": "dist_new_delhi",
        "district_name": "New Delhi",
        "state_name": "Delhi",
        "bbox": [77.18, 28.58, 77.24, 28.65],
        "polygon": [[77.18, 28.6], [77.21, 28.65], [77.24, 28.62], [77.22, 28.58], [77.18, 28.6]]
    },
    {
        "id": "subdist_rajarhat",
        "lgd_code": 3101,
        "name": "Rajarhat",
        "canonical_name": "Rajarhat",
        "admin_type": "Block",
        "district_id": "dist_north_24_parganas",
        "district_name": "North 24 Parganas",
        "state_name": "West Bengal",
        "bbox": [88.4, 22.54, 88.54, 22.65],
        "polygon": [[88.4, 22.58], [88.48, 22.65], [88.54, 22.61], [88.49, 22.54], [88.4, 22.58]]
    }
]

# 4. Detailed Localities / Villages / Wards
LOCALITIES = [
    {
        "name": "Kharadi",
        "canonical_name": "Kharadi",
        "name_hi": "खराड़ी",
        "name_mr": "खराडी",
        "aliases": ["Kharadi Gaon", "Kharadi Bypass", "EON Free Zone Kharadi"],
        "subdistrict_id": "subdist_haveli",
        "subdistrict": "Haveli",
        "district_id": "dist_pune",
        "district": "Pune",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "411014",
        "coordinates": {"latitude": 18.5514, "longitude": 73.9405},
        "bbox": [73.92, 18.53, 73.96, 18.57],
        "polygon": [
            [73.92, 18.54], [73.93, 18.57], [73.96, 18.56], [73.95, 18.53], [73.92, 18.54]
        ]
    },
    {
        "name": "Viman Nagar",
        "canonical_name": "Viman Nagar",
        "name_hi": "विमान नगर",
        "name_mr": "विमान नगर",
        "aliases": ["Vimannagar", "Viman Nagar Pune"],
        "subdistrict_id": "subdist_haveli",
        "subdistrict": "Haveli",
        "district_id": "dist_pune",
        "district": "Pune",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "411014",
        "coordinates": {"latitude": 18.5679, "longitude": 73.9143},
        "bbox": [73.90, 18.55, 73.93, 18.58],
        "polygon": [
            [73.90, 18.56], [73.91, 18.58], [73.93, 18.57], [73.92, 18.55], [73.90, 18.56]
        ]
    },
    {
        "name": "Hinjewadi",
        "canonical_name": "Hinjewadi",
        "name_hi": "हिंजेवाड़ी",
        "name_mr": "हिंजवडी",
        "aliases": ["Hinjawadi", "Hinjawadi Phase 1", "Hinjewadi Phase 2", "Hinjewadi Phase 3"],
        "subdistrict_id": "subdist_mulshi",
        "subdistrict": "Mulshi",
        "district_id": "dist_pune",
        "district": "Pune",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "411057",
        "coordinates": {"latitude": 18.5913, "longitude": 73.7389},
        "bbox": [73.70, 18.57, 73.77, 18.62],
        "polygon": [
            [73.70, 18.58], [73.72, 18.62], [73.77, 18.60], [73.75, 18.57], [73.70, 18.58]
        ]
    },
    {
        "name": "Kothrud",
        "canonical_name": "Kothrud",
        "name_hi": "कोथरुड",
        "name_mr": "कोथरूड",
        "aliases": ["Kothrud Pune", "Paud Road"],
        "subdistrict_id": "subdist_pune_city",
        "subdistrict": "Pune City",
        "district_id": "dist_pune",
        "district": "Pune",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "411038",
        "coordinates": {"latitude": 18.5074, "longitude": 73.8077},
        "bbox": [73.78, 18.49, 73.83, 18.53],
        "polygon": [
            [73.78, 18.50], [73.80, 18.53], [73.83, 18.52], [73.82, 18.49], [73.78, 18.50]
        ]
    },
    {
        "name": "Baner",
        "canonical_name": "Baner",
        "name_hi": "बानेर",
        "name_mr": "बाणेर",
        "aliases": ["Baner Gaon", "Baner Road"],
        "subdistrict_id": "subdist_haveli",
        "subdistrict": "Haveli",
        "district_id": "dist_pune",
        "district": "Pune",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "411045",
        "coordinates": {"latitude": 18.5590, "longitude": 73.7868},
        "bbox": [73.76, 18.54, 73.81, 18.58],
        "polygon": [
            [73.76, 18.55], [73.78, 18.58], [73.81, 18.57], [73.79, 18.54], [73.76, 18.55]
        ]
    },
    {
        "name": "Bandra West",
        "canonical_name": "Bandra West",
        "name_hi": "बांद्रा पश्चिम",
        "name_mr": "वांद्रे पश्चिम",
        "aliases": ["Bandra", "Bandra W", "Bandstand", "Vandre"],
        "subdistrict_id": "subdist_andheri",
        "subdistrict": "Andheri",
        "district_id": "dist_mumbai_suburban",
        "district": "Mumbai Suburban",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "400050",
        "coordinates": {"latitude": 19.0596, "longitude": 72.8295},
        "bbox": [72.81, 19.04, 72.85, 19.08],
        "polygon": [
            [72.81, 19.05], [72.82, 19.08], [72.85, 19.07], [72.84, 19.04], [72.81, 19.05]
        ]
    },
    {
        "name": "Andheri East",
        "canonical_name": "Andheri East",
        "name_hi": "अंधेरी पूर्व",
        "name_mr": "अंधेरी पूर्व",
        "aliases": ["Andheri", "Andheri E", "MIDC Andheri", "Chakala"],
        "subdistrict_id": "subdist_andheri",
        "subdistrict": "Andheri",
        "district_id": "dist_mumbai_suburban",
        "district": "Mumbai Suburban",
        "state_id": 27,
        "state": "Maharashtra",
        "state_code": "MH",
        "pincode": "400069",
        "coordinates": {"latitude": 19.1136, "longitude": 72.8697},
        "bbox": [72.85, 19.09, 72.89, 19.14],
        "polygon": [
            [72.85, 19.10], [72.86, 19.14], [72.89, 19.13], [72.88, 19.09], [72.85, 19.10]
        ]
    },
    {
        "name": "Whitefield",
        "canonical_name": "Whitefield",
        "name_hi": "व्हाइटफील्ड",
        "name_mr": "व्हाईटफिल्ड",
        "aliases": ["Whitefield Bangalore", "ITPB", "EPIP Zone"],
        "subdistrict_id": "subdist_bengaluru_east",
        "subdistrict": "Bengaluru East",
        "district_id": "dist_bengaluru_urban",
        "district": "Bengaluru Urban",
        "state_id": 29,
        "state": "Karnataka",
        "state_code": "KA",
        "pincode": "560066",
        "coordinates": {"latitude": 12.9698, "longitude": 77.7499},
        "bbox": [77.72, 12.94, 77.78, 13.00],
        "polygon": [
            [77.72, 12.95], [77.73, 13.00], [77.78, 12.98], [77.76, 12.94], [77.72, 12.95]
        ]
    },
    {
        "name": "Indiranagar",
        "canonical_name": "Indiranagar",
        "name_hi": "इंदिरानगर",
        "name_mr": "इंदिरानगर",
        "aliases": ["Indira Nagar", "100 Feet Road Indiranagar"],
        "subdistrict_id": "subdist_bengaluru_east",
        "subdistrict": "Bengaluru East",
        "district_id": "dist_bengaluru_urban",
        "district": "Bengaluru Urban",
        "state_id": 29,
        "state": "Karnataka",
        "state_code": "KA",
        "pincode": "560038",
        "coordinates": {"latitude": 12.9784, "longitude": 77.6408},
        "bbox": [77.62, 12.96, 77.66, 13.00],
        "polygon": [
            [77.62, 12.97], [77.63, 13.00], [77.66, 12.99], [77.65, 12.96], [77.62, 12.97]
        ]
    },
    {
        "name": "Connaught Place",
        "canonical_name": "Connaught Place",
        "name_hi": "कनॉट प्लेस",
        "name_mr": "कनॉट प्लेस",
        "aliases": ["CP", "Rajiv Chowk", "Connaught Circus"],
        "subdistrict_id": "subdist_chanakyapuri",
        "subdistrict": "Chanakyapuri",
        "district_id": "dist_new_delhi",
        "district": "New Delhi",
        "state_id": 7,
        "state": "Delhi",
        "state_code": "DL",
        "pincode": "110001",
        "coordinates": {"latitude": 28.6315, "longitude": 77.2167},
        "bbox": [77.20, 28.62, 77.23, 28.64],
        "polygon": [
            [77.20, 28.63], [77.21, 28.64], [77.23, 28.635], [77.22, 28.62], [77.20, 28.63]
        ]
    },
    {
        "name": "Hauz Khas",
        "canonical_name": "Hauz Khas",
        "name_hi": "हौज़ खास",
        "name_mr": "हौज खास",
        "aliases": ["Hauz Khas Village", "HKV"],
        "subdistrict_id": "subdist_chanakyapuri",
        "subdistrict": "Chanakyapuri",
        "district_id": "dist_new_delhi",
        "district": "New Delhi",
        "state_id": 7,
        "state": "Delhi",
        "state_code": "DL",
        "pincode": "110016",
        "coordinates": {"latitude": 28.5494, "longitude": 77.2001},
        "bbox": [77.18, 28.53, 77.22, 28.57],
        "polygon": [
            [77.18, 28.54], [77.19, 28.57], [77.22, 28.56], [77.21, 28.53], [77.18, 28.54]
        ]
    },
    {
        "name": "Rajarhat",
        "canonical_name": "Rajarhat",
        "name_hi": "राजारहाट",
        "name_mr": "राजारहाट",
        "aliases": ["New Town Rajarhat", "Action Area 1"],
        "subdistrict_id": "subdist_rajarhat",
        "subdistrict": "Rajarhat",
        "district_id": "dist_north_24_parganas",
        "district": "North 24 Parganas",
        "state_id": 19,
        "state": "West Bengal",
        "state_code": "WB",
        "pincode": "700156",
        "coordinates": {"latitude": 22.5867, "longitude": 88.4756},
        "bbox": [88.44, 22.56, 88.51, 22.62],
        "polygon": [
            [88.45, 22.57], [88.47, 22.62], [88.51, 22.60], [88.49, 22.56], [88.45, 22.57]
        ]
    },
    {
        "name": "Rampur",
        "canonical_name": "Rampur",
        "name_hi": "रामपुर",
        "name_mr": "रामपूर",
        "aliases": ["Rampur City"],
        "subdistrict_id": None,
        "subdistrict": "Rampur",
        "district_id": "dist_rampur",
        "district": "Rampur",
        "state_id": 9,
        "state": "Uttar Pradesh",
        "state_code": "UP",
        "pincode": "244901",
        "coordinates": {"latitude": 28.8154, "longitude": 79.0257},
        "bbox": [78.98, 28.78, 79.07, 28.85],
        "polygon": [
            [78.98, 28.80], [79.01, 28.85], [79.07, 28.83], [79.05, 28.78], [78.98, 28.80]
        ]
    }
]

# 5. PIN Codes
PINCODES = [
    {
        "pincode": "411014",
        "circle": "Maharashtra",
        "region": "Pune",
        "division": "Pune City East",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Kharadi B.O", "Viman Nagar S.O", "Vadgaon Sheri S.O", "Dunkirk Lines S.O"],
        "district": "Pune",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 18.555, "longitude": 73.935}
    },
    {
        "pincode": "411057",
        "circle": "Maharashtra",
        "region": "Pune",
        "division": "Pune City West",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Infotech Park (Hinjawadi) S.O", "Hinjawadi B.O", "Wakand B.O"],
        "district": "Pune",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 18.591, "longitude": 73.738}
    },
    {
        "pincode": "411038",
        "circle": "Maharashtra",
        "region": "Pune",
        "division": "Pune City West",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Kothrud S.O", "Ex-Servicemen Colony S.O"],
        "district": "Pune",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 18.507, "longitude": 73.807}
    },
    {
        "pincode": "411045",
        "circle": "Maharashtra",
        "region": "Pune",
        "division": "Pune City West",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Baner Gaon S.O", "Baner Road S.O"],
        "district": "Pune",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 18.559, "longitude": 73.786}
    },
    {
        "pincode": "400050",
        "circle": "Maharashtra",
        "region": "Mumbai",
        "division": "Mumbai West",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Bandra West S.O", "Waterfield Road S.O"],
        "district": "Mumbai Suburban",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 19.059, "longitude": 72.829}
    },
    {
        "pincode": "400069",
        "circle": "Maharashtra",
        "region": "Mumbai",
        "division": "Mumbai West",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Andheri East S.O", "Chakala MIDC S.O"],
        "district": "Mumbai Suburban",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 19.113, "longitude": 72.869}
    },
    {
        "pincode": "560066",
        "circle": "Karnataka",
        "region": "Bengaluru HQ",
        "division": "Bangalore East",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Whitefield S.O", "EPIP S.O"],
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "state_code": "KA",
        "centroid": {"latitude": 12.969, "longitude": 77.749}
    },
    {
        "pincode": "560038",
        "circle": "Karnataka",
        "region": "Bengaluru HQ",
        "division": "Bangalore East",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Indiranagar S.O", "HAL II Stage S.O"],
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "state_code": "KA",
        "centroid": {"latitude": 12.978, "longitude": 77.640}
    },
    {
        "pincode": "110001",
        "circle": "Delhi",
        "region": "Delhi",
        "division": "New Delhi Central",
        "office_type": "H.O",
        "delivery_status": "Delivery",
        "post_offices": ["Connaught Place H.O", "Barakhamba Road S.O", "Janpath S.O"],
        "district": "New Delhi",
        "state": "Delhi",
        "state_code": "DL",
        "centroid": {"latitude": 28.631, "longitude": 77.216}
    },
    {
        "pincode": "110016",
        "circle": "Delhi",
        "region": "Delhi",
        "division": "New Delhi South",
        "office_type": "S.O",
        "delivery_status": "Delivery",
        "post_offices": ["Hauz Khas S.O", "IIT Delhi S.O"],
        "district": "New Delhi",
        "state": "Delhi",
        "state_code": "DL",
        "centroid": {"latitude": 28.549, "longitude": 77.200}
    },
    {
        "pincode": "416001",
        "circle": "Maharashtra",
        "region": "Goa-Kolhapur",
        "division": "Kolhapur",
        "office_type": "H.O",
        "delivery_status": "Delivery",
        "post_offices": ["Kolhapur H.O", "Shahupuri S.O", "Laxmipuri S.O"],
        "district": "Kolhapur",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 16.705, "longitude": 74.243}
    }
]

# 6. Points of Interest
POIS = [
    {
        "name": "EON IT Park",
        "category": "commercial",
        "subtype": "IT Park / Tech Zone",
        "coordinates": {"latitude": 18.5515, "longitude": 73.9515},
        "address": "Kharadi, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "World Trade Center Pune",
        "category": "commercial",
        "subtype": "Business Center",
        "coordinates": {"latitude": 18.5528, "longitude": 73.9534},
        "address": "Opposite EON Free Zone, Kharadi, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Manipal Hospital Kharadi",
        "category": "hospital",
        "subtype": "Multi-speciality Hospital",
        "coordinates": {"latitude": 18.5510, "longitude": 73.9370},
        "address": "Kharadi Bypass, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Chandan Nagar Police Station",
        "category": "police",
        "subtype": "Police Station",
        "coordinates": {"latitude": 18.5540, "longitude": 73.9310},
        "address": "Nagar Road, Chandan Nagar, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Kharadi Post Office",
        "category": "post_office",
        "subtype": "Postal Sub-Office",
        "coordinates": {"latitude": 18.5490, "longitude": 73.9420},
        "address": "Main Road, Kharadi, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Pune International Airport (PNQ)",
        "category": "transit",
        "subtype": "Airport",
        "coordinates": {"latitude": 18.5822, "longitude": 73.9197},
        "address": "New Airport Rd, Lohegaon, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Phoenix Marketcity Pune",
        "category": "landmark",
        "subtype": "Shopping Mall",
        "coordinates": {"latitude": 18.5620, "longitude": 73.9168},
        "address": "Viman Nagar, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Pune Railway Station",
        "category": "transit",
        "subtype": "Railway Junction",
        "coordinates": {"latitude": 18.5289, "longitude": 73.8744},
        "address": "Agarkar Nagar, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Rajiv Gandhi Infotech Park",
        "category": "commercial",
        "subtype": "IT Park",
        "coordinates": {"latitude": 18.5915, "longitude": 73.7380},
        "address": "Hinjewadi Phase 1, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "Hinjewadi Police Station",
        "category": "police",
        "subtype": "Police Station",
        "coordinates": {"latitude": 18.5930, "longitude": 73.7420},
        "address": "Hinjewadi, Pune",
        "district": "Pune",
        "state": "Maharashtra"
    },
    {
        "name": "International Tech Park Bangalore (ITPB)",
        "category": "commercial",
        "subtype": "Tech Park",
        "coordinates": {"latitude": 12.9860, "longitude": 77.7400},
        "address": "Whitefield, Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka"
    },
    {
        "name": "Manipal Hospital Whitefield",
        "category": "hospital",
        "subtype": "Hospital",
        "coordinates": {"latitude": 12.9750, "longitude": 77.7420},
        "address": "Whitefield Main Rd, Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka"
    },
    {
        "name": "Whitefield Railway Station",
        "category": "transit",
        "subtype": "Railway Station",
        "coordinates": {"latitude": 12.9960, "longitude": 77.7600},
        "address": "Kadugodi, Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka"
    },
    {
        "name": "Rajiv Chowk Metro Station",
        "category": "transit",
        "subtype": "Metro Interchange Station",
        "coordinates": {"latitude": 28.6328, "longitude": 77.2195},
        "address": "Connaught Place, New Delhi",
        "district": "New Delhi",
        "state": "Delhi"
    },
    {
        "name": "Dr. Ram Manohar Lohia Hospital",
        "category": "hospital",
        "subtype": "Government Hospital",
        "coordinates": {"latitude": 28.6240, "longitude": 77.2010},
        "address": "Baba Kharak Singh Marg, Connaught Place, New Delhi",
        "district": "New Delhi",
        "state": "Delhi"
    },
    {
        "name": "Connaught Place Police Station",
        "category": "police",
        "subtype": "Police Station",
        "coordinates": {"latitude": 28.6300, "longitude": 77.2150},
        "address": "Janpath, New Delhi",
        "district": "New Delhi",
        "state": "Delhi"
    }
]


def transform_all():
    """Transform and write all normalized reference datasets."""
    with open(PROCESSED_DIR / "states.json", "w", encoding="utf-8") as f:
        json.dump(ALL_36_STATES, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(ALL_36_STATES)} states to {PROCESSED_DIR / 'states.json'}")

    with open(PROCESSED_DIR / "districts.json", "w", encoding="utf-8") as f:
        json.dump(DISTRICTS, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(DISTRICTS)} districts to {PROCESSED_DIR / 'districts.json'}")

    with open(PROCESSED_DIR / "subdistricts.json", "w", encoding="utf-8") as f:
        json.dump(SUBDISTRICTS, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(SUBDISTRICTS)} subdistricts to {PROCESSED_DIR / 'subdistricts.json'}")

    with open(PROCESSED_DIR / "localities.json", "w", encoding="utf-8") as f:
        json.dump(LOCALITIES, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(LOCALITIES)} localities to {PROCESSED_DIR / 'localities.json'}")

    with open(PROCESSED_DIR / "pincodes.json", "w", encoding="utf-8") as f:
        json.dump(PINCODES, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(PINCODES)} pincodes to {PROCESSED_DIR / 'pincodes.json'}")

    with open(PROCESSED_DIR / "pois.json", "w", encoding="utf-8") as f:
        json.dump(POIS, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(POIS)} POIs to {PROCESSED_DIR / 'pois.json'}")


if __name__ == "__main__":
    transform_all()
