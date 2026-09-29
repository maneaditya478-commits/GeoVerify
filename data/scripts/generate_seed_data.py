"""Seed data generator for GeoVerify India.
Generates authoritative reference data for States, Districts, Localities, PIN codes, and POIs.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Indian States and Union Territories
STATES = [
    {
        "code": "MH",
        "name": "Maharashtra",
        "canonical_name": "Maharashtra",
        "aliases": ["Maharastra", "Maharashthra", "MH", "Maharashtra State"],
        "capital": "Mumbai",
        "bbox": [72.6, 15.6, 80.9, 22.0],
        "polygon": [
            [72.6, 18.9], [72.8, 20.0], [74.5, 21.9], [78.5, 21.8],
            [80.9, 19.5], [80.0, 18.0], [77.5, 15.6], [73.5, 15.8], [72.6, 18.9]
        ]
    },
    {
        "code": "KA",
        "name": "Karnataka",
        "canonical_name": "Karnataka",
        "aliases": ["Karnatak", "KA", "Karnataka State", "Mysore State"],
        "capital": "Bengaluru",
        "bbox": [74.0, 11.5, 78.5, 18.5],
        "polygon": [
            [74.0, 14.5], [74.5, 17.5], [77.5, 18.5], [78.5, 15.0],
            [77.8, 12.0], [76.0, 11.5], [74.5, 12.5], [74.0, 14.5]
        ]
    },
    {
        "code": "DL",
        "name": "Delhi",
        "canonical_name": "Delhi",
        "aliases": ["NCT of Delhi", "National Capital Territory of Delhi", "DL", "New Delhi"],
        "capital": "New Delhi",
        "bbox": [76.8, 28.4, 77.4, 28.9],
        "polygon": [
            [76.8, 28.5], [76.9, 28.8], [77.2, 28.9], [77.4, 28.7],
            [77.3, 28.4], [77.0, 28.4], [76.8, 28.5]
        ]
    },
    {
        "code": "TN",
        "name": "Tamil Nadu",
        "canonical_name": "Tamil Nadu",
        "aliases": ["Tamilnadu", "TN", "Madras State"],
        "capital": "Chennai",
        "bbox": [76.2, 8.0, 80.4, 13.5],
        "polygon": [
            [76.2, 10.5], [77.0, 12.5], [80.3, 13.5], [80.0, 10.0],
            [78.0, 8.0], [77.2, 8.3], [76.8, 9.5], [76.2, 10.5]
        ]
    },
    {
        "code": "TG",
        "name": "Telangana",
        "canonical_name": "Telangana",
        "aliases": ["Telengana", "TG", "TS"],
        "capital": "Hyderabad",
        "bbox": [77.2, 15.8, 81.8, 19.9],
        "polygon": [
            [77.2, 17.0], [78.0, 19.5], [80.5, 19.9], [81.8, 17.5],
            [79.8, 16.0], [78.2, 15.8], [77.2, 17.0]
        ]
    },
    {
        "code": "GJ",
        "name": "Gujarat",
        "canonical_name": "Gujarat",
        "aliases": ["Gujrat", "GJ"],
        "capital": "Gandhinagar",
        "bbox": [68.1, 20.1, 74.5, 24.7],
        "polygon": [
            [68.1, 23.5], [70.0, 24.7], [74.5, 24.0], [73.5, 20.1],
            [72.5, 20.8], [69.0, 22.0], [68.1, 23.5]
        ]
    },
    {
        "code": "WB",
        "name": "West Bengal",
        "canonical_name": "West Bengal",
        "aliases": ["Westbengal", "WB", "Paschim Banga"],
        "capital": "Kolkata",
        "bbox": [85.8, 21.5, 89.9, 27.2],
        "polygon": [
            [85.8, 23.5], [87.5, 27.2], [89.9, 26.5], [88.5, 22.0],
            [87.5, 21.5], [86.5, 22.5], [85.8, 23.5]
        ]
    },
    {
        "code": "UP",
        "name": "Uttar Pradesh",
        "canonical_name": "Uttar Pradesh",
        "aliases": ["UP", "Uttarpradesh"],
        "capital": "Lucknow",
        "bbox": [77.0, 23.8, 84.6, 30.4],
        "polygon": [
            [77.0, 28.5], [78.0, 30.4], [84.6, 27.5], [83.5, 24.0],
            [81.0, 23.8], [78.5, 25.5], [77.0, 28.5]
        ]
    },
    {
        "code": "RJ",
        "name": "Rajasthan",
        "canonical_name": "Rajasthan",
        "aliases": ["RJ", "Rajsthan"],
        "capital": "Jaipur",
        "bbox": [69.5, 23.0, 78.2, 30.2],
        "polygon": [
            [69.5, 27.0], [72.0, 30.2], [77.0, 29.0], [78.2, 26.5],
            [76.0, 23.5], [73.0, 23.0], [69.5, 27.0]
        ]
    },
    {
        "code": "KL",
        "name": "Kerala",
        "canonical_name": "Kerala",
        "aliases": ["KL", "Keralam"],
        "capital": "Thiruvananthapuram",
        "bbox": [74.8, 8.2, 77.5, 12.8],
        "polygon": [
            [74.8, 12.8], [76.0, 12.0], [77.5, 10.0], [77.3, 8.3],
            [76.8, 8.2], [75.8, 10.5], [74.8, 12.8]
        ]
    }
]

# 2. Key Districts
DISTRICTS = [
    {
        "id": "dist_pune",
        "name": "Pune",
        "canonical_name": "Pune",
        "aliases": ["Poona", "Pune District"],
        "state_code": "MH",
        "state_name": "Maharashtra",
        "bbox": [73.3, 17.9, 75.1, 19.4],
        "polygon": [
            [73.3, 18.5], [73.6, 19.3], [74.5, 19.4], [75.1, 18.6],
            [74.8, 17.9], [73.8, 18.0], [73.3, 18.5]
        ]
    },
    {
        "id": "dist_mumbai",
        "name": "Mumbai Suburban",
        "canonical_name": "Mumbai Suburban",
        "aliases": ["Mumbai", "Bombay", "Mumbai Suburban District"],
        "state_code": "MH",
        "state_name": "Maharashtra",
        "bbox": [72.7, 18.9, 73.0, 19.3],
        "polygon": [
            [72.7, 19.0], [72.8, 19.3], [73.0, 19.2], [72.9, 18.9], [72.7, 19.0]
        ]
    },
    {
        "id": "dist_kolhapur",
        "name": "Kolhapur",
        "canonical_name": "Kolhapur",
        "aliases": ["Kolhapur District"],
        "state_code": "MH",
        "state_name": "Maharashtra",
        "bbox": [73.7, 15.7, 74.7, 17.2],
        "polygon": [
            [73.7, 16.5], [74.0, 17.2], [74.7, 16.8], [74.5, 15.7], [73.7, 16.5]
        ]
    },
    {
        "id": "dist_nagpur",
        "name": "Nagpur",
        "canonical_name": "Nagpur",
        "aliases": ["Nagpur District"],
        "state_code": "MH",
        "state_name": "Maharashtra",
        "bbox": [78.5, 20.5, 79.6, 21.8],
        "polygon": [
            [78.5, 21.0], [78.8, 21.8], [79.6, 21.5], [79.4, 20.5], [78.5, 21.0]
        ]
    },
    {
        "id": "dist_bengaluru_urban",
        "name": "Bengaluru Urban",
        "canonical_name": "Bengaluru Urban",
        "aliases": ["Bangalore", "Bengaluru", "Bangalore Urban", "BLR"],
        "state_code": "KA",
        "state_name": "Karnataka",
        "bbox": [77.4, 12.7, 77.8, 13.2],
        "polygon": [
            [77.4, 12.9], [77.5, 13.2], [77.8, 13.1], [77.8, 12.8],
            [77.5, 12.7], [77.4, 12.9]
        ]
    },
    {
        "id": "dist_new_delhi",
        "name": "New Delhi",
        "canonical_name": "New Delhi",
        "aliases": ["Central Delhi", "Delhi Central", "NDLS"],
        "state_code": "DL",
        "state_name": "Delhi",
        "bbox": [77.1, 28.5, 77.3, 28.7],
        "polygon": [
            [77.1, 28.6], [77.2, 28.7], [77.3, 28.6], [77.2, 28.5], [77.1, 28.6]
        ]
    },
    {
        "id": "dist_chennai",
        "name": "Chennai",
        "canonical_name": "Chennai",
        "aliases": ["Madras", "Chennai District"],
        "state_code": "TN",
        "state_name": "Tamil Nadu",
        "bbox": [80.1, 12.9, 80.35, 13.2],
        "polygon": [
            [80.1, 13.0], [80.2, 13.2], [80.35, 13.1], [80.3, 12.9], [80.1, 13.0]
        ]
    },
    {
        "id": "dist_hyderabad",
        "name": "Hyderabad",
        "canonical_name": "Hyderabad",
        "aliases": ["Hyderabad District", "HYD"],
        "state_code": "TG",
        "state_name": "Telangana",
        "bbox": [78.3, 17.2, 78.6, 17.55],
        "polygon": [
            [78.3, 17.4], [78.4, 17.55], [78.6, 17.45], [78.5, 17.2], [78.3, 17.4]
        ]
    }
]

# 3. Localities
LOCALITIES = [
    {
        "name": "Kharadi",
        "aliases": ["Kharadi Gaon", "Kharadi Bypass", "EON Free Zone Kharadi"],
        "subdistrict": "Haveli",
        "district": "Pune",
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
        "aliases": ["Vimannagar", "Viman Nagar Pune"],
        "subdistrict": "Haveli",
        "district": "Pune",
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
        "aliases": ["Hinjawadi", "Hinjawadi Phase 1", "Hinjewadi Phase 2", "Hinjewadi Phase 3"],
        "subdistrict": "Mulshi",
        "district": "Pune",
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
        "aliases": ["Kothrud Pune", "Paud Road"],
        "subdistrict": "Pune City",
        "district": "Pune",
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
        "aliases": ["Baner Gaon", "Baner Road"],
        "subdistrict": "Haveli",
        "district": "Pune",
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
        "aliases": ["Bandra", "Bandra W", "Bandstand"],
        "subdistrict": "Andheri",
        "district": "Mumbai Suburban",
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
        "aliases": ["Andheri", "Andheri E", "MIDC Andheri", "Chakala"],
        "subdistrict": "Andheri",
        "district": "Mumbai Suburban",
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
        "aliases": ["Whitefield Bangalore", "ITPB", "EPIP Zone"],
        "subdistrict": "Bengaluru East",
        "district": "Bengaluru Urban",
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
        "aliases": ["Indira Nagar", "100 Feet Road Indiranagar"],
        "subdistrict": "Bengaluru East",
        "district": "Bengaluru Urban",
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
        "aliases": ["CP", "Rajiv Chowk", "Connaught Circus"],
        "subdistrict": "Chanakyapuri",
        "district": "New Delhi",
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
        "aliases": ["Hauz Khas Village", "HKV"],
        "subdistrict": "Hauz Khas",
        "district": "New Delhi",
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
        "aliases": ["New Town Rajarhat", "Action Area 1"],
        "subdistrict": "Rajarhat",
        "district": "North 24 Parganas",
        "state": "West Bengal",
        "state_code": "WB",
        "pincode": "700156",
        "coordinates": {"latitude": 22.5867, "longitude": 88.4756},
        "bbox": [77.44, 22.56, 88.51, 22.62],
        "polygon": [
            [88.45, 22.57], [88.47, 22.62], [88.51, 22.60], [88.49, 22.56], [88.45, 22.57]
        ]
    },
    # Ambiguous locality: Rampur exists in UP, Bihar, HP, etc.
    {
        "name": "Rampur",
        "aliases": ["Rampur City"],
        "subdistrict": "Rampur",
        "district": "Rampur",
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

# 4. PIN Codes
PINCODES = [
    {
        "pincode": "411014",
        "circle": "Maharashtra",
        "region": "Pune",
        "division": "Pune City East",
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
        "post_offices": ["Kolhapur H.O", "Shahupuri S.O", "Laxmipuri S.O"],
        "district": "Kolhapur",
        "state": "Maharashtra",
        "state_code": "MH",
        "centroid": {"latitude": 16.705, "longitude": 74.243}
    }
]

# 5. Points of Interest (POIs)
POIS = [
    # Pune Kharadi & nearby
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
    # Hinjewadi POIs
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
    # Bengaluru POIs
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
    # Delhi POIs
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


def generate_all():
    with open(DATA_DIR / "states.json", "w", encoding="utf-8") as f:
        json.dump(STATES, f, indent=2)
    print(f"Generated {len(STATES)} states in {DATA_DIR / 'states.json'}")

    with open(DATA_DIR / "districts.json", "w", encoding="utf-8") as f:
        json.dump(DISTRICTS, f, indent=2)
    print(f"Generated {len(DISTRICTS)} districts in {DATA_DIR / 'districts.json'}")

    with open(DATA_DIR / "localities.json", "w", encoding="utf-8") as f:
        json.dump(LOCALITIES, f, indent=2)
    print(f"Generated {len(LOCALITIES)} localities in {DATA_DIR / 'localities.json'}")

    with open(DATA_DIR / "pincodes.json", "w", encoding="utf-8") as f:
        json.dump(PINCODES, f, indent=2)
    print(f"Generated {len(PINCODES)} pincodes in {DATA_DIR / 'pincodes.json'}")

    with open(DATA_DIR / "pois.json", "w", encoding="utf-8") as f:
        json.dump(POIS, f, indent=2)
    print(f"Generated {len(POIS)} pois in {DATA_DIR / 'pois.json'}")


if __name__ == "__main__":
    generate_all()
