from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/profile")
def get_current_user_profile(request: Request):
    """Get current authenticated user profile information"""
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
