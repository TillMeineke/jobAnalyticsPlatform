# Technical Details

This document provides in-depth technical information about the Job Analytics Platform implementation.

## Web Scraping

### Browser Automation with Selenium

We use Firefox/GeckoDriver for browser automation in our web scrapers for the following reasons:

- **Cross-platform compatibility**: Works consistently across macOS, Linux, and Windows
- **Headless mode support**: Can run without a visible UI for production environments
- **Memory efficiency**: Generally uses less memory than Chrome for long-running scraping tasks
- **Better performance**: Specifically for our use cases with StepStone and similar job sites

#### Setup Requirements

1. **Firefox Browser**:
   - Install the latest Firefox browser on your system
   - Firefox is our standard browser for all scraping operations

2. **GeckoDriver**:
   - We use GeckoDriver as the WebDriver implementation for Firefox
   - The `webdriver-manager` Python package automatically installs the appropriate GeckoDriver version

3. **Python Dependencies**:

   ```bash
   pip install selenium webdriver-manager
   ```

### Scraper Implementation

Our scrapers are configured to use Firefox via the following pattern:

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Set up Firefox options
firefox_options = FirefoxOptions()
if headless:
    firefox_options.add_argument("--headless")

# Additional stability options
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-dev-shm-usage")

# Initialize Firefox driver
driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install()),
    options=firefox_options
)
```

### Testing Scrapers

To test scrapers locally:

```bash
cd /Users/tillmeineke/ML/jobAnalyticsPlatform/01_local
python src/scrapers/stepstone.py --job-title "data engineer" --location "hamburg" --max-pages 1
```

## 🔍 Data Collection

# 🗂️ Project Structure Implementation Plan

We need to create the following directory structure for the job analytics platform:

```
jobAnalyticsPlatform/
├── 01_local/               # Local development environment
│   ├── docker/             # Docker configuration
│   ├── scrapers/           # Data collection modules
│   │   ├── __init__.py
│   │   ├── job_scraper.py  # Main job scraping script
│   │   └── README.md       # Documentation for scrapers
│   ├── dlt_pipelines/      # Data loading pipelines
│   │   ├── __init__.py
│   │   ├── process_jobs.py # Pipeline to process scraped jobs
│   │   └── README.md       # Documentation for pipelines
│   ├── dbt_models/         # Transformation models
│   │   └── README.md       # Documentation for dbt models
│   └── tests/              # Test suite
│       └── README.md       # Documentation for tests
├── data/                   # Data directory
│   ├── bronze/             # Raw data
│   ├── silver/             # Processed data
│   └── gold/               # Analytics-ready data
├── docs/                   # Documentation
├── Makefile                # Automation commands
└── README.md               # Project overview (already exists)
```

We'll implement this structure and basic functionality for the job scraper and data pipeline.

### Scraper Implementation

The platform includes specialized scrapers for major job platforms:

#### StepStone Scraper

```python
# Example implementation pattern
class StepStoneScraper:
    def __init__(self, config):
        self.driver = self._setup_selenium()
        self.config = config
        
    def search_jobs(self, keywords, location, radius=30):
        """Search for jobs with given parameters"""
        # Implementation
        
    def extract_listings(self, max_pages=5):
        """Extract job listings from search results"""
        # Implementation
        
    def get_job_details(self, job_url):
        """Extract detailed information from a job posting"""
        # Implementation
```

Key technical considerations:

- Uses Selenium WebDriver for dynamic content
- Implements rate limiting to avoid being blocked
- Handles pagination and dynamic loading
- Extracts structured data from semi-structured HTML

#### Data Collection Configuration

Scrapers are configured via YAML files:

```yaml
# Example configuration
stepstone:
  search_params:
    keywords: ["data engineer", "python developer"]
    locations: ["Berlin", "Munich", "Remote"]
    days_since_posted: 30
  extraction:
    max_pages: 10
    detail_scraping: true
  scheduling:
    frequency: "daily"
    time: "01:00"
