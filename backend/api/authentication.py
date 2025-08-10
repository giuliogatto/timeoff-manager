from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.leave_requests import User
from database import get_db
from pydantic import BaseModel
import bcrypt
import jwt
import os
import secrets
import requests
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# Pydantic models for request/response
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class RegisterConfirmRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    token: str
    user_id: int
    email: str
    name: str

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Brevo Configuration
BREVO_TOKEN = os.getenv("BREVO_TOKEN")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# Store confirmation tokens (in production, use Redis or database)
confirmation_tokens = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def send_confirmation_email(email: str, name: str, token: str):
    """Send confirmation email using Brevo API"""
    if not BREVO_TOKEN:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    confirmation_url = f"http://localhost:8000/register_confirm?token={token}"
    
    payload = {
        "sender": {
            "name": "Timeoff Manager",
            "email": "noreply@timeoffmanager.com"
        },
        "to": [
            {
                "email": email,
                "name": name
            }
        ],
        "subject": "Confirm your Timeoff Manager account",
        "htmlContent": f"""
        <html>
            <body>
                <h2>Welcome to Timeoff Manager!</h2>
                <p>Hi {name},</p>
                <p>Thank you for registering with Timeoff Manager. Please click the link below to confirm your account:</p>
                <p><a href="{confirmation_url}">Confirm Account</a></p>
                <p>If you didn't create this account, you can safely ignore this email.</p>
                <p>Best regards,<br>Timeoff Manager Team</p>
            </body>
        </html>
        """
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_TOKEN
    }
    
    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send confirmation email: {str(e)}")

@router.post("/login", response_model=AuthResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - authenticate user and return JWT token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is validated
        if not user.validated:
            raise HTTPException(status_code=401, detail="Account not validated. Please check your email for confirmation link.")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            token=access_token,
            user_id=user.id,
            email=user.email,
            name=user.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/register")
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register endpoint - create new user and send confirmation email"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = get_password_hash(register_data.password)
        
        # Create new user (not validated yet)
        new_user = User(
            name=register_data.name,
            email=register_data.email,
            password_hash=hashed_password,
            validated=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate confirmation token
        confirmation_token = secrets.token_urlsafe(32)
        confirmation_tokens[confirmation_token] = new_user.id
        
        # Send confirmation email
        send_confirmation_email(register_data.email, register_data.name, confirmation_token)
        
        return {
            "message": "Registration successful. Please check your email to confirm your account.",
            "user_id": new_user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.post("/register_confirm")
def register_confirm(confirm_data: RegisterConfirmRequest, db: Session = Depends(get_db)):
    """Register confirmation endpoint - validate user account"""
    try:
        # Check if token exists
        if confirm_data.token not in confirmation_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired confirmation token")
        
        user_id = confirmation_tokens[confirm_data.token]
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already validated
        if user.validated:
            raise HTTPException(status_code=400, detail="Account already validated")
        
        # Validate user
        user.validated = True
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Remove token from storage
        del confirmation_tokens[confirm_data.token]
        
        return {
            "message": "Account confirmed successfully. You can now login.",
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Confirmation error: {str(e)}")
