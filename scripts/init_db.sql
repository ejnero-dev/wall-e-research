-- Database initialization script for Wallapop Bot
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional databases if needed
-- CREATE DATABASE wallapop_bot_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For composite indexes

-- Create custom types or functions if needed
-- (None needed for MVP)

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE wallapop_bot TO wallapop_user;

-- Connect to the main database
\c wallapop_bot;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO wallapop_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wallapop_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wallapop_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wallapop_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wallapop_user;