"""
Authentication and authorization logic
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from backend.models import User, get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Support fallback simple hash for compatibility
    if hashed_password.startswith("sha256$"):
        import hashlib
        stored_hash = hashed_password.replace("sha256$", "")
        computed_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return stored_hash == computed_hash
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        
        # If no users exist and trying to login as admin, create admin user (lazy initialization)
        if not user and username == os.getenv("ADMIN_USERNAME", "admin"):
            db.close()
            try:
                from backend.models import create_admin_user
                create_admin_user()
                db = next(get_db())
                user = db.query(User).filter(User.username == username).first()
            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.close()
                return None
        
        if not user:
            db.close()
            return None
        
        # Verify password
        password_valid = verify_password(password, user.hashed_password)
        db.close()
        
        if not password_valid:
            return None
        return user
    except Exception as e:
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"username": username}

def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user"""
    db = next(get_db())
    user = db.query(User).filter(User.username == token_data["username"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return {"username": user.username, "id": user.id}

