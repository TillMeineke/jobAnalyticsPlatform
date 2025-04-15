# 🥇 Gold Layer - Analytics-Ready Data

This directory contains analytics-ready aggregated data derived from the silver layer.

## 🔄 Data Flow

Bronze → Silver → **Gold**

## 📋 Available Aggregations

Each aggregation is stored in CSV format with naming convention:
`{aggregation_name}_{timestamp}.csv`

### Job Market Analytics
- `job_count_by_company_{timestamp}.csv`: Job postings per company over time
- `job_count_by_location_{timestamp}.csv`: Geographic distribution of jobs
- `job_count_by_title_{timestamp}.csv`: Job roles frequency analysis
- `daily_job_count_{timestamp}.csv`: Daily posting volume trends

### Salary Analytics
- `salary_by_role_{timestamp}.csv`: Salary ranges by job role
- `salary_by_location_{timestamp}.csv`: Geographic salary variations

### Skills Analytics
- `skills_frequency_{timestamp}.csv`: Most requested skills
- `skills_cooccurrence_{timestamp}.csv`: Skills commonly requested together
