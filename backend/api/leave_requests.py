from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from models.leave_requests import LeaveRequest, StatusEnum, RequestTypeEnum, User
from database import get_db
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Union

# Pydantic models for leave requests
class CreateLeaveRequest(BaseModel):
    """Unified model for both timeoff and permission requests"""
    request_type: RequestTypeEnum
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = None

class UpdateLeaveRequestStatus(BaseModel):
    """Model for updating leave request status (manager only)"""
    status: StatusEnum
    review_comment: Optional[str] = None

router = APIRouter()

@router.get("/leave_requests")
def get_leave_requests(request: Request):
    """Get leave requests based on user role: managers see all, users see only their own"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = next(get_db())
        
        # Filter based on user role
        if user["role"] == "manager":
            # Managers can see all leave requests with user information
            leave_requests = db.query(LeaveRequest, User).join(User, LeaveRequest.user_id == User.id).all()
            message = "All leave requests retrieved (manager view)"
        else:
            # Regular users can only see their own leave requests with user information
            leave_requests = db.query(LeaveRequest, User).join(User, LeaveRequest.user_id == User.id).filter(LeaveRequest.user_id == user["id"]).all()
            message = "Your leave requests retrieved (user view)"
        
        # Convert to dictionary format
        result = []
        for request, user_info in leave_requests:
            result.append({
                "id": request.id,
                "user_id": request.user_id,
                "user_name": user_info.name,
                "user_email": user_info.email,
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
            "message": message,
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
    """Create a new leave request (timeoff or permission) for the authenticated user"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Validate request type and required fields
        if leave_data.request_type == RequestTypeEnum.timeoff:
            if not leave_data.start_date or not leave_data.end_date:
                raise HTTPException(status_code=400, detail="start_date and end_date are required for timeoff requests")
            
            # Validate dates
            if leave_data.start_date >= leave_data.end_date:
                raise HTTPException(status_code=400, detail="End date must be after start date")
            
            if leave_data.start_date < date.today():
                raise HTTPException(status_code=400, detail="Start date cannot be in the past")
                
        elif leave_data.request_type == RequestTypeEnum.permission:
            if not leave_data.start_datetime or not leave_data.end_datetime:
                raise HTTPException(status_code=400, detail="start_datetime and end_datetime are required for permission requests")
            
            # Validate datetimes
            if leave_data.start_datetime >= leave_data.end_datetime:
                raise HTTPException(status_code=400, detail="End datetime must be after start datetime")
            
            if leave_data.start_datetime < datetime.now():
                raise HTTPException(status_code=400, detail="Start datetime cannot be in the past")
        
        db = next(get_db())
        
        # Create new leave request based on type
        if leave_data.request_type == RequestTypeEnum.timeoff:
            new_leave_request = LeaveRequest(
                user_id=user["id"],
                request_type=RequestTypeEnum.timeoff,
                start_date=leave_data.start_date,
                end_date=leave_data.end_date,
                reason=leave_data.reason,
                status=StatusEnum.pending
            )
        else:  # permission
            new_leave_request = LeaveRequest(
                user_id=user["id"],
                request_type=RequestTypeEnum.permission,
                start_datetime=leave_data.start_datetime,
                end_datetime=leave_data.end_datetime,
                reason=leave_data.reason,
                status=StatusEnum.pending
            )
        
        db.add(new_leave_request)
        db.commit()
        db.refresh(new_leave_request)
        
        # Return the created leave request
        response_data = {
            "id": new_leave_request.id,
            "user_id": new_leave_request.user_id,
            "request_type": new_leave_request.request_type,
            "reason": new_leave_request.reason,
            "status": new_leave_request.status,
            "reviewed_by": new_leave_request.reviewed_by,
            "reviewed_at": new_leave_request.reviewed_at.isoformat() if new_leave_request.reviewed_at else None,
            "created_at": new_leave_request.created_at.isoformat(),
            "updated_at": new_leave_request.updated_at.isoformat(),
            "message": f"{leave_data.request_type.title()} request created successfully"
        }
        
        # Add type-specific fields to response
        if leave_data.request_type == RequestTypeEnum.timeoff:
            response_data.update({
                "start_date": new_leave_request.start_date.isoformat(),
                "end_date": new_leave_request.end_date.isoformat()
            })
        else:  # permission
            response_data.update({
                "start_datetime": new_leave_request.start_datetime.isoformat(),
                "end_datetime": new_leave_request.end_datetime.isoformat()
            })
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create leave request: {str(e)}")

@router.put("/leave_requests/{request_id}/status")
def update_leave_request_status(request_id: int, request: Request, status_data: UpdateLeaveRequestStatus):
    """Update leave request status (manager only)"""
    try:
        # Access authenticated user from middleware
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if user is a manager
        if user["role"] != "manager":
            raise HTTPException(status_code=403, detail="Only managers can update leave request status")
        
        db = next(get_db())
        
        # Find the leave request
        leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
        if not leave_request:
            raise HTTPException(status_code=404, detail="Leave request not found")
        
        # Check if request is already processed
        if leave_request.status != StatusEnum.pending:
            raise HTTPException(status_code=400, detail=f"Leave request is already {leave_request.status}")
        
        # Update the status
        leave_request.status = status_data.status
        leave_request.reviewed_by = user["id"]
        leave_request.reviewed_at = datetime.now()
        leave_request.updated_at = datetime.now()
        
        db.commit()
        db.refresh(leave_request)
        
        # Return the updated leave request
        response_data = {
            "id": leave_request.id,
            "user_id": leave_request.user_id,
            "request_type": leave_request.request_type,
            "reason": leave_request.reason,
            "status": leave_request.status,
            "reviewed_by": leave_request.reviewed_by,
            "reviewed_at": leave_request.reviewed_at.isoformat() if leave_request.reviewed_at else None,
            "created_at": leave_request.created_at.isoformat(),
            "updated_at": leave_request.updated_at.isoformat(),
            "message": f"Leave request {status_data.status} successfully"
        }
        
        # Add type-specific fields to response
        if leave_request.request_type == RequestTypeEnum.timeoff:
            response_data.update({
                "start_date": leave_request.start_date.isoformat(),
                "end_date": leave_request.end_date.isoformat()
            })
        else:  # permission
            response_data.update({
                "start_datetime": leave_request.start_datetime.isoformat(),
                "end_datetime": leave_request.end_datetime.isoformat()
            })
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update leave request status: {str(e)}")
