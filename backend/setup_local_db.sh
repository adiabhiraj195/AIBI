#!/bin/bash

# Setup script for local PostgreSQL database
# This creates the database user, database, and schema

echo "Setting up local PostgreSQL database for AIBI Backend..."

# Database configuration
DB_NAME="AIBI_Backend"
DB_USER="AIBI_user"
DB_PASSWORD="AIBI_password"

# Create the database user if it doesn't exist
echo "Creating database user..."
psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"

# Create the database
echo "Creating database..."
psql postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER $DB_USER;" 2>/dev/null || echo "Database already exists"

# Grant privileges
echo "Granting privileges..."
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO $DB_USER;"

# Create the schema
echo "Creating database schema..."
psql -U $DB_USER -d $DB_NAME -f database_schema.sql

echo ""
echo "✅ Database setup complete!"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Host: localhost"
echo "   Port: 5432"
echo ""
echo "You can now run: python3 ./main.py"
