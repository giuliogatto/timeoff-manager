from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models.leave_requests import User, AuthProviderEnum
from database import get_db
from pydantic import BaseModel
import os
import jwt
import requests
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

router = APIRouter()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class GoogleAuthResponse(BaseModel):
    token: str
    user_id: int
    email: str
    name: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/google/auth-url")
def get_google_auth_url(request: Request):
    """Get Google OAuth URL for frontend integration"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = f"{request.base_url}google/callback"
    scope = "openid email profile"
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline'
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return {"auth_url": auth_url}

@router.get("/google/callback")
def google_callback(code: str, request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{request.base_url}google/callback"
        
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Get user info using access token
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user with Google auth
            user = User(
                name=name,
                email=email,
                auth_provider=AuthProviderEnum.google,
                validated=True,  # Google users are pre-validated
                password_hash=None  # No password for Google users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user's auth provider if needed
            if user.auth_provider != AuthProviderEnum.google:
                user.auth_provider = AuthProviderEnum.google
                user.validated = True
                db.commit()
                db.refresh(user)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}&user_id={user.id}&email={user.email}&name={user.name}"
        
        return RedirectResponse(url=redirect_url)
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")
