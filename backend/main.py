from fastapi import FastAPI

app = FastAPI(title="Timeoff Manager API")

@app.get("/")
def read_root():
    return {"message": "Timeoff Manager API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}