#!/bin/bash
# Script to create the database

echo "Creating database 'security_platform'..."

# Try to create database
createdb -U postgres security_platform 2>/dev/null || psql -U postgres -c "CREATE DATABASE security_platform;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database 'security_platform' created successfully!"
    echo "Now run: alembic upgrade head"
else
    echo "❌ Failed to create database. Try manually:"
    echo "  psql -U postgres"
    echo "  CREATE DATABASE security_platform;"
fi
