from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from models.leave_requests import LeaveRequest
from database import get_db

router = APIRouter()

@router.get("/leave_requests")
def get_leave_requests():
    """Get all leave requests from the database"""
    try:
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
        
        return {"leave_requests": result, "count": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
