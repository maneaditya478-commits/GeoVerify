"""PIN code verification and postal consistency service for Indian addresses."""

import math
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.schemas.address import Coordinates
from app.schemas.verification import PinVerificationResult

# Indian Postal Circle mappings by first 2 digits of PIN
PIN_CIRCLE_MAP = {
    "11": ("Delhi", "DL"),
    "12": ("Haryana", "HR"),
    "13": ("Haryana", "HR"),
    "14": ("Punjab", "PB"),
    "15": ("Punjab", "PB"),
    "16": ("Chandigarh", "CH"),
    "17": ("Himachal Pradesh", "HP"),
    "18": ("Jammu and Kashmir", "JK"),
    "19": ("Jammu and Kashmir", "JK"),
    "20": ("Uttar Pradesh", "UP"),
    "21": ("Uttar Pradesh", "UP"),
    "22": ("Uttar Pradesh", "UP"),
    "23": ("Uttar Pradesh", "UP"),
    "24": ("Uttarakhand", "UK"),
    "25": ("Uttar Pradesh", "UP"),
    "26": ("Uttar Pradesh", "UP"),
    "27": ("Uttar Pradesh", "UP"),
    "28": ("Uttar Pradesh", "UP"),
    "30": ("Rajasthan", "RJ"),
    "31": ("Rajasthan", "RJ"),
    "32": ("Rajasthan", "RJ"),
    "33": ("Rajasthan", "RJ"),
    "34": ("Rajasthan", "RJ"),
    "36": ("Gujarat", "GJ"),
    "37": ("Gujarat", "GJ"),
    "38": ("Gujarat", "GJ"),
    "39": ("Gujarat", "GJ"),
    "40": ("Maharashtra", "MH"),
    "41": ("Maharashtra", "MH"),
    "42": ("Maharashtra", "MH"),
    "43": ("Maharashtra", "MH"),
    "44": ("Maharashtra", "MH"),
    "45": ("Madhya Pradesh", "MP"),
    "46": ("Madhya Pradesh", "MP"),
    "47": ("Madhya Pradesh", "MP"),
    "48": ("Madhya Pradesh", "MP"),
    "49": ("Chhattisgarh", "CG"),
    "50": ("Telangana", "TG"),
    "51": ("Andhra Pradesh", "AP"),
    "52": ("Andhra Pradesh", "AP"),
    "53": ("Andhra Pradesh", "AP"),
    "56": ("Karnataka", "KA"),
    "57": ("Karnataka", "KA"),
    "58": ("Karnataka", "KA"),
    "59": ("Karnataka", "KA"),
    "60": ("Tamil Nadu", "TN"),
    "61": ("Tamil Nadu", "TN"),
    "62": ("Tamil Nadu", "TN"),
    "63": ("Tamil Nadu", "TN"),
    "64": ("Tamil Nadu", "TN"),
    "67": ("Kerala", "KL"),
    "68": ("Kerala", "KL"),
    "69": ("Kerala", "KL"),
    "70": ("West Bengal", "WB"),
    "71": ("West Bengal", "WB"),
    "72": ("West Bengal", "WB"),
    "73": ("West Bengal", "WB"),
    "74": ("West Bengal", "WB"),
    "75": ("Odisha", "OD"),
    "76": ("Odisha", "OD"),
    "78": ("Assam", "AS"),
    "79": ("North East", "NE"),
    "80": ("Bihar", "BR"),
    "81": ("Bihar", "BR"),
    "82": ("Jharkhand", "JH"),
    "83": ("Jharkhand", "JH"),
    "84": ("Bihar", "BR"),
    "85": ("Bihar", "BR"),
}


def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculate the great circle distance between two points on Earth in kilometers."""
    R = 6371.0  # Earth's radius in km
    lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
    lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class PinValidator:
    """Validates Indian PIN codes against format, postal circle, directory, and coordinates."""

    def __init__(self):
        self.pincode_db: Dict[str, Dict[str, Any]] = {}
        data_file = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "pincodes.json"
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    self.pincode_db[r["pincode"]] = r

    def validate(
        self,
        pincode: Optional[str],
        state: Optional[str] = None,
        district: Optional[str] = None,
        coordinates: Optional[Coordinates] = None
    ) -> PinVerificationResult:
        if not pincode:
            return PinVerificationResult(
                pincode=None,
                is_valid_format=False,
                matched=False,
                evidence="No PIN code provided for verification."
            )

        cleaned_pin = pincode.strip()
        is_valid_format = bool(re.match(r"^[1-9][0-9]{5}$", cleaned_pin))

        if not is_valid_format:
            return PinVerificationResult(
                pincode=cleaned_pin,
                is_valid_format=False,
                matched=False,
                evidence=f"PIN code '{cleaned_pin}' does not match standard 6-digit Indian PIN format (e.g. 411014)."
            )

        # 1. Circle check by prefix
        prefix = cleaned_pin[:2]
        circle_state, circle_code = PIN_CIRCLE_MAP.get(prefix, (None, None))

        matched_district = None
        matched_state = circle_state
        matched_post_offices: List[str] = []
        centroid: Optional[Coordinates] = None
        distance_km: Optional[float] = None

        # 2. Lookup in database
        db_record = self.pincode_db.get(cleaned_pin)
        if db_record:
            matched_district = db_record.get("district")
            matched_state = db_record.get("state", circle_state)
            matched_post_offices = db_record.get("post_offices", [])
            if "centroid" in db_record and db_record["centroid"]:
                centroid = Coordinates(
                    latitude=db_record["centroid"]["latitude"],
                    longitude=db_record["centroid"]["longitude"]
                )

        # 3. Distance check if coordinates are present
        if coordinates and centroid:
            distance_km = haversine_distance(coordinates, centroid)

        # 4. Formulate evidence narrative
        evidence_parts = []
        is_match = True

        if is_valid_format:
            evidence_parts.append(f"Valid 6-digit postal format.")

        if circle_state:
            evidence_parts.append(f"Postal circle mapped to '{circle_state}'.")
            if state and state.lower() != circle_state.lower():
                evidence_parts.append(f"Warning: Supplied state '{state}' differs from PIN circle '{circle_state}'.")
                is_match = False

        if db_record:
            if matched_district:
                evidence_parts.append(f"Mapped to district '{matched_district}'.")
                if district and district.lower() not in matched_district.lower() and matched_district.lower() not in district.lower():
                    evidence_parts.append(f"Warning: Supplied district '{district}' differs from PIN district '{matched_district}'.")
                    is_match = False

            if matched_post_offices:
                evidence_parts.append(f"Associated post offices: {', '.join(matched_post_offices[:3])}.")

        if distance_km is not None:
            if distance_km <= 20.0:
                evidence_parts.append(f"Coordinates are within {distance_km} km of PIN centroid.")
            else:
                evidence_parts.append(f"Coordinates are {distance_km} km away from expected PIN centroid.")
                is_match = False

        return PinVerificationResult(
            pincode=cleaned_pin,
            is_valid_format=is_valid_format,
            matched=is_match,
            matched_post_offices=matched_post_offices,
            matched_district=matched_district,
            matched_state=matched_state,
            pin_centroid=centroid,
            distance_to_coordinates_km=distance_km,
            evidence=" ".join(evidence_parts)
        )


pin_validator = PinValidator()
