import pytest
import tempfile
from pathlib import Path
from app.services.document_validation_service import DocumentValidationService

class TestDocumentValidation:
    """Test file validation logic"""
    
    def test_valid_pdf(self):
        """Test valid PDF file"""
        # Create a minimal PDF for testing
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Minimal valid PDF
            f.write(b'%PDF-1.4\n%EOF')
            f.flush()
            
            validation, is_valid = DocumentValidationService.validate_file(
                f.name, "test.pdf"
            )
            
            assert validation['is_supported'] == True
            assert validation['file_type'] == 'pdf'
    
    def test_unsupported_file_type(self):
        """Test unsupported file type"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'test')
            f.flush()
            
            validation, is_valid = DocumentValidationService.validate_file(
                f.name, "test.txt"
            )
            
            assert validation['is_supported'] == False
            assert is_valid == False
            assert 'Unsupported' in validation.get('error', '')
    
    def test_empty_file(self):
        """Test empty file handling"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.flush()
            
            validation, is_valid = DocumentValidationService.validate_file(
                f.name, "test.pdf"
            )
            
            assert validation['status'] == 'FAILED'
            assert is_valid == False
            assert 'empty' in validation.get('error', '').lower()
    
    def test_valid_image(self):
        """Test valid image file"""
        # Create a minimal valid PNG
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            # Minimal PNG header
            f.write(b'\x89PNG\r\n\x1a\n')
            f.flush()
            
            validation, is_valid = DocumentValidationService.validate_file(
                f.name, "test.png"
            )
            
            assert validation['is_supported'] == True
            assert validation['file_type'] == 'png'
    
    def test_file_size_limit(self):
        """Test file size limit"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Write data exceeding limit (simulated)
            # Note: actual test would need to mock file size
            pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
