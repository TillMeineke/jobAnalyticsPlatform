-- Create the bronze, silver, and gold schemas for our medallion architecture
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Grant privileges to the jobanalytics user
GRANT ALL PRIVILEGES ON SCHEMA bronze TO jobanalytics;
GRANT ALL PRIVILEGES ON SCHEMA silver TO jobanalytics;
GRANT ALL PRIVILEGES ON SCHEMA gold TO jobanalytics;

-- Set search path
ALTER ROLE jobanalytics SET search_path TO public, bronze, silver, gold;

-- Create sample bronze tables
CREATE TABLE IF NOT EXISTS bronze.raw_job_listings (
    id SERIAL PRIMARY KEY,
    job_id TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    url TEXT,
    posting_date TIMESTAMP,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB
);

-- Create sample silver tables
CREATE TABLE IF NOT EXISTS silver.standardized_job_listings (
    id SERIAL PRIMARY KEY,
    listing_id TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    normalized_location TEXT,
    description TEXT,
    skills TEXT[],
    seniority_level TEXT,
    posting_date DATE,
    source TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sample gold tables
CREATE TABLE IF NOT EXISTS gold.job_market_trends (
    id SERIAL PRIMARY KEY,
    period DATE,
    job_category TEXT,
    location TEXT,
    job_count INT,
    avg_salary_estimate NUMERIC,
    salary_min NUMERIC,
    salary_max NUMERIC,
    top_skills JSONB,
    growth_rate NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.skill_demand (
    id SERIAL PRIMARY KEY,
    period DATE,
    skill TEXT,
    job_category TEXT,
    demand_count INT,
    growth_percentage NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON SCHEMA bronze IS 'Raw data layer containing minimally processed job data';
COMMENT ON SCHEMA silver IS 'Intermediate layer with cleaned and standardized job data';
COMMENT ON SCHEMA gold IS 'Analytics-ready layer with aggregated metrics and insights';