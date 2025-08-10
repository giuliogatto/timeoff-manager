from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import jwt
import os
from database import SessionLocal
from models.leave_requests import User

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/",
    "/health",
    "/login",
    "/register", 
    "/register_confirm",
    "/google/login",
    "/google/callback",
    "/google/auth-url",
    "/ws/status",
    "/docs",
    "/redoc",
    "/openapi.json"
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS requests (CORS preflight) without authentication
        if request.method == "OPTIONS":
            request.state.user = None
            return await call_next(request)
        
        # Check if the route is public
        if request.url.path in PUBLIC_ROUTES:
            request.state.user = None
            return await call_next(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing"}
            )
        
        # Check if it's a Bearer token
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization header format"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify and decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            email = payload.get("sub")
            
            if user_id is None or email is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token payload"}
                )
            
            # Get user from database to ensure they still exist and are validated
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id, User.email == email).first()
                if not user:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "User not found"}
                    )
                
                if not user.validated:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Account not validated"}
                    )
                
                # Store user info in request state
                request.state.user = {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "unit_id": user.unit_id
                }
                
            finally:
                db.close()
                
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        return await call_next(request)
