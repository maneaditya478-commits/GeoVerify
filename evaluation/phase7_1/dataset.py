"""OCR Address Extraction & Geographic Calibration Benchmark Dataset (Phase 7.1).

Defines 105 standardized Indian document test cases across 7 distinct evaluation categories:
1. Clean Standard Documents (English)
2. Multilingual & Devanagari Documents (Hindi, Marathi, Mixed scripts, Devanagari numerals)
3. Scan Degradations (Skew, Low contrast, Blur, Resolution artifacts)
4. OCR Noise & Character Substitutions ('O'/'0', 'l'/'1', 'S'/'5', 'B'/'8')
5. Complex Multi-Address Documents (Billing, Shipping, Office, Permanent)
6. Multi-Token Localities (Multi-word localities requiring compound entity matching)
7. Negative & Adversarial Documents (Non-address receipts, PAN without address, log traces)

Split Configuration (60/20/20):
- Development (DEV): 63 cases (60%)
- Validation (VAL): 21 cases (20%)
- Frozen Held-Out (HELD_OUT): 21 cases (20%)
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
    degradation_type: Optional[str] = None  # skew, blur, noise, low_res, clean
    skew_angle: float = 0.0
    ground_truth: Optional[GroundTruthAddress] = None
    is_negative_case: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _build_dataset() -> List[OCRTestCase]:
    cases: List[OCRTestCase] = []

    # =========================================================================
    # CATEGORY 1: Clean Standard Documents (English) [15 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="CLEAN_01",
            category="clean_documents",
            description="Electricity bill with standard single-line address",
            document_text=(
                "MAHARASHTRA STATE ELECTRICITY DISTRIBUTION CO. LTD.\n"
                "CONSUMER BILLING RECEIPT\n"
                "Consumer No: 028491823941\n"
                "Name: ADITYA MANE\n"
                "Address: Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014\n"
                "Billing Date: 15/09/2026\n"
                "Amount: Rs. 2,450.00"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014",
                premise="Flat 402, Ganga Carnation",
                locality="Kharadi",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_02",
            category="clean_documents",
            description="Bank statement from Bengaluru Karnataka",
            document_text=(
                "STATE BANK OF INDIA\n"
                "STATEMENT OF ACCOUNT\n"
                "Account Number: 39182049182\n"
                "Customer Name: ROHAN VERMA\n"
                "Communication Address:\n"
                "#45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 560038\n"
                "IFSC Code: SBIN0001234"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="#45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 560038",
                locality="Indiranagar",
                district="Bengaluru",
                state="Karnataka",
                pincode="560038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_03",
            category="clean_documents",
            description="Delhi municipal tax receipt with Connaught Place address",
            document_text=(
                "NEW DELHI MUNICIPAL COUNCIL\n"
                "PROPERTY TAX ASSESSMENT ORDER\n"
                "Property ID: DL-NDMC-2026-99\n"
                "Owner: SANJAY GUPTA\n"
                "Address: Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001\n"
                "Financial Year: 2026-2027"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001",
                premise="Flat 12B",
                locality="Connaught Place",
                district="New Delhi",
                state="Delhi",
                pincode="110001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_04",
            category="clean_documents",
            description="Mumbai apartment maintenance receipt with Bandra West address",
            document_text=(
                "SEA VIEW COOPERATIVE HOUSING SOCIETY LTD.\n"
                "MAINTENANCE BILL - AUG 2026\n"
                "Member: PRIYA SHARMA\n"
                "Unit: Flat 501, 5th Floor, Perry Cross Road, Bandra West, Mumbai, Maharashtra 400050\n"
                "Due Date: 30-08-2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 501, 5th Floor, Perry Cross Road, Bandra West, Mumbai, Maharashtra 400050",
                premise="Flat 501, 5th Floor",
                locality="Bandra West",
                district="Mumbai",
                state="Maharashtra",
                pincode="400050",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_05",
            category="clean_documents",
            description="Kolkata telecom service invoice",
            document_text=(
                "AIRTEL FIBER INVOICE\n"
                "Account No: 9283719283\n"
                "Customer: DEBASHIS BANERJEE\n"
                "Installation Address:\n"
                "Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091\n"
                "Amount Payable: 1179.00"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091",
                locality="Salt Lake",
                district="Kolkata",
                state="West Bengal",
                pincode="700091",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_06",
            category="clean_documents",
            description="Pune broadband bill with Kothrud address",
            document_text=(
                "TATA PLAY FIBER INVOICE\n"
                "Subscriber ID: TP-98127391\n"
                "Name: SNEHA KULKARNI\n"
                "Service Address: Shop No 3, Karve Road, Near Mayur Colony, Kothrud, Pune, Maharashtra 411038\n"
                "Bill Period: Sep 2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Shop No 3, Karve Road, Near Mayur Colony, Kothrud, Pune, Maharashtra 411038",
                premise="Shop No 3",
                locality="Kothrud",
                district="Pune",
                state="Maharashtra",
                pincode="411038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_07",
            category="clean_documents",
            description="Gurugram commercial lease agreement header",
            document_text=(
                "DLF CYBER PARK LEASE AGREEMENT\n"
                "Tenant: ACME CONSULTING INDIA PVT LTD\n"
                "Registered Office:\n"
                "Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002\n"
                "Commencement Date: 01-10-2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_08",
            category="clean_documents",
            description="Hyderabad gas utility invoice",
            document_text=(
                "BHAGYANAGAR GAS LIMITED\n"
                "DOMESTIC PNG BILL\n"
                "Consumer: VENKAT REDDY\n"
                "Supply Address: Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033\n"
                "Net Amount Due: 840.00"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033",
                locality="Jubilee Hills",
                district="Hyderabad",
                state="Telangana",
                pincode="500033",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_09",
            category="clean_documents",
            description="Chennai water supply assessment",
            document_text=(
                "CHENNAI METRO WATER BOARD\n"
                "TAX CARD 2026\n"
                "Assessee: KARTHIK RAJAN\n"
                "Address: Old No 14, New No 28, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040\n"
                "Zone: V"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Old No 14, New No 28, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040",
                locality="Anna Nagar",
                district="Chennai",
                state="Tamil Nadu",
                pincode="600040",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_10",
            category="clean_documents",
            description="Noida tech company certificate of incorporation address",
            document_text=(
                "MINISTRY OF CORPORATE AFFAIRS\n"
                "CERTIFICATE OF INCORPORATION\n"
                "Company: FINVISTA DIGITAL TECHNOLOGIES LLP\n"
                "Registered Office Address: Unit 804, Express Trade Tower, Sector 132, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Unit 804, Express Trade Tower, Sector 132, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301",
                locality="Noida",
                district="Gautam Buddha Nagar",
                state="Uttar Pradesh",
                pincode="201301",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_11",
            category="clean_documents",
            description="Ahmedabad residential electricity bill",
            document_text=(
                "TORRENT POWER LIMITED\n"
                "ELECTRICITY BILL\n"
                "Customer: BHAVESH PATEL\n"
                "Billing Address: 4B, Shantiniketan Flats, CG Road, Navrangpura, Ahmedabad, Gujarat 380009\n"
                "Billing Cycle: SEP-2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="4B, Shantiniketan Flats, CG Road, Navrangpura, Ahmedabad, Gujarat 380009",
                locality="Navrangpura",
                district="Ahmedabad",
                state="Gujarat",
                pincode="380009",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_12",
            category="clean_documents",
            description="Jaipur bank passbook first page",
            document_text=(
                "BANK OF BARODA\n"
                "SAVINGS ACCOUNT PASSBOOK\n"
                "A/C Holder: MEENA MEENA\n"
                "Address: Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021\n"
                "Branch: Vaishali Nagar Jaipur"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_13",
            category="clean_documents",
            description="Kochi insurance policy schedule",
            document_text=(
                "HDFC ERGO GENERAL INSURANCE\n"
                "MOTOR POLICY SCHEDULE\n"
                "Insured: MATHEW VARGHESE\n"
                "Address: 12/482, Panampilly Nagar, Kochi, Ernakulam, Kerala 682036\n"
                "Policy Period: 2026-2027"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="12/482, Panampilly Nagar, Kochi, Ernakulam, Kerala 682036",
                locality="Panampilly Nagar",
                district="Ernakulam",
                state="Kerala",
                pincode="682036",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_14",
            category="clean_documents",
            description="Lucknow municipal house tax receipt",
            document_text=(
                "LUCKNOW NAGAR NIGAM\n"
                "PROPERTY TAX RECEIPT\n"
                "Owner: ANURAG TRIVEDI\n"
                "House No: 5/112, Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226010\n"
                "Year: 2026-27"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="5/112, Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226010",
                locality="Gomti Nagar",
                district="Lucknow",
                state="Uttar Pradesh",
                pincode="226010",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="CLEAN_15",
            category="clean_documents",
            description="Chandigarh resident identity verification card",
            document_text=(
                "CHANDIGARH ADMINISTRATION\n"
                "RESIDENT CARD\n"
                "Name: SIMRANJEET KAUR\n"
                "Address: House No 1420, Sector 35B, Chandigarh 160022\n"
                "Valid upto: 2030"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="House No 1420, Sector 35B, Chandigarh 160022",
                locality="Sector 35B",
                district="Chandigarh",
                state="Chandigarh",
                pincode="160022",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 2: Multilingual & Devanagari Documents [20 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="DEVA_01",
            category="multilingual_devanagari",
            description="Marathi property registration index document with Devanagari labels",
            document_text=(
                "महाराष्ट्र शासन नोंदणी व मुद्रांक विभाग\n"
                "सूची क्रमांक २\n"
                "दस्त क्रमांक: हवेली-४-१२९४/२०२६\n"
                "पत्ता: फ्लॅट क्रमांक ३०४, गंगा व्हिलेज, बाणेर रस्ता, बाणेर, जि. पुणे, महाराष्ट्र ४११०४५\n"
                "मुद्रांक शुल्क: रु. १,५०,०००"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="फ्लॅट क्रमांक ३०४, गंगा व्हिलेज, बाणेर रस्ता, बाणेर, जि. पुणे, महाराष्ट्र ४११०४५",
                premise="फ्लॅट क्रमांक ३०४, गंगा व्हिलेज",
                locality="Baner",
                district="Pune",
                state="Maharashtra",
                pincode="411045",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_02",
            category="multilingual_devanagari",
            description="Hindi domicile certificate issued by UP Government",
            document_text=(
                "उत्तर प्रदेश सरकार - राजस्व विभाग\n"
                "निवास प्रमाण पत्र\n"
                "प्रमाण पत्र क्रमांक: UP-DOM-2026-9481\n"
                "नाम: राजेश कुमार\n"
                "पता: मकान नं. ४५, कबीर नगर, दुर्गाकुंड, वाराणसी, उत्तर प्रदेश २२१००५\n"
                "जारी दिनांक: १२/०८/२०२६"
            ),
            split=Split.DEV,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="मकान नं. ४५, कबीर नगर, दुर्गाकुंड, वाराणसी, उत्तर प्रदेश २२१००५",
                locality="Varanasi",
                district="Varanasi",
                state="Uttar Pradesh",
                pincode="221005",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_03",
            category="multilingual_devanagari",
            description="Marathi electricity bill with Devanagari numerals in PIN code",
            document_text=(
                "महाराष्ट्र राज्य विद्युत वितरण कंपनी मर्यादित\n"
                "वीज देयक\n"
                "ग्राहक नाव: विलास तुकाराम पाटील\n"
                "पत्ता: प्लॉट नं १२, गणेश कॉलनी, कोथरूड, पुणे ४११०३८\n"
                "देयक महिना: ऑगस्ट २०२६"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="प्लॉट नं १२, गणेश कॉलनी, कोथरूड, पुणे ४११०३८",
                locality="Kothrud",
                district="Pune",
                state="Maharashtra",
                pincode="411038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_04",
            category="multilingual_devanagari",
            description="Hindi commercial tax assessment with formal administrative labels",
            document_text=(
                "मध्य प्रदेश वाणिज्यिक कर विभाग\n"
                "पंजीकरण विवरण\n"
                "संस्थान: मालवा ट्रेडर्स\n"
                "व्यावसायिक पता:\n"
                "दुकान नं १८, न्यू लोहा मंडी, विजय नगर, इंदौर, मध्य प्रदेश ४५२०१०\n"
                "जीएसटी नं: 23AABCT1330L1Z2"
            ),
            split=Split.VAL,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="दुकान नं १८, न्यू लोहा मंडी, विजय नगर, इंदौर, मध्य प्रदेश ४५२०१०",
                locality="Vijay Nagar",
                district="Indore",
                state="Madhya Pradesh",
                pincode="452010",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_05",
            category="multilingual_devanagari",
            description="Bilingual English-Marathi driving license address header",
            document_text=(
                "MOTOR DRIVING LICENCE / वाहन चालक परवाना\n"
                "MAHARASHTRA STATE / महाराष्ट्र शासन\n"
                "Name / नाव: AMOL SURESH JADHAV\n"
                "Address: घर क्र. १०१, सह्याद्री नगर, ता. हवेली, जि. पुणे, महाराष्ट्र 411028\n"
                "Licence No: MH-12-2026-00918"
            ),
            split=Split.DEV,
            language="mixed",
            script="Mixed",
            ground_truth=GroundTruthAddress(
                raw_text="घर क्र. १०१, सह्याद्री नगर, ता. हवेली, जि. पुणे, महाराष्ट्र 411028",
                subdistrict="Haveli",
                district="Pune",
                state="Maharashtra",
                pincode="411028",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_06",
            category="multilingual_devanagari",
            description="Marathi municipal tax receipt with Hadapsar address",
            document_text=(
                "पुणे महानगरपालिका मिळकत कर पावती\n"
                "मालमत्ता क्र: PMC-HAD-2026-44\n"
                "मालक: दीपक मोरे\n"
                "पत्ता: सर्व्हे नं १५, मगरपट्टा रोड, हडपसर, पुणे ४११०२८\n"
                "रक्कम: रु. ५,६००"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="सर्व्हे नं १५, मगरपट्टा रोड, हडपसर, पुणे ४११०२८",
                locality="Hadapsar",
                district="Pune",
                state="Maharashtra",
                pincode="411028",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_07",
            category="multilingual_devanagari",
            description="Hindi Delhi domicile certificate",
            document_text=(
                "राष्ट्रीय राजधानी क्षेत्र दिल्ली सरकार\n"
                "स्थानीय निवास प्रमाण पत्र\n"
                "नाम: अमित कुमार\n"
                "पता: मकान नं बी-१२, रोहिणी सेक्टर ७, उत्तर पश्चिम दिल्ली, दिल्ली ११००८५\n"
                "प्राधिकृत अधिकारी: एसडीएम रोहिणी"
            ),
            split=Split.HELD_OUT,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="मकान नं बी-१२, रोहिणी सेक्टर ७, उत्तर पश्चिम दिल्ली, दिल्ली ११००८५",
                locality="Rohini",
                district="North West Delhi",
                state="Delhi",
                pincode="110085",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_08",
            category="multilingual_devanagari",
            description="Marathi Kolhapur agricultural land 7/12 extract header",
            document_text=(
                "महाराष्ट्र शासन महसूल विभाग - ७/१२ उतारा\n"
                "गाव: राजारामपुरी, ता. करवीर, जि. कोल्हापूर, महाराष्ट्र ४१६००८\n"
                "खातेदार नाव: संभाजी पाटील"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="गाव: राजारामपुरी, ता. करवीर, जि. कोल्हापूर, महाराष्ट्र ४१६००८",
                locality="Rajarampuri",
                subdistrict="Karvir",
                district="Kolhapur",
                state="Maharashtra",
                pincode="416008",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_09",
            category="multilingual_devanagari",
            description="Hindi Rajasthan water utility bill with Vaishali Nagar Jaipur",
            document_text=(
                "जन स्वास्थ्य अभियांत्रिकी विभाग राजस्थान\n"
                "जल उपभोग देयक\n"
                "उपभोक्ता: सीताराम शर्मा\n"
                "पता: मकान नं २२, आम्रपाली मार्ग, वैशाली नगर, जयपुर, राजस्थान ३०२०२१"
            ),
            split=Split.VAL,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="मकान नं २२, आम्रपाली मार्ग, वैशाली नगर, जयपुर, राजस्थान ३०२०२१",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_10",
            category="multilingual_devanagari",
            description="Marathi Nashik LPG gas cylinder subscription voucher",
            document_text=(
                "भारत गॅस वितरक - नाशिक\n"
                "ग्राहक पावती क्र: BG-9921\n"
                "पत्ता: फ्लॅट ५, साई अपार्टमेन्ट, कॉलेज रोड, नाशिक, महाराष्ट्र ४२२००५\n"
                "दिनांक: ०१/०९/२०२६"
            ),
            split=Split.HELD_OUT,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="फ्लॅट ५, साई अपार्टमेन्ट, कॉलेज रोड, नाशिक, महाराष्ट्र ४२२००५",
                locality="Nashik",
                district="Nashik",
                state="Maharashtra",
                pincode="422005",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_11",
            category="multilingual_devanagari",
            description="Hindi Bihar ration card extract with Patna address",
            document_text=(
                "खाद्य एवं उपभोक्ता संरक्षण विभाग बिहार\n"
                "राशन कार्ड विवरणी\n"
                "मुखिया: रामेश्वर प्रसाद\n"
                "पता: वार्ड नं १२, कंकड़बाग, पटना, बिहार ८०००२०"
            ),
            split=Split.DEV,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="वार्ड नं १२, कंकड़बाग, पटना, बिहार ८०००२०",
                locality="Kankarbagh",
                district="Patna",
                state="Bihar",
                pincode="800020",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_12",
            category="multilingual_devanagari",
            description="Marathi Thane corporation birth certificate address section",
            document_text=(
                "ठाणे महानगरपालिका जन्म नोंदणी दाखला\n"
                "आई-वडिलांचा पत्ता:\n"
                "घर क्र ४, नौपाडा, ठाणे पश्चिम, जि. ठाणे, महाराष्ट्र ४००६०२"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="घर क्र ४, नौपाडा, ठाणे पश्चिम, जि. ठाणे, महाराष्ट्र ४००६०२",
                locality="Naupada",
                district="Thane",
                state="Maharashtra",
                pincode="400602",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_13",
            category="multilingual_devanagari",
            description="Hindi Bhopal municipal tax invoice",
            document_text=(
                "भोपाल नगर पालिक निगम\n"
                "संपत्ति कर निर्धारण आदेश\n"
                "करदाता: राकेश सक्सेना\n"
                "पता: प्लॉट ५६, एमपी नगर जोन १, भोपाल, मध्य प्रदेश ४६२०११"
            ),
            split=Split.DEV,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="प्लॉट ५६, एमपी नगर जोन १, भोपाल, मध्य प्रदेश ४६२०११",
                locality="MP Nagar",
                district="Bhopal",
                state="Madhya Pradesh",
                pincode="462011",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_14",
            category="multilingual_devanagari",
            description="Marathi Nagpur shop act license",
            document_text=(
                "नागपूर महानगरपालिका गुमास्ता परवाना\n"
                "दुकान नाव: विदर्भ ऑटोमोबाईल्स\n"
                "पत्ता: सीताबर्डी मेन रोड, नागपूर, महाराष्ट्र ४४००१२"
            ),
            split=Split.VAL,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="सीताबर्डी मेन रोड, नागपूर, महाराष्ट्र ४४००१२",
                locality="Sitabuldi",
                district="Nagpur",
                state="Maharashtra",
                pincode="440012",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_15",
            category="multilingual_devanagari",
            description="Hindi Raipur Chhattisgarh electricity bill",
            document_text=(
                "छत्तीसगढ़ राज्य विद्युत वितरण कंपनी\n"
                "माह: सितम्बर २०२६\n"
                "पता: मकान नं १०, पंडरी, रायपुर, छत्तीसगढ़ ४९२००४"
            ),
            split=Split.DEV,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="मकान नं १०, पंडरी, रायपुर, छत्तीसगढ़ ४९२००४",
                locality="Pandri",
                district="Raipur",
                state="Chhattisgarh",
                pincode="492004",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_16",
            category="multilingual_devanagari",
            description="Bilingual English-Hindi rent receipt Delhi",
            document_text=(
                "RENT RECEIPT / किराया रसीद\n"
                "Tenant Name: VIKAS JAIN\n"
                "Premises Address:\n"
                "Flat 204, Pocket A, Dilshad Garden, Shahdara, Delhi 110095\n"
                "Rent Amount: Rs. 14,000"
            ),
            split=Split.HELD_OUT,
            language="mixed",
            script="Mixed",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 204, Pocket A, Dilshad Garden, Shahdara, Delhi 110095",
                locality="Dilshad Garden",
                district="Shahdara",
                state="Delhi",
                pincode="110095",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_17",
            category="multilingual_devanagari",
            description="Marathi Solapur municipal receipt",
            document_text=(
                "सोलापूर महानगरपालिका कर पावती\n"
                "पत्ता: ७२, नवी पेठ, सोलापूर, महाराष्ट्र ४१३००१"
            ),
            split=Split.DEV,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="७२, नवी पेठ, सोलापूर, महाराष्ट्र ४१३००१",
                locality="Navi Peth",
                district="Solapur",
                state="Maharashtra",
                pincode="413001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_18",
            category="multilingual_devanagari",
            description="Hindi Agra property registration receipt",
            document_text=(
                "उत्तर प्रदेश स्टाम्प एवं निबंधन विभाग\n"
                "पंजीकृत पता: भवन नं १२, संजय प्लेस, आगरा, उत्तर प्रदेश २८२००२"
            ),
            split=Split.DEV,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="भवन नं १२, संजय प्लेस, आगरा, उत्तर प्रदेश २८२००२",
                locality="Sanjay Place",
                district="Agra",
                state="Uttar Pradesh",
                pincode="282002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_19",
            category="multilingual_devanagari",
            description="Marathi Aurangabad Sambhajinagar water bill",
            document_text=(
                "छत्रपती संभाजीनगर महानगरपालिका\n"
                "पाणीपट्टी देयक\n"
                "पत्ता: घर क्र १५, समर्थनगर, छत्रपती संभाजीनगर, महाराष्ट्र ४३१००१"
            ),
            split=Split.VAL,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="घर क्र १५, समर्थनगर, छत्रपती संभाजीनगर, महाराष्ट्र ४३१००१",
                locality="Samarth Nagar",
                district="Aurangabad",
                state="Maharashtra",
                pincode="431001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEVA_20",
            category="multilingual_devanagari",
            description="Hindi Ranchi Jharkhand electricity bill",
            document_text=(
                "झारखंड बिजली वितरण निगम लिमिटेड\n"
                "उपभोक्ता पता: मकान नं ८, मेन रोड, हिनू, रांची, झारखंड ८३४००२"
            ),
            split=Split.HELD_OUT,
            language="hin",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="मकान नं ८, मेन रोड, हिनू, रांची, झारखंड ८३४००२",
                locality="Hinoo",
                district="Ranchi",
                state="Jharkhand",
                pincode="834002",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 3: Scan Degradations (Skew, Blur, Noise, Low Contrast) [15 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="DEG_01",
            category="scan_degradations",
            description="Skewed document (+5 degrees) with Pune Kharadi address",
            document_text=(
                "MAHARASHTRA GAS COMPANY\n"
                "MONTHLY STATEMENT\n"
                "Address: Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014\n"
                "Customer: 9812739"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="skew",
            skew_angle=5.0,
            ground_truth=GroundTruthAddress(
                raw_text="Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014",
                locality="Kharadi",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_02",
            category="scan_degradations",
            description="Skewed document (-7 degrees) with Indiranagar Bengaluru address",
            document_text=(
                "BESCOM ELECTRICITY BILL\n"
                "Consumer No: 0981283\n"
                "Supply Address: #45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 560038\n"
                "Due Date: 20/09/2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="skew",
            skew_angle=-7.0,
            ground_truth=GroundTruthAddress(
                raw_text="#45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 560038",
                locality="Indiranagar",
                district="Bengaluru",
                state="Karnataka",
                pincode="560038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_03",
            category="scan_degradations",
            description="Blurry / out-of-focus phone camera photo of utility receipt",
            document_text=(
                "TATA POWER MUMBAI\n"
                "Premises: Flat 501, 5th Floor, Perry Cross Road, Bandra West, Mumbai, Maharashtra 400050\n"
                "Amount: 3,200"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            degradation_type="blur",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 501, 5th Floor, Perry Cross Road, Bandra West, Mumbai, Maharashtra 400050",
                locality="Bandra West",
                district="Mumbai",
                state="Maharashtra",
                pincode="400050",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_04",
            category="scan_degradations",
            description="Low-contrast thermal receipt from Delhi municipal counter",
            document_text=(
                "NDMC RECEIPT\n"
                "Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001\n"
                "PAID: 1500"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="low_contrast",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001",
                locality="Connaught Place",
                district="New Delhi",
                state="Delhi",
                pincode="110001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_05",
            category="scan_degradations",
            description="Noisy scanned document with Salt Lake Kolkata address",
            document_text=(
                "WBSEDCL BILL\n"
                "Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091\n"
                "Tariff: L&MV"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            degradation_type="noise",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091",
                locality="Salt Lake",
                district="Kolkata",
                state="West Bengal",
                pincode="700091",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_06",
            category="scan_degradations",
            description="Heavy skew (+12 degrees) with Pune Hinjewadi IT park address",
            document_text=(
                "INFOSYS PHASE 1 PUNE\n"
                "Campus Gate Pass\n"
                "Location: Plot No 44, Hinjewadi Phase 1, Mulshi, Pune, Maharashtra 411057\n"
                "Validity: 2026"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="skew",
            skew_angle=12.0,
            ground_truth=GroundTruthAddress(
                raw_text="Plot No 44, Hinjewadi Phase 1, Mulshi, Pune, Maharashtra 411057",
                locality="Hinjewadi",
                subdistrict="Mulshi",
                district="Pune",
                state="Maharashtra",
                pincode="411057",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_07",
            category="scan_degradations",
            description="Low resolution scan of Chennai telecom bill",
            document_text=(
                "BSNL CHENNAI TELEPHONES\n"
                "Address: Old No 14, New No 28, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040\n"
                "Due: 599.00"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="low_res",
            ground_truth=GroundTruthAddress(
                raw_text="Old No 14, New No 28, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040",
                locality="Anna Nagar",
                district="Chennai",
                state="Tamil Nadu",
                pincode="600040",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_08",
            category="scan_degradations",
            description="Skewed Marathi property tax document",
            document_text=(
                "पुणे महानगरपालिका\n"
                "पत्ता: सर्व्हे नं १५, मगरपट्टा रोड, हडपसर, पुणे ४११०२८\n"
                "कर आकारणी"
            ),
            split=Split.VAL,
            language="mar",
            script="Devanagari",
            degradation_type="skew",
            skew_angle=4.5,
            ground_truth=GroundTruthAddress(
                raw_text="सर्व्हे नं १५, मगरपट्टा रोड, हडपसर, पुणे ४११०२८",
                locality="Hadapsar",
                district="Pune",
                state="Maharashtra",
                pincode="411028",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_09",
            category="scan_degradations",
            description="Blurry gas bill with Koramangala Bengaluru address",
            document_text=(
                "GAIL GAS LIMITED\n"
                "Connection Address: 80 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka 560034"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="blur",
            ground_truth=GroundTruthAddress(
                raw_text="80 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka 560034",
                locality="Koramangala",
                district="Bengaluru",
                state="Karnataka",
                pincode="560034",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_10",
            category="scan_degradations",
            description="Low-contrast Aadhaar back side scan fragment",
            document_text=(
                "Address:\n"
                "S/O Ramesh Kumar, House 12, Gali No 3, Karol Bagh, Central Delhi, Delhi 110005"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            degradation_type="low_contrast",
            ground_truth=GroundTruthAddress(
                raw_text="House 12, Gali No 3, Karol Bagh, Central Delhi, Delhi 110005",
                locality="Karol Bagh",
                district="Central Delhi",
                state="Delhi",
                pincode="110005",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_11",
            category="scan_degradations",
            description="Skewed Gurgaon invoice (+8 degrees)",
            document_text=(
                "CYBER GREEN INVOICE\n"
                "Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="skew",
            skew_angle=8.0,
            ground_truth=GroundTruthAddress(
                raw_text="Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_12",
            category="scan_degradations",
            description="Noisy dot matrix bank statement printout",
            document_text=(
                "PUNJAB NATIONAL BANK\n"
                "CUSTOMER ADDRESS: 4B, SHANTINIKETAN FLATS, CG ROAD, NAVRANGPURA, AHMEDABAD, GUJARAT 380009"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="noise",
            ground_truth=GroundTruthAddress(
                raw_text="4B, SHANTINIKETAN FLATS, CG ROAD, NAVRANGPURA, AHMEDABAD, GUJARAT 380009",
                locality="Navrangpura",
                district="Ahmedabad",
                state="Gujarat",
                pincode="380009",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_13",
            category="scan_degradations",
            description="Blurry Hyderabad courier consignment note",
            document_text=(
                "BLUE DART AIRBILL\n"
                "DELIVERY TO: PLOT 108, JUBILEE HILLS, ROAD NO 36, HYDERABAD, TELANGANA 500033"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            degradation_type="blur",
            ground_truth=GroundTruthAddress(
                raw_text="PLOT 108, JUBILEE HILLS, ROAD NO 36, HYDERABAD, TELANGANA 500033",
                locality="Jubilee Hills",
                district="Hyderabad",
                state="Telangana",
                pincode="500033",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_14",
            category="scan_degradations",
            description="Negative skew (-6 degrees) Jaipur tax assessment",
            document_text=(
                "JAIPUR DEVELOPMENT AUTHORITY\n"
                "PLOT 21, QUEENS ROAD, VAISHALI NAGAR, JAIPUR, RAJASTHAN 302021"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            degradation_type="skew",
            skew_angle=-6.0,
            ground_truth=GroundTruthAddress(
                raw_text="PLOT 21, QUEENS ROAD, VAISHALI NAGAR, JAIPUR, RAJASTHAN 302021",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="DEG_15",
            category="scan_degradations",
            description="Low resolution Noida trade certificate",
            document_text=(
                "NOIDA AUTHORITY ORDER\n"
                "UNIT 804, EXPRESS TRADE TOWER, SECTOR 132, NOIDA, GAUTAM BUDDHA NAGAR, UTTAR PRADESH 201301"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            degradation_type="low_res",
            ground_truth=GroundTruthAddress(
                raw_text="UNIT 804, EXPRESS TRADE TOWER, SECTOR 132, NOIDA, GAUTAM BUDDHA NAGAR, UTTAR PRADESH 201301",
                locality="Noida",
                district="Gautam Buddha Nagar",
                state="Uttar Pradesh",
                pincode="201301",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 4: OCR Noise & Character Substitutions [15 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="NOISE_01",
            category="ocr_noise_substitutions",
            description="PIN code letter 'O' substituted for digit '0' (411O14)",
            document_text=(
                "ELECTRICITY SUPPLY RECEIPT\n"
                "Consumer Name: ADITYA MANE\n"
                "Address: Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411O14"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014",
                locality="Kharadi",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_02",
            category="ocr_noise_substitutions",
            description="PIN code letter 'l' substituted for digit '1' and 'O' for '0' (56OO38)",
            document_text=(
                "BANK STATEMENT\n"
                "Communication Address:\n"
                "#45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 56OO38"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="#45, 2nd Cross, 7th Main Road, Indiranagar, Bengaluru, Karnataka 560038",
                locality="Indiranagar",
                district="Bengaluru",
                state="Karnataka",
                pincode="560038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_03",
            category="ocr_noise_substitutions",
            description="OCR letter 'S' substituted for leading '5' (S60066)",
            document_text=(
                "BROADBAND INVOICE\n"
                "Installation:\n"
                "Flat 204, Palm Meadows, Varthur Road, Whitefield, Bengaluru, Karnataka S60066"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 204, Palm Meadows, Varthur Road, Whitefield, Bengaluru, Karnataka 560066",
                locality="Whitefield",
                district="Bengaluru",
                state="Karnataka",
                pincode="560066",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_04",
            category="ocr_noise_substitutions",
            description="OCR administrative keyword errors ('D1st:', 'Ta1uka:', 'P1n:')",
            document_text=(
                "RESIDENCE CERTIFICATE\n"
                "Name: PRADEEP KULKARNI\n"
                "Address: House 4, MG Road, Loc: Kothrud, Ta1uka: Haveli, D1st: Pune, Maharashtra, P1n: 411038"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="House 4, MG Road, Kothrud, Haveli, Pune, Maharashtra 411038",
                locality="Kothrud",
                subdistrict="Haveli",
                district="Pune",
                state="Maharashtra",
                pincode="411038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_05",
            category="ocr_noise_substitutions",
            description="Letter 'B' substituted for digit '8' in PIN (40005B -> 400058)",
            document_text=(
                "SOCIETY BILL\n"
                "Unit: Flat 501, SV Road, Andheri West, Mumbai, Maharashtra 40005B"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 501, SV Road, Andheri West, Mumbai, Maharashtra 400058",
                locality="Andheri West",
                district="Mumbai",
                state="Maharashtra",
                pincode="400058",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_06",
            category="ocr_noise_substitutions",
            description="Delhi PIN code substitution 11OOO1 (O -> 0)",
            document_text=(
                "TAX INVOICE\n"
                "Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 11OOO1"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 12B, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001",
                locality="Connaught Place",
                district="New Delhi",
                state="Delhi",
                pincode="110001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_07",
            category="ocr_noise_substitutions",
            description="State name character corruption 'M@h@r@shtr@'",
            document_text=(
                "UTILITY BILL\n"
                "Address: Flat 10, Ganga Orchard, Kharadi, Pune, M@h@r@shtr@ 411014"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 10, Ganga Orchard, Kharadi, Pune, Maharashtra 411014",
                locality="Kharadi",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_08",
            category="ocr_noise_substitutions",
            description="Kolkata Sector V Salt Lake with OCR digit substitution 7OOOO1",
            document_text=(
                "COMMERCIAL LEASE\n"
                "Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 7OOOO1"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091",
                locality="Salt Lake",
                district="Kolkata",
                state="West Bengal",
                pincode="700091",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_09",
            category="ocr_noise_substitutions",
            description="Chennai PIN substitution 6OOOO4",
            document_text=(
                "WATER BILL\n"
                "2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 6OOOO4"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040",
                locality="Anna Nagar",
                district="Chennai",
                state="Tamil Nadu",
                pincode="600040",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_10",
            category="ocr_noise_substitutions",
            description="Hyderabad PIN digit confusion 5OOOO3",
            document_text=(
                "GAS RECEIPT\n"
                "Road No 36, Jubilee Hills, Hyderabad, Telangana 5OOOO3"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Road No 36, Jubilee Hills, Hyderabad, Telangana 500033",
                locality="Jubilee Hills",
                district="Hyderabad",
                state="Telangana",
                pincode="500033",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_11",
            category="ocr_noise_substitutions",
            description="Gurugram PIN digit substitution 122OO2",
            document_text=(
                "OFFICE LEASE\n"
                "DLF Cyber City, Sector 25, Gurugram, Haryana 122OO2"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="DLF Cyber City, Sector 25, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_12",
            category="ocr_noise_substitutions",
            description="Ahmedabad PIN substitution 38OOO9",
            document_text=(
                "BANK VOUCHER\n"
                "CG Road, Navrangpura, Ahmedabad, Gujarat 38OOO9"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="CG Road, Navrangpura, Ahmedabad, Gujarat 380009",
                locality="Navrangpura",
                district="Ahmedabad",
                state="Gujarat",
                pincode="380009",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_13",
            category="ocr_noise_substitutions",
            description="Jaipur PIN substitution 3O2O21",
            document_text=(
                "PASSBOOK ENTRY\n"
                "Queens Road, Vaishali Nagar, Jaipur, Rajasthan 3O2O21"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_14",
            category="ocr_noise_substitutions",
            description="Lucknow PIN substitution 226O1O",
            document_text=(
                "MUNICIPAL RECEIPT\n"
                "Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226O1O"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226010",
                locality="Gomti Nagar",
                district="Lucknow",
                state="Uttar Pradesh",
                pincode="226010",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="NOISE_15",
            category="ocr_noise_substitutions",
            description="Chandigarh PIN substitution 16OO22",
            document_text=(
                "IDENTITY CARD\n"
                "Sector 35B, Chandigarh 16OO22"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Sector 35B, Chandigarh 160022",
                locality="Sector 35B",
                district="Chandigarh",
                state="Chandigarh",
                pincode="160022",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 5: Complex Multi-Address Documents [15 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="MULTI_01",
            category="complex_multi_address",
            description="E-commerce invoice with Billing and Shipping addresses",
            document_text=(
                "AMAZON SELLER SERVICES PVT LTD - TAX INVOICE\n"
                "Invoice Number: IN-2026-98124\n\n"
                "BILLING ADDRESS:\n"
                "Pooja Deshmukh\n"
                "Flat 101, A-Wing, Rohan Mithila, Viman Nagar, Pune, Maharashtra 411014\n\n"
                "SHIPPING ADDRESS:\n"
                "Pooja Deshmukh (Workplace)\n"
                "Tech Mahindra, Gate 2, Rajiv Gandhi Infotech Park, Hinjewadi, Pune, Maharashtra 411057\n\n"
                "Item: Wireless Keyboard | Qty: 1 | Total: Rs. 1,899"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 101, A-Wing, Rohan Mithila, Viman Nagar, Pune, Maharashtra 411014",
                locality="Viman Nagar",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_02",
            category="complex_multi_address",
            description="Corporate invoice with Registered Office and Branch address",
            document_text=(
                "INFOSYS LIMITED - OFFICIAL CORRESPONDENCE\n\n"
                "REGISTERED OFFICE:\n"
                "Electronics City, Hosur Road, Bengaluru, Karnataka 560100\n\n"
                "BRANCH / DEVELOPMENT CENTRE:\n"
                "Plot No 24, Hinjewadi Phase 2, Pune, Maharashtra 411057\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Electronics City, Hosur Road, Bengaluru, Karnataka 560100",
                locality="Electronic City",
                district="Bengaluru",
                state="Karnataka",
                pincode="560100",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_03",
            category="complex_multi_address",
            description="Bank KYC form with Permanent and Correspondence address",
            document_text=(
                "HDFC BANK - CUSTOMER PROFILE FORM\n\n"
                "1. PERMANENT ADDRESS:\n"
                "H.No 12, Subhash Nagar, Karve Road, Kothrud, Pune, Maharashtra 411038\n\n"
                "2. CURRENT / CORRESPONDENCE ADDRESS:\n"
                "Flat 602, Prestige Shantiniketan, ITPL Main Road, Whitefield, Bengaluru, Karnataka 560066\n"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="H.No 12, Subhash Nagar, Karve Road, Kothrud, Pune, Maharashtra 411038",
                locality="Kothrud",
                district="Pune",
                state="Maharashtra",
                pincode="411038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_04",
            category="complex_multi_address",
            description="Flipkart invoice with Seller and Buyer address",
            document_text=(
                "FLIPKART INTERNET PRIVATE LIMITED\n\n"
                "SOLD BY: RETAILNET PVT LTD\n"
                "Warehouse 4, Bhiwandi, Thane, Maharashtra 421302\n\n"
                "DELIVER TO: VIJAY PATIL\n"
                "Flat 12, Shanti Heights, Baner Road, Baner, Pune, Maharashtra 411045\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 12, Shanti Heights, Baner Road, Baner, Pune, Maharashtra 411045",
                locality="Baner",
                district="Pune",
                state="Maharashtra",
                pincode="411045",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_05",
            category="complex_multi_address",
            description="Lease agreement with Lessor and Lessee addresses",
            document_text=(
                "RESIDENTIAL LEASE DEED\n\n"
                "LESSOR ADDRESS:\n"
                "Villa 14, Palm Grove, Bandra West, Mumbai, Maharashtra 400050\n\n"
                "DEMISED PROPERTY ADDRESS:\n"
                "Flat 302, Cyber Heights, Sector 62, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301\n"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Villa 14, Palm Grove, Bandra West, Mumbai, Maharashtra 400050",
                locality="Bandra West",
                district="Mumbai",
                state="Maharashtra",
                pincode="400050",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_06",
            category="complex_multi_address",
            description="Logistics consignment with Origin and Destination addresses",
            document_text=(
                "DTDC CONSIGNMENT MANIFEST\n\n"
                "ORIGIN:\n"
                "Shop 12, Connaught Place, New Delhi, Delhi 110001\n\n"
                "DESTINATION:\n"
                "Plot 88, Sector V, Salt Lake, Kolkata, West Bengal 700091\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Shop 12, Connaught Place, New Delhi, Delhi 110001",
                locality="Connaught Place",
                district="New Delhi",
                state="Delhi",
                pincode="110001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_07",
            category="complex_multi_address",
            description="Insurance claim form with Hospital and Insured address",
            document_text=(
                "STAR HEALTH INSURANCE CLAIM\n\n"
                "INSURED RESIDENCE:\n"
                "House 24, 7th Main, Indiranagar, Bengaluru, Karnataka 560038\n\n"
                "HOSPITAL ADDRESS:\n"
                "Manipal Hospital, HAL Airport Road, Bengaluru, Karnataka 560017\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="House 24, 7th Main, Indiranagar, Bengaluru, Karnataka 560038",
                locality="Indiranagar",
                district="Bengaluru",
                state="Karnataka",
                pincode="560038",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_08",
            category="complex_multi_address",
            description="Bilingual Marathi electricity receipt with Head Office and Substation address",
            document_text=(
                "महावितरण उपविभाग\n\n"
                "मुख्य कार्यालय पत्ता:\n"
                "प्रकाशगड, बांद्रा पूर्व, मुंबई, महाराष्ट्र ४०००५१\n\n"
                "ग्राहक वीज वापर पत्ता:\n"
                "फ्लॅट ४, मगरपट्टा सिटी, हडपसर, पुणे, महाराष्ट्र ४११०२८\n"
            ),
            split=Split.VAL,
            language="mar",
            script="Devanagari",
            ground_truth=GroundTruthAddress(
                raw_text="फ्लॅट ४, मगरपट्टा सिटी, हडपसर, पुणे, महाराष्ट्र ४११०२८",
                locality="Hadapsar",
                district="Pune",
                state="Maharashtra",
                pincode="411028",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_09",
            category="complex_multi_address",
            description="Vehicle service job card with Customer and Workshop address",
            document_text=(
                "MARUTI SUZUKI SERVICE CENTER\n\n"
                "WORKSHOP:\n"
                "Plot 5, Industrial Area, Sector 18, Gurugram, Haryana 122015\n\n"
                "CUSTOMER ADDRESS:\n"
                "House 110, DLF Phase 3, Gurugram, Haryana 122002\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="House 110, DLF Phase 3, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_10",
            category="complex_multi_address",
            description="Credit card monthly statement with Branch and Cardholder address",
            document_text=(
                "ICICI BANK CREDIT CARDS\n\n"
                "CARDHOLDER MAILING ADDRESS:\n"
                "Flat 102, Shivalik Residency, CG Road, Navrangpura, Ahmedabad, Gujarat 380009\n\n"
                "ISSUING BRANCH:\n"
                "ICICI Towers, Bandra Kurla Complex, Mumbai, Maharashtra 400051\n"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 102, Shivalik Residency, CG Road, Navrangpura, Ahmedabad, Gujarat 380009",
                locality="Navrangpura",
                district="Ahmedabad",
                state="Gujarat",
                pincode="380009",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_11",
            category="complex_multi_address",
            description="Telecommunication corporate bill with HQ and Billing address",
            document_text=(
                "JIO ENTERPRISE SERVICES\n\n"
                "BILLING TO:\n"
                "Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021\n\n"
                "CORPORATE HEADQUARTERS:\n"
                "Reliance Corporate Park, Navi Mumbai, Thane, Maharashtra 400701\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_12",
            category="complex_multi_address",
            description="Medical pathology lab report with Lab and Patient address",
            document_text=(
                "DR LAL PATHLABS\n\n"
                "COLLECTION CENTRE:\n"
                "Block C, Sector 18, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301\n\n"
                "PATIENT ADDRESS:\n"
                "Flat 804, Express Trade Tower, Sector 132, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 804, Express Trade Tower, Sector 132, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301",
                locality="Noida",
                district="Gautam Buddha Nagar",
                state="Uttar Pradesh",
                pincode="201301",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_13",
            category="complex_multi_address",
            description="B2B Hardware supplier invoice with Factory and Consignee address",
            document_text=(
                "SUPREME STEEL TUBES LTD\n\n"
                "DISPATCHED FROM:\n"
                "MIDC Bhosari, Haveli, Pune, Maharashtra 411026\n\n"
                "CONSIGNEE ADDRESS:\n"
                "Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014\n"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014",
                locality="Kharadi",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_14",
            category="complex_multi_address",
            description="Chartered accountant audit engagement letter with Client and CA address",
            document_text=(
                "KAPOOR & ASSOCIATES CHARTERED ACCOUNTANTS\n\n"
                "AUDITOR OFFICE:\n"
                "15, Barakhamba Road, Connaught Place, New Delhi, Delhi 110001\n\n"
                "CLIENT HEAD OFFICE:\n"
                "Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Tower B, 6th Floor, DLF Cyber City, Sector 25, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MULTI_15",
            category="complex_multi_address",
            description="Hotel booking confirmation with Hotel and Guest billing address",
            document_text=(
                "TAJ COROMANDEL CHENNAI\n\n"
                "HOTEL PROPERTY:\n"
                "37, Mahatma Gandhi Road, Nungambakkam, Chennai, Tamil Nadu 600034\n\n"
                "GUEST BILLING ADDRESS:\n"
                "Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033\n"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033",
                locality="Jubilee Hills",
                district="Hyderabad",
                state="Telangana",
                pincode="500033",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 6: Multi-Token Localities [15 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="MTL_01",
            category="multi_token_localities",
            description="Pune Viman Nagar multi-word locality extraction",
            document_text=(
                "MAHARASHTRA GAS BILL\n"
                "Consumer: ROHIT SHINDE\n"
                "Address: Flat 203, Clover Park, Viman Nagar, Pune, Maharashtra 411014\n"
                "Bill No: 91823"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Flat 203, Clover Park, Viman Nagar, Pune, Maharashtra 411014",
                locality="Viman Nagar",
                district="Pune",
                state="Maharashtra",
                pincode="411014",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_02",
            category="multi_token_localities",
            description="Mumbai Bandra West multi-token locality parsing",
            document_text=(
                "MUNICIPAL CORPORATION OF GREATER MUMBAI\n"
                "Address: Sea Breeze Apt, Hill Road, Bandra West, Mumbai, Maharashtra 400050"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Sea Breeze Apt, Hill Road, Bandra West, Mumbai, Maharashtra 400050",
                locality="Bandra West",
                district="Mumbai",
                state="Maharashtra",
                pincode="400050",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_03",
            category="multi_token_localities",
            description="Delhi Connaught Place compound commercial locality",
            document_text=(
                "DELHI POLICE VERIFICATION\n"
                "Premises: Shop 4, Inner Circle, Connaught Place, New Delhi, Delhi 110001"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Shop 4, Inner Circle, Connaught Place, New Delhi, Delhi 110001",
                locality="Connaught Place",
                district="New Delhi",
                state="Delhi",
                pincode="110001",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_04",
            category="multi_token_localities",
            description="Pune Hinjewadi Phase 1 compound token",
            document_text=(
                "MIDC ALLOTMENT ORDER\n"
                "Unit: Plot 22, MIDC Road, Hinjewadi Phase 1, Mulshi, Pune, Maharashtra 411057"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 22, MIDC Road, Hinjewadi Phase 1, Mulshi, Pune, Maharashtra 411057",
                locality="Hinjewadi",
                subdistrict="Mulshi",
                district="Pune",
                state="Maharashtra",
                pincode="411057",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_05",
            category="multi_token_localities",
            description="Kolkata Salt Lake compound locality",
            document_text=(
                "WBIDC ALLOTMENT LETTER\n"
                "Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 42, Block EP, Sector V, Salt Lake, Kolkata, West Bengal 700091",
                locality="Salt Lake",
                district="Kolkata",
                state="West Bengal",
                pincode="700091",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_06",
            category="multi_token_localities",
            description="Bengaluru Electronic City tech hub multi-token address",
            document_text=(
                "KARNATAKA INDUSTRIAL AREA DEVELOPMENT BOARD\n"
                "Address: Plot 15, Phase 1, Electronic City, Bengaluru, Karnataka 560100"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 15, Phase 1, Electronic City, Bengaluru, Karnataka 560100",
                locality="Electronic City",
                district="Bengaluru",
                state="Karnataka",
                pincode="560100",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_07",
            category="multi_token_localities",
            description="Bengaluru Koramangala 4th Block multi-word token",
            document_text=(
                "BWSSB WATER INVOICE\n"
                "Address: #12, 80 Feet Road, Koramangala 4th Block, Bengaluru, Karnataka 560034"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="#12, 80 Feet Road, Koramangala 4th Block, Bengaluru, Karnataka 560034",
                locality="Koramangala",
                district="Bengaluru",
                state="Karnataka",
                pincode="560034",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_08",
            category="multi_token_localities",
            description="Gurugram DLF Cyber City compound business hub",
            document_text=(
                "BUILDING MANAGEMENT RECEIPT\n"
                "Tower B, DLF Cyber City, Sector 25, Gurugram, Haryana 122002"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Tower B, DLF Cyber City, Sector 25, Gurugram, Haryana 122002",
                locality="DLF Cyber City",
                district="Gurugram",
                state="Haryana",
                pincode="122002",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_09",
            category="multi_token_localities",
            description="Mumbai Andheri East industrial area",
            document_text=(
                "MAHARASHTRA POLLUTION CONTROL BOARD\n"
                "Unit: Plot 10, MIDC Central Road, Andheri East, Mumbai, Maharashtra 400093"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 10, MIDC Central Road, Andheri East, Mumbai, Maharashtra 400093",
                locality="Andheri East",
                district="Mumbai",
                state="Maharashtra",
                pincode="400093",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_10",
            category="multi_token_localities",
            description="Pune Hadapsar Industrial Estate",
            document_text=(
                "COMMERCIAL REGISTRATION\n"
                "Shed 12, Hadapsar Industrial Estate, Hadapsar, Pune, Maharashtra 411013"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Shed 12, Hadapsar Industrial Estate, Hadapsar, Pune, Maharashtra 411013",
                locality="Hadapsar",
                district="Pune",
                state="Maharashtra",
                pincode="411013",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_11",
            category="multi_token_localities",
            description="Hyderabad Jubilee Hills luxury enclave",
            document_text=(
                "GREATER HYDERABAD MUNICIPAL CORPORATION\n"
                "Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 108, Jubilee Hills, Road No 36, Hyderabad, Telangana 500033",
                locality="Jubilee Hills",
                district="Hyderabad",
                state="Telangana",
                pincode="500033",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_12",
            category="multi_token_localities",
            description="Chennai Anna Nagar multi-token residential hub",
            document_text=(
                "TAMIL NADU ELECTRICITY BOARD\n"
                "Old No 14, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Old No 14, 2nd Avenue, Anna Nagar, Chennai, Tamil Nadu 600040",
                locality="Anna Nagar",
                district="Chennai",
                state="Tamil Nadu",
                pincode="600040",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_13",
            category="multi_token_localities",
            description="Jaipur Vaishali Nagar residential locality",
            document_text=(
                "RAJASTHAN HOUSING BOARD\n"
                "Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Plot 21, Queens Road, Vaishali Nagar, Jaipur, Rajasthan 302021",
                locality="Vaishali Nagar",
                district="Jaipur",
                state="Rajasthan",
                pincode="302021",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_14",
            category="multi_token_localities",
            description="Noida Sector 62 tech hub",
            document_text=(
                "NEW OKHLA INDUSTRIAL DEVELOPMENT AUTHORITY\n"
                "Block C, Industrial Area, Sector 62, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="Block C, Industrial Area, Sector 62, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301",
                locality="Noida",
                district="Gautam Buddha Nagar",
                state="Uttar Pradesh",
                pincode="201301",
                expected_status="VERIFIED",
            ),
        ),
        OCRTestCase(
            case_id="MTL_15",
            category="multi_token_localities",
            description="Lucknow Gomti Nagar residential development",
            document_text=(
                "LUCKNOW DEVELOPMENT AUTHORITY\n"
                "House 5/112, Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226010"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            ground_truth=GroundTruthAddress(
                raw_text="House 5/112, Viram Khand, Gomti Nagar, Lucknow, Uttar Pradesh 226010",
                locality="Gomti Nagar",
                district="Lucknow",
                state="Uttar Pradesh",
                pincode="226010",
                expected_status="VERIFIED",
            ),
        ),
    ])

    # =========================================================================
    # CATEGORY 7: Negative & Adversarial Documents [10 cases]
    # =========================================================================
    cases.extend([
        OCRTestCase(
            case_id="NEG_01",
            category="negative_adversarial",
            description="PAN card front with no physical address",
            document_text=(
                "INCOME TAX DEPARTMENT - GOVT OF INDIA\n"
                "Permanent Account Number Card\n"
                "ABCDE1234F\n"
                "Name: ADITYA MANE\n"
                "Father's Name: DILIP MANE\n"
                "Date of Birth: 15/08/1995"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_02",
            category="negative_adversarial",
            description="UPI payment confirmation receipt without address",
            document_text=(
                "GOOGLE PAY - PAYMENT SUCCESSFUL\n"
                "Paid to: STARBUCKS COFFEE INDIA\n"
                "Amount: Rs. 420.00\n"
                "UPI Ref ID: 294819284918\n"
                "Date: 29 Sep 2026, 14:32 PM\n"
                "From: HDFC Bank A/C XX9918"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_03",
            category="negative_adversarial",
            description="Grocery store cash register invoice with line items only",
            document_text=(
                "D-MART AVENUE SUPERMARTS LTD\n"
                "Tax Invoice / Cash Memo\n"
                "Item 1: Aashirvaad Atta 10kg - 425.00\n"
                "Item 2: Fortune Sunflower Oil 1L - 145.00\n"
                "Item 3: Tata Salt 1kg - 28.00\n"
                "Total Items: 3 | Total Qty: 12\n"
                "Sub Total: 598.00 | GST: 0.00\n"
                "Grand Total: 598.00\n"
                "Thank You Visit Again!"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_04",
            category="negative_adversarial",
            description="Python source code snippet with comments",
            document_text=(
                "import os\n"
                "import sys\n\n"
                "def verify_checksum(filepath: str) -> bool:\n"
                "    # Calculates SHA-256 for integrity verification\n"
                "    with open(filepath, 'rb') as f:\n"
                "        return hashlib.sha256(f.read()).hexdigest()\n"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_05",
            category="negative_adversarial",
            description="Airline boarding pass without residential address",
            document_text=(
                "INDIGO AIRLINES - BOARDING PASS\n"
                "Passenger: MANE / ADITYA MR\n"
                "Flight: 6E 402\n"
                "Date: 12 OCT 2026\n"
                "From: PNQ (Pune) To: DEL (Delhi)\n"
                "Gate: 4 | Seat: 12A | Seq: 045\n"
                "Boarding Time: 06:15 AM"
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_06",
            category="negative_adversarial",
            description="Restaurant dining bill",
            document_text=(
                "MAINLAND CHINA RESTAURANT\n"
                "Table No: 14 | Covers: 4\n"
                "1 Veg Manchurian - 380\n"
                "1 Hakka Noodles - 340\n"
                "2 Jasmine Tea - 220\n"
                "CGST (2.5%): 23.50\n"
                "SGST (2.5%): 23.50\n"
                "Total Amount: Rs. 987.00"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_07",
            category="negative_adversarial",
            description="Software license agreement terms and conditions",
            document_text=(
                "END USER LICENSE AGREEMENT (EULA)\n"
                "BY INSTALLING THIS SOFTWARE YOU AGREE TO BE BOUND BY THE TERMS.\n"
                "SECTION 1: GRANT OF LICENSE\n"
                "THE SOFTWARE IS LICENSED, NOT SOLD.\n"
                "COPYRIGHT 2026 GEOLABS INC. ALL RIGHTS RESERVED."
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_08",
            category="negative_adversarial",
            description="Train e-ticket PNR status printout",
            document_text=(
                "INDIAN RAILWAY CATERING AND TOURISM CORPORATION\n"
                "ELECTRONIC RESERVATION SLIP (ERS)\n"
                "PNR: 284-9182391 | Train: 12128 / INTERCITY EXP\n"
                "From: PUNE (Pune Jn) To: CSMT (Mumbai CSMT)\n"
                "Class: CC | Quota: GENERAL\n"
                "Status: CNF / C1 / 44"
            ),
            split=Split.VAL,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_09",
            category="negative_adversarial",
            description="Server access log dump snippet",
            document_text=(
                "127.0.0.1 - - [29/Sep/2026:14:55:01 +0530] \"GET /api/v1/health HTTP/1.1\" 200 48\n"
                "192.168.1.104 - - [29/Sep/2026:14:55:02 +0530] \"POST /api/v1/auth HTTP/1.1\" 200 128\n"
                "10.0.0.15 - - [29/Sep/2026:14:55:05 +0530] \"GET /metrics HTTP/1.1\" 200 4096"
            ),
            split=Split.DEV,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
        OCRTestCase(
            case_id="NEG_10",
            category="negative_adversarial",
            description="Prescription medical dosage sheet without address",
            document_text=(
                "APOLLO CLINIC - DOCTOR PRESCRIPTION\n"
                "Patient: Rahul Verma | Age: 34 | Gender: Male\n"
                "Rx:\n"
                "1. Tab Paracetamol 650mg - 1-0-1 x 3 days\n"
                "2. Tab Cetirizine 10mg - 0-0-1 x 5 days\n"
                "Advice: Steam inhalation twice daily."
            ),
            split=Split.HELD_OUT,
            language="eng",
            script="Latin",
            is_negative_case=True,
            ground_truth=None,
        ),
    ])

    return cases


PHASE7_1_BENCHMARK_CASES = _build_dataset()


def get_phase7_1_benchmark_cases(split: Optional[Split] = None) -> List[OCRTestCase]:
    """Retrieve Phase 7.1 benchmark test cases, optionally filtered by split (DEV, VAL, HELD_OUT)."""
    if split is None:
        return PHASE7_1_BENCHMARK_CASES
    return [c for c in PHASE7_1_BENCHMARK_CASES if c.split == split]
