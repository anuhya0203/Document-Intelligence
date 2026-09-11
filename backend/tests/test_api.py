import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal

client = TestClient(app)

class TestAPI:
    """Test REST API endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'docs' in data
    
    def test_list_documents_empty(self):
        """Test list documents when empty"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert 'documents' in data
        assert 'limit' in data
    
    def test_get_nonexistent_document(self):
        """Test getting non-existent document"""
        response = client.get("/api/v1/documents/nonexistent.pdf")
        assert response.status_code == 404
    
    def test_upload_unsupported_type(self):
        """Test uploading unsupported file type"""
        files = {'file': ('test.txt', b'content', 'text/plain')}
        data = {'document_type': 'invoice'}
        
        response = client.post(
            "/api/v1/documents/process",
            files=files,
            data=data
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            result = response.json()
            assert result['processing_status'] == 'FAILED'
    
    def test_upload_missing_type(self):
        """Test upload without document type"""
        files = {'file': ('test.pdf', b'%PDF-1.4\n%EOF', 'application/pdf')}
        
        response = client.post(
            "/api/v1/documents/process",
            files=files
        )
        
        # Should fail due to missing document_type
        assert response.status_code in [422, 400]
    
    def test_openapi_docs(self):
        """Test OpenAPI documentation"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert 'swagger' in response.text.lower() or 'rapidoc' in response.text.lower()
    
    def test_openapi_json(self):
        """Test OpenAPI JSON schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert 'paths' in data
        assert '/api/v1/documents/process' in data['paths']

class TestAPIIntegration:
    """Integration tests with mock data"""
    
    def test_workflow_invoice(self):
        """Test complete invoice workflow"""
        # 1. Process invoice
        # Note: Requires actual PDF or mock
        pass
    
    def test_workflow_balance_sheet(self):
        """Test complete balance sheet workflow"""
        pass
    
    def test_concurrent_uploads(self):
        """Test concurrent document uploads"""
        # Would require async test setup
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
