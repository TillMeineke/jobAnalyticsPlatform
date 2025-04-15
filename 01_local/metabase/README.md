# 📊 Metabase Dashboards

This directory contains configuration and documentation for Metabase dashboards.

## 🎯 Available Dashboards

### 1. Job Market Overview

- Daily job posting volume
- Top hiring companies
- Geographic distribution
- Role distribution

### 2. Skills Analysis

- Top requested skills
- Emerging skills trends
- Skills by job role
- Technology stack combinations

### 3. Salary Insights

- Salary ranges by role
- Geographic salary variations
- Experience level impact
- Industry comparisons

## 🚀 Local Setup

```bash
cd 01_local/metabase
docker-compose up -d
```

Access Metabase UI at: <http://localhost:3000>

## 🔄 Data Refresh

- Market Overview: Daily
- Skills Analysis: Weekly
- Salary Insights: Weekly

## 📋 Data Sources

All visualizations use the Gold layer tables:

- `job_postings_daily`
- `skills_analysis`
- `salary_trends`
- `company_metrics`