```

## 🧱 Data Pipeline

### Ingestion (Bronze Layer)

The data ingestion layer uses DLT (Data Load Tool) to:

1. Extract data from scrapers
2. Validate against basic schema
3. Load into Bronze tables with minimal transformation

```python
# Example DLT pipeline
import dlt

def job_listing_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="job_listings_bronze",
        destination="postgresql",
        dataset_name="bronze_job_listings"
    )
    
    data = StepStoneScraper(config).extract_listings()
    
    # Load data with source metadata
    pipeline.run(data, 
                table_name="raw_listings",
                write_disposition="append",
                metadata={"source": "stepstone", "extraction_time": datetime.now()}
    )
```

### Transformation (Silver Layer)

The data transformation layer uses dbt to:

1. Clean and standardize data
2. Remove duplicates
3. Apply common schema across sources

Example dbt model (`models/silver/standardized_job_listings.sql`):

```sql
WITH source_data AS (
    SELECT
        id,
        title,
        company,
        location,
        description,
        posted_date,
        salary_min,
        salary_max,
        source,
        url,
        extraction_time
    FROM {{ source('bronze', 'raw_listings') }}
),

cleaned AS (
    SELECT
        id,
        TRIM(REGEXP_REPLACE(title, '\s+', ' ')) AS title,
        TRIM(company) AS company,
        -- Location normalization logic
        CASE
            WHEN location ILIKE '%remote%' THEN 'Remote'
            WHEN location ILIKE '%berlin%' THEN 'Berlin'
            -- More location standardization
            ELSE TRIM(location)
        END AS location,
        description,
        COALESCE(posted_date, extraction_time::DATE - INTERVAL '1 day') AS posted_date,
        -- Salary standardization
        CASE 
            WHEN salary_min < 10000 THEN salary_min * 1000 
            ELSE salary_min
        END AS salary_min,
        CASE 
            WHEN salary_max < 10000 THEN salary_max * 1000 
            ELSE salary_max
        END AS salary_max,
        source,
        url,
        extraction_time
    FROM source_data
)

SELECT 
    -- Generate stable ID for deduplication
    MD5(CONCAT(
        LOWER(title),
        LOWER(company),
        COALESCE(LOWER(location), ''),
        source
    )) AS listing_id,
    *
FROM cleaned
```

### Analytics Models (Gold Layer)

The analytics layer uses dbt to:

1. Create aggregations and metrics
2. Build dimensional models
3. Optimize for dashboard performance

Example dbt model (`models/gold/job_market_trends.sql`):

```sql
SELECT
    DATE_TRUNC('week', posted_date) AS week,
    location,
    COUNT(*) AS job_count,
    AVG(CASE WHEN salary_min > 0 THEN salary_min END) AS avg_min_salary,
    AVG(CASE WHEN salary_max > 0 THEN salary_max END) AS avg_max_salary,
    -- Skills extraction via regex pattern matching
    SUM(CASE WHEN description ILIKE '%python%' THEN 1 ELSE 0 END) AS python_count,
    SUM(CASE WHEN description ILIKE '%sql%' THEN 1 ELSE 0 END) AS sql_count,
    SUM(CASE WHEN description ILIKE '%aws%' THEN 1 ELSE 0 END) AS aws_count,
    SUM(CASE WHEN description ILIKE '%spark%' THEN 1 ELSE 0 END) AS spark_count
FROM {{ ref('standardized_job_listings') }}
GROUP BY 1, 2
```

## 🔄 Workflow Orchestration

### Kestra Workflows

The platform uses Kestra for workflow orchestration:

```yaml
# Example kestra.yml flow
id: job-analytics-daily-pipeline
namespace: job_analytics
labels:
  team: data-engineering
  owner: data-team

