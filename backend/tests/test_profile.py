import pytest
from fastapi import status

class TestProfile:
    """Test profile endpoint"""
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication"""
        response = client.get("/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_profile_success(self, client, auth_headers, test_user):
        """Test getting profile with authentication"""
        response = client.get("/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["name"] == test_user.name
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role
        assert data["unit_id"] == test_user.unit_id
    
    def test_get_profile_manager(self, client, manager_headers, test_manager):
        """Test getting profile for manager"""
        response = client.get("/profile", headers=manager_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_manager.id
        assert data["name"] == test_manager.name
        assert data["email"] == test_manager.email
        assert data["role"] == test_manager.role
        assert data["unit_id"] == test_manager.unit_id
