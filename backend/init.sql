-- GhostWorker Database Initialization

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'member', 'viewer');
CREATE TYPE platform_type AS ENUM ('whatsapp', 'instagram', 'tiktok', 'email');
CREATE TYPE message_status AS ENUM ('pending', 'sent', 'delivered', 'read', 'failed');
CREATE TYPE message_direction AS ENUM ('inbound', 'outbound');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE integration_status AS ENUM ('connected', 'disconnected', 'error');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');

-- Create full-text search configuration
CREATE TEXT SEARCH CONFIGURATION ghostworker (COPY = english);
