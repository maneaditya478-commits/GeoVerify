"""Document address extraction, region detection, normalization, and assembly package."""

from app.document.address.region_detector import AddressRegionDetector
from app.document.address.ocr_normalizer import OCRNormalizer
from app.document.address.field_extractor import AddressFieldExtractor
from app.document.address.pin_recovery import PINFirstRecoveryService
from app.document.address.assembler import AddressCandidateAssembler

__all__ = [
    "AddressRegionDetector",
    "OCRNormalizer",
    "AddressFieldExtractor",
    "PINFirstRecoveryService",
    "AddressCandidateAssembler",
]
