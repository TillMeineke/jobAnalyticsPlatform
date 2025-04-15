# 🔄 Job Analytics dbt Transformation Layer

This directory contains the dbt (data build tool) models and configurations for transforming job data from raw sources into analytics-ready datasets.

## 📂 Directory Structure

- `models/` - SQL models organized by processing phase (bronze, silver, gold)
- `analyses/` - Ad-hoc analytical queries
- `macros/` - Reusable SQL snippets and functions
- `seeds/` - Static data files
- `tests/` - Data quality tests

## 🚀 Getting Started

### Prerequisites

- dbt Core installed (`pip install dbt-core dbt-postgres`)
- Configured `~/.dbt/profiles.yml` file (use our template from `profiles.yml.example`)

### Running Transformations

Run all models:

```bash
cd 01_local/dbt
make run-dbt
```

Run specific models:

```bash
cd 01_local/dbt
dbt run --select stg_job_listings
dbt run --select job_analytics_enriched
```

### Running Tests

```bash
cd 01_local/dbt
dbt test
```

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated models
- [ ] Ensure all models follow naming conventions
- [ ] Add/Update documentation for each model

---

See the README.md in `src/` for code that generates input data for these models.
