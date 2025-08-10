import pytest
from fastapi import status
from models.leave_requests import User

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_success(self, client, db_session):
        """Test successful user registration"""
        response = client.post("/register", json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert "Registration successful" in data["message"]
        
        # Check user was created in database
        user = db_session.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.name == "New User"
        assert user.validated == False
        assert user.confirmation_token is not None
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post("/register", json={
            "name": "Another User",
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Email already registered" in data["detail"]
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/login", json={
            "email": test_user.email,
            "password": "testpassword"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        assert "role" in data
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    def test_login_unvalidated_account(self, client, db_session, test_unit):
        """Test login with unvalidated account"""
        # Create unvalidated user
        from models.leave_requests import User
        import bcrypt
        
        password_hash = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        unvalidated_user = User(
            name="Unvalidated User",
            email="unvalidated@example.com",
            password_hash=password_hash,
            role="user",
            unit_id=test_unit.id,
            validated=False
        )
        db_session.add(unvalidated_user)
        db_session.commit()
        
        response = client.post("/login", json={
            "email": unvalidated_user.email,
            "password": "testpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Account not validated" in data["detail"]
    
    def test_register_confirm_success(self, client, db_session, test_unit):
        """Test successful account confirmation"""
        # Create user with confirmation token
        from models.leave_requests import User
        import bcrypt
        
        password_hash = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            name="Confirm User",
            email="confirm@example.com",
            password_hash=password_hash,
            role="user",
            unit_id=test_unit.id,
            validated=False,
            confirmation_token="test-token-123"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/register_confirm", json={
            "token": "test-token-123"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Account confirmed successfully" in data["message"]
        
        # Check user is now validated
        db_session.refresh(user)
        assert user.validated == True
        assert user.confirmation_token is None
    
    def test_register_confirm_invalid_token(self, client):
        """Test confirmation with invalid token"""
        response = client.post("/register_confirm", json={
            "token": "invalid-token"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid or expired confirmation token" in data["detail"]
    
    def test_register_confirm_already_validated(self, client, db_session, test_unit):
        """Test confirmation of already validated account"""
        # Create validated user with confirmation token
        from models.leave_requests import User
        import bcrypt
        
        password_hash = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            name="Validated User",
            email="validated@example.com",
            password_hash=password_hash,
            role="user",
            unit_id=test_unit.id,
            validated=True,
            confirmation_token="test-token-123"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/register_confirm", json={
            "token": "test-token-123"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Account already validated" in data["detail"]
