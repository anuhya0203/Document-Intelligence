import logging
from typing import Optional

import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service for PDFs and images."""

    # Load EasyOCR model once
    reader = easyocr.Reader(["en"], gpu=False)

    @staticmethod
    def extract_text(file_path: str, file_ext: str) -> Optional[str]:
        """Extract text from PDF or image."""
        try:
            file_ext = file_ext.lower()

            if file_ext == "pdf":
                return OCRService._extract_text_from_pdf(file_path)

            if file_ext in ["jpg", "jpeg", "png"]:
                return OCRService._extract_text_from_image(file_path)

            return None

        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return None

    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """Extract text from native PDFs or scanned PDFs."""

        try:
            doc = fitz.open(pdf_path)
            text = ""

            # Native PDF extraction
            for page in doc:
                text += page.get_text()

            if text.strip():
                doc.close()
                logger.info("Native PDF text extracted.")
                return text.strip()

            logger.info("Scanned PDF detected. Running EasyOCR.")

            ocr_text = []

            for page in doc:
                pix = page.get_pixmap(dpi=300)

                image = Image.frombytes(
                    "RGB",
                    (pix.width, pix.height),
                    pix.samples,
                )

                results = OCRService.reader.readtext(
                    np.array(image),
                    detail=0
                )

                ocr_text.extend(results)

            doc.close()
            return "\n".join(ocr_text).strip()

        except Exception as e:
            logger.error(f"PDF OCR error: {e}")
            return None

    @staticmethod
    def _extract_text_from_image(image_path: str) -> Optional[str]:
        """Extract text from JPG/PNG using EasyOCR."""

        try:
            image = Image.open(image_path).convert("RGB")

            results = OCRService.reader.readtext(
                np.array(image),
                detail=0
            )

            if not results:
                return None

            return "\n".join(results).strip()

        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return None