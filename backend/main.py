from fastapi import FastAPI
from api.leave_requests import router as leave_requests_router
from api.authentication import router as auth_router

app = FastAPI(title="Timeoff Manager API")

# Include routers
app.include_router(leave_requests_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Timeoff Manager API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}