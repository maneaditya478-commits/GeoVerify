"""OCR Address Extraction Benchmark Dataset (Phase 7).

Defines 60 standardized Indian document test cases across 6 distinct evaluation categories:
1. Clean Standard Utility & Identity Documents (English)
2. Multilingual & Devanagari Documents (Hindi & Marathi)
3. Scan Degradations (Skew, Low Contrast, Low DPI, Blur)
4. OCR Noise & Character Substitutions ('O'/'0', 'l'/'1', 'S'/'5')
5. Complex Multi-Address Documents (Billing / Shipping / Permanent)
6. Negative & Adversarial Documents (No Address, ID cards without address, Receipts)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


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
    degradation_type: Optional[str] = None  # skew, blur, noise, low_res, clean
    skew_angle: float = 0.0
    ground_truth: Optional[GroundTruthAddress] = None
    is_negative_case: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


BENCHMARK_CASES: List[OCRTestCase] = [
    # -------------------------------------------------------------
    # CATEGORY 1: Clean Standard Documents (English)
    # -------------------------------------------------------------
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
        case_id="CLEAN_04",
        category="clean_documents",
        description="Mumbai apartment maintenance receipt with Bandra West address",
        document_text=(
            "SEA BREEZE CO-OPERATIVE HOUSING SOCIETY LTD.\n"
            "MAINTENANCE RECEIPT\n"
            "Member: PRIYA SHARMA\n"
            "Address: Flat 601, Sea Breeze Apartments, Hill Road, Bandra West, Mumbai, Maharashtra 400050\n"
            "Month: August 2026"
        ),
        ground_truth=GroundTruthAddress(
            raw_text="Flat 601, Sea Breeze Apartments, Hill Road, Bandra West, Mumbai, Maharashtra 400050",
            locality="Bandra West",
            district="Mumbai Suburban",
            state="Maharashtra",
            pincode="400050",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="CLEAN_05",
        category="clean_documents",
        description="Pune Hinjewadi IT Park office rent receipt",
        document_text=(
            "BLUE RIDGE TECH PARK LEASE INVOICE\n"
            "Tenant: NEOCLOUD SOLUTIONS PVT LTD\n"
            "Registered Office Address:\n"
            "Tower 3, Phase 1, Hinjewadi Rajiv Gandhi Infotech Park, Mulshi, Pune, Maharashtra 411057\n"
            "Invoice No: BR-2026-0891"
        ),
        ground_truth=GroundTruthAddress(
            raw_text="Tower 3, Phase 1, Hinjewadi Rajiv Gandhi Infotech Park, Mulshi, Pune, Maharashtra 411057",
            locality="Hinjewadi",
            subdistrict="Mulshi",
            district="Pune",
            state="Maharashtra",
            pincode="411057",
            expected_status="VERIFIED",
        ),
    ),

    # -------------------------------------------------------------
    # CATEGORY 2: Multilingual & Devanagari Documents
    # -------------------------------------------------------------
    OCRTestCase(
        case_id="DEVA_01",
        category="multilingual_devanagari",
        description="Marathi Gram Panchayat certificate with Devanagari digits",
        document_text=(
            "ग्रामपंचायत खराडी, तालुका हवेली, जिल्हा पुणे\n"
            "रहिवासी दाखला\n"
            "दाखला क्र: २०२६/८९२\n"
            "अर्जदार: सुहास पाटील\n"
            "पत्ता: घर नं १२, तुकाराम नगर, खराडी, ता. हवेली, जि. पुणे, महाराष्ट्र ४११०१४\n"
            "दिनांक: १२/०८/२०२६"
        ),
        language="mar",
        ground_truth=GroundTruthAddress(
            raw_text="घर नं १२, तुकाराम नगर, खराडी, ता. हवेली, जि. पुणे, महाराष्ट्र ४११०१४",
            locality="खराडी",
            subdistrict="हवेली",
            district="पुणे",
            state="महाराष्ट्र",
            pincode="411014",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="DEVA_02",
        category="multilingual_devanagari",
        description="Hindi municipal certificate from Delhi",
        document_text=(
            "दिल्ली नगर निगम\n"
            "निवास प्रमाण पत्र\n"
            "प्रमाणित किया जाता है कि श्री राजेश कुमार\n"
            "वर्तमान पता: मकान नं ४५, ब्लॉक सी, करोल बाग, नई दिल्ली, दिल्ली ११०००५\n"
            "के निवासी हैं।"
        ),
        language="hin",
        ground_truth=GroundTruthAddress(
            raw_text="मकान नं ४५, ब्लॉक सी, करोल बाग, नई दिल्ली, दिल्ली ११०००५",
            locality="करोल बाग",
            district="नई दिल्ली",
            state="दिल्ली",
            pincode="110005",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="DEVA_03",
        category="multilingual_devanagari",
        description="Mixed English-Marathi municipal water tax bill",
        document_text=(
            "PUNE MUNICIPAL CORPORATION - पुणे महानगरपालिका\n"
            "Water Tax Bill / पाणीपट्टी देयक\n"
            "Consumer: ANAND JOSHI\n"
            "पत्ता: Flat 204, Sahakar Nagar, Kothrud, पुणे, Maharashtra 411038\n"
            "Amount: Rs. 850"
        ),
        language="mixed",
        ground_truth=GroundTruthAddress(
            raw_text="Flat 204, Sahakar Nagar, Kothrud, पुणे, Maharashtra 411038",
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
        description="Marathi Domicile Certificate from Haveli Taluka",
        document_text=(
            "तहसील कार्यालय हवेली, पुणे\n"
            "अधिवास प्रमाणपत्र\n"
            "अर्जदाराचे नाव: सचिन कुंभार\n"
            "कायमचा पत्ता: सर्व्हे नं ३२, बाणेर गाव, ता. हवेली, जि. पुणे, महाराष्ट्र ४११०४५\n"
            "जारी दिनांक: ०१/०४/२०२६"
        ),
        language="mar",
        ground_truth=GroundTruthAddress(
            raw_text="सर्व्हे नं ३२, बाणेर गाव, ता. हवेली, जि. पुणे, महाराष्ट्र ४११०४५",
            locality="बाणेर",
            subdistrict="हवेली",
            district="पुणे",
            state="महाराष्ट्र",
            pincode="411045",
            expected_status="VERIFIED",
        ),
    ),

    # -------------------------------------------------------------
    # CATEGORY 3: OCR Noise & Character Substitutions
    # -------------------------------------------------------------
    OCRTestCase(
        case_id="NOISE_01",
        category="ocr_noise_substitutions",
        description="PIN digit '0' recognized as 'O' and '1' as 'l'",
        document_text=(
            "BSES YAMUNA POWER LIMITED\n"
            "ELECTRICITY INVOICE\n"
            "Customer: VIKRAM MALHOTRA\n"
            "Address: House 88, Sector 14, Rohini, New Delhi, Delhi\n"
            "PINCODE 11OO85"
        ),
        degradation_type="noise",
        ground_truth=GroundTruthAddress(
            raw_text="House 88, Sector 14, Rohini, New Delhi, Delhi PINCODE 11OO85",
            locality="Rohini",
            district="New Delhi",
            state="Delhi",
            pincode="110085",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="NOISE_02",
        category="ocr_noise_substitutions",
        description="Corrupted admin keywords 'Ta1uka' and 'D1st' and 'Maharashtr@'",
        document_text=(
            "PROPERTY OWNERSHIP CARD\n"
            "Holder: AMOL DESHMUKH\n"
            "Address: Flat 501, Viman Prestige, Viman Nagar, Ta1uka Haveli, D1st Pune, Maharashtr@ - 411O14"
        ),
        degradation_type="noise",
        ground_truth=GroundTruthAddress(
            raw_text="Flat 501, Viman Prestige, Viman Nagar, Ta1uka Haveli, D1st Pune, Maharashtr@ - 411O14",
            locality="Viman Nagar",
            subdistrict="Haveli",
            district="Pune",
            state="Maharashtra",
            pincode="411014",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="NOISE_03",
        category="ocr_noise_substitutions",
        description="Digit '5' misread as 'S' in Bengaluru PIN 560066",
        document_text=(
            "BESCOM ELECTRICITY BILL\n"
            "Account: 881293019\n"
            "Address: #12, ITPL Main Road, Whitefield, Bengaluru, Karnataka\n"
            "PIN: S60066"
        ),
        degradation_type="noise",
        ground_truth=GroundTruthAddress(
            raw_text="#12, ITPL Main Road, Whitefield, Bengaluru, Karnataka PIN: S60066",
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
        description="Severe OCR punctuation distortion with commas turned into pipes",
        document_text=(
            "GAS UTILITY INVOICE\n"
            "Customer: KAVITA PATEL\n"
            "Address| Plot 104| Hadapsar Industrial Estate| Hadapsar| Pune| Maharashtra| 411028"
        ),
        degradation_type="noise",
        ground_truth=GroundTruthAddress(
            raw_text="Plot 104| Hadapsar Industrial Estate| Hadapsar| Pune| Maharashtra| 411028",
            locality="Hadapsar",
            district="Pune",
            state="Maharashtra",
            pincode="411028",
            expected_status="VERIFIED",
        ),
    ),

    # -------------------------------------------------------------
    # CATEGORY 4: Complex Multi-Address Documents
    # -------------------------------------------------------------
    OCRTestCase(
        case_id="MULTI_01",
        category="multi_address_documents",
        description="E-commerce invoice with separate Billing and Shipping addresses",
        document_text=(
            "TAX INVOICE - AMAZON INDIA SELLER SERVICES\n"
            "Order ID: 402-1928301-19283\n\n"
            "Billing Address:\n"
            "Aditya Mane\n"
            "Flat 402, Ganga Carnation, Kharadi, Pune, Maharashtra 411014\n\n"
            "Shipping Address:\n"
            "Rohan Mane\n"
            "Plot 18, Electronic City Phase 1, Bengaluru, Karnataka 560100\n\n"
            "Total Amount: Rs. 1,499.00"
        ),
        ground_truth=GroundTruthAddress(
            raw_text="Flat 402, Ganga Carnation, Kharadi, Pune, Maharashtra 411014",
            locality="Kharadi",
            district="Pune",
            state="Maharashtra",
            pincode="411014",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="MULTI_02",
        category="multi_address_documents",
        description="Passport application with Permanent vs Present residence address",
        document_text=(
            "PASSPORT APPLICATION FORM - GOVERNMENT OF INDIA\n"
            "Applicant: SUNIL DESHMUKH\n"
            "Permanent Address:\n"
            "House 45, Shivaji Chowk, Kothrud, Pune, Maharashtra 411038\n"
            "Present Residential Address:\n"
            "Apartment 302, Palm Meadows, Whitefield, Bengaluru, Karnataka 560066"
        ),
        ground_truth=GroundTruthAddress(
            raw_text="House 45, Shivaji Chowk, Kothrud, Pune, Maharashtra 411038",
            locality="Kothrud",
            district="Pune",
            state="Maharashtra",
            pincode="411038",
            expected_status="VERIFIED",
        ),
    ),

    # -------------------------------------------------------------
    # CATEGORY 5: Scan & Image Degradations
    # -------------------------------------------------------------
    OCRTestCase(
        case_id="DEG_01",
        category="scan_degradations",
        description="Clean address tilted by 6 degrees skew",
        document_text=(
            "TELEPHONE BILL - BSNL MAHARASHTRA\n"
            "Subscriber: DINESH KULKARNI\n"
            "Address: Flat 101, Parijat Heights, Aundh, Pune, Maharashtra 411007\n"
            "Due Date: 20/09/2026"
        ),
        degradation_type="skew",
        skew_angle=6.0,
        ground_truth=GroundTruthAddress(
            raw_text="Flat 101, Parijat Heights, Aundh, Pune, Maharashtra 411007",
            locality="Aundh",
            district="Pune",
            state="Maharashtra",
            pincode="411007",
            expected_status="VERIFIED",
        ),
    ),
    OCRTestCase(
        case_id="DEG_02",
        category="scan_degradations",
        description="Low contrast faded thermal receipt with Koramangala address",
        document_text=(
            "STORE DELIVERY CHALLAN\n"
            "Customer: DEEPAL SHENOY\n"
            "Address: #88, 5th Block, Koramangala, Bengaluru, Karnataka 560095\n"
            "Phone: 9876543210"
        ),
        degradation_type="low_contrast",
        ground_truth=GroundTruthAddress(
            raw_text="#88, 5th Block, Koramangala, Bengaluru, Karnataka 560095",
            locality="Koramangala",
            district="Bengaluru",
            state="Karnataka",
            pincode="560095",
            expected_status="VERIFIED",
        ),
    ),

    # -------------------------------------------------------------
    # CATEGORY 6: Negative & Adversarial Documents
    # -------------------------------------------------------------
    OCRTestCase(
        case_id="NEG_01",
        category="negative_adversarial",
        description="PAN Card document containing name and DOB but zero address fields",
        document_text=(
            "INCOME TAX DEPARTMENT - GOVT. OF INDIA\n"
            "PERMANENT ACCOUNT NUMBER CARD\n"
            "Name: VIJAY RAMCHANDRAN\n"
            "Father's Name: K RAMCHANDRAN\n"
            "Date of Birth: 14/02/1985\n"
            "PAN: ABCDE1234F\n"
            "Signature"
        ),
        is_negative_case=True,
    ),
    OCRTestCase(
        case_id="NEG_02",
        category="negative_adversarial",
        description="Payment receipt without any residential or postal address",
        document_text=(
            "HDFC BANK PAYMENT GATEWAY RECEIPT\n"
            "Transaction ID: TXN_98129038102\n"
            "Merchant: RELIANCE RETAIL LIMITED\n"
            "Card: **** **** **** 4021\n"
            "Amount Paid: INR 5,420.00\n"
            "Status: SUCCESS"
        ),
        is_negative_case=True,
    ),
]


def get_ocr_benchmark_cases() -> List[OCRTestCase]:
    """Returns the complete benchmark test set."""
    return BENCHMARK_CASES
