# 🔄 Job Analytics dbt Transformation Layer

This directory contains the dbt (data build tool) models and configurations for transforming job data from raw sources into analytics-ready datasets.

## 📂 Directory Structure

- `models/` - Contains SQL models organized by processing phase
  - `core/` - Base models that transform raw data into a usable format
  - `marts/` - Business-specific aggregations and transformations
- `analyses/` - Ad-hoc analytical queries
- `macros/` - Reusable SQL snippets and functions
- `seeds/` - Static data files
- `tests/` - Data quality tests

## 🔄 Data Flow

Our transformation pipeline follows the medallion architecture:

1. 🥉 **Bronze Layer** - Raw data ingested from scraping, preserved in original format
2. 🥈 **Silver Layer** - Cleansed, validated, and transformed data
3. 🥇 **Gold Layer** - Business-ready aggregations and metrics

## 🚀 Getting Started

### Prerequisites

- dbt Core installed (`pip install dbt-core dbt-postgres dbt-athena`)
- Configured `~/.dbt/profiles.yml` file (use our template from `profiles.yml.example`)

### Running Transformations

Run all models:

```bash
cd dbt
dbt run
```

Run specific models:

```bash
dbt run --select stg_job_listings
dbt run --select job_analytics_enriched
```

### Running Tests

```bash
dbt test
```

## 📊 Key Models

- `stg_job_listings` - Base staging model for job data with cleaned fields
- `job_analytics_enriched` - Enhanced analytics model with job categorization and tech stack analysis

## 🔄 Integration

These transformations are automatically triggered after data quality checks via Kestra workflows.
