import logging
import tempfile
import time
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

router = APIRouter(prefix="/api/v1", tags=["documents"])

extraction_service = ExtractionService()

@router.post("/documents/process")
async def process_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document for extraction and validation.
    
    Args:
        file: PDF, JPG, or PNG file
        document_type: invoice | balance_sheet | profit_and_loss | cash_flow_statement
    """
    start_time = time.time()
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        
        # Step 1: File Validation
        file_validation_dict, is_valid = DocumentValidationService.validate_file(
            tmp_path, file.filename
        )
        
        if not is_valid:
            logger.warning(f"File validation failed: {file.filename}")
            processing_metadata = {"error": file_validation_dict.get("error")}
            result = {
                "document_name": file.filename,   # API response
                "file_name": file.filename,       # Database field
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
                "processing_metadata": processing_metadata
            }
            
            # Store result in DB
            DocumentRepository.create(db, result)
            return result
        
        # Step 2: OCR / Text Extraction
        extracted_text = OCRService.extract_text(tmp_path, file_ext)
        if not extracted_text:
            logger.warning(f"OCR extraction failed: {file.filename}")
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from document"
            )
        
        # Step 3: AI Extraction using Claude
        extracted_data = extraction_service.extract_fields(
            extracted_text, 
            document_type.value,
            file_validation_dict.get("page_count", 1)
        )
        
        # Step 4: Financial Validation
        validation_result = FinancialValidationService.validate_document(
            extracted_data,
            document_type.value
        )
        
        # Calculate confidence (optional)
        overall_confidence = 0.85 if validation_result["overall_status"] == "PASS" else 0.60
        
        # Prepare final response
        result = {
            "document_name": file.filename,   # API response
            "file_name": file.filename,       # Database field
            "document_type": document_type.value,
            "processing_status": "PASS" if extracted_data else "FAILED",
            "file_validation": file_validation_dict,
            "extracted_data": extracted_data,
            "validation": validation_result,
            "overall_confidence": overall_confidence,
            "processing_metadata": {
                "ocr_used": file_ext in ["jpg", "jpeg", "png"],
                "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        
        # Store in database
        DocumentRepository.create(db, result)
        
        logger.info(f"Document processed successfully: {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {str(e)}"
        )
    finally:
        # Cleanup
        try:
            Path(tmp_path).unlink()
        except:
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
