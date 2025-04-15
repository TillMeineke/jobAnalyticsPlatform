# 🥉 Bronze Layer - Raw Data

This directory contains raw job listings data scraped from various sources.

Files are saved in JSON format with naming convention:
`{job_type}_{location}_{timestamp}.json`

Example: `data_scientist_hamburg_20240520_124532.json`

## 🔄 Data Flow

Source → **Bronze** → Silver → Gold

## 📋 Schema

Raw job postings contain the following fields:

- `job_id`: Unique identifier for the job posting
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `url`: URL to the job posting
- `posting_date`: Date when the job was posted
- `description`: Job description
- `scrape_timestamp`: Timestamp when the data was collected
