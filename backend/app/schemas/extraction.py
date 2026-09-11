from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class Evidence(BaseModel):
    source_text: Optional[str] = None
    page_number: Optional[int] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)

class FileValidation(BaseModel):
    file_type: str
    is_supported: bool
    is_readable: bool
    page_count: int
    status: str  # PASS or FAILED
    error: Optional[str] = None

class ValidationCheck(BaseModel):
    name: str
    formula: Optional[str] = None
    operands: Optional[Dict[str, Any]] = None
    calculated_value: Optional[float] = None
    reported_value: Optional[float] = None
    variance: Optional[float] = None
    status: str  # PASS, FAIL, NOT_APPLICABLE

class ValidationResult(BaseModel):
    checks: List[ValidationCheck] = []
    overall_status: str
    issues: List[str] = []

class ProcessedDocumentResponse(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    overall_confidence: Optional[float] = None
    file_validation: FileValidation
    extracted_data: Dict[str, Any]
    validation: ValidationResult
    processing_metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True
