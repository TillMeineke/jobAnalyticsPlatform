-- Setup test schema for Job Analytics Platform

-- Create schemas for medallion architecture
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Bronze layer tables
CREATE TABLE IF NOT EXISTS bronze.raw_listings (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    url TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    currency TEXT,
    posted_date DATE,
    extraction_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
    source TEXT,
    raw_data JSONB
);

-- Create index on job_id for faster lookups
CREATE INDEX IF NOT EXISTS raw_listings_job_id_idx ON bronze.raw_listings(job_id);
CREATE INDEX IF NOT EXISTS raw_listings_source_idx ON bronze.raw_listings(source);

-- Silver layer tables
CREATE TABLE IF NOT EXISTS silver.standardized_job_listings (
    listing_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    title TEXT,
    company TEXT,
    location TEXT,
    standardized_location TEXT,
    description TEXT,
    url TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    currency TEXT,
    posted_date DATE,
    extracted_skills JSONB,
    source TEXT,
    extraction_time TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS std_listings_location_idx ON silver.standardized_job_listings(standardized_location);
CREATE INDEX IF NOT EXISTS std_listings_company_idx ON silver.standardized_job_listings(company);

-- Gold layer tables
CREATE TABLE IF NOT EXISTS gold.job_market_trends (
    id SERIAL PRIMARY KEY,
    week DATE NOT NULL,
    location TEXT NOT NULL,
    job_count INTEGER NOT NULL,
    avg_min_salary NUMERIC,
    avg_max_salary NUMERIC,
    python_count INTEGER,
    sql_count INTEGER,
    aws_count INTEGER,
    spark_count INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS job_market_trends_week_location_idx 
ON gold.job_market_trends(week, location);

CREATE TABLE IF NOT EXISTS gold.company_hiring_trends (
    id SERIAL PRIMARY KEY,
    month DATE NOT NULL,
    company TEXT NOT NULL,
    job_count INTEGER NOT NULL,
    avg_min_salary NUMERIC,
    avg_max_salary NUMERIC,
    most_requested_skills JSONB,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS company_trends_month_company_idx 
ON gold.company_hiring_trends(month, company);

-- Insert some test data for bronze layer
INSERT INTO bronze.raw_listings (job_id, title, company, location, description, url, salary_min, salary_max, posted_date, source)
VALUES
    ('test-123', 'Senior Data Engineer', 'Test Corp', 'Berlin, Germany', 'Looking for an experienced data engineer...', 'https://example.com/jobs/123', 80000, 100000, '2023-05-15', 'stepstone'),
    ('test-456', 'Data Scientist', 'Analytics Inc', 'Munich, Germany', 'Join our team of data scientists...', 'https://example.com/jobs/456', 75000, 95000, '2023-05-12', 'linkedin'),
    ('test-789', 'Python Developer', 'Tech GmbH', 'Remote', 'Seeking Python developer with 3+ years experience...', 'https://example.com/jobs/789', 65000, 85000, '2023-05-10', 'indeed');

-- Insert test data for silver layer (as if it had been transformed from bronze)
INSERT INTO silver.standardized_job_listings (listing_id, job_id, title, company, location, standardized_location, description, url, salary_min, salary_max, posted_date, source, extraction_time, extracted_skills)
VALUES
    ('md5-123', 'test-123', 'Senior Data Engineer', 'Test Corp', 'Berlin, Germany', 'Berlin', 'Looking for an experienced data engineer...', 'https://example.com/jobs/123', 80000, 100000, '2023-05-15', 'stepstone', '2023-05-16 10:00:00+00', '["Python", "SQL", "AWS", "Spark"]'::jsonb),
    ('md5-456', 'test-456', 'Data Scientist', 'Analytics Inc', 'Munich, Germany', 'Munich', 'Join our team of data scientists...', 'https://example.com/jobs/456', 75000, 95000, '2023-05-12', 'linkedin', '2023-05-13 14:30:00+00', '["Python", "R", "Machine Learning", "Statistics"]'::jsonb),
    ('md5-789', 'test-789', 'Python Developer', 'Tech GmbH', 'Remote', 'Remote', 'Seeking Python developer with 3+ years experience...', 'https://example.com/jobs/789', 65000, 85000, '2023-05-10', 'indeed', '2023-05-11 09:45:00+00', '["Python", "Django", "Flask", "REST API"]'::jsonb);

-- Insert test data for gold layer
INSERT INTO gold.job_market_trends (week, location, job_count, avg_min_salary, avg_max_salary, python_count, sql_count, aws_count, spark_count)
VALUES
    ('2023-05-15', 'Berlin', 3, 75000, 95000, 3, 2, 1, 1),
    ('2023-05-15', 'Munich', 2, 72500, 92500, 2, 1, 0, 0),
    ('2023-05-15', 'Remote', 1, 65000, 85000, 1, 0, 0, 0);

INSERT INTO gold.company_hiring_trends (month, company, job_count, avg_min_salary, avg_max_salary, most_requested_skills)
VALUES
    ('2023-05-01', 'Test Corp', 1, 80000, 100000, '{"Python": 1, "SQL": 1, "AWS": 1, "Spark": 1}'::jsonb),
    ('2023-05-01', 'Analytics Inc', 1, 75000, 95000, '{"Python": 1, "R": 1, "Machine Learning": 1, "Statistics": 1}'::jsonb),
    ('2023-05-01', 'Tech GmbH', 1, 65000, 85000, '{"Python": 1, "Django": 1, "Flask": 1, "REST API": 1}'::jsonb);

-- Print completion message
SELECT 'Test schema and data setup complete' as message;