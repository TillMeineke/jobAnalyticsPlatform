# 🕸️ Job Scrapers

This directory contains scrapers for various job platforms.

## 🦊 Firefox/GeckoDriver Requirement

**Important**: All scrapers in this project use Firefox and GeckoDriver for browser automation.

### Prerequisites

1. Install Firefox browser on your system
2. Required Python packages:

   ```bash
   pip install selenium webdriver-manager
   ```

The `webdriver-manager` package will automatically download and manage the appropriate GeckoDriver version for your system.

## 🔄 Available Scrapers

- `stepstone.py` - Scraper for StepStone job listings

## 🚀 Usage

Run scrapers directly from the command line:

```bash
# Change to the 01_local directory
cd /Users/tillmeineke/ML/jobAnalyticsPlatform/01_local

# Run StepStone scraper
python src/scrapers/stepstone.py --job-title "data engineer" --location "hamburg" --max-pages 1
```

## 📋 Common Parameters

- `--job-title`: Job title to search for (e.g., "data engineer", "python developer")
- `--location`: Location to search in (e.g., "berlin", "hamburg")
- `--max-pages`: Maximum number of pages to scrape (default: 10)
- `--headless`: Run in headless mode (no browser UI)
- `--output`: Path to save the results CSV file
- `--scrape-details`: Scrape detailed information for each job

## ⚙️ Configuration

Scrapers can be configured through parameters or environment variables. See the specific scraper documentation for details.

## 🧪 Testing

Test scrapers with:

```bash
cd /Users/tillmeineke/ML/jobAnalyticsPlatform/01_local
python tests/run_scraper_test.py --job-title "data engineer" --location "hamburg" --max-pages 1 --details
```
