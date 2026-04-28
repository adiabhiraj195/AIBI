-- Run this file to set up the database user and permissions
-- Execute: psql postgres < setup_database.sql

-- Create user
CREATE USER AIBI_user WITH PASSWORD 'AIBI_password';

-- Create database
CREATE DATABASE "AIBI_Backend" OWNER AIBI_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "AIBI_Backend" TO AIBI_user;

-- Connect to the new database and grant schema privileges
\c AIBI_Backend
GRANT ALL ON SCHEMA public TO AIBI_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO AIBI_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO AIBI_user;
