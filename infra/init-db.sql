-- Initialize database
CREATE DATABASE IF NOT EXISTS sunog;

-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sunog') THEN
        CREATE ROLE sunog LOGIN PASSWORD 'sunog_password';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sunog TO sunog;
GRANT ALL PRIVILEGES ON SCHEMA public TO sunog;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sunog;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sunog;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sunog;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sunog;

