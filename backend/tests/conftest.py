import pytest
import os
import sys
from fastapi.testclient import TestClient
from fastapi import Request
from starlette.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import jwt

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db
from models.leave_requests import Base, User, Unit, LeaveRequest
from api.authentication import create_access_token
import bcrypt

# JWT Configuration for tests
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Override the middleware to use the test database
    from middleware.auth import AuthMiddleware
    
    class TestAuthMiddleware(AuthMiddleware):
        def __init__(self, app, db_session):
            super().__init__(app)
            self.db_session = db_session
        
        async def dispatch(self, request: Request, call_next):
            # Allow OPTIONS requests (CORS preflight) without authentication
            if request.method == "OPTIONS":
                request.state.user = None
                return await call_next(request)
            
            # Check if the route is public
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
                
                # Use the test database session instead of creating a new one
                user = self.db_session.query(User).filter(User.id == user_id, User.email == email).first()
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
    
    # Create a new app instance for testing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    test_app = FastAPI(title="Timeoff Manager API Test")
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add test auth middleware
    test_app.add_middleware(TestAuthMiddleware, db_session=db_session)
    
    # Override the database dependency for the test app
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Include routers
    from api.leave_requests import router as leave_requests_router
    from api.authentication import router as auth_router
    from api.profile import router as profile_router
    from api.google_oauth import router as google_oauth_router
    from api.websocket import router as websocket_router
    
    test_app.include_router(leave_requests_router)
    test_app.include_router(auth_router)
    test_app.include_router(profile_router)
    test_app.include_router(google_oauth_router)
    test_app.include_router(websocket_router)
    
    @test_app.get("/")
    def read_root():
        return {"message": "Timeoff Manager API is running!"}
    
    @test_app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
def test_unit(db_session):
    """Create a test unit"""
    unit = Unit(name="Test Unit")
    db_session.add(unit)
    db_session.commit()
    db_session.refresh(unit)
    return unit

@pytest.fixture
def test_user(db_session, test_unit):
    """Create a test user"""
    password_hash = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=password_hash,
        role="user",
        unit_id=test_unit.id,
        validated=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_manager(db_session, test_unit):
    """Create a test manager"""
    password_hash = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    manager = User(
        name="Test Manager",
        email="manager@example.com",
        password_hash=password_hash,
        role="manager",
        unit_id=test_unit.id,
        validated=True
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for a test user"""
    token = create_access_token(
        data={"sub": test_user.email, "user_id": test_user.id},
        expires_delta=None
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def manager_headers(test_manager):
    """Create authentication headers for a test manager"""
    token = create_access_token(
        data={"sub": test_manager.email, "user_id": test_manager.id},
        expires_delta=None
    )
    return {"Authorization": f"Bearer {token}"}
