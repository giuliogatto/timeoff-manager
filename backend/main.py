from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.leave_requests import router as leave_requests_router
from api.authentication import router as auth_router
from api.profile import router as profile_router
from api.google_oauth import router as google_oauth_router
from api.websocket import router as websocket_router
from middleware.auth import AuthMiddleware

app = FastAPI(title="Timeoff Manager API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(leave_requests_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(google_oauth_router)
app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"message": "Timeoff Manager API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}