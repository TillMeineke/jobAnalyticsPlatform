-- Create databases for services
CREATE DATABASE metabase;
CREATE DATABASE kestra;

-- Create role with appropriate permissions
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'jobanalytics') THEN
    CREATE ROLE jobanalytics WITH LOGIN PASSWORD 'jobanalytics' CREATEDB;
  END IF;
END
$$;

-- Grant all privileges on these databases to jobanalytics user
GRANT ALL PRIVILEGES ON DATABASE metabase TO jobanalytics;
GRANT ALL PRIVILEGES ON DATABASE kestra TO jobanalytics;

-- Connect to metabase database and set ownership
\c metabase
ALTER SCHEMA public OWNER TO jobanalytics;
GRANT ALL PRIVILEGES ON SCHEMA public TO jobanalytics;

-- Connect to kestra database and set ownership
\c kestra
ALTER SCHEMA public OWNER TO jobanalytics;
GRANT ALL PRIVILEGES ON SCHEMA public TO jobanalytics;