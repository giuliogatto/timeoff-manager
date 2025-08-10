from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://timeoff_manager:time_off_manager@host.docker.internal:3306/timeoff_manager_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
