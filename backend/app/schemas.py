"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Website Schemas
class WebsiteBase(BaseModel):
    url: str = Field(..., description="Website URL to scan")
    name: Optional[str] = Field(None, description="Friendly name for the website")
    description: Optional[str] = Field(None, description="Description of the website")


class WebsiteCreate(WebsiteBase):
    pass


class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Website(WebsiteBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Issue Schemas
class IssueBase(BaseModel):
    impact: str
    issue_type: str
    description: str


class IssueCreate(IssueBase):
    scan_id: int
    status: str = "open"


class IssueUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None


class Issue(IssueBase):
    id: int
    scan_id: int
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ZAP Scan Result Schemas
class ZapScanSummary(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0


class ZapAlert(BaseModel):
    risk: str
    risk_lower: str
    name: str
    description: str
    solution: Optional[str] = None
    url: Optional[str] = None
    parameter: Optional[str] = None
    evidence: Optional[str] = None


class ZapScanResult(BaseModel):
    success: bool
    error: Optional[str] = None
    total_alerts: int = 0
    summary: ZapScanSummary = ZapScanSummary()
    alerts: List[ZapAlert] = []
    scan_time: Optional[str] = None


# Scan Schemas
class ScanBase(BaseModel):
    scan_type: str = Field(..., description="Type of scan: 'quick' (HTTPS/headers only) or 'deep' (includes OWASP ZAP)")
    website_id: int
    
    @field_validator('scan_type')
    @classmethod
    def validate_scan_type(cls, v):
        allowed_types = ['quick', 'deep']
        if v not in allowed_types:
            raise ValueError(f"scan_type must be one of {allowed_types}")
        return v


class ScanCreate(ScanBase):
    pass


class Scan(ScanBase):
    id: int
    scan_time: datetime
    status: str
    error_message: Optional[str] = None
    total_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    security_score: Optional[float] = None
    owasp_aligned: bool
    scan_data: Optional[Dict[str, Any]] = None
    zap_results: Optional[ZapScanResult] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanWithIssues(Scan):
    issues: List[Issue] = []
    website: Optional[Website] = None


# Security Feature Schemas
class SecurityFeatureBase(BaseModel):
    feature_name: str
    feature_type: str
    is_implemented: bool
    implementation_details: Optional[str] = None


class SecurityFeatureCreate(SecurityFeatureBase):
    scan_id: int


class SecurityFeature(SecurityFeatureBase):
    id: int
    scan_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Summary Schemas
class SecuritySummary(BaseModel):
    total_websites: int
    active_websites: int
    secure_websites: int
    security_score: float
    total_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    last_scan_time: Optional[datetime] = None


class LandingPageData(BaseModel):
    last_updated: datetime
    summary: SecuritySummary
    security_features: Dict[str, bool]
    websites: List[Dict[str, Any]]


# Authentication Schemas
class UserBase(BaseModel):
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserLogin(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds
    user: User


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to get new access token")


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Email address to send reset link")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class PasswordResetResponse(BaseModel):
    message: str


# Demo Scan Schemas (Public, no auth required)
class DemoScanRequest(BaseModel):
    url: str = Field(..., description="Website URL to scan (demo)")


class DemoScanResponse(BaseModel):
    scan_time: datetime
    status: str
    error_message: Optional[str] = None
    total_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    security_score: Optional[float] = None
    owasp_aligned: bool
    issues: List[Dict[str, Any]] = []
    scan_type: str = "quick"
    is_demo: bool = True

