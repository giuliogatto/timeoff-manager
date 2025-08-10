import pytest
from fastapi import status

class TestMain:
    """Test main application endpoints"""
    
    def test_read_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Timeoff Manager API is running!" in data["message"]
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_docs_endpoint(self, client):
        """Test that docs endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
    
    def test_openapi_endpoint(self, client):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
