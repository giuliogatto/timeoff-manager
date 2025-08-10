from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from models.leave_requests import LeaveRequest, StatusEnum, RequestTypeEnum
from database import get_db
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Union

# Pydantic models for creating leave requests
class CreateTimeoffRequest(BaseModel):
    """Model for day-based timeoff requests"""
    start_date: date
    end_date: date
    reason: Optional[str] = None

class CreatePermissionRequest(BaseModel):
    """Model for hour-based permission requests"""
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None

router = APIRouter()

@router.get("/leave_requests")
def get_leave_requests(request: Request):
    """Get all leave requests from the database"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = next(get_db())
        leave_requests = db.query(LeaveRequest).all()
        
        # Convert to dictionary format
        result = []
        for request in leave_requests:
            result.append({
                "id": request.id,
                "user_id": request.user_id,
                "request_type": request.request_type,
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None,
                "start_datetime": request.start_datetime.isoformat() if request.start_datetime else None,
                "end_datetime": request.end_datetime.isoformat() if request.end_datetime else None,
                "reason": request.reason,
                "status": request.status,
                "reviewed_by": request.reviewed_by,
                "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
                "created_at": request.created_at.isoformat() if request.created_at else None,
                "updated_at": request.updated_at.isoformat() if request.updated_at else None
            })
        
        return {
            "leave_requests": result, 
            "count": len(result),
            "authenticated_user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/timeoff")
def create_timeoff_request(request: Request, timeoff_data: CreateTimeoffRequest):
    """Create a new timeoff request (day-based) for the authenticated user"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate dates
        if timeoff_data.start_date >= timeoff_data.end_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if timeoff_data.start_date < date.today():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")
        
        db = next(get_db())
        
        # Create new timeoff request
        new_leave_request = LeaveRequest(
            user_id=user["id"],
            request_type=RequestTypeEnum.timeoff,
            start_date=timeoff_data.start_date,
            end_date=timeoff_data.end_date,
            reason=timeoff_data.reason,
            status=StatusEnum.pending
        )
        
        db.add(new_leave_request)
        db.commit()
        db.refresh(new_leave_request)
        
        # Return the created timeoff request
        return {
            "id": new_leave_request.id,
            "user_id": new_leave_request.user_id,
            "request_type": new_leave_request.request_type,
            "start_date": new_leave_request.start_date.isoformat(),
            "end_date": new_leave_request.end_date.isoformat(),
            "reason": new_leave_request.reason,
            "status": new_leave_request.status,
            "reviewed_by": new_leave_request.reviewed_by,
            "reviewed_at": new_leave_request.reviewed_at.isoformat() if new_leave_request.reviewed_at else None,
            "created_at": new_leave_request.created_at.isoformat(),
            "updated_at": new_leave_request.updated_at.isoformat(),
            "message": "Timeoff request created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create timeoff request: {str(e)}")

@router.post("/permission")
def create_permission_request(request: Request, permission_data: CreatePermissionRequest):
    """Create a new permission request (hour-based) for the authenticated user"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate datetimes
        if permission_data.start_datetime >= permission_data.end_datetime:
            raise HTTPException(status_code=400, detail="End datetime must be after start datetime")
        
        if permission_data.start_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Start datetime cannot be in the past")
        
        db = next(get_db())
        
        # Create new permission request
        new_leave_request = LeaveRequest(
            user_id=user["id"],
            request_type=RequestTypeEnum.permission,
            start_datetime=permission_data.start_datetime,
            end_datetime=permission_data.end_datetime,
            reason=permission_data.reason,
            status=StatusEnum.pending
        )
        
        db.add(new_leave_request)
        db.commit()
        db.refresh(new_leave_request)
        
        # Return the created permission request
        return {
            "id": new_leave_request.id,
            "user_id": new_leave_request.user_id,
            "request_type": new_leave_request.request_type,
            "start_datetime": new_leave_request.start_datetime.isoformat(),
            "end_datetime": new_leave_request.end_datetime.isoformat(),
            "reason": new_leave_request.reason,
            "status": new_leave_request.status,
            "reviewed_by": new_leave_request.reviewed_by,
            "reviewed_at": new_leave_request.reviewed_at.isoformat() if new_leave_request.reviewed_at else None,
            "created_at": new_leave_request.created_at.isoformat(),
            "updated_at": new_leave_request.updated_at.isoformat(),
            "message": "Permission request created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create permission request: {str(e)}")
