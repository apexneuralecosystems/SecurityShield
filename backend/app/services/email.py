"""Email service for authentication and notifications"""
import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings


def send_password_reset_email(user_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
    """
    Send password reset email using SendGrid
    
    Args:
        user_email: Recipient email address
        reset_token: Password reset token
        user_name: Optional user name for personalization
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Support both SEND_GRID_API and SENDGRID_API_KEY for backward compatibility
    api_key = os.getenv("SEND_GRID_API") or os.getenv("SENDGRID_API_KEY") or settings.SENDGRID_API_KEY
    # Support both FROM_EMAIL and PASSWORD_RESET_EMAIL_FROM for backward compatibility
    sender_email = os.getenv("FROM_EMAIL") or os.getenv("PASSWORD_RESET_EMAIL_FROM") or settings.PASSWORD_RESET_EMAIL_FROM or "hello@apexneural.com"
    frontend_url = os.getenv("FRONTEND_URL") or settings.FRONTEND_URL
    
    if not api_key:
        print("⚠️  SendGrid API key not configured. Password reset email not sent.")
        print(f"   Checking env vars: SEND_GRID_API={bool(os.getenv('SEND_GRID_API'))}, SENDGRID_API_KEY={bool(os.getenv('SENDGRID_API_KEY'))}")
        print(f"   Settings.SENDGRID_API_KEY={bool(settings.SENDGRID_API_KEY)}")
        return False
    
    if not frontend_url:
        print("⚠️  FRONTEND_URL not configured. Password reset email not sent.")
        print(f"   Checking env vars: FRONTEND_URL={os.getenv('FRONTEND_URL', 'NOT SET')}")
        print(f"   Settings.FRONTEND_URL={settings.FRONTEND_URL}")
        return False
    
    # Log configuration (without exposing sensitive data)
    print(f"📧 Attempting to send password reset email:")
    print(f"   From: {sender_email}")
    print(f"   To: {user_email}")
    print(f"   Frontend URL: {frontend_url}")
    print(f"   API Key: {'SET' if api_key else 'NOT SET'} (length: {len(api_key) if api_key else 0})")
    
    # Construct reset URL with token
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    
    # Personalize greeting
    greeting = f"Hi {user_name}," if user_name else "Hi,"
    
    # HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 30px; margin: 20px 0;">
            <h1 style="color: #2c3e50; margin-top: 0;">Password Reset Request</h1>
            <p>{greeting}</p>
            <p>We received a request to reset your password for your ShieldOps account.</p>
            <p>Click the button below to reset your password. This link will expire in {settings.RESET_TOKEN_EXPIRE_HOURS} hour(s).</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #007bff; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Reset Password</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="background-color: #e9ecef; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px; color: #495057;">{reset_url}</p>
            <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
            <p style="color: #6c757d; font-size: 12px; margin: 0;">This is an automated message from ShieldOps Security Platform. Please do not reply to this email.</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text content (for email clients that don't support HTML)
    plain_text_content = f"""
Password Reset Request

{greeting}

We received a request to reset your password for your ShieldOps account.

Click the following link to reset your password. This link will expire in {settings.RESET_TOKEN_EXPIRE_HOURS} hour(s).

{reset_url}

If you didn't request this password reset, please ignore this email or contact support if you have concerns.

---
This is an automated message from ShieldOps Security Platform. Please do not reply to this email.
"""
    
    message = Mail(
        from_email=sender_email,
        to_emails=user_email,
        subject="🔐 ShieldOps Password Reset Request",
        plain_text_content=plain_text_content,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        # Check response status
        if response.status_code >= 200 and response.status_code < 300:
            print(f"✅ Password reset email sent successfully to {user_email}")
            return True
        else:
            # Log response details for debugging
            response_body = response.body.decode('utf-8') if response.body else "No response body"
            print(f"⚠️  Failed to send password reset email. Status code: {response.status_code}")
            print(f"Response body: {response_body}")
            print(f"Response headers: {dict(response.headers) if hasattr(response, 'headers') else 'N/A'}")
            return False
    except Exception as e:
        # Log detailed error information
        error_type = type(e).__name__
        error_message = str(e)
        print(f"❌ Error sending password reset email to {user_email}")
        print(f"Error type: {error_type}")
        print(f"Error message: {error_message}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

