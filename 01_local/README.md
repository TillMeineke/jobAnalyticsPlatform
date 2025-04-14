# 🏠 Local Development Environment

This directory contains all components needed for local development and testing of the job analytics platform.

## 📂 Directory Structure

- `src/` - Source code for data collection and processing
  - `scrapers/` - Web scrapers for different job platforms
  - `pipeline/` - Data processing pipeline components
  - `database/` - Database models and utilities
  - `scripts/` - Utility scripts

## 🤖 Web Scrapers

### StepStone Scraper

The StepStone scraper has two main components:

1. **Search Retriever**
   - Collects basic job listing information
   - Stores data in SQLite database

2. **Details Retriever**
   - Fetches comprehensive job details
   - Updates existing records in the database

### Running the Scrapers

#### Prerequisites

1. Ensure geckodriver is installed (handled automatically by Makefile)
2. Create and configure `.env` file with login credentials (if needed)

#### Search Retriever

```bash
make search-jobs ARGS="--job-titles 'Data Engineer' 'Data Scientist' --location 'Deutschland'"
```

This will:

- Search for multiple job titles
- Store basic job information in the SQLite database
- Continue running until interrupted (Ctrl+C)

#### Details Retriever

```bash
make fetch-details ARGS="--max-updates 10 --sleep-time 30"
```

This will:

- Fetch detailed information for jobs in the database
- Process 10 jobs per batch
- Wait 30 seconds between batches

## 💾 Database

The scrapers store data in an SQLite database named `stepstone_jobs.db` in the project root directory.

### Database Schema

```
Table: jobs
- job_id (TEXT, PRIMARY KEY): Unique identifier for the job
- title (TEXT): Job title
- company (TEXT): Company name
- location (TEXT): Job location
- url (TEXT): URL to the job posting
- salary (TEXT): Salary information (if available)
- posted (TEXT): When the job was posted
- source (TEXT): Source platform (e.g., "StepStone")
- scraped (INTEGER): Flag indicating if detailed info was scraped (0/1)
- scraped_at (TEXT): Timestamp of when job was scraped
- description (TEXT): Full job description
- created_at (TEXT): Record creation timestamp

Table: job_skills
- id (INTEGER, PRIMARY KEY): Auto-incrementing ID
- job_id (TEXT): Reference to jobs table
- skill (TEXT): Skill name
- UNIQUE(job_id, skill): Prevents duplicate skills per job
```

### Querying the Database

You can query the database using SQLite:

```bash
sqlite3 stepstone_jobs.db

# View all tables
.tables

# Count total jobs
SELECT COUNT(*) FROM jobs;

# View jobs with details
SELECT job_id, title, company, location FROM jobs WHERE scraped = 1;

# View job skills
SELECT j.title, s.skill 
FROM jobs j 
JOIN job_skills s ON j.job_id = s.job_id 
LIMIT 10;
```

## 🐳 Docker

Local services are managed using Docker Compose:

```bash
# Build and start services
make setup-local
make run-local

# Stop services
make clean-local
```

## 🧪 Testing

Run tests for the local components:

```bash
make test-local
```

## 📝 Development Workflow

1. Run the scrapers to collect data
2. Process the data using the pipeline
3. Visualize using local Metabase instance

## 🔄 Data Flow

```
Web Scraping → SQLite (Bronze) → Transformation → PostgreSQL (Silver) → Analytics → Metabase (Gold)
```

## 🛠️ Troubleshooting

### Common Issues

1. **Geckodriver compatibility warnings**
   - The system automatically installs the correct version (0.36.0)
   - If warnings persist, run `make clean-geckodriver && make setup-geckodriver`

2. **Login failures**
   - Ensure your `.env` file contains valid credentials:

     ```
     STEPSTONE_EMAIL=your.email@example.com
     STEPSTONE_PASSWORD=your_password
     ```

3. **No jobs found**
   - Try different job titles or locations
   - Check if the site structure has changed (may require scraper updates)

4. **Rate limiting**
   - Increase sleep time between requests: `--sleep-time 120`
