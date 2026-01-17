"""Application configuration"""
import os
from typing import Optional


class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/security"
    )
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Advanced Security Platform"
    VERSION: str = "1.0.0"
    
    # Security
    SECURITY_CONTACT_EMAIL: Optional[str] = os.getenv("SECURITY_CONTACT_EMAIL", "security@yourdomain.com")
    SECURITY_POLICY_URL: Optional[str] = os.getenv("SECURITY_POLICY_URL", "")
    
    # Frontend URL (for password reset links, etc.)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Alerting
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    # Support both SEND_GRID_API and SENDGRID_API_KEY for backward compatibility
    SENDGRID_API_KEY: Optional[str] = os.getenv("SEND_GRID_API") or os.getenv("SENDGRID_API_KEY")
    ALERT_EMAIL_FROM: Optional[str] = os.getenv("ALERT_EMAIL_FROM")
    ALERT_EMAIL_TO: Optional[str] = os.getenv("ALERT_EMAIL_TO")
    
    # Password Reset Email - Support both FROM_EMAIL and PASSWORD_RESET_EMAIL_FROM
    PASSWORD_RESET_EMAIL_FROM: str = os.getenv("FROM_EMAIL") or os.getenv("PASSWORD_RESET_EMAIL_FROM") or "hello@apexneural.com"
    
    # OWASP ZAP
    ZAP_URL: str = os.getenv("ZAP_URL", "http://localhost:8080")
    ZAP_API_KEY: Optional[str] = os.getenv("ZAP_API_KEY")
    ZAP_ENABLED: bool = os.getenv("ZAP_ENABLED", "false").lower() == "true"
    ZAP_TIMEOUT: int = int(os.getenv("ZAP_TIMEOUT", "300"))  # 5 minutes default
    ZAP_SPIDER_MAX_DURATION: int = int(os.getenv("ZAP_SPIDER_MAX_DURATION", "2"))  # 2 minutes default
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 days
    RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("RESET_TOKEN_EXPIRE_HOURS", "1"))  # 1 hour
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "168"))  # 7 days
    
    # Cookie settings
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # Set to True in production with HTTPS
    COOKIE_HTTP_ONLY: bool = True
    COOKIE_SAME_SITE: str = os.getenv("COOKIE_SAME_SITE", "lax")  # lax, strict, none


settings = Settings()

