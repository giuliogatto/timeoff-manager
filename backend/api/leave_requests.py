from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from models.leave_requests import LeaveRequest, StatusEnum
from database import get_db
from pydantic import BaseModel
from datetime import date
from typing import Optional

# Pydantic model for creating leave requests
class CreateLeaveRequest(BaseModel):
    start_date: date
    end_date: date
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
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None,
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

@router.post("/leave_requests")
def create_leave_request(request: Request, leave_data: CreateLeaveRequest):
    """Create a new leave request for the authenticated user"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate dates
        if leave_data.start_date >= leave_data.end_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if leave_data.start_date < date.today():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")
        
        db = next(get_db())
        
        # Create new leave request
        new_leave_request = LeaveRequest(
            user_id=user["id"],
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            reason=leave_data.reason,
            status=StatusEnum.pending
        )
        
        db.add(new_leave_request)
        db.commit()
        db.refresh(new_leave_request)
        
        # Return the created leave request
        return {
            "id": new_leave_request.id,
            "user_id": new_leave_request.user_id,
            "start_date": new_leave_request.start_date.isoformat(),
            "end_date": new_leave_request.end_date.isoformat(),
            "reason": new_leave_request.reason,
            "status": new_leave_request.status,
            "reviewed_by": new_leave_request.reviewed_by,
            "reviewed_at": new_leave_request.reviewed_at.isoformat() if new_leave_request.reviewed_at else None,
            "created_at": new_leave_request.created_at.isoformat(),
            "updated_at": new_leave_request.updated_at.isoformat(),
            "message": "Leave request created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create leave request: {str(e)}")
