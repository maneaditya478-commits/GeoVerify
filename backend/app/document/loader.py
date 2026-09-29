"""Document Loader and Page Renderer for GeoVerify India (Phase 7).

Handles loading document bytes, rendering multi-page PDFs into image representations,
and extracting embedded text streams where applicable.
"""

import io
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import pypdf

from app.document.models import DocumentType


class LoadedPage:
    """Represents a loaded page with image representation and optional embedded text."""
    def __init__(self, page_num: int, image: Image.Image, embedded_text: str = ""):
        self.page_num = page_num
        self.image = image
        self.embedded_text = embedded_text
        self.width, self.height = image.size


class DocumentLoader:
    """Loads document bytes and returns loaded pages with PIL image handles."""

    @classmethod
    def load_pages(cls, file_bytes: bytes, doc_type: DocumentType) -> List[LoadedPage]:
        """Loads and returns all pages from the document bytes."""
        pages: List[LoadedPage] = []

        if doc_type == DocumentType.IMAGE:
            img = Image.open(io.BytesIO(file_bytes))
            # Convert RGBA/Palette to RGB
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            pages.append(LoadedPage(page_num=1, image=img, embedded_text=""))

        elif doc_type == DocumentType.PDF:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for idx, p in enumerate(reader.pages):
                page_num = idx + 1
                text = p.extract_text() or ""
                
                # Check if page has embedded images or render text to bitmap
                img = cls._render_pdf_page_to_image(p, text)
                pages.append(LoadedPage(page_num=page_num, image=img, embedded_text=text))

        return pages

    @classmethod
    def _render_pdf_page_to_image(cls, pdf_page: Any, extracted_text: str) -> Image.Image:
        """
        Renders PDF page to image. If raster images are embedded, extracts the primary image;
        otherwise synthesizes a high-DPI text canvas for OCR analysis.
        """
        # 1. Try extracting raster image from page images
        if hasattr(pdf_page, "images") and len(pdf_page.images) > 0:
            try:
                first_img = pdf_page.images[0]
                img = Image.open(io.BytesIO(first_img.data))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                return img
            except Exception:
                pass

        # 2. Render text onto a standard 300 DPI canvas (8.5x11 inch page = 2550x3300)
        width, height = 1800, 2400
        canvas = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(canvas)

        lines = extracted_text.splitlines() if extracted_text else ["Document Page"]
        y_cursor = 100
        x_margin = 100

        for line in lines[:80]:  # Up to 80 lines
            if line.strip():
                draw.text((x_margin, y_cursor), line.strip(), fill="black")
                y_cursor += 30

        return canvas


document_loader = DocumentLoader()
