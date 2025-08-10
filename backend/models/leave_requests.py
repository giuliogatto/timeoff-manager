from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Enum definitions
class StatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class RequestTypeEnum(str, enum.Enum):
    timeoff = "timeoff"      # Day-based leave
    permission = "permission" # Hour-based leave

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
    validated = Column(Boolean, default=False)
    confirmation_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_type = Column(Enum(RequestTypeEnum), nullable=False)
    
    # For timeoff (day-based): start_date and end_date
    # For permission (hour-based): start_datetime and end_datetime
    start_date = Column(Date, nullable=True)  # For timeoff
    end_date = Column(Date, nullable=True)    # For timeoff
    start_datetime = Column(DateTime, nullable=True)  # For permission
    end_datetime = Column(DateTime, nullable=True)    # For permission
    
    reason = Column(Text)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
