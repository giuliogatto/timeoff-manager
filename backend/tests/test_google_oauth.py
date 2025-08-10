import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from models.leave_requests import User, AuthProviderEnum

class TestGoogleOAuth:
    """Test Google OAuth endpoints"""
    
    def test_get_google_auth_url_success(self, client):
        """Test getting Google OAuth URL"""
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret'
        }):
            response = client.get("/google/auth-url")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "auth_url" in data
            assert "accounts.google.com" in data["auth_url"]
            assert "test-client-id" in data["auth_url"]
    
    def test_get_google_auth_url_not_configured(self, client):
        """Test getting Google OAuth URL when not configured"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.get("/google/auth-url")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Google OAuth not configured" in data["detail"]
    
    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback_success_new_user(self, mock_get, mock_post, client, db_session):
        """Test successful Google OAuth callback for new user"""
        # Mock token exchange response
        mock_token_response = MagicMock()
        mock_token_response.json.return_value = {
            'access_token': 'test-access-token'
        }
        mock_token_response.raise_for_status.return_value = None
        mock_post.return_value = mock_token_response
        
        # Mock user info response
        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {
            'email': 'newuser@gmail.com',
            'name': 'New Google User'
        }
        mock_user_response.raise_for_status.return_value = None
        mock_get.return_value = mock_user_response
        
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret'
        }):
            response = client.get("/google/callback?code=test-code")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "token" in data
            assert data["email"] == "newuser@gmail.com"
            assert data["name"] == "New Google User"
            assert data["auth_provider"] == "google"
            
            # Check user was created in database
            user = db_session.query(User).filter(User.email == "newuser@gmail.com").first()
            assert user is not None
            assert user.name == "New Google User"
            assert user.auth_provider == AuthProviderEnum.google
            assert user.validated == True
    
    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback_existing_user(self, mock_get, mock_post, client, db_session, test_unit):
        """Test Google OAuth callback for existing user"""
        # Create existing user
        existing_user = User(
            name="Existing User",
            email="existing@gmail.com",
            auth_provider=AuthProviderEnum.google,
            validated=True,
            unit_id=test_unit.id
        )
        db_session.add(existing_user)
        db_session.commit()
        
        # Mock token exchange response
        mock_token_response = MagicMock()
        mock_token_response.json.return_value = {
            'access_token': 'test-access-token'
        }
        mock_token_response.raise_for_status.return_value = None
        mock_post.return_value = mock_token_response
        
        # Mock user info response
        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {
            'email': 'existing@gmail.com',
            'name': 'Updated Name'
        }
        mock_user_response.raise_for_status.return_value = None
        mock_get.return_value = mock_user_response
        
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret'
        }):
            response = client.get("/google/callback?code=test-code")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "token" in data
            assert data["email"] == "existing@gmail.com"
            assert data["auth_provider"] == "google"
    
    def test_google_callback_no_code(self, client):
        """Test Google OAuth callback without code"""
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret'
        }):
            response = client.get("/google/callback")
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Authorization code not provided" in data["detail"]
    
    def test_google_callback_not_configured(self, client):
        """Test Google OAuth callback when not configured"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.get("/google/callback?code=test-code")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Google OAuth not configured" in data["detail"]
    
    @patch('requests.post')
    def test_google_callback_token_exchange_error(self, mock_post, client):
        """Test Google OAuth callback with token exchange error"""
        # Mock failed token exchange
        mock_post.side_effect = Exception("Token exchange failed")
        
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-client-secret'
        }):
            response = client.get("/google/callback?code=test-code")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Google OAuth error" in data["detail"]
