# ShieldOps Backend - Advanced Security Platform

## Overview

ShieldOps is an **OWASP Top-10 aligned automated security scanning platform** that provides continuous monitoring, vulnerability detection, and comprehensive security reporting for websites. The backend is built with FastAPI and provides a RESTful API for managing websites, performing security scans, tracking issues, and generating audit-ready reports.

### Key Features

- 🔒 **HTTPS & TLS Encryption Validation** - Enforces HTTPS, validates TLS versions, monitors certificate expiry
- 🛡️ **Secure HTTP Headers Scanning** - Checks for CSP, HSTS, X-Frame-Options, X-Content-Type-Options, and more
- 🔍 **OWASP Top-10 Aligned Scanning** - Automated vulnerability detection aligned with OWASP standards
- 🕷️ **OWASP ZAP Integration** - Deep security scanning with spider crawling and active vulnerability testing (optional)
- 📊 **Continuous Monitoring** - Regular scans with automated alerts for high-priority issues
- 📋 **Audit-Ready Reporting** - Comprehensive security reports with historical scan data
- 👥 **Multi-User Support** - User authentication with JWT tokens, session management, and role-based access
- 🚨 **Automated Alerting** - Slack and email notifications for critical security findings
- 🔐 **Responsible Disclosure** - Built-in security contact and vulnerability reporting support

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│                    (User Interface & Dashboard)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend (Python)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer (app/api/)                                    │  │
│  │  ├── auth.py      - Authentication & Authorization      │  │
│  │  └── routes.py    - Website, Scan, Issue endpoints       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Service Layer (app/services/)                           │  │
│  │  ├── scanner.py   - Security scanning engine             │  │
│  │  ├── alerts.py    - Slack & email notifications          │  │
│  │  └── email.py     - Email service (SendGrid)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Core Layer (app/core/)                                  │  │
│  │  ├── config.py    - Application settings                 │  │
│  │  └── security.py  - JWT, password hashing, tokens        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Layer (app/models.py, app/database.py)            │  │
│  │  ├── User         - User accounts & authentication        │  │
│  │  ├── Session      - Active user sessions                  │  │
│  │  ├── Website      - Monitored websites                    │  │
│  │  ├── Scan         - Security scan records                 │  │
│  │  ├── Issue        - Security vulnerabilities              │  │
│  │  └── SecurityFeature - Security feature tracking         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQLAlchemy ORM
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    PostgreSQL Database                          │
│              (Persistent data storage)                          │
└─────────────────────────────────────────────────────────────────┘

External Services:
  ├── OWASP ZAP (Optional) - Deep security scanning with spider & active scans
  ├── SendGrid - Email delivery
  └── Slack - Alert notifications
```

### Architecture Components

1. **API Layer** (`app/api/`)
   - RESTful endpoints for websites, scans, issues, and authentication
   - Request validation using Pydantic schemas
   - JWT-based authentication and authorization
   - User-scoped data access (users can only access their own websites)

2. **Service Layer** (`app/services/`)
   - **SecurityScanner**: Performs quick security scans (HTTPS, TLS, headers, cookies)
   - **Alert Services**: Sends notifications via Slack and email for high-priority issues
   - **Email Service**: Handles password reset and notification emails

3. **Core Layer** (`app/core/`)
   - Configuration management via environment variables
   - JWT token generation and validation
   - Password hashing and verification
   - Session management with single-login enforcement

4. **Data Layer** (`app/models.py`, `app/database.py`)
   - SQLAlchemy ORM models for database entities
   - Database connection pooling and session management
   - Alembic migrations for schema versioning

5. **Database Schema**
   - **Users**: User accounts with email verification and password reset
   - **Sessions**: Active user sessions with refresh token tracking
   - **Websites**: Monitored websites (user-scoped)
   - **Scans**: Security scan records with results and metadata
   - **Issues**: Individual security vulnerabilities found in scans
   - **SecurityFeatures**: Tracking of implemented security features

## Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast Python web framework with automatic API documentation
- **Uvicorn** - ASGI server for running FastAPI applications
- **Python 3.8+** - Programming language

### Database
- **PostgreSQL 12+** - Relational database for persistent storage
- **SQLAlchemy 2.0+** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool

### Authentication & Security
- **python-jose** - JWT token handling
- **passlib** - Password hashing (bcrypt)
- **python-dotenv** - Environment variable management

### External Services
- **SendGrid** - Email delivery service
- **OWASP ZAP** (Optional) - Deep security scanning tool
  - Integrated via `python-owasp-zap-v2.4` library
  - Supports spider and active scanning
  - Configurable via environment variables
- **Slack** (Optional) - Alert notifications

### Development Tools
- **Docker & Docker Compose** - Containerization and orchestration
- **Pydantic** - Data validation using Python type annotations

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py            # Database connection and session management
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic schemas for API validation
│   ├── api/
│   │   ├── auth.py            # Authentication endpoints (signup, login, password reset)
│   │   └── routes.py         # Main API routes (websites, scans, issues)
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── security.py        # JWT, password hashing, token utilities
│   └── services/
│       ├── scanner.py          # Security scanning engine
│       ├── alerts.py          # Slack and email alerting
│       └── email.py           # Email service (SendGrid)
├── alembic/                   # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── requirements.txt           # Python dependencies
├── env.example                # Environment variables template
├── run_api.py                 # API startup script
└── README.md                  # This file
```

