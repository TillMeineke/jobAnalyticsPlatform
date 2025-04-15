# 🥈 Silver Layer - Processed Data

This directory contains cleaned and processed job listings data from the bronze layer.

Files are saved in CSV format with naming convention:
`processed_jobs_{timestamp}.csv`

Example: `processed_jobs_20240520_125043.csv`

## 🔄 Data Flow

Bronze → **Silver** → Gold

## 📋 Schema

Processed job postings contain standardized and cleaned fields:

- `job_id`: Unique identifier for the job posting
- `title`: Standardized job title
- `company`: Normalized company name
- `location`: Standardized location format
- `url`: URL to the job posting
- `posting_date`: Standardized date format (YYYY-MM-DD)
- `description`: Cleaned job description
- `scrape_timestamp`: Timestamp when the data was collected
- `processed_timestamp`: Timestamp when the data was processed