tasks:
  - id: stepstone_scraper
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import sys
      sys.path.append("/app")
      from scrapers.stepstone.run import main
      main()
  
  - id: linkedin_scraper
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import sys
      sys.path.append("/app")
      from scrapers.linkedin.run import main
      main()
  
  - id: dlt_bronze_ingest
    type: io.kestra.plugin.scripts.python.Script
    depends:
      - stepstone_scraper
      - linkedin_scraper
    script: |
      import sys
      sys.path.append("/app")
      from pipelines.dlt_pipelines.bronze_ingest import main
      main()
  
  - id: dbt_transform
    type: io.kestra.plugin.scripts.shell.Shell
    depends:
      - dlt_bronze_ingest
    commands:
      - cd /app && dbt run --profiles-dir=profiles --select tag:daily --target prod
```

## 🔐 Data Security

### Authentication and Authorization

- IAM roles for AWS resources
- Database users with limited permissions
- Service account principles

### Data Protection

- PII detection and masking in job data
- Encryption at rest for all storage
- TLS for all communications

## 📊 Dashboard Implementation

### Metabase Dashboards

The platform uses Metabase for visualization with:

1. **Job Market Overview**:
   - Job count trends over time
   - Geographic distribution of opportunities
   - Top employers and industries

2. **Skill Analysis**:
   - In-demand skills trends
   - Skills correlation analysis
   - Salary ranges by skill

3. **Salary Insights**:
   - Salary distributions by role
   - Location-based compensation differences
   - Experience level impact on compensation

## 🧪 Testing Strategy

### Scraper Tests

```python
def test_stepstone_search():
    """Test the search functionality of the StepStone scraper"""
    scraper = StepStoneScraper(test_config)
    results = scraper.search_jobs("data engineer", "Berlin")
    
    assert len(results) > 0
    assert all(["data engineer" in job["title"].lower() for job in results])
```

### Data Quality Tests

The platform uses dbt's testing framework:

```yaml
# models/schema.yml
models:
  - name: standardized_job_listings
    description: "Cleaned and standardized job listings"
    columns:
      - name: listing_id
        tests:
          - unique
          - not_null
      - name: title
        tests:
          - not_null
      - name: company
        tests:
          - not_null
      - name: posted_date
        tests:
          - not_null
          - dbt_utils.date_in_range:
              min_date: '2020-01-01'
              max_date: "{{ dbt_utils.current_timestamp() }}"
```

## 🛠️ DevOps Configuration

### Docker Compose Setup

```yaml
# Example docker-compose.yml structure
version: '3'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_USER: user
      POSTGRES_DB: job_analytics
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  metabase:
    image: metabase/metabase:v0.44.6
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: metabase
      MB_DB_PORT: 5432
      MB_DB_USER: metabase
      MB_DB_PASS: metabase
      MB_DB_HOST: postgres
    depends_on:
      - postgres

  kestra:
    image: kestra/kestra:latest
    environment:
      KESTRA_CONFIGURATION: |
        kestra:
          repository:
            type: postgres
            postgres:
              url: jdbc:postgresql://postgres:5432/kestra
              user: kestra
              password: kestra
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### AWS Infrastructure

Key Terraform components:

```hcl
# Example terraform resource structure
resource "aws_s3_bucket" "data_lake" {
  bucket = "job-analytics-data-lake"
  
  tags = {
    Environment = var.environment
    Project     = "JobAnalytics"
  }
}

resource "aws_rds_cluster" "data_warehouse" {
  cluster_identifier      = "job-analytics-dw"
  engine                  = "aurora-postgresql"
  database_name           = "jobanalytics"
  master_username         = var.db_username
  master_password         = var.db_password
  backup_retention_period = 7
  preferred_backup_window = "07:00-09:00"
  
  tags = {
    Environment = var.environment
    Project     = "JobAnalytics"
  }
}

resource "aws_ecs_cluster" "pipeline_cluster" {
  name = "job-analytics-pipeline"
  
  tags = {
    Environment = var.environment
    Project     = "JobAnalytics"
  }
}
```
