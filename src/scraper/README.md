# 🕸️ Stepstone Job Scraper

This module provides functionality to scrape job listings from [Stepstone.de](https://www.stepstone.de), extract structured data from them, and prepare the data for further processing in the data pipeline.

## 📚 Features

- Search for jobs by role, location, and radius
- Extract detailed information from job listings
- Parse and normalize job attributes (title, company, location, posting date)
- Extract skills mentioned in job descriptions
- Parse salary information into structured format
- Handle errors and retries gracefully
- Configurable for different environments (dev, test, prod)

## 🧰 Components

### 1. `StepstoneScraper`

The main scraper class that handles making requests to Stepstone and extracting job listings.

```python
from src.scraper import StepstoneScraper

# Create a scraper
scraper = StepstoneScraper()

# Search for data scientist jobs in Hamburg
jobs = scraper.search_jobs(
    role="data-scientist", 
    location="hamburg", 
    radius=30,
    max_pages=3
)

# Get detailed information for a specific job
job_details = scraper.get_job_details(jobs[0]["job_url"])
```

### 2. `JobParser`

A specialized class for parsing HTML elements and extracting structured data from job listings.

```python
from src.scraper import JobParser
from bs4 import BeautifulSoup

# Create a parser
parser = JobParser()

# Parse a job details page
with open("job_details.html", "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
    job_details = parser.parse_job_details(soup)
    
# Extract skills from a description
skills = parser._extract_skills("We are looking for experience with Python and AWS...")
```

### 3. Utility Functions

Helper functions for logging, file handling, and other common tasks.

```python
from src.scraper.utils import setup_logger, ensure_directory_exists, format_filename

# Set up a logger
logger = setup_logger("my_logger")

# Create a directory if it doesn't exist
ensure_directory_exists("data/raw")

# Format a valid filename from job title and company
filename = format_filename("Data Scientist", "Example Company")
```

## 🧪 Testing

The module includes comprehensive unit tests for both the `StepstoneScraper` and `JobParser` classes:

```bash
# Run all tests
python -m unittest discover src/tests

# Run specific test file
python -m unittest src/tests/scraper/test_stepstone_scraper.py
```

## 🔧 Configuration

The scraper is configurable through the central configuration system:

```python
from src.config import config

# Access scraper configuration
request_delay = config.scraper.request_delay
max_pages = config.scraper.max_pages_per_search

# Environment-specific settings
environment = config.environment  # 'dev', 'test', or 'prod'
```

## 📈 Next Steps

Future improvements planned for the scraper:

1. Add support for additional job portals (LinkedIn, Indeed, etc.)
2. Implement more advanced skill extraction using NLP techniques
3. Add geolocation enrichment for job locations
4. Support for proxy rotation to avoid rate limiting
5. Implement more comprehensive error handling and logging