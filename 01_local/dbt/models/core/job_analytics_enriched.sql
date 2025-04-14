{{ config(
  materialized='table',
  schema='gold'
) }}

WITH job_listings AS (
    SELECT * FROM {{ ref('stg_job_listings') }}
),

-- Extract technology mentions from job descriptions
tech_mentions AS (
    SELECT
        job_title,
        company,
        location,
        -- Python technologies
        CASE WHEN LOWER(job_description) LIKE '%python%' THEN 1 ELSE 0 END AS has_python,
        CASE WHEN LOWER(job_description) LIKE '%pandas%' THEN 1 ELSE 0 END AS has_pandas,
        CASE WHEN LOWER(job_description) LIKE '%numpy%' THEN 1 ELSE 0 END AS has_numpy,
        CASE WHEN LOWER(job_description) LIKE '%scikit%learn%' OR 
                  LOWER(job_description) LIKE '%scikit-learn%' THEN 1 ELSE 0 END AS has_sklearn,
        
        -- Data processing
        CASE WHEN LOWER(job_description) LIKE '%spark%' THEN 1 ELSE 0 END AS has_spark,
        CASE WHEN LOWER(job_description) LIKE '%hadoop%' THEN 1 ELSE 0 END AS has_hadoop,
        CASE WHEN LOWER(job_description) LIKE '%airflow%' THEN 1 ELSE 0 END AS has_airflow,
        CASE WHEN LOWER(job_description) LIKE '%kestra%' THEN 1 ELSE 0 END AS has_kestra,
        CASE WHEN LOWER(job_description) LIKE '%dbt%' THEN 1 ELSE 0 END AS has_dbt,
        
        -- Cloud platforms
        CASE WHEN LOWER(job_description) LIKE '%aws%' OR 
                  LOWER(job_description) LIKE '%amazon%web%services%' THEN 1 ELSE 0 END AS has_aws,
        CASE WHEN LOWER(job_description) LIKE '%azure%' THEN 1 ELSE 0 END AS has_azure,
        CASE WHEN LOWER(job_description) LIKE '%gcp%' OR 
                  LOWER(job_description) LIKE '%google%cloud%' THEN 1 ELSE 0 END AS has_gcp,
        
        -- Job details
        COALESCE(salary_min, 0) as salary_min,
        COALESCE(salary_max, 0) as salary_max,
        CASE WHEN salary_min > 0 AND salary_max > 0 THEN (salary_min + salary_max) / 2 
             WHEN salary_min > 0 THEN salary_min 
             WHEN salary_max > 0 THEN salary_max 
             ELSE NULL END as avg_salary,
        currency,
        job_type,
        posting_date,
        extracted_date
    FROM job_listings
),

-- Job Role Classification
job_categories AS (
    SELECT
        *,
        CASE
            WHEN LOWER(job_title) LIKE '%data%engineer%' OR 
                 LOWER(job_title) LIKE '%data%pipeline%' OR
                 LOWER(job_title) LIKE '%etl%' THEN 'Data Engineer'
            WHEN LOWER(job_title) LIKE '%data%scientist%' OR 
                 LOWER(job_title) LIKE '%machine%learning%' THEN 'Data Scientist'
            WHEN LOWER(job_title) LIKE '%data%analyst%' OR 
                 LOWER(job_title) LIKE '%business%intelligence%' OR
                 LOWER(job_title) LIKE '%bi%developer%' THEN 'Data Analyst'
            WHEN LOWER(job_title) LIKE '%software%engineer%' OR 
                 LOWER(job_title) LIKE '%developer%' OR
                 LOWER(job_title) LIKE '%programmer%' THEN 'Software Engineer'
            WHEN LOWER(job_title) LIKE '%devops%' OR 
                 LOWER(job_title) LIKE '%sre%' OR
                 LOWER(job_title) LIKE '%site%reliability%' THEN 'DevOps/SRE'
            ELSE 'Other'
        END as job_category,
        
        -- Create tech stack score (higher means more technologies mentioned)
        has_python + has_pandas + has_numpy + has_sklearn +
        has_spark + has_hadoop + has_airflow + has_kestra + has_dbt +
        has_aws + has_azure + has_gcp as tech_stack_score
    FROM tech_mentions
)

SELECT
    *,
    DATE_TRUNC('month', posting_date) as posting_month,
    EXTRACT(YEAR FROM posting_date) as posting_year
FROM job_categories