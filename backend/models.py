"""
Database models
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# Import will be done in create_admin_user to avoid circular import

Base = declarative_base()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./documents_calendar.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    from backend.auth import get_password_hash  # Import here to avoid circular dependency
    
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        # If no password is set, use a default (user should change this)
        if not admin_password:
            admin_password = "admin123"  # CHANGE THIS IN PRODUCTION
            print("WARNING: Using default admin password. Set ADMIN_PASSWORD environment variable.")
        
        existing_user = db.query(User).filter(User.username == admin_username).first()
        if not existing_user:
            hashed_password = get_password_hash(admin_password)
            admin_user = User(username=admin_username, hashed_password=hashed_password)
            db.add(admin_user)
            db.commit()
            print(f"Created admin user: {admin_username}")
    finally:
        db.close()

