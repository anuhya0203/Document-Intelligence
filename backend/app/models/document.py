from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class ProcessedDocument(Base):
    __tablename__ = "processed_documents"
    
    id = Column(String(255), primary_key=True, index=True)
    file_name = Column(String(255), unique=True, index=True)
    document_type = Column(String(50))  # invoice, balance_sheet, profit_and_loss, cash_flow_statement
    
    # Processing metadata
    file_validation = Column(JSON)
    processing_status = Column(String(50))  # PASS, FAILED
    
    # Extraction results
    extracted_data = Column(JSON)
    validation_results = Column(JSON)
    
    # Confidence and evidence
    overall_confidence = Column(Float, nullable=True)
    processing_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "document_type": self.document_type,
            "file_validation": self.file_validation,
            "processing_status": self.processing_status,
            "extracted_data": self.extracted_data,
            "validation": self.validation_results,
            "overall_confidence": self.overall_confidence,
            "processing_metadata": self.processing_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
