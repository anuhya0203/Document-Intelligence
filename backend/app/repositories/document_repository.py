import logging
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import ProcessedDocument

logger = logging.getLogger(__name__)

class DocumentRepository:
    """Database operations for processed documents"""
    
    @staticmethod
    def create(db: Session, document_data: dict) -> ProcessedDocument:
        """Create and store a processed document"""
        doc_id = str(uuid.uuid4())
        
        db_doc = ProcessedDocument(
            id=doc_id,
            file_name=document_data.get("file_name"),
            document_type=document_data.get("document_type"),
            file_validation=document_data.get("file_validation"),
            processing_status=document_data.get("processing_status"),
            extracted_data=document_data.get("extracted_data"),
            validation_results=document_data.get("validation"),
            overall_confidence=document_data.get("overall_confidence"),
            processing_metadata=document_data.get("processing_metadata")
        )
        
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        logger.info(f"Document {doc_id} stored: {document_data.get('file_name')}")
        return db_doc
    
    @staticmethod
    def get_by_name(db: Session, file_name: str) -> Optional[ProcessedDocument]:
        """Retrieve latest document by file name"""
        return db.query(ProcessedDocument).filter(
            ProcessedDocument.file_name == file_name
        ).order_by(ProcessedDocument.created_at.desc()).first()
    
    @staticmethod
    def get_by_id(db: Session, doc_id: str) -> Optional[ProcessedDocument]:
        """Retrieve document by ID"""
        return db.query(ProcessedDocument).filter(
            ProcessedDocument.id == doc_id
        ).first()
    
    @staticmethod
    def list_all(db: Session, limit: int = 100, offset: int = 0) -> list:
        """List all processed documents"""
        return db.query(ProcessedDocument).order_by(
            ProcessedDocument.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def update(db: Session, doc_id: str, update_data: dict) -> Optional[ProcessedDocument]:
        """Update document record"""
        doc = DocumentRepository.get_by_id(db, doc_id)
        if not doc:
            return None
        
        for key, value in update_data.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        db.commit()
        db.refresh(doc)
        return doc
