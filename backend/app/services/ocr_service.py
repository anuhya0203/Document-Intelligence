import logging
from typing import Optional

import fitz
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service using PyMuPDF + OCR.space."""

    OCR_URL = "https://api.ocr.space/parse/image"

    @staticmethod
    def extract_text(file_path: str, file_ext: str) -> Optional[str]:
        file_ext = file_ext.lower()

        if file_ext == "pdf":
            return OCRService._extract_pdf(file_path)

        if file_ext in ["jpg", "jpeg", "png"]:
            return OCRService._ocr_space(file_path)

        return None

    @staticmethod
    def _extract_pdf(pdf_path: str) -> Optional[str]:
        """
        First try native PDF extraction.
        If no text exists, send PDF to OCR.space.
        """
        try:
            doc = fitz.open(pdf_path)

            native_text = []

            for page in doc:
                native_text.append(page.get_text())

            doc.close()

            text = "\n".join(native_text).strip()

            # Digital PDF
            if len(text) > 50:
                logger.info("Native PDF text extracted.")
                return text

            logger.info("Scanned PDF detected. Using OCR.space.")
            return OCRService._ocr_space(pdf_path)

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            return None

    @staticmethod
    def _ocr_space(file_path: str) -> Optional[str]:
        """
        OCR using OCR.space API.
        """
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    OCRService.OCR_URL,
                    files={"file": f},
                    data={
                        "apikey": settings.OCR_SPACE_API_KEY,
                        "language": "eng",
                        "isOverlayRequired": False,
                        "OCREngine": 2,
                    },
                    timeout=60,
                )

            response.raise_for_status()

            result = response.json()

            if result.get("IsErroredOnProcessing"):
                logger.error(result.get("ErrorMessage"))
                return None

            parsed = result.get("ParsedResults", [])

            if not parsed:
                return None

            text = "\n".join(
                page.get("ParsedText", "") for page in parsed
            ).strip()

            logger.info(f"OCR.space extracted {len(text)} characters.")

            return text if text else None

        except Exception as e:
            logger.error(f"OCR.space error: {e}", exc_info=True)
            return None