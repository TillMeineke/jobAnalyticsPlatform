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

- Bronze: `{job_type}_{location}_{timestamp}.json`
- Silver: `processed_jobs_{timestamp}.csv`
- Gold: `{aggregation_name}_{timestamp}.csv`

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated files in each layer
- [ ] Ensure all data follows naming conventions
- [ ] Document any manual data changes here

---

See the README.md in `src/` for code that generates and processes these files.
