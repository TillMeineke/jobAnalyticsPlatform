# 🔍 Job Scrapers

This directory contains scrapers for collecting job posting data from various sources.

## 🚀 Available Scrapers

- `job_scraper.py`: Main scraping script that collects job postings based on job type and location

## 📋 Usage

```bash
# Run the job scraper for a specific job type and location
python job_scraper.py --job-type "data analytics" --location "hamburg"

# Examples for other job types
python job_scraper.py --job-type "data scientist" --location "hamburg"
python job_scraper.py --job-type "data engineer" --location "hamburg"
python job_scraper.py --job-type "machine learning engineer" --location "hamburg"
```

## 🔧 Configuration

The scraper saves data in the `data/bronze/` directory with filenames based on job type, location, and timestamp.
