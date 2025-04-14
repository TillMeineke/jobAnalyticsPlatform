{{ config(
  materialized='table',
  schema='silver'
) }}

WITH source_data AS (
  SELECT 
    job_title,
    company,
    location,
    job_description,
    job_url,
    date_posted,
    salary_min,
    salary_max,
    currency,
    job_type,
    extracted_date
  FROM {{ source('bronze', 'job_listings') }}
)

SELECT 
  job_title,
  company,
  location,
  job_description,
  job_url,
  COALESCE(date_posted, extracted_date) AS posting_date,
  salary_min,
  salary_max,
  currency,
  job_type,
  extracted_date,
  CURRENT_TIMESTAMP() AS loaded_at
FROM source_data