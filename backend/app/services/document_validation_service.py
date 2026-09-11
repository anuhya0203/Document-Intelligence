import logging
from pathlib import Path
from typing import Dict, Tuple
import PyPDF2
from PIL import Image
from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentValidationService:
    ALLOWED_TYPES = settings.ALLOWED_FILE_TYPES
    MAX_PAGES = settings.MAX_PAGES
    MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    @staticmethod
    def validate_file(file_path: str, file_name: str) -> Tuple[Dict, bool]:
        """
        Validate uploaded document before processing.
        Returns: (validation_dict, is_valid)
        """
        try:
            file_ext = Path(file_name).suffix.lower().lstrip('.')
            
            # Check file type
            if file_ext not in DocumentValidationService.ALLOWED_TYPES:
                return {
                    "file_type": file_ext,
                    "is_supported": False,
                    "is_readable": False,
                    "page_count": 0,
                    "status": "FAILED",
                    "error": f"Unsupported file type: {file_ext}"
                }, False
            
            # Check file size
            file_size = Path(file_path).stat().st_size
            if file_size > DocumentValidationService.MAX_SIZE:
                return {
                    "file_type": file_ext,
                    "is_supported": True,
                    "is_readable": False,
                    "page_count": 0,
                    "status": "FAILED",
                    "error": f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB"
                }, False
            
            # Check if file is empty
            if file_size == 0:
                return {
                    "file_type": file_ext,
                    "is_supported": True,
                    "is_readable": False,
                    "page_count": 0,
                    "status": "FAILED",
                    "error": "File is empty"
                }, False
            
            # Get page count
            page_count = DocumentValidationService._get_page_count(file_path, file_ext)
            
            if page_count == -1:
                return {
                    "file_type": file_ext,
                    "is_supported": True,
                    "is_readable": False,
                    "page_count": 0,
                    "status": "FAILED",
                    "error": "Failed to read document or corrupted PDF"
                }, False
            
            if page_count > DocumentValidationService.MAX_PAGES:
                return {
                    "file_type": file_ext,
                    "is_supported": True,
                    "is_readable": True,
                    "page_count": page_count,
                    "status": "FAILED",
                    "error": f"Document exceeds max {DocumentValidationService.MAX_PAGES} pages"
                }, False
            
            return {
                "file_type": file_ext,
                "is_supported": True,
                "is_readable": True,
                "page_count": page_count,
                "status": "PASS"
            }, True
            
        except Exception as e:
            logger.error(f"Validation error for {file_name}: {str(e)}")
            return {
                "file_type": "unknown",
                "is_supported": False,
                "is_readable": False,
                "page_count": 0,
                "status": "FAILED",
                "error": str(e)
            }, False
    
    @staticmethod
    def _get_page_count(file_path: str, file_ext: str) -> int:
        """Get page count for PDF or image files"""
        try:
            if file_ext == "pdf":
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return len(reader.pages)
            elif file_ext in ["jpg", "jpeg", "png"]:
                # Images are single page
                Image.open(file_path)
                return 1
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return -1
        
        return -1
