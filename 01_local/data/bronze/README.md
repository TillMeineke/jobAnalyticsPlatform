# 🥉 Bronze Layer - Raw Data

This directory contains raw job listings data scraped from various sources.

## 🔄 Data Flow

Source → **Bronze** → Silver → Gold

## 📋 Schema

Files are saved in JSON format with naming convention:
`{source}_{job_type}_{location}_{timestamp}.json`

Example: `stepstone_data_engineer_berlin_20240520_124532.json`

### Raw Job Listing Fields
- `source_id`: Original ID from the job platform
- `title`: Raw job title as posted
- `company`: Company name as displayed
- `location`: Raw location string
- `url`: URL to the job posting
- `posted_date`: Date as provided by source
- `salary_text`: Raw salary information
- `description_html`: Original HTML job description
- `metadata`: Additional source-specific fields
  - `page_number`: Page in search results
  - `position`: Position on page
  - `total_results`: Total search results
- `scrape_timestamp`: When the data was collected (UTC)

### Supported Sources
- StepStone
- LinkedIn (planned)
- Indeed (planned)
- Xing (planned)
