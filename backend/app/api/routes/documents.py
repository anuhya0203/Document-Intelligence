import logging
import tempfile
import time
import shutil
import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import logger
from app.schemas.extraction import ProcessedDocumentResponse, FileValidation, ValidationResult
from app.services.document_validation_service import DocumentValidationService
from app.services.ocr_service import OCRService
from app.services.extraction_service import ExtractionService
from app.services.financial_validation_service import FinancialValidationService
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_type import DocumentType
from app.services.document_classifier_service import DocumentClassifierService

router = APIRouter(prefix="/api/v1", tags=["documents"])

extraction_service = ExtractionService()

@router.post("/documents/process")
async def process_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    db: Session = Depends(get_db)
):
    start_time = time.time()

    SUPPORTED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    SUPPORTED_MIME_TYPES = {
        "application/pdf",
        "image/pdf",
        "image/jpeg",
        "image/png",
    }

    tmp_path = None

    try:
        file_ext = Path(file.filename).suffix.lower().lstrip(".")

        # -----------------------------------
        # STEP 0: FILE TYPE VALIDATION
        # -----------------------------------
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "UNSUPPORTED_FILE_TYPE",
                        "message": "Only PDF / JPG / PNG documents are supported."
                    }
                }
            )

        if file.content_type not in SUPPORTED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "UNSUPPORTED_FILE_TYPE",
                        "message": "Only PDF / JPG / PNG documents are supported."
                    }
                }
            )

        # -----------------------------------
        # SAVE TEMP FILE
        # -----------------------------------
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(file.filename).suffix
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # -----------------------------------
        # STEP 1: FILE VALIDATION
        # -----------------------------------
        file_validation_dict, is_valid = (
            DocumentValidationService.validate_file(
                tmp_path,
                file.filename
            )
        )

        if not is_valid:
            return {
                "document_name": file.filename,
                "file_name": file.filename,
                "document_type": document_type.value,
                "processing_status": "FAILED",
                "file_validation": file_validation_dict,
                "extracted_data": {},
                "validation": {
                    "checks": [],
                    "overall_status": "FAILED",
                    "issues": [file_validation_dict.get("error")]
                },
                "overall_confidence": 0.0,
                "processing_metadata": {
                    "error": file_validation_dict.get("error")
                }
            }

        # -----------------------------------
        # STEP 2: OCR
        # -----------------------------------
        extracted_text = OCRService.extract_text(
            tmp_path,
            file_ext
        )

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "OCR_FAILED",
                        "message": "Could not extract text from document"
                    }
                }
            )

        logger.info(
            f"OCR extracted {len(extracted_text)} characters"
        )

        # -----------------------------------
        # STEP 3: DOCUMENT TYPE VALIDATION
        # -----------------------------------
        classifier = DocumentClassifierService()

        detected_type = classifier.classify(extracted_text)

        logger.info(
            f"Detected: {detected_type}, "
            f"Selected: {document_type.value}"
        )

        if (
            detected_type != "unknown"
            and detected_type != document_type.value
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "DOCUMENT_TYPE_MISMATCH",
                        "message": (
                            f"Uploaded document appears to be "
                            f"'{detected_type}' but "
                            f"'{document_type.value}' was selected."
                        )
                    }
                }
            )

        # -----------------------------------
        # STEP 4: EXTRACTION
        # -----------------------------------
        extracted_data = extraction_service.extract_fields(
            extracted_text,
            document_type.value,
            file_validation_dict.get("page_count", 1)
        )

        # -----------------------------------
        # STEP 5: FINANCIAL VALIDATION
        # -----------------------------------
        validation_result = (
            FinancialValidationService.validate_document(
                extracted_data,
                document_type.value
            )
        )

        overall_confidence = (
            0.85
            if validation_result["overall_status"] == "PASS"
            else 0.60
        )

        result = {
            "document_name": file.filename,
            "file_name": file.filename,
            "document_type": document_type.value,
            "processing_status": (
                "PASS" if extracted_data else "FAILED"
            ),
            "file_validation": file_validation_dict,
            "extracted_data": extracted_data,
            "validation": validation_result,
            "overall_confidence": overall_confidence,
            "processing_metadata": {
                "ocr_used": file_ext in ["jpg", "jpeg", "png"],
                "processed_at": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "processing_time_ms": int(
                    (time.time() - start_time) * 1000
                )
            }
        }

        DocumentRepository.create(db, result)

        logger.info(
            f"Document processed successfully: {file.filename}"
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Document processing error: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {str(e)}"
        )

    finally:
        if tmp_path and Path(tmp_path).exists():
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

@router.get("/documents/{document_name}", response_model=ProcessedDocumentResponse)
async def get_document(
    document_name: str,
    db: Session = Depends(get_db)
):
    """Retrieve latest processed document by name"""
    doc = DocumentRepository.get_by_name(db, document_name)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc.to_dict()

@router.get("/documents")
async def list_documents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all processed documents for dashboard"""
    documents = DocumentRepository.list_all(db, limit=limit, offset=offset)
    
    return {
        "total": len(documents),
        "limit": limit,
        "offset": offset,
        "documents": [doc.to_dict() for doc in documents]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Document Intelligence API",
        "version": "1.0.0"
    }
