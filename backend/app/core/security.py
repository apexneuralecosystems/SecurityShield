"""Security utilities for authentication"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.core.config import settings
from app.database import get_db
from app.models import User, Session

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> str:
    """Create a JWT access token with optional JWT ID for revocation"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    if jti:
        to_encode.update({"jti": jti})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str) -> Optional[dict]:
    """Verify and decode a refresh token"""
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def verify_reset_token(token: str, db: Session) -> Optional[User]:
    """Verify a password reset token and return the user if valid"""
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user:
        return None
    
    if not user.reset_token_expires:
        return None
    
    if user.reset_token_expires < datetime.now(timezone.utc):
        return None
    
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token with session validation"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # JWT 'sub' claim is a string, convert to int
        user_id_str = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")
        
        if user_id_str is None or token_type != "access":
            raise credentials_exception
        
        # Convert string to int
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception
    except JWTError as e:
        # Log the error for debugging
        print(f"JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Validate session if JTI is present (for token revocation)
    if jti and user.current_session_id:
        session = db.query(Session).filter(
            Session.session_id == user.current_session_id,
            Session.user_id == user.id,
            Session.is_active == True,
            Session.access_token_jti == jti
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalidated. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session expired
        if session.expires_at < datetime.now(timezone.utc):
            session.is_active = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        db.commit()
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None. Supports both header and cookie tokens."""
    token = None
    
    # Try to get token from Authorization header first
    try:
        authorization = request.headers.get("Authorization")
        if authorization:
            parts = authorization.split()
            if len(parts) == 2:
                scheme, token = parts
                if scheme.lower() != "bearer":
                    token = None
    except (ValueError, AttributeError, IndexError):
        pass
    
    # If no header token, try to get from cookie
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # JWT 'sub' claim is a string, convert to int
        user_id_str = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id_str is None or token_type != "access":
            return None
        
        # Convert string to int
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None
        
        # Validate session if JTI is present
        jti = payload.get("jti")
        if jti:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.current_session_id:
                session = db.query(Session).filter(
                    Session.session_id == user.current_session_id,
                    Session.user_id == user.id,
                    Session.is_active == True,
                    Session.access_token_jti == jti,
                    Session.expires_at > datetime.now(timezone.utc)
                ).first()
                if not session:
                    return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None
    
    return user

