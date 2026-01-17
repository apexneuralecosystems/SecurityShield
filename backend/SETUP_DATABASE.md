# Database Setup Guide

## Quick Fix: Create the Database

The error shows the database doesn't exist. Here's how to create it:

### Option 1: Using psql (Command Line)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE security_platform;

# Exit psql
\q
```

### Option 2: Using createdb Command

```bash
# Create database directly
createdb -U postgres security_platform
```

### Option 3: Using Docker (if using Docker for PostgreSQL)

```bash
# Connect to PostgreSQL container
docker exec -it security_platform_db psql -U postgres

# Create database
CREATE DATABASE security_platform;

# Exit
\q
```

## After Creating Database

Once the database is created, run migrations:

```bash
cd backend
alembic upgrade head
```

## Verify Database Exists

```bash
# List all databases
psql -U postgres -l

# Or using Docker
docker exec -it security_platform_db psql -U postgres -l
```

You should see `security_platform` in the list.

## Common Issues

### Issue: "role postgres does not exist"

**Solution:**
```bash
# Create postgres user
createuser -s postgres
```

### Issue: "password authentication failed"

**Solution:**
- Check your `.env` file has correct password
- Or set PostgreSQL to trust local connections (development only)

### Issue: "connection refused"

**Solution:**
- Make sure PostgreSQL is running:
  ```bash
  # macOS
  brew services start postgresql@15
  
  # Linux
  sudo systemctl start postgresql
  
  # Docker
  docker-compose up -d postgres
  ```

## Using Different Database Name

If you want to use a different database name (like "security" instead of "security_platform"):

1. Update `.env` file:
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/security
   ```

2. Create the database:
   ```bash
   createdb -U postgres security
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

