# 📊 dbt Transformations

This directory contains dbt models for transforming job listings data through the medallion architecture.

## 📂 Model Organization

```
models/
├── bronze/      # Source models
├── silver/      # Cleaned models
├── gold/        # Analytics models
└── shared/      # Common CTEs and macros
```

## 🔄 Model Dependencies

1. Bronze (Sources)
   - `raw_stepstone.sql`
   - `raw_linkedin.sql` (planned)
   - `raw_indeed.sql` (planned)

2. Silver (Processing)
   - `stg_jobs_cleaned.sql`
   - `stg_companies_normalized.sql`
   - `stg_locations_parsed.sql`
   - `stg_salaries_standardized.sql`
   - `stg_skills_extracted.sql`

3. Gold (Analytics)
   - `job_postings_daily.sql`
   - `company_metrics.sql`
   - `skills_analysis.sql`
   - `salary_trends.sql`

## 🚀 Running Models

### Local Development

```bash
cd 01_local/dbt
dbt run --profiles-dir .
```

### Testing

```bash
dbt test --profiles-dir .
```

## 📋 Data Quality Tests

- Source freshness checks
- Uniqueness constraints
- Not-null validations
- Range checks for salaries
- Custom data validation rules