## Quick Start

### Option 1: Docker (Recommended - Easiest)

This will start both PostgreSQL and the API automatically:

```bash
cd backend
docker-compose up
```

The API will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Option 2: Manual Setup

#### Prerequisites

1. **Python 3.8+**
2. **PostgreSQL 12+** (or use Docker for just the database)

#### Step 1: Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Or use Docker for just PostgreSQL:**
```bash
docker run -d \
  --name security_platform_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=security_platform \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE security_platform;

# Exit
\q
```

#### Step 3: Setup Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Setup Environment Variables

Create `.env` file from the example:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your values
# At minimum, update DATABASE_URL if your PostgreSQL credentials differ
```

The `env.example` file contains all available environment variables with descriptions.

#### Step 5: Run Database Migrations

```bash
# Make sure you're in the backend directory
cd backend

# Run migrations (includes ZAP integration schema updates)
alembic upgrade head
```

**Note**: The migration `003_add_zap_results_to_scans` adds the `zap_results` JSON column to the `scans` table for storing OWASP ZAP scan results.

#### Step 6: Run the API

```bash
# Option A: Using the run script
python run_api.py

# Option B: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option C: Using uvicorn with specific app
uvicorn app.main:app --reload
```

The API will start at: `http://localhost:8000`

## Verify It's Working

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Docs:**
   Open in browser: `http://localhost:8000/docs`

3. **Root Endpoint:**
   ```bash
   curl http://localhost:8000/
   ```

## Common Issues

### Database Connection Error

**Error:** `could not connect to server`

**Solution:**
- Make sure PostgreSQL is running
- Check DATABASE_URL in `.env` or environment
- Verify database exists: `psql -U postgres -l`

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Migration Errors

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Check current migration status
alembic current

# Upgrade to latest
alembic upgrade head

# If needed, downgrade and re-upgrade
alembic downgrade -1
alembic upgrade head
```

**Error:** `Multiple head revisions are present`

**Solution:**
This happens when migrations have branched. Check heads and merge:
```bash
# Check all head revisions
alembic heads

# If multiple heads exist, upgrade to all heads
alembic upgrade heads

# Or specify a specific head
alembic upgrade <revision_id>
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
- Make sure you're in the `backend/` directory
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

## Development Mode

For development with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This will automatically restart when you make code changes.

## Production Mode

For production:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

Once running, you can access:

- **API Root:** `http://localhost:8000/`
- **Health Check:** `http://localhost:8000/health`
- **API Docs (Swagger):** `http://localhost:8000/docs`
- **API Docs (ReDoc):** `http://localhost:8000/redoc`
- **API v1:** `http://localhost:8000/api/v1/`

## Testing Endpoints

### Create a Website
```bash
curl -X POST "http://localhost:8000/api/v1/websites" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=your-token" \
  -d '{
    "url": "https://example.com",
    "name": "Example Site"
  }'
```

### Get All Websites
```bash
curl "http://localhost:8000/api/v1/websites" \
  -H "Cookie: access_token=your-token"
```

### Perform Quick Scan
```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=your-token" \
  -d '{
    "website_id": 1,
    "scan_type": "quick"
  }'
```

### Perform Deep Scan (with OWASP ZAP)
```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=your-token" \
  -d '{
    "website_id": 1,
    "scan_type": "deep"
  }'
```

### Check ZAP Status
```bash
curl "http://localhost:8000/api/v1/zap/status" \
  -H "Cookie: access_token=your-token"
```

### Get Security Summary
```bash
curl "http://localhost:8000/api/v1/summary" \
  -H "Cookie: access_token=your-token"
```

### Get Landing Page Data
```bash
curl "http://localhost:8000/api/v1/landing-page-data"
```

## Docker Commands

### Start Services
```bash
docker-compose up
```

### Start in Background
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f api
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Rebuild After Changes
```bash
docker-compose up --build
```

## Next Steps

1. ✅ Backend is running
2. ✅ Database is connected
3. ✅ API endpoints are accessible
4. 🔍 (Optional) Set up OWASP ZAP for deep scanning:
   - Install and start ZAP (see "Deep Scan (OWASP ZAP - Optional)" section)
   - Set `ZAP_ENABLED=true` in `.env`
   - Test with: `curl http://localhost:8000/api/v1/zap/status`
5. 🚀 Start the frontend: `cd ../frontend && npm run dev`

## Troubleshooting

### Check Database Connection
```bash
psql -U postgres -d security_platform -c "SELECT 1;"
```

### Check API Logs
If using Docker:
```bash
docker-compose logs api
```

If running manually, check the terminal output.

### Reset Database (Development Only)
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE security_platform;"
psql -U postgres -c "CREATE DATABASE security_platform;"
alembic upgrade head
```

## API Documentation

### Authentication Endpoints

All authentication endpoints are under `/api/v1/auth/`:

- `POST /api/v1/auth/signup` - Register a new user
- `POST /api/v1/auth/login` - Login and get access/refresh tokens
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `POST /api/v1/auth/forgot-password` - Request password reset email
- `POST /api/v1/auth/reset-password` - Reset password with token
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/logout` - Logout and invalidate session

### Website Management Endpoints

All website endpoints require authentication and are user-scoped:

- `POST /api/v1/websites` - Create a new website
- `GET /api/v1/websites` - Get all websites for current user
- `GET /api/v1/websites/{website_id}` - Get specific website
- `PUT /api/v1/websites/{website_id}` - Update website
- `DELETE /api/v1/websites/{website_id}` - Delete website

### Security Scanning Endpoints

- `POST /api/v1/scans` - Create and perform a security scan
  - `scan_type`: `"quick"` (HTTPS/headers only) or `"deep"` (includes OWASP ZAP)
  - Example: `{"website_id": 1, "scan_type": "deep"}`
- `GET /api/v1/scans` - Get all scans (filtered by user's websites)
- `GET /api/v1/scans/{scan_id}` - Get specific scan with issues
- `GET /api/v1/scans/latest/{website_id}` - Get latest scan for a website
- `GET /api/v1/zap/status` - Check OWASP ZAP scanner availability and status

### Issue Management Endpoints

- `GET /api/v1/issues` - Get all issues (filtered by user's websites)
- `PUT /api/v1/issues/{issue_id}` - Update issue (e.g., mark as resolved)

### Summary & Analytics Endpoints

- `GET /api/v1/summary` - Get security summary for current user
- `GET /api/v1/landing-page-data` - Get data for landing page (public, shows user data if authenticated)

### Public Demo Endpoint

- `POST /api/v1/demo/scan` - Perform a demo scan without authentication (results not saved)

### Interactive API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Security Scanning Features

### Quick Scan (Default)

The quick scan performs the following checks:

1. **HTTPS Enforcement**
   - Verifies site uses HTTPS
   - Checks TLS version (flags TLSv1.0 and TLSv1.1 as HIGH severity)
   - Monitors SSL certificate expiry (HIGH if <7 days, MEDIUM if <30 days)

2. **Security HTTP Headers**
   - Content-Security-Policy (CSP) - HIGH
   - Strict-Transport-Security (HSTS) - HIGH
   - X-Frame-Options - HIGH
   - X-Content-Type-Options - MEDIUM
   - X-XSS-Protection - MEDIUM
   - Referrer-Policy - MEDIUM
   - Permissions-Policy - LOW

3. **Cookie Security**
   - Secure flag validation - MEDIUM
   - HttpOnly flag validation - MEDIUM
   - SameSite attribute validation - LOW

4. **Information Disclosure**
   - Server header disclosure - LOW

### Deep Scan (OWASP ZAP - Optional)

For comprehensive vulnerability scanning, the platform integrates with **OWASP ZAP** (Zed Attack Proxy) to perform deep security analysis.

#### What Deep Scans Include

Deep scans combine the quick scan with OWASP ZAP's comprehensive analysis:

1. **Quick Scan** (always performed)
   - HTTPS/TLS validation
   - Security headers check
   - Cookie security analysis

2. **OWASP ZAP Deep Scan** (when `scan_type="deep"`)
   - **Spider Scan**: Automated web crawling to discover all pages and endpoints
   - **Active Scan**: Automated vulnerability testing using OWASP Top-10 aligned rules
   - **Alert Categorization**: Issues categorized by severity (High/Medium/Low/Informational)
   - **Comprehensive Reporting**: Detailed vulnerability descriptions with solutions

#### Setting Up OWASP ZAP

**Option 1: Using Docker (Recommended - No Java Installation Required)**

This is the easiest method as Docker includes Java:

```bash
# Run ZAP in daemon mode (no API key required)
docker run -d \
  --name zap \
  -p 8080:8080 \
  -i owasp/zap2docker-stable \
  zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true

# Or with API key
docker run -d \
  --name zap \
  -p 8080:8080 \
  -i owasp/zap2docker-stable \
  zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=your-secret-key

# Verify ZAP is running
curl http://localhost:8080/JSON/core/view/version/
```

**Option 2: Manual Installation (Requires Java)**

OWASP ZAP requires **Java 11 or higher** (Java SE 17 LTS or Java SE 21 LTS recommended).

1. **Install Java** (if not already installed):
   
   **macOS:**
   ```bash
   # Using Homebrew
   brew install openjdk@21
   # Or download from: https://www.oracle.com/java/technologies/downloads/
   ```
   
   **Linux:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install openjdk-21-jdk
   
   # Or for Java 17
   sudo apt-get install openjdk-17-jdk
   ```
   
   **Verify Java installation:**
   ```bash
   java -version
   # Should show Java 11, 17, or 21
   ```

2. **Download OWASP ZAP:**
   - Download from: https://www.zaproxy.org/download/
   - Or use the weekly release: https://github.com/zaproxy/zaproxy/releases

3. **Start ZAP in daemon mode:**
   ```bash
   # Navigate to ZAP directory
   cd /path/to/zap
   
   # Start ZAP daemon (no API key)
   ./zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
   
   # Or with API key
   ./zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=your-secret-key
   ```

4. **Verify ZAP is running:**
   ```bash
   curl http://localhost:8080/JSON/core/view/version/
   # Should return ZAP version information
   ```

**Option 1b: Using Docker Compose (with backend)**

Add to your `docker-compose.yml`:

```yaml
services:
  zap:
    image: owasp/zap2docker-stable
    container_name: shieldops_zap
    ports:
      - "8080:8080"
    command: zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
    restart: unless-stopped
```

Then start with: `docker-compose up zap`

#### Configuration

Update your `.env` file:

```bash
# Enable ZAP scanning
ZAP_ENABLED=true

# ZAP API URL (default: http://localhost:8080)
ZAP_URL=http://localhost:8080

# ZAP API Key (optional, only if ZAP authentication is enabled)
ZAP_API_KEY=

# ZAP scan timeout in seconds (default: 300 = 5 minutes)
ZAP_TIMEOUT=300

# ZAP spider maximum duration in minutes (default: 2)
ZAP_SPIDER_MAX_DURATION=2
```

#### Using Deep Scans via API

**Request a Deep Scan:**

```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=your-token" \
  -d '{
    "website_id": 1,
    "scan_type": "deep"
  }'
```

**Response includes both quick and ZAP results:**

```json
{
  "id": 123,
  "website_id": 1,
  "scan_type": "deep",
  "status": "completed",
  "total_issues": 18,
  "high_issues": 3,
  "medium_issues": 7,
  "low_issues": 8,
  "security_score": 65.0,
  "zap_results": {
    "success": true,
    "total_alerts": 15,
    "summary": {
      "high": 2,
      "medium": 5,
      "low": 6,
      "informational": 2
    },
    "alerts": [...]
  }
}
```

**Check ZAP Status:**

```bash
curl "http://localhost:8000/api/v1/zap/status" \
  -H "Cookie: access_token=your-token"
```

**Response:**

```json
{
  "enabled": true,
  "available": true,
  "url": "http://localhost:8080",
  "version": "2.14.0"
}
```

#### Deep Scan Process

1. **Quick Scan**: Performs immediate HTTPS, headers, and cookie checks
2. **Spider Scan**: ZAP crawls the website to discover all pages (configurable duration)
3. **Active Scan**: ZAP performs automated vulnerability testing
4. **Alert Processing**: ZAP alerts are categorized and converted to Issue records
5. **Result Merging**: Quick scan and ZAP results are combined with unified severity counts
6. **Database Storage**: All results stored with ZAP data in `zap_results` JSON field

#### Performance Considerations

- **Quick Scan**: ~5-10 seconds
- **Deep Scan**: 2-5 minutes (depending on site size and ZAP_TIMEOUT)
- Deep scans are asynchronous and may take longer for large websites
- Monitor ZAP status endpoint to ensure ZAP is available before requesting deep scans

#### Quick Start Guide

**1. Start ZAP (Choose one method):**

**Docker (Easiest - No Java Required):**
```bash
docker run -d --name zap -p 8080:8080 -i owasp/zap2docker-stable \
  zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
```

**Manual Installation (Requires Java 11+):**

**Step 1: Download OWASP ZAP**
```bash
# Option A: Download from website
# Visit: https://www.zaproxy.org/download/
# Download the latest stable release for your OS

# Option B: Using Homebrew (macOS)
brew install --cask owasp-zap
# Note: macOS may show a Gatekeeper warning. See troubleshooting section below.

# Option C: Using wget/curl (Linux/macOS)
# Get latest release URL from: https://github.com/zaproxy/zaproxy/releases/latest
wget https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2.14.0_unix.sh
chmod +x ZAP_2.14.0_unix.sh
./ZAP_2.14.0_unix.sh
```

**Step 2: Navigate to ZAP Directory**
```bash
# After installation, ZAP is typically in:
# macOS Homebrew: /Applications/ZAP.app/Contents/Java/
# macOS Manual: /Applications/OWASP\ ZAP.app/Contents/Java/
# Linux: ~/ZAP_2.14.0/ or /opt/zap/

# For macOS Homebrew installation:
cd /Applications/ZAP.app/Contents/Java/

# For macOS manual installation:
cd /Applications/OWASP\ ZAP.app/Contents/Java/

# For Linux/Unix installation:
cd ~/ZAP_2.14.0/  # or wherever you installed it
```

**Step 3: Start ZAP in Daemon Mode**
```bash
# Make sure you're in the ZAP directory
./zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true

# Or with API key (more secure):
./zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=your-secret-key-here
```

**Alternative: Start ZAP from Anywhere**
```bash
# Create an alias or add to PATH
# macOS Homebrew installation:
alias zap-daemon='/Applications/ZAP.app/Contents/Java/zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true'

# macOS Manual installation:
alias zap-daemon='/Applications/OWASP\ ZAP.app/Contents/Java/zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true'

# Then just run:
zap-daemon
```

**Quick Start Command (macOS Homebrew):**
```bash
/Applications/ZAP.app/Contents/Java/zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
```

**2. Verify ZAP is Running:**
```bash
# Check ZAP version (this is the most reliable check)
curl http://localhost:8080/JSON/core/view/version/
# Should return: {"version":"2.x.x"}
# Example: {"version":"2.17.0"}

# Alternative: Check ZAP mode
curl http://localhost:8080/JSON/core/view/mode/
# Should return: {"mode":"daemon"} or {"mode":"standard"}

# If version check works, ZAP is running correctly!
```

**Troubleshooting: "The home directory is already in use"**
ooo
This meaons ZAP is already running or a stale lock file exists. Fix it:

```bash
# 1. Check if ZAP is running on port 8080
lsof -i :8080

# 2. Kill the existing ZAP process
kill -9 <PID>  # Replace <PID> with the process ID from step 1
# Or kioll all Java processes (be careful!):
pkill -f zap

# 3. Remove the lock file
rm "/Users/$USER/Library/Application Support/ZAP/.homelock"

# 4. Start ZAP fresh
/Applications/ZAP.app/Contents/Java/zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
```

**Troubleshooting: "zap.sh: no such file or directory"**

If you get this error, you need to:
1. **Download ZAP first** (see Step 1 above)
2. **Navigate to the ZAP directory** where `zap.sh` is located
3. **Make it executable** (if needed): `chmod +x zap.sh`
4. **Then run the command** from that directory

**Quick Check:**
```bash
# Find where ZAP is installed
which zap.sh  # Usually won't work unless in PATH
find ~ -name "zap.sh" 2>/dev/null  # Search for zap.sh
find /Applications -name "zap.sh" 2>/dev/null  # macOS search
```

**Troubleshooting: Java Not Found**

If you get "Unable to locate a Java Runtime" error:

1. **Verify Java is installed:**
   ```bash
   java -version
   # Should show Java version (11, 17, or 21)
   ```

2. **Set JAVA_HOME (if needed):**
   ```bash
   # Find Java installation
   /usr/libexec/java_home -V
   
   # Set JAVA_HOME for current session
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)  # For Java 21
   # or
   export JAVA_HOME=$(/usr/libexec/java_home -v 17)  # For Java 17
   iiii
   # Add to ~iiiiiiiii/.zshrc or ~/.bash_profile for permanent:
   echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 21)' >> ~/.zshrc
   source ~/i.zshrc
   ```9iiiii

3. **Start ZAP with explicit Java path:**
   ```bash
   # If Java is installed but not found, specify it explicitly
   JAVA_HOME=$(/usr/libexec/java_home -v 21) \
     /Applications/ZAP.app/Contents/Java/zap.sh \
     -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
   ```

4. **Install Java if missing:**
   ```bash
   # macOS using Homebrew
   brew install openjdk@21
   # or
   brew install openjdk@17
   ```

**Troubleshooting: macOS Gatekeeper Warning**

If you see: *"Apple could not verify 'ZAP' is free of malware"*

This is a macOS security feature. Here's how to allow ZAP:

**Method 1: Right-Click Open (Easiest)**
1. Go to `/Applications/` in Finder
2. **Right-click** on `ZAP.app`
3. Select **"Open"** from the context menu
4. Click **"Open"** in the security dialog
5. This allows ZAP to run (you only need to do this once)

**Method 2: Remove Quarantine Attribute (Command Line)**
```bash
# Remove the quarantine attribute that macOS adds to downloaded apps
sudo xattr -rd com.apple.quarantine /Applications/ZAP.app

# Then you can run ZAP normally
/Applications/ZAP.app/Contents/Java/zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
```

**Method 3: System Settings (macOS Ventura/Sonoma)**
1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security**
3. Scroll down to find the message about ZAP being blocked
4. Click **"Open Anyway"** or **"Allow"**

**Method 4: Allow via Terminal (Advanced)**
```bash
# Allow ZAP to run (requires admin password)
sudo spctl --master-disable  # Disables Gatekeeper (not recommended)
# OR
sudo spctl --add /Applications/ZAP.app  # Adds ZAP to allowed list
sudo spctl --enable --label "ZAP"  # Enables for ZAP specifically
```

**Recommended:** Use Method 1 (Right-Click Open) as it's the safest and easiest.

**3. Configure Backend:**
```bash
# In your .env file:
ZAP_ENABLED=true
ZAP_URL=http://localhost:8080
```

**4. Test ZAP Integration:**
```bash
# First, verify ZAP is running directly
curl http://localhost:8080/JSON/core/view/version/
# Should return: {"version":"2.17.0"} (or your version)

# Then check ZAP status via your backend API
curl http://localhost:8000/api/v1/zap/status \
  -H "Cookie: access_token=your-token"

# Should return:
# {"enabled": true, "available": true, "url": "http://localhost:8080", "version": "2.17.0"}
```

**✅ ZAP is Working!**

If you see `{"version":"2.17.0"}` (or similar), ZAP is running correctly and ready to use!

#### Troubleshooting ZAP

**ZAP Not Available:**

```bash
# Check if ZAP is running
curl http://localhost:8080/JSON/core/view/version/

# Check ZAP status via API
curl http://localhost:8000/api/v1/zap/status
```

**Common Issues:**

1. **ZAP not running**: 
   - Start ZAP daemon (see setup above)
   - Verify port 8080 is not in use: `lsof -i :8080`

2. **Java not found** (Manual installation):
   - Install Java 11+ (Java SE 17 LTS or 21 LTS recommended)
   - Verify: `java -version`
   - Set `JAVA_HOME` environment variable if needed

3. **Connection refused**: 
   - Check `ZAP_URL` in `.env` matches ZAP's address
   - Ensure ZAP is listening on `0.0.0.0` (not just `127.0.0.1`)

4. **Authentication error**: 
   - Set `ZAP_API_KEY` in `.env` if ZAP requires authentication
   - Or use `api.disablekey=true` when starting ZAP

5. **Timeout errors**: 
   - Increase `ZAP_TIMEOUT` in `.env` for large websites
   - Increase `ZAP_SPIDER_MAX_DURATION` for sites with many pages

## Environment Variables

Key environment variables (see `env.example` for complete list):

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (min 32 characters)
- `REFRESH_SECRET_KEY` - Refresh token secret key

### Optional (with defaults)
- `FRONTEND_URL` - Frontend application URL (default: `http://localhost:3000`)
- `SECURITY_CONTACT_EMAIL` - Security contact email for reports

