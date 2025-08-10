from fastapi import FastAPI
from api.leave_requests import router as leave_requests_router
from api.authentication import router as auth_router
from api.profile import router as profile_router
from middleware.auth import AuthMiddleware

app = FastAPI(title="Timeoff Manager API")

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(leave_requests_router)
app.include_router(auth_router)
app.include_router(profile_router)

@app.get("/")
def read_root():
    return {"message": "Timeoff Manager API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}