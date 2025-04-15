# 📦 Source Code

This directory contains the shared source code for data collection, processing, and utilities used by the Job Analytics Platform.

## 📂 Directory Structure

- `scrapers/` - Web scrapers for job platforms
- `dlt_pipelines/` - Data loading pipelines
- `utils/` - Utility functions (logging, validation, etc.)
- `tests/` - Unit and integration tests for components

## 🕸️ Scrapers

- Add new scrapers in `scrapers/` following the base class pattern.
- Example usage:

  ```python
  from src.scrapers.stepstone import StepStoneScraper
  scraper = StepStoneScraper()
  jobs = scraper.search(job_titles=["Data Engineer"], location="Berlin")
  ```

## 🧪 Testing

Run all tests:

```bash
cd 01_local
pytest src/tests/
```

## 🧹 Codebase Consolidation Checklist

- [ ] Review for duplicate logic between `scrapers/`, `utils/`, and other modules
- [ ] Refactor files >300 lines
- [ ] Add/Update docstrings and comments
- [ ] Remove/archive old or duplicate files

---

See other subfolder README.md files for more details on orchestration, data, and dashboards.
