from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime, date
from typing import List, Optional
import enum

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://timeoff_manager:time_off_manager@host.docker.internal:3306/timeoff_manager_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enum definitions
class StatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class AuthProviderEnum(str, enum.Enum):
    local = "local"
    google = "google"

class RoleEnum(str, enum.Enum):
    user = "user"
    manager = "manager"

# Database models
class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    auth_provider = Column(Enum(AuthProviderEnum), default=AuthProviderEnum.local)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    unit_id = Column(Integer, ForeignKey("units.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Timeoff Manager API")

@app.get("/")
def read_root():
    return {"message": "Timeoff Manager API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/leave_requests")
def get_leave_requests():
    """Get all leave requests from the database"""
    try:
        db = SessionLocal()
        leave_requests = db.query(LeaveRequest).all()
        db.close()
        
        # Convert to dictionary format
        result = []
        for request in leave_requests:
            result.append({
                "id": request.id,
                "user_id": request.user_id,
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None,
                "reason": request.reason,
                "status": request.status,
                "reviewed_by": request.reviewed_by,
                "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
                "created_at": request.created_at.isoformat() if request.created_at else None,
                "updated_at": request.updated_at.isoformat() if request.updated_at else None
            })
        
        return {"leave_requests": result, "count": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")