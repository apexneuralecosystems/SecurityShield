# Authentication System Setup Guide

## Overview

A complete authentication system has been implemented with:
- ✅ User registration (signup)
- ✅ User login with JWT tokens
- ✅ Forgot password functionality
- ✅ Password reset with secure tokens
- ✅ Token expiration handling
- ✅ Protected routes
- ✅ Password hashing with bcrypt

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

New dependencies added:
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing

### 2. Configure Environment Variables

Update your `.env` file with:

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
RESET_TOKEN_EXPIRE_HOURS=1  # 1 hour

# Database (if not already set)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/security
```

**Important**: Change `SECRET_KEY` to a secure random string in production (minimum 32 characters).

### 3. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This will create the `users` table with the following fields:
- `id` - Primary key
- `email` - Unique email address (indexed)
- `hashed_password` - Bcrypt hashed password
- `full_name` - User's full name
- `is_active` - Account status
- `is_verified` - Email verification status (for future use)
- `reset_token` - Password reset token (indexed)
- `reset_token_expires` - Token expiration timestamp
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

### 4. Start the Backend Server

```bash
python run_api.py
# Or: uvicorn app.main:app --reload
```

## Frontend Setup

### 1. Install Dependencies (if needed)

```bash
cd frontend
npm install
```

No new dependencies required - uses existing React Router and Axios.

### 2. Configure API URL

Ensure your `.env` file (or environment) has:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Start the Frontend

```bash
npm run dev
```

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/signup`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-16T18:00:00Z",
  "updated_at": "2026-01-16T18:00:00Z"
}
```

#### POST `/api/v1/auth/login`
Authenticate user and get access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false
  }
}
```

#### POST `/api/v1/auth/forgot-password`
Request password reset.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent."
}
```

**Note**: In production, implement email sending with the reset token link.

#### POST `/api/v1/auth/reset-password`
Reset password using token.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "newsecurepassword123"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully"
}
```

#### GET `/api/v1/auth/me`
Get current authenticated user (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-16T18:00:00Z",
  "updated_at": "2026-01-16T18:00:00Z"
}
```

## Frontend Routes

- `/login` - Login page
- `/signup` - Registration page
- `/forgot-password` - Request password reset
- `/reset-password?token=<token>` - Reset password with token
- `/dashboard` - Protected route (requires authentication)
- `/security` - Protected route (requires authentication)
- `/website/:websiteId` - Protected route (requires authentication)

## Security Features

### Password Security
- Passwords are hashed using bcrypt
- Minimum 8 characters required
- Passwords are never stored in plain text

### Token Security
- JWT tokens with configurable expiration (default: 24 hours)
- Tokens stored in localStorage (consider httpOnly cookies for production)
- Automatic token validation on protected routes
- Automatic logout on token expiration

### Reset Token Security
- Cryptographically secure random tokens (32 bytes, URL-safe)
- Tokens expire after 1 hour (configurable)
- Tokens are single-use (cleared after password reset)
- Tokens are indexed for fast lookup

### Protected Routes
- Dashboard, Security, and Website Details pages require authentication
- Unauthenticated users are redirected to login
- Token is automatically included in API requests

## Usage Flow

### Registration Flow
1. User visits `/signup`
2. Fills in email, name, and password
3. Account is created
4. User is automatically logged in
5. Redirected to `/dashboard`

### Login Flow
1. User visits `/login`
2. Enters email and password
3. Receives JWT token
4. Token stored in localStorage
5. Redirected to `/dashboard`

### Forgot Password Flow
1. User visits `/forgot-password`
2. Enters email address
3. Reset token generated and stored (expires in 1 hour)
4. **TODO**: Email sent with reset link (implement email service)
5. User clicks link: `/reset-password?token=<token>`
6. User enters new password
7. Password updated, token cleared
8. Redirected to login

### Reset Password Flow
1. User receives reset link (via email - to be implemented)
2. Clicks link: `/reset-password?token=<token>`
3. Enters new password
4. Token validated (checks expiration)
5. Password updated
6. Token cleared
7. Redirected to login

## Production Considerations

### 1. Environment Variables
- Set a strong `SECRET_KEY` (use `secrets.token_urlsafe(32)`)
- Use environment-specific database URLs
- Configure email service for password resets

### 2. Email Service
Currently, password reset emails are not sent. To implement:

1. Add email service (SendGrid, AWS SES, etc.)
2. Update `forgot_password` endpoint in `backend/app/api/auth.py`
3. Send email with reset link: `{FRONTEND_URL}/reset-password?token={reset_token}`

### 3. Token Storage
Consider using httpOnly cookies instead of localStorage for better XSS protection.

### 4. Rate Limiting
Add rate limiting to prevent brute force attacks on login endpoints.

### 5. Email Verification
The `is_verified` field is ready for email verification implementation.

## Testing

### Test Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Troubleshooting

### Migration Errors
If migration fails, ensure:
- Database exists and is accessible
- `.env` file has correct `DATABASE_URL`
- All dependencies are installed

### Authentication Errors
- Check token expiration (default 24 hours)
- Verify `SECRET_KEY` is set correctly
- Ensure token is included in Authorization header

### Reset Token Issues
- Tokens expire after 1 hour
- Tokens are single-use
- Ensure token is passed correctly in URL parameter

## Files Modified/Created

### Backend
- `app/models.py` - Added User model
- `app/schemas.py` - Added authentication schemas
- `app/core/config.py` - Added JWT configuration
- `app/core/security.py` - New file: Security utilities
- `app/api/auth.py` - New file: Authentication routes
- `app/main.py` - Added auth router
- `requirements.txt` - Added auth dependencies
- `alembic/env.py` - Updated to include User model
- `alembic/versions/002_add_users_table.py` - New migration

### Frontend
- `src/services/api.js` - Added authAPI and token handling
- `src/pages/Login.jsx` - Connected to backend
- `src/pages/Signup.jsx` - Connected to backend
- `src/pages/ForgotPassword.jsx` - New file
- `src/pages/ResetPassword.jsx` - New file
- `src/pages/Auth.css` - Added success message styles
- `src/components/Layout.jsx` - Added logout functionality
- `src/components/Layout.css` - Added logout button styles
- `src/App.jsx` - Added protected routes and auth routes

