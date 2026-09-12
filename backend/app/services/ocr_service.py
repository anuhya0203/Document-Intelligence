import logging
from typing import Optional
import fitz  # PyMuPDF
import pytesseract
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service optimized for Railway deployment - lightweight, handles 5-10MB PDFs."""

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
        """Extract text from native or scanned PDFs (handles 5-10MB files)."""
        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            # First pass: Try native text extraction
            native_text_count = 0
            for page_num, page in enumerate(doc):
                try:
                    page_text = page.get_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                        native_text_count += 1
                except Exception as e:
                    logger.warning(f"Native extraction failed on page {page_num}: {e}")

            # If we got native text from most pages, return it
            if native_text_count >= len(doc) * 0.5:  # 50% threshold
                doc.close()
                logger.info(f"Native PDF text extracted from {native_text_count}/{len(doc)} pages")
                return "\n".join(text_parts).strip()

            # Second pass: OCR on pages without native text
            logger.info("Running Tesseract OCR on scanned/low-text pages...")
            text_parts = []

            for page_num, page in enumerate(doc):
                try:
                    # Render page to image at reasonable DPI (150 for speed, 200 for quality)
                    pix = page.get_pixmap(dpi=150, clip=page.rect)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("ppm")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Run Tesseract OCR
                    page_text = pytesseract.image_to_string(image)
                    if page_text.strip():
                        text_parts.append(page_text)
                        logger.debug(f"OCR extracted {len(page_text)} chars from page {page_num + 1}")
                    
                except Exception as e:
                    logger.warning(f"OCR failed on page {page_num}: {e}")
                    continue

            doc.close()
            
            if not text_parts:
                logger.warning("No text extracted from PDF")
                return None
            
            return "\n".join(text_parts).strip()

        except Exception as e:
            logger.error(f"PDF extraction error: {e}", exc_info=True)
            return None

    @staticmethod
    def _extract_text_from_image(image_path: str) -> Optional[str]:
        """Extract text from JPG/PNG using Tesseract."""
        try:
            image = Image.open(image_path)
            
            # Convert RGBA to RGB if needed
            if image.mode in ("RGBA", "LA", "P"):
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = rgb_image
            
            # Tesseract config for better accuracy
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            if not text.strip():
                logger.warning(f"No text extracted from image: {image_path}")
                return None
            
            logger.info(f"Extracted {len(text)} chars from image")
            return text.strip()

        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return None
