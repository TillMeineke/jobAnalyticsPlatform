# 🥇 Gold Layer - Analytics-Ready Data

This directory contains analytics-ready aggregated data derived from the silver layer.

Files are saved in CSV format with naming convention:
`{aggregation_name}_{timestamp}.csv`

Examples:

- `job_count_by_company_20240520_125043.csv`
- `job_count_by_location_20240520_125043.csv`
- `job_count_by_title_20240520_125043.csv`
- `daily_job_count_20240520_125043.csv`

## 🔄 Data Flow

Bronze → Silver → **Gold**

## 📋 Available Aggregations

1. **Job Count by Company**
   - Schema: `company`, `job_count`
   - Description: Number of job listings per company

2. **Job Count by Location**
   - Schema: `location`, `job_count`
   - Description: Number of job listings per location

3. **Job Count by Title**
   - Schema: `title`, `job_count`
   - Description: Number of job listings per job title

4. **Daily Job Count**
   - Schema: `posting_date`, `job_count`
   - Description: Number of job listings posted per day

These aggregated datasets are used to power the analytics dashboards in Metabase.
