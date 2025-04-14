# 📊 DBT Transformations

This directory contains the dbt models for transforming job data through the medallion architecture:

- **Bronze** 🥉 → **Silver** 🥈 → **Gold** 🥇

## 🏗️ Architecture

The dbt project follows the medallion architecture with clear separation between layers:

```
Bronze Layer (Raw Data)
      ↓
   Cleaning
      ↓
Silver Layer (Cleaned Data)
      ↓
  Aggregation
      ↓
 Gold Layer (Analytics-Ready)
```

## 📂 Directory Structure

```
.
├── dbt_project.yml         # DBT project configuration
├── models/                 # DBT models
│   ├── bronze_to_silver/   # Transformations from bronze to silver
│   │   ├── job_listings_cleaned.sql
│   │   ├── companies_cleaned.sql
│   │   └── schema.yml
│   ├── silver_to_gold/     # Transformations from silver to gold
│   │   ├── job_count_by_company.sql
│   │   ├── job_count_by_location.sql
│   │   ├── job_count_by_time.sql
│   │   └── schema.yml
│   └── sources.yml         # Sources configuration
├── seeds/                  # Reference data
│   └── job_categories.csv
├── snapshots/              # Slowly changing dimensions
├── macros/                 # Custom macros
└── tests/                  # Custom tests
```

## 🔄 Transformation Flow

### Bronze to Silver Transformations

The bronze to silver transformation focuses on:

- Data cleaning and validation
- Type conversion
- Column standardization
- Deduplication
- Handling missing values

Key models:

- `job_listings_cleaned.sql`: Cleans raw job listing data
- `companies_cleaned.sql`: Extracts and normalizes company information

### Silver to Gold Transformations

The silver to gold transformation focuses on:

- Creating analytics-ready aggregations
- Developing time-series views
- Building dimensional models
- Calculating metrics

Key models:

- `job_count_by_company.sql`: Counts jobs by company
- `job_count_by_location.sql`: Counts jobs by location
- `job_count_by_time.sql`: Tracks job listings over time

## 📊 Data Model

### Bronze Layer

Tables:

- `bronze.job_listings`: Raw job listings scraped from platforms

### Silver Layer

Tables:

- `silver.job_listings`: Cleaned job listings
- `silver.companies`: Normalized company information

### Gold Layer

Tables:

- `gold.job_count_by_company`: Aggregation by company
- `gold.job_count_by_location`: Aggregation by location
- `gold.job_count_by_time`: Time series analysis
- `gold.job_market_insights`: Combined insights for dashboards

## 🧪 Testing

The dbt project includes:

- Schema tests (uniqueness, not null, etc.)
- Custom data quality tests
- Row count validation

Run tests with:

```bash
cd 01_local/dbt_project
dbt test
```

## 🚀 Running the Models

To run the entire dbt project:

```bash
cd 01_local/dbt_project
dbt run
```

To run specific models:

```bash
dbt run --models bronze_to_silver
dbt run --models silver_to_gold
```

## 📚 Documentation

Generate and view dbt documentation:

```bash
dbt docs generate
dbt docs serve
```