### OWASP ZAP Configuration (Optional)
- `ZAP_ENABLED` - Enable ZAP scanning (default: `false`)
- `ZAP_URL` - OWASP ZAP API URL (default: `http://localhost:8080`)
- `ZAP_API_KEY` - OWASP ZAP API key (optional, only if ZAP authentication enabled)
- `ZAP_TIMEOUT` - ZAP scan timeout in seconds (default: `300` = 5 minutes)
- `ZAP_SPIDER_MAX_DURATION` - ZAP spider max duration in minutes (default: `2`)

### Alerting (Optional)
- `SLACK_WEBHOOK_URL` - Slack webhook for alerts
- `SENDGRID_API_KEY` - SendGrid API key for email alerts
- `ALERT_EMAIL_FROM` - Email address to send alerts from
- `ALERT_EMAIL_TO` - Email address to receive alerts

### Email Configuration
- `SEND_GRID_API` or `SENDGRID_API_KEY` - SendGrid API key
- `FROM_EMAIL` or `PASSWORD_RESET_EMAIL_FROM` - Email for password resets

## Development Workflow

### Running Tests

```bash
# Install test dependencies (if any)
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current migration version
alembic current
```

### Code Style

The project follows Python PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `pylint` for linting
- `mypy` for type checking

## Production Deployment

### Security Considerations

1. **Environment Variables**
   - Never commit `.env` file to version control
   - Use secure secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Generate strong `SECRET_KEY` and `REFRESH_SECRET_KEY` (min 32 characters)

2. **Database**
   - Use strong PostgreSQL passwords
   - Enable SSL/TLS for database connections
   - Regular backups

3. **HTTPS**
   - Deploy behind reverse proxy (nginx, Traefik) with HTTPS
   - Set `COOKIE_SECURE=true` in production
   - Configure proper CORS origins

4. **Rate Limiting**
   - Implement rate limiting for API endpoints
   - Consider using `slowapi` or similar

5. **Monitoring**
   - Set up application monitoring (Sentry, DataDog, etc.)
   - Monitor database performance
   - Set up log aggregation

### Docker Production Deployment

```bash
# Build production image
docker build -t shieldops-backend:latest .

# Run with production settings
docker run -d \
  --name shieldops-api \
  -p 8000:8000 \
  --env-file .env.production \
  shieldops-backend:latest \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker Compose for Production

Update `docker-compose.yml` for production:
- Remove volume mounts (use built image)
- Set `workers` in uvicorn command
- Use production environment file
- Configure proper networking and volumes

## API Response Formats

### Success Response
```json
{
  "id": 1,
  "url": "https://example.com",
  "name": "Example Site",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message description"
}
```

### Authentication
- Access tokens expire in 15 minutes (configurable)
- Refresh tokens expire in 7 days (configurable)
- Tokens are sent as HTTP-only cookies for security

## Performance Considerations

- Database connection pooling is configured (pool_size=10, max_overflow=20)
- Use database indexes on frequently queried columns
- Consider caching for frequently accessed data
- Use async endpoints for I/O-bound operations
- Monitor query performance and optimize slow queries

## Contributing

1. Follow existing code style and conventions
2. Write tests for new features
3. Update documentation for API changes
4. Ensure all migrations are reversible
5. Test with both authenticated and unauthenticated requests

## Support & Resources

- **API Documentation**: `http://localhost:8000/docs` (when running)
- **Health Check**: `http://localhost:8000/health`
- **Security Contact**: Configure via `SECURITY_CONTACT_EMAIL` environment variable

## License

[Add your license information here]

---

**Note**: This is a production-ready security scanning platform. Always follow security best practices when deploying to production environments.
