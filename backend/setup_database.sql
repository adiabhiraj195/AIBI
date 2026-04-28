-- Run this file to set up the database user and permissions
-- Execute: psql postgres < setup_database.sql

-- Create user
CREATE USER suzlon_user WITH PASSWORD 'suzlon_password';

-- Create database
CREATE DATABASE "Suzlon_Backend" OWNER suzlon_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "Suzlon_Backend" TO suzlon_user;

-- Connect to the new database and grant schema privileges
\c Suzlon_Backend
GRANT ALL ON SCHEMA public TO suzlon_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO suzlon_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO suzlon_user;
