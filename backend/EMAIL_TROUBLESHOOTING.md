# Password Reset Email Troubleshooting Guide

## Quick Checks

### 1. Check Backend Logs
When you request a password reset, check your terminal/console where the FastAPI server is running. You should see detailed logs like:

```
📧 Attempting to send password reset email:
   From: hello@apexneural.com
   To: user@example.com
   Frontend URL: http://localhost:3000
   API Key: SET (length: 68)
✅ Password reset email sent successfully to user@example.com
```

### 2. Verify Environment Variables

Check that your `.env` file contains:
```bash
SEND_GRID_API=SG.your_api_key_here
FROM_EMAIL=hello@apexneural.com
FRONTEND_URL=http://localhost:3000
```

### 3. Common Issues

#### Issue: "SendGrid API key not configured"
**Solution:**
- Ensure `.env` file exists in the `backend` directory
- Check that `SEND_GRID_API` or `SENDGRID_API_KEY` is set
- Verify the API key starts with `SG.` and is the full key
- Restart your FastAPI server after changing `.env`

#### Issue: "Failed to send password reset email. Status code: 401"
**Solution:**
- Invalid SendGrid API key
- Regenerate API key in SendGrid dashboard
- Make sure you're using the correct API key with "Mail Send" permissions

#### Issue: "Failed to send password reset email. Status code: 403"
**Solution:**
- The `FROM_EMAIL` (hello@apexneural.com) is not verified in SendGrid
- Go to SendGrid → Settings → Sender Authentication
- Verify the sender email address or domain

#### Issue: "Failed to send password reset email. Status code: 400"
**Solution:**
- Check the email addresses are valid format
- Ensure the "from" email is verified in SendGrid
- Check SendGrid response body in logs for specific error

### 4. Verify SendGrid Setup

1. **API Key:**
   - Go to SendGrid → Settings → API Keys
   - Create a new API key with "Mail Send" permissions
   - Copy the full key (starts with `SG.`)

2. **Sender Verification:**
   - Go to SendGrid → Settings → Sender Authentication
   - Verify "hello@apexneural.com" as a single sender
   - OR verify your domain "apexneural.com"

3. **Test Email:**
   - Try sending a test email from SendGrid dashboard
   - Verify it arrives in your inbox

### 5. Check Backend Logs for Errors

Look for these log messages:

**Success:**
```
✅ Password reset email sent successfully to user@example.com
```

**Configuration Error:**
```
⚠️  SendGrid API key not configured...
⚠️  FRONTEND_URL not configured...
```

**SendGrid API Error:**
```
⚠️  Failed to send password reset email. Status code: XXX
Response body: {...}
```

**Exception Error:**
```
❌ Error sending password reset email...
Error type: ...
Error message: ...
```

### 6. Debugging Steps

1. **Check .env file exists:**
   ```bash
   cd backend
   ls -la .env
   ```

2. **Verify variables are loaded:**
   Check server logs on startup - should not show "SendGrid API key not configured"

3. **Test email function directly:**
   Add this temporary endpoint to test:
   ```python
   @router.post("/test-email")
   def test_email(db: Session = Depends(get_db)):
       from app.services.email import send_password_reset_email
       result = send_password_reset_email(
           user_email="your-email@example.com",
           reset_token="test-token-123",
           user_name="Test User"
       )
       return {"success": result}
   ```

4. **Check SendGrid Activity:**
   - Go to SendGrid → Activity Feed
   - Look for email attempts and any failures
   - Check for error messages

### 7. Common SendGrid Errors

| Status Code | Meaning | Solution |
|------------|---------|----------|
| 401 | Unauthorized | Check API key is correct |
| 403 | Forbidden | Verify sender email/domain |
| 400 | Bad Request | Check email format, message content |
| 413 | Payload Too Large | Email content too large |
| 429 | Too Many Requests | Rate limited - wait before retry |

## Still Not Working?

1. Check backend terminal/console logs for detailed error messages
2. Verify SendGrid account status (not suspended)
3. Check SendGrid Activity Feed for delivery attempts
4. Ensure `.env` file is in `backend` directory (not root)
5. Restart FastAPI server after changing `.env`

