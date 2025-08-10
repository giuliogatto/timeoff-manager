from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from models.leave_requests import LeaveRequest
from database import get_db

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

@router.get("/me")
def get_current_user(request: Request):
    """Get current authenticated user information"""
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "unit_id": user["unit_id"]
    }
