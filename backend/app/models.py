"""Database models"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Password reset fields
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Session tracking for single login enforcement
    current_session_id = Column(String(255), nullable=True, index=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Session(Base):
    """Session model for tracking active user sessions"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=False, index=True)
    access_token_jti = Column(String(255), nullable=True, index=True)  # JWT ID for token revocation
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, session_id='{self.session_id[:8]}...')>"


class Website(Base):
    """Website model"""
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(500), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="websites")
    scans = relationship("Scan", back_populates="website", cascade="all, delete-orphan")
    
    # Composite unique constraint: same URL can exist for different users
    __table_args__ = (
        UniqueConstraint('user_id', 'url', name='uq_websites_user_url'),
    )
    
    def __repr__(self):
        return f"<Website(id={self.id}, user_id={self.user_id}, url='{self.url}')>"


class Scan(Base):
    """Scan model - represents a security scan of a website"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_type = Column(String(50), nullable=False, index=True)  # 'quick', 'deep', 'both'
    scan_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(String(50), default="completed", nullable=False)  # 'completed', 'failed', 'in_progress'
    error_message = Column(Text, nullable=True)
    
    # Scan results summary
    total_issues = Column(Integer, default=0, nullable=False)
    high_issues = Column(Integer, default=0, nullable=False)
    medium_issues = Column(Integer, default=0, nullable=False)
    low_issues = Column(Integer, default=0, nullable=False)
    security_score = Column(Float, nullable=True)
    
    # OWASP alignment
    owasp_aligned = Column(Boolean, default=True, nullable=False)
    
    # Raw scan data (JSON)
    scan_data = Column(JSON, nullable=True)
    
    # ZAP scan results (JSON)
    zap_results = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    website = relationship("Website", back_populates="scans")
    issues = relationship("Issue", back_populates="scan", cascade="all, delete-orphan")
    security_features = relationship("SecurityFeature", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan(id={self.id}, website_id={self.website_id}, scan_type='{self.scan_type}')>"


class Issue(Base):
    """Security issue model"""
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Issue details
    impact = Column(String(20), nullable=False, index=True)  # 'HIGH', 'MEDIUM', 'LOW'
    issue_type = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(String(50), default="open", nullable=False, index=True)  # 'open', 'resolved', 'ignored'
    reported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    scan = relationship("Scan", back_populates="issues")
    
    def __repr__(self):
        return f"<Issue(id={self.id}, scan_id={self.scan_id}, impact='{self.impact}', type='{self.issue_type}')>"


class SecurityFeature(Base):
    """Security feature implementation tracking"""
    __tablename__ = "security_features"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Feature details
    feature_name = Column(String(255), nullable=False, index=True)
    feature_type = Column(String(100), nullable=False)  # 'header', 'tls', 'cookie', 'owasp'
    is_implemented = Column(Boolean, default=False, nullable=False)
    implementation_details = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    scan = relationship("Scan", back_populates="security_features")
    
    def __repr__(self):
        return f"<SecurityFeature(id={self.id}, scan_id={self.scan_id}, feature='{self.feature_name}', implemented={self.is_implemented})>"

