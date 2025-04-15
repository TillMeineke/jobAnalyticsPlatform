# 📦 Source Code

This directory contains the shared source code used by both the local and cloud pipelines for the Job Analytics Platform.

## 📂 Directory Structure

```
.
├── scrapers/                    # Job listing scrapers
│   ├── stepstone.py             # StepStone scraper
│   ├── linkedin.py              # LinkedIn scraper
│   ├── indeed.py                # Indeed scraper
│   ├── xing.py                  # Xing scraper
│   ├── base.py                  # Base scraper class
│   └── README.md                # Scraper documentation
├── utils/                       # Utility functions
│   ├── logging_utils.py         # Logging utilities
│   ├── data_validation.py       # Data validation utilities
│   └── README.md                # Utilities documentation
└── tests/                       # Unit and integration tests
    ├── test_scrapers/           # Tests for scrapers
    └── test_utils/              # Tests for utilities
```

## 🕸️ Scrapers

The `scrapers` directory contains modules for extracting job data from various online job platforms:

- **StepStone**: Main target for initial implementation
- **LinkedIn**: For professional job listings
- **Indeed**: For general job listings
- **Xing**: For German market job listings

Each scraper implements a common interface defined in the base scraper class, making it easy to add new platforms.

### Common Parameters

All scrapers support the following parameters:

- `job_titles`: List of job titles to search for
- `location`: Location to search within
- `max_results`: Maximum number of results to fetch
- `days_back`: How far back to search (in days)

## 🔧 Utilities

The `utils` directory contains shared utility functions used across the project:

- **Logging**: Standardized logging configuration
- **Data Validation**: Functions to validate job data
- **Date Handling**: Utilities for date parsing and manipulation

## 🧪 Testing

The `tests` directory contains unit and integration tests for all components:

- **Unit Tests**: For testing individual functions and classes
- **Integration Tests**: For testing components working together

Run the tests with:

```bash
pytest src/tests/
```

## 🔄 Development Workflow

1. **Adding a new scraper**:
   - Create a new file in the `scrapers` directory
   - Inherit from the base scraper class
   - Implement the required methods
   - Add unit tests

2. **Using the scrapers**:

   ```python
   from src.scrapers.stepstone import StepStoneScraper
   
   scraper = StepStoneScraper()
   jobs = scraper.search(
       job_titles=["Data Engineer", "Data Scientist"],
       location="Berlin",
       max_results=100
   )
   ```

3. **Logging**:

   ```python
   from src.utils.logging_utils import setup_logger
   
   logger = setup_logger(__name__)
   logger.info("Starting the scraping process")
   ```

## 📚 Additional Documentation

- [Scraper Documentation](./scrapers/README.md)
- [Utilities Documentation](./utils/README.md)
