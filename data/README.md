# 📊 Data Directory

This directory contains all data files for the Job Analytics Platform organized in the medallion architecture.

## 🏗️ Directory Structure

```
data/
├── bronze/  🥉  # Raw data scraped from sources
├── silver/  🥈  # Cleaned and processed data 
└── gold/    🥇  # Analytics-ready data
```

## 🔄 Data Flow

1. **Bronze Layer**: Raw job listings are saved here directly from the scraper in JSON format
2. **Silver Layer**: Cleaned and deduplicated data from the processing pipeline in CSV format
3. **Gold Layer**: Aggregated metrics and analytics-ready data for visualization in CSV format

## 📋 Data Files

### Bronze Layer

- Format: `{job_type}_{location}_{timestamp}.json`
- Example: `data_analytics_hamburg_20240520_124532.json`

### Silver Layer

- Format: `processed_jobs_{timestamp}.csv`
- Example: `processed_jobs_20240520_125043.csv`

### Gold Layer

- Format: `{aggregation_name}_{timestamp}.csv`
- Examples:
  - `job_count_by_company_20240520_125043.csv`
  - `job_count_by_location_20240520_125043.csv`
  - `job_count_by_title_20240520_125043.csv`
  - `daily_job_count_20240520_125043.csv`
