# Quick Fix: Database Name Mismatch

## Problem
You have a database named `security` in TablePlus, but the code is looking for `security_platform`.

## Solution: Update .env File

Since you already have the `security` database, update your `.env` file:

```bash
cd backend
cp env.example .env
```

Then edit `.env` and change:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/security
```

(Note: It should already say `security` in env.example, but make sure your `.env` matches)

## Then Run Migrations

```bash
alembic upgrade head
```

## Alternative: Create security_platform Database

If you prefer to use `security_platform`:

1. In TablePlus, run:
   ```sql
   CREATE DATABASE security_platform;
   ```

2. Or via command line:
   ```bash
   createdb -U postgres security_platform
   ```

3. Keep `.env` as:
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/security_platform
   ```

## Verify Your Database Name

In TablePlus, check what database you're connected to. The connection string shows:
- `LOCAL | PostgreSQL 14.19 : local : security`

So your database is named `security`. Make sure your `.env` file matches this!

