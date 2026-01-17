"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

from app.database import get_db
from app.models import User, Session
from app.schemas import (
    UserCreate,
    UserLogin,
    User as UserSchema,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    RefreshTokenRequest
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    hash_refresh_token,
    generate_reset_token,
    verify_reset_token,
    get_current_active_user,
    generate_session_id
)
from app.core.config import settings
from app.services.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email.lower(),
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False  # Email verification can be added later
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token, refresh token, and set cookies"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Single login enforcement: Invalidate all existing sessions for this user
    if user.current_session_id:
        # Deactivate all existing sessions
        db.query(Session).filter(
            Session.user_id == user.id,
            Session.is_active == True
        ).update({"is_active": False})
        db.commit()
    
    # Generate new session
    session_id = generate_session_id()
    # JWT 'sub' claim must be a string
    refresh_token = create_refresh_token(data={"sub": str(user.id), "session_id": session_id})
    refresh_token_hash = hash_refresh_token(refresh_token)
    access_token_jti = secrets.token_urlsafe(32)
    
    # Create access token with JTI for revocation
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "session_id": session_id},
        expires_delta=access_token_expires,
        jti=access_token_jti
    )
    
    # Create session record
    session_expires = datetime.now(timezone.utc) + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.client.host if request.client else None
    
    db_session = Session(
        user_id=user.id,
        session_id=session_id,
        refresh_token_hash=refresh_token_hash,
        access_token_jti=access_token_jti,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=session_expires,
        is_active=True
    )
    db.add(db_session)
    
    # Update user's current session
    user.current_session_id = session_id
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    # Set HTTP-only cookies for tokens
    access_token_expires_seconds = int(access_token_expires.total_seconds())
    refresh_token_expires_seconds = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_token_expires_seconds,
        httponly=settings.COOKIE_HTTP_ONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAME_SITE,
        path="/"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_token_expires_seconds,
        httponly=settings.COOKIE_HTTP_ONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAME_SITE,
        path="/"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": access_token_expires_seconds,
        "user": user
    }


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request password reset - generates reset token and sends email"""
    user = db.query(User).filter(User.email == request.email.lower()).first()
    
    # Don't reveal if email exists or not (security best practice)
    if not user:
        return {
            "message": "If the email exists, a password reset link has been sent."
        }
    
    # Rate limiting: Prevent too frequent password reset requests
    # Check if a reset email was sent recently (within last 60 seconds)
    # Only rate limit if token exists AND was created very recently
    if user.reset_token and user.reset_token_expires and user.updated_at:
        try:
            # Get updated_at as timezone-aware datetime
            if user.updated_at.tzinfo is None:
                # Naive datetime - assume UTC
                updated_at_utc = user.updated_at.replace(tzinfo=timezone.utc)
            else:
                updated_at_utc = user.updated_at
            
            # Calculate time since last token update
            now_utc = datetime.now(timezone.utc)
            time_since_update = (now_utc - updated_at_utc).total_seconds()
            
            # Only rate limit if token was created within last 60 seconds
            # AND token is still valid (not expired)
            if time_since_update < 60 and user.reset_token_expires > now_utc:
                remaining_time = int(60 - time_since_update)
                print(f"⏱️  Rate limiting password reset for {user.email}. Last reset was {int(time_since_update)} seconds ago. Wait {remaining_time} more seconds.")
                return {
                    "message": f"If the email exists, a password reset link has been sent. Please wait {remaining_time} seconds before requesting another."
                }
        except Exception as e:
            # If there's an error calculating time, log but don't block
            print(f"⚠️  Error in rate limiting check: {e}. Proceeding with email send.")
    
    # Generate reset token
    reset_token = generate_reset_token()
    reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    
    # Save token to user
    user.reset_token = reset_token
    user.reset_token_expires = reset_token_expires
    db.commit()
    
    # Send password reset email
    email_sent = False
    try:
        email_sent = send_password_reset_email(
            user_email=user.email,
            reset_token=reset_token,
            user_name=user.full_name
        )
        if email_sent:
            print(f"✅ Password reset email successfully sent to {user.email}")
        else:
            print(f"⚠️  Password reset email was not sent to {user.email} (check logs above for details)")
    except Exception as e:
        # Log error but don't reveal to user (security best practice)
        print(f"❌ Exception while sending password reset email to {user.email}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Continue to return success message even if email fails
    
    return {
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    # Verify token and get user
    user = verify_reset_token(request.token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {
        "message": "Password has been reset successfully"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: RefreshTokenRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token (from body or cookie)"""
    # Get refresh token from request body or cookie
    refresh_token_value = request.refresh_token
    if not refresh_token_value:
        refresh_token_value = http_request.cookies.get("refresh_token")
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Verify refresh token
    payload = verify_refresh_token(refresh_token_value)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id_str = payload.get("sub")
    session_id = payload.get("session_id")
    
    if not user_id_str or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Convert string to int
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify session exists and is active
    refresh_token_hash = hash_refresh_token(refresh_token_value)
    session = db.query(Session).filter(
        Session.user_id == user_id,
        Session.session_id == session_id,
        Session.refresh_token_hash == refresh_token_hash,
        Session.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or invalidated"
        )
    
    # Check if session expired
    if session.expires_at < datetime.now(timezone.utc):
        session.is_active = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token with new JTI
    new_access_token_jti = secrets.token_urlsafe(32)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT 'sub' claim must be a string
    new_access_token = create_access_token(
        data={"sub": str(user.id), "session_id": session_id},
        expires_delta=access_token_expires,
        jti=new_access_token_jti
    )
    
    # Update session with new access token JTI
    session.access_token_jti = new_access_token_jti
    session.last_activity = datetime.now(timezone.utc)
    db.commit()
    
    # Set new access token cookie
    access_token_expires_seconds = int(access_token_expires.total_seconds())
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=access_token_expires_seconds,
        httponly=settings.COOKIE_HTTP_ONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAME_SITE,
        path="/"
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token_value,  # Refresh token remains the same
        "token_type": "bearer",
        "expires_in": access_token_expires_seconds,
        "user": user
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate session"""
    # Get session ID from token (from header or cookie)
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
    else:
        token = request.cookies.get("access_token")
    
    if token:
        try:
            from jose import jwt
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            session_id = payload.get("session_id")
            jti = payload.get("jti")
            # Note: user_id from payload is already validated by get_current_active_user
            
            if session_id:
                # Deactivate session
                db.query(Session).filter(
                    Session.session_id == session_id,
                    Session.user_id == current_user.id
                ).update({"is_active": False})
                
                # Clear user's current session if it matches
                if current_user.current_session_id == session_id:
                    current_user.current_session_id = None
            elif jti:
                # Deactivate session by JTI
                db.query(Session).filter(
                    Session.access_token_jti == jti,
                    Session.user_id == current_user.id
                ).update({"is_active": False})
        except Exception:
            pass  # Token might be invalid, but we still want to clear cookies
    
    db.commit()
    
    # Clear cookies with same settings as when they were set
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite=settings.COOKIE_SAME_SITE,
        secure=settings.COOKIE_SECURE,
        httponly=settings.COOKIE_HTTP_ONLY
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite=settings.COOKIE_SAME_SITE,
        secure=settings.COOKIE_SECURE,
        httponly=settings.COOKIE_HTTP_ONLY
    )
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return current_user

