# 🥈 Silver Layer - Processed Data

This directory contains cleaned and processed job listings data from the bronze layer.

## 🔄 Data Flow

Bronze → **Silver** → Gold

## 📋 Schema

Files are saved in CSV format with naming convention:
`processed_jobs_{timestamp}.csv`

Example: `processed_jobs_20240520_125043.csv`

### Job Listing Fields

- `job_id`: Unique identifier (MD5 hash of key fields)
- `title`: Standardized job title
- `company`: Normalized company name
- `location`: Standardized location format (City, Country)
- `url`: URL to the job posting
- `posting_date`: Standardized date format (YYYY-MM-DD)
- `salary_min`: Standardized minimum salary in EUR
- `salary_max`: Standardized maximum salary in EUR
- `skills`: Array of extracted skills from description
- `experience_years_min`: Extracted minimum years of experience
- `experience_years_max`: Extracted maximum years of experience
- `employment_type`: Full-time, Part-time, Contract, etc.
- `description`: Cleaned job description (HTML removed)
- `source`: Source platform (StepStone, LinkedIn, etc.)
- `scrape_timestamp`: When the data was collected (UTC)
- `processed_timestamp`: When the data was processed (UTC)
