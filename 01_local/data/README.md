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

1. [Bronze Layer](bronze/README.md): Raw job listings in JSON format
   - Direct scraper output
   - Preserves original data structure
   - No transformations applied

2. [Silver Layer](silver/README.md): Processed data in CSV format
   - Cleaned and standardized
   - Deduplicated records
   - Extracted structured fields

3. [Gold Layer](gold/README.md): Analytics-ready aggregations
   - Aggregated metrics
   - Pre-computed statistics
   - Ready for visualization

## 📋 File Naming Conventions

- Bronze: `{source}_{job_type}_{location}_{timestamp}.json`
- Silver: `processed_jobs_{timestamp}.csv`
- Gold: `{aggregation_name}_{timestamp}.csv`

## 🧹 Data Retention

- Bronze: 30 days
- Silver: 90 days
- Gold: Indefinite

For schema details and field descriptions, see the README.md in each layer's directory.
