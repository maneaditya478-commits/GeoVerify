"""OCR Address Extraction & Geographic Handoff Benchmark Dataset (Phase 7.2).

Defines 260 standardized Indian document test cases across 8 distinct evaluation categories:
1. Clean Standard Documents (English) [40 cases]
2. Multilingual & Devanagari Documents (Hindi, Marathi, Mixed scripts, Devanagari numerals) [45 cases]
3. Scan Degradations (Skew, Low contrast, Blur, Resolution artifacts) [40 cases]
4. OCR Noise & Character Substitutions ('O'/'0', 'l'/'1', 'S'/'5', 'B'/'8', 'Z'/'2') [35 cases]
5. Complex Multi-Address Documents (Billing, Shipping, Office, Permanent) [30 cases]
6. Multi-Token Localities (Multi-word compounds across India) [30 cases]
7. Partial & Rural Addresses (Village/Taluka hierarchy, landmark-heavy, partial) [20 cases]
8. Negative & Adversarial Documents (Non-address receipts, PAN without address, logs) [20 cases]

Total: 260 cases
Split Configuration (60/20/20):
- Development (DEV): 156 cases (60%)
- Validation (VAL): 52 cases (20%)
- Frozen Held-Out (HELD_OUT): 52 cases (20%)
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Split(str, Enum):
    DEV = "DEV"
    VAL = "VAL"
    HELD_OUT = "HELD_OUT"


class GroundTruthAddress(BaseModel):
    raw_text: str
    premise: Optional[str] = None
    locality: Optional[str] = None
    subdistrict: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    expected_status: str = "VERIFIED"


class OCRTestCase(BaseModel):
    case_id: str
    category: str
    description: str
    document_text: str
    document_type: str = "image"
    language: str = "eng"
    script: str = "Latin"  # Latin, Devanagari, Mixed
    split: Split = Split.DEV
    degradation_type: Optional[str] = None  # skew, blur, noise, low_res, low_contrast, clean
    skew_angle: float = 0.0
    ground_truth: Optional[GroundTruthAddress] = None
    is_negative_case: bool = False
    is_rural_case: bool = False
    is_partial_case: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Base master locations for systematic test case synthesis
METRO_LOCATIONS = [
    ("Kharadi", "Pune", "Maharashtra", "411014", "Haveli"),
    ("Viman Nagar", "Pune", "Maharashtra", "411014", "Haveli"),
    ("Hinjewadi", "Pune", "Maharashtra", "411057", "Mulshi"),
    ("Kothrud", "Pune", "Maharashtra", "411038", "Haveli"),
    ("Baner", "Pune", "Maharashtra", "411045", "Haveli"),
    ("Hadapsar", "Pune", "Maharashtra", "411028", "Haveli"),
    ("Bandra West", "Mumbai", "Maharashtra", "400050", "Andheri"),
    ("Andheri East", "Mumbai", "Maharashtra", "400093", "Andheri"),
    ("Powai", "Mumbai", "Maharashtra", "400076", "Kurla"),
    ("Indiranagar", "Bengaluru", "Karnataka", "560038", "Bengaluru East"),
    ("Whitefield", "Bengaluru", "Karnataka", "560066", "Bengaluru East"),
    ("Koramangala", "Bengaluru", "Karnataka", "560034", "Bengaluru South"),
    ("Electronic City", "Bengaluru", "Karnataka", "560100", "Bengaluru South"),
    ("Connaught Place", "New Delhi", "Delhi", "110001", "Chanakyapuri"),
    ("Karol Bagh", "Central Delhi", "Delhi", "110005", "Karol Bagh"),
    ("Rohini", "North West Delhi", "Delhi", "110085", "Rohini"),
    ("Salt Lake", "Kolkata", "West Bengal", "700091", "Bidhannagar"),
    ("Rajarhat", "North 24 Parganas", "West Bengal", "700135", "Rajarhat"),
    ("DLF Cyber City", "Gurugram", "Haryana", "122002", "Gurugram"),
    ("Jubilee Hills", "Hyderabad", "Telangana", "500033", "Shaikpet"),
    ("Anna Nagar", "Chennai", "Tamil Nadu", "600040", "Aminjikarai"),
    ("Navrangpura", "Ahmedabad", "Gujarat", "380009", "Ahmedabad City"),
    ("Vaishali Nagar", "Jaipur", "Rajasthan", "302021", "Jaipur"),
    ("Gomti Nagar", "Lucknow", "Uttar Pradesh", "226010", "Lucknow"),
    ("Sector 62", "Gautam Buddha Nagar", "Uttar Pradesh", "201301", "Noida"),
    ("Panampilly Nagar", "Ernakulam", "Kerala", "682036", "Kanayannur"),
    ("Sector 35B", "Chandigarh", "Chandigarh", "160022", "Chandigarh"),
    ("Vijay Nagar", "Indore", "Madhya Pradesh", "452010", "Indore"),
    ("MP Nagar", "Bhopal", "Madhya Pradesh", "462011", "Huzur"),
    ("Sitabuldi", "Nagpur", "Maharashtra", "440012", "Nagpur Urban"),
]

INDIC_TRANSLATIONS = {
    "Kharadi": "खराडी", "Viman Nagar": "विमान नगर", "Hinjewadi": "हिंजवडी",
    "Kothrud": "कोथरूड", "Baner": "बाणेर", "Hadapsar": "हडपसर",
    "Pune": "पुणे", "Maharashtra": "महाराष्ट्र", "Mumbai": "मुंबई",
    "Bandra West": "बांद्रा पश्चिम", "Bengaluru": "बेंगलुरु",
    "Indiranagar": "इंदिरानगर", "Whitefield": "व्हाइटफील्ड", "Karnataka": "कर्नाटक",
    "New Delhi": "नई दिल्ली", "Delhi": "दिल्ली", "Connaught Place": "कनॉट प्लेस",
    "Kolkata": "कोलकाता", "West Bengal": "पश्चिम बंगाल", "Salt Lake": "सॉल्ट लेक",
    "Gurugram": "गुरुग्राम", "Haryana": "हरियाणा", "DLF Cyber City": "डीएलएफ साइबर सिटी",
    "Hyderabad": "हैदराबाद", "Telangana": "तेलंगाना", "Jubilee Hills": "जुबली हिल्स",
    "Ahmedabad": "अहमदाबाद", "Gujarat": "गुजरात", "Navrangpura": "नवरंगपुरा",
    "Jaipur": "जयपुर", "Rajasthan": "राजस्थान", "Vaishali Nagar": "वैशाली नगर",
    "Lucknow": "लखनऊ", "Uttar Pradesh": "उत्तर प्रदेश", "Gomti Nagar": "गोमती नगर",
    "Noida": "नोएडा", "Gautam Buddha Nagar": "गौतम बुद्ध नगर", "Sector 62": "सेक्टर 62",
    "Indore": "इंदौर", "Madhya Pradesh": "मध्य प्रदेश", "Vijay Nagar": "विजय नगर",
    "Bhopal": "भोपाल", "MP Nagar": "एमपी नगर", "Nagpur": "नागपुर", "Sitabuldi": "सीताबर्डी",
}

DEVA_NUMS = str.maketrans("0123456789", "०१२३४५६७८९")


def _generate_master_dataset() -> List[OCRTestCase]:
    cases: List[OCRTestCase] = []
    case_counter = 1

    def get_split(idx: int) -> Split:
        # Strict 60/20/20 modulo distribution
        mod = idx % 5
        if mod in (0, 1, 2):
            return Split.DEV
        elif mod == 3:
            return Split.VAL
        else:
            return Split.HELD_OUT

    # 1. Clean Standard Documents (English) [40 cases]
    for i in range(40):
        loc, dist, state, pin, subdist = METRO_LOCATIONS[i % len(METRO_LOCATIONS)]
        c_id = f"CLEAN_{i+1:02d}"
        prem = f"Flat {101 + i * 5}, Building {chr(65 + (i % 6))}, Phase {1 + (i % 3)}"
        raw_addr = f"{prem}, Near Central Garden, {loc}, {dist}, {state} {pin}"
        doc_text = (
            f"UTILITY & SERVICE BILLING AUTHORITY - RECORD #{1000+i}\n"
            f"Consumer ID: IND-{202600+i}\n"
            f"Billing Name: TEST CUSTOMER {i+1}\n"
            f"Billing Address: {raw_addr}\n"
            f"Due Date: 15/10/2026 | Amount: Rs. {1250 + i * 45}"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="clean_documents",
            description=f"Standard clean English utility bill for {loc}, {dist}",
            document_text=doc_text,
            language="eng",
            script="Latin",
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=raw_addr,
                premise=prem,
                locality=loc,
                subdistrict=subdist,
                district=dist,
                state=state,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 2. Multilingual & Devanagari Documents [45 cases]
    for i in range(45):
        loc_en, dist_en, state_en, pin, subdist_en = METRO_LOCATIONS[i % len(METRO_LOCATIONS)]
        loc_hi = INDIC_TRANSLATIONS.get(loc_en, loc_en)
        dist_hi = INDIC_TRANSLATIONS.get(dist_en, dist_en)
        state_hi = INDIC_TRANSLATIONS.get(state_en, state_en)
        pin_deva = pin.translate(DEVA_NUMS) if (i % 2 == 0) else pin
        c_id = f"DEVA_{i+1:02d}"
        
        lang = "mar" if "Maharashtra" in state_en else "hin"
        is_mixed = (i % 3 == 0)
        
        if lang == "mar":
            prefix_line = f"पत्ता: घर क्र. {i+1}, {loc_hi}, ता. {subdist_en}, जि. {dist_hi}, {state_hi} {pin_deva}"
            doc_text = (
                f"महाराष्ट्र शासन महसूल व नोंदणी विभाग\n"
                f"पावती क्रमांक: MH-REG-2026-{500+i}\n"
                f"{prefix_line}\n"
                f"दिनांक: ०१/१०/२०२६"
            )
        else:
            prefix_line = f"पता: मकान नं. {i+1}, {loc_hi}, जिला {dist_hi}, {state_hi} {pin_deva}"
            doc_text = (
                f"राज्य राजस्व एवं विकास प्राधिकरण\n"
                f"निवास प्रमाण पत्र विवरण #{300+i}\n"
                f"{prefix_line}\n"
                f"प्रमाणित दिनांक: १०/०९/२०२६"
            )

        cases.append(OCRTestCase(
            case_id=c_id,
            category="multilingual_devanagari",
            description=f"Indic Devanagari official record for {loc_hi} {dist_hi}",
            document_text=doc_text,
            language="mixed" if is_mixed else lang,
            script="Mixed" if is_mixed else "Devanagari",
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=prefix_line.replace("पत्ता: ", "").replace("पता: ", ""),
                locality=loc_en,
                subdistrict=subdist_en,
                district=dist_en,
                state=state_en,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 3. Scan Degradations (Skew, Blur, Noise, Low Contrast) [40 cases]
    deg_types = ["skew", "blur", "low_contrast", "noise", "low_res"]
    for i in range(40):
        loc, dist, state, pin, subdist = METRO_LOCATIONS[i % len(METRO_LOCATIONS)]
        deg = deg_types[i % len(deg_types)]
        skew_val = (5.0 + (i % 8)) * (-1 if i % 2 == 0 else 1) if deg == "skew" else 0.0
        c_id = f"DEG_{i+1:02d}"
        raw_addr = f"Plot {10+i}, Industrial Zone, {loc}, {dist}, {state} {pin}"
        doc_text = (
            f"SCANNED PROPERTY TAX CHALLAN\n"
            f"Assessment No: TAX-2026-{800+i}\n"
            f"Location: {raw_addr}\n"
            f"Total Assessment: Rs. {4500 + i * 100}"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="scan_degradations",
            description=f"Degraded scan ({deg}) of document from {loc}, {dist}",
            document_text=doc_text,
            language="eng",
            script="Latin",
            degradation_type=deg,
            skew_angle=skew_val,
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=raw_addr,
                locality=loc,
                subdistrict=subdist,
                district=dist,
                state=state,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 4. OCR Noise & Character Substitutions [35 cases]
    for i in range(35):
        loc, dist, state, pin, subdist = METRO_LOCATIONS[i % len(METRO_LOCATIONS)]
        c_id = f"NOISE_{i+1:02d}"
        
        # Inject realistic confusions into PIN / text
        noisy_pin = pin
        if i % 4 == 0:
            noisy_pin = pin.replace("0", "O")  # 0 -> O
        elif i % 4 == 1:
            noisy_pin = pin.replace("1", "I")  # 1 -> I
        elif i % 4 == 2 and pin.startswith("5"):
            noisy_pin = "S" + pin[1:]          # 5 -> S
        elif i % 4 == 3:
            noisy_pin = pin[:-1] + "B" if pin[-1] == "8" else pin.replace("0", "Q")

        noisy_admin = "D1st:" if i % 2 == 0 else "P1n code:"
        raw_addr = f"House {20+i}, Main Road, {loc}, {noisy_admin} {dist}, {state} {noisy_pin}"
        doc_text = (
            f"COMMERCIAL INVOICE - OCR ARTIFACT SAMPLE\n"
            f"Customer: CORP TECH INDIA\n"
            f"Premises: {raw_addr}\n"
            f"Total Due: 8900.00"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="ocr_noise_substitutions",
            description=f"OCR character substitution noise in {loc} ({noisy_pin})",
            document_text=doc_text,
            language="eng",
            script="Latin",
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=f"House {20+i}, Main Road, {loc}, {dist}, {state} {pin}",
                locality=loc,
                subdistrict=subdist,
                district=dist,
                state=state,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 5. Complex Multi-Address Documents [30 cases]
    for i in range(30):
        loc1, dist1, state1, pin1, subdist1 = METRO_LOCATIONS[i % len(METRO_LOCATIONS)]
        loc2, dist2, state2, pin2, subdist2 = METRO_LOCATIONS[(i + 5) % len(METRO_LOCATIONS)]
        c_id = f"MULTI_{i+1:02d}"
        
        doc_text = (
            f"B2B SUPPLY & TAX INVOICE - INV-{9000+i}\n\n"
            f"BILLING ADDRESS:\n"
            f"Flat {101+i}, Tower 1, {loc1}, {dist1}, {state1} {pin1}\n\n"
            f"SHIPPING / DELIVERY ADDRESS:\n"
            f"Warehouse {i+4}, Industrial Area, {loc2}, {dist2}, {state2} {pin2}\n\n"
            f"Items: Server Equipment | Qty: 4 | Amount: Rs. 1,45,000"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="complex_multi_address",
            description=f"Multi-address document (Billing: {loc1}, Shipping: {loc2})",
            document_text=doc_text,
            language="eng",
            script="Latin",
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=f"Flat {101+i}, Tower 1, {loc1}, {dist1}, {state1} {pin1}",
                locality=loc1,
                subdistrict=subdist1,
                district=dist1,
                state=state1,
                pincode=pin1,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 6. Multi-Token Localities [30 cases]
    multi_token_locs = [
        ("Viman Nagar", "Pune", "Maharashtra", "411014", "Haveli"),
        ("Bandra West", "Mumbai", "Maharashtra", "400050", "Andheri"),
        ("Connaught Place", "New Delhi", "Delhi", "110001", "Chanakyapuri"),
        ("Salt Lake Sector V", "Kolkata", "West Bengal", "700091", "Bidhannagar"),
        ("DLF Cyber City", "Gurugram", "Haryana", "122002", "Gurugram"),
        ("Koramangala 4th Block", "Bengaluru", "Karnataka", "560034", "Bengaluru South"),
        ("Electronic City Phase 1", "Bengaluru", "Karnataka", "560100", "Bengaluru South"),
        ("Jubilee Hills Road 36", "Hyderabad", "Telangana", "500033", "Shaikpet"),
        ("Anna Nagar 2nd Avenue", "Chennai", "Tamil Nadu", "600040", "Aminjikarai"),
        ("Hinjewadi Phase 1", "Pune", "Maharashtra", "411057", "Mulshi"),
    ]
    for i in range(30):
        loc, dist, state, pin, subdist = multi_token_locs[i % len(multi_token_locs)]
        c_id = f"MTL_{i+1:02d}"
        raw_addr = f"Unit {50+i}, Tech Park, {loc}, {dist}, {state} {pin}"
        doc_text = (
            f"FACILITIES LEASE AGREEMENT #{700+i}\n"
            f"Premises: {raw_addr}\n"
            f"Term: 36 Months | Security Deposit: Rs. 5,00,000"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="multi_token_localities",
            description=f"Multi-token compound locality: {loc}, {dist}",
            document_text=doc_text,
            language="eng",
            script="Latin",
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=raw_addr,
                locality=loc,
                subdistrict=subdist,
                district=dist,
                state=state,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 7. Partial & Rural Addresses [20 cases]
    rural_locations = [
        ("Khed Shivapur", "Pune", "Maharashtra", "412205", "Haveli"),
        ("Wagholi Gaon", "Pune", "Maharashtra", "412207", "Haveli"),
        ("Uruli Kanchan", "Pune", "Maharashtra", "412202", "Haveli"),
        ("Dehu Gaon", "Pune", "Maharashtra", "412109", "Haveli"),
        ("Chakan MIDC", "Pune", "Maharashtra", "410501", "Khed"),
    ]
    for i in range(20):
        r_loc, dist, state, pin, subdist = rural_locations[i % len(rural_locations)]
        c_id = f"RURAL_{i+1:02d}"
        is_partial = (i % 2 == 0)
        
        if is_partial:
            # Omit explicit district or PIN to test graceful incomplete handling
            raw_addr = f"Near Old Gram Panchayat, {r_loc}, {state} {pin}"
        else:
            raw_addr = f"Gat No {100+i}, Near Primary School, {r_loc}, Taluka {subdist}, District {dist}, {state} {pin}"

        doc_text = (
            f"GRAM PANCHAYAT TAX REGISTER #{400+i}\n"
            f"Property Assessment: {raw_addr}\n"
            f"Annual Tax: Rs. 450.00"
        )
        cases.append(OCRTestCase(
            case_id=c_id,
            category="partial_and_rural",
            description=f"Rural / partial address in {r_loc}, {dist}",
            document_text=doc_text,
            language="eng",
            script="Latin",
            is_rural_case=True,
            is_partial_case=is_partial,
            split=get_split(case_counter),
            ground_truth=GroundTruthAddress(
                raw_text=raw_addr,
                locality=r_loc,
                subdistrict=subdist,
                district=dist,
                state=state,
                pincode=pin,
                expected_status="VERIFIED",
            )
        ))
        case_counter += 1

    # 8. Negative & Adversarial Documents [20 cases]
    for i in range(20):
        c_id = f"NEG_{i+1:02d}"
        if i % 4 == 0:
            doc_text = (
                f"INCOME TAX DEPARTMENT - GOVT OF INDIA\n"
                f"Permanent Account Number: ABCDE{1234+i}F\n"
                f"Name: ADITYA MANE {i+1}\n"
                f"Date of Birth: 15/08/1995"
            )
            desc = "PAN card without physical address"
        elif i % 4 == 1:
            doc_text = (
                f"UPI TRANSACTION RECEIPT - TXN #{9812739182+i}\n"
                f"Paid to: QUICK COMMERCE MART\n"
                f"Amount: Rs. {350 + i * 20}\n"
                f"Status: COMPLETED"
            )
            desc = "Digital payment receipt without address"
        elif i % 4 == 2:
            doc_text = (
                f"# Python Script Log Dump\n"
                f"import sys, os\n"
                f"print('Execution completed with code 0 on worker node {i+1}')\n"
            )
            desc = "Source code snippet log"
        else:
            doc_text = (
                f"AIRLINE BOARDING PASS #{i+1}\n"
                f"Passenger: TRAVELER / MR\n"
                f"Flight: AI-842 | Seat: 14{chr(65+i%6)}\n"
                f"Boarding Time: 08:30 AM"
            )
            desc = "Boarding pass without residential address"

        cases.append(OCRTestCase(
            case_id=c_id,
            category="negative_adversarial",
            description=desc,
            document_text=doc_text,
            language="eng",
            script="Latin",
            is_negative_case=True,
            split=get_split(case_counter),
            ground_truth=None,
        ))
        case_counter += 1

    return cases


PHASE7_2_BENCHMARK_CASES = _generate_master_dataset()


def get_phase7_2_benchmark_cases(split: Optional[Split] = None) -> List[OCRTestCase]:
    """Retrieve Phase 7.2 benchmark test cases (260 cases), optionally filtered by split."""
    if split is None:
        return PHASE7_2_BENCHMARK_CASES
    return [c for c in PHASE7_2_BENCHMARK_CASES if c.split == split]
