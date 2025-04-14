# 📊 Job Analytics Platform

A comprehensive data engineering platform for collecting, processing, and visualizing job market data.

## 🚀 Project Overview

This project implements a complete data pipeline for job analytics:

1. **Data Collection** - Scrape job listings from platforms like StepStone, LinkedIn, and Indeed
2. **Data Processing** - Transform raw data through medallion architecture (bronze → silver → gold)
3. **Data Visualization** - Analyze job market trends with Metabase dashboards

## 📂 Project Structure

The project follows a clear separation between local development and cloud deployment:

- `01_local/` - Local development environment (Docker-based)
- `02_cloud/` - AWS cloud deployment (Terraform)
- `docs/` - Project documentation
- `bin/` - Binary files like geckodriver (automatically managed)

## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Make
- Firefox (for web scraping)

### Local Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/jobAnalyticsPlatform.git
cd jobAnalyticsPlatform
```

2. Install dependencies

```bash
make install
```

3. Set up environment variables

```bash
cp .env.template .env
# Edit .env with your credentials
```

### Initial Testing

To verify the setup is working correctly, run:

```bash
make test-scraper
```

This will perform a basic test of the StepStone scraper, fetching a small number of job listings.

## 🔍 Running the Scrapers

### Step 1: Job Search Retriever

The search retriever continuously collects job listings and stores them in a SQLite database:

```bash
make search-jobs ARGS="--job-titles 'Data Engineer' 'Machine Learning Engineer' --location 'Deutschland'"
```

Parameters:

- `--job-titles`: One or more job titles to search for (space-separated)
- `--location`: Location to search in
- `--max-results`: Maximum number of results to fetch per job title (default: 100)
- `--sleep-time`: Time to sleep between searches in seconds (default: 60)

### Step 2: Job Details Retriever

The details retriever fetches comprehensive information for each job listing:

```bash
make fetch-details ARGS="--max-updates 10 --sleep-time 30"
```

Parameters:

- `--max-updates`: Maximum number of jobs to update per iteration (default: 25)
- `--sleep-time`: Time to sleep between iterations in seconds (default: 60)
- `--verbose`: Enable verbose logging

### Running Both Components

For complete data collection, run both scripts in separate terminal windows:

1. Start the search retriever to collect basic job information
2. Start the details retriever to collect comprehensive job details

## 📊 Data Pipeline

The data pipeline follows the medallion architecture:

1. **Bronze Layer** (Raw Data)
   - Scraped job listings stored in SQLite database

2. **Silver Layer** (Cleaned Data)
   - Structured and deduplicated job data

3. **Gold Layer** (Analytics-Ready)
   - Aggregated metrics and insights

## 📝 Development

### Makefile Commands

Run `make help` to see available commands:

```
make help
```

Key commands:

- `make install`: Install dependencies
- `make test-scraper`: Test the basic scraper
- `make search-jobs`: Run the job search retriever
- `make fetch-details`: Run the job details retriever
- `make setup-local`: Set up local development environment
- `make run-local`: Start local services
- `make setup-cloud`: Set up cloud environment

## 🧪 Testing

Run tests with:

```bash
make test-local
```

## 🚀 Deployment

Instructions for deploying to AWS are in the [cloud deployment guide](02_cloud/README.md).

## 📚 Documentation

- [Local Development](01_local/README.md)
- [Cloud Deployment](02_cloud/README.md)
- [Data Model](docs/data_model.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
