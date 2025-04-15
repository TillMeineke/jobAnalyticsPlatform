"""Test fixtures for data validation."""
import pytest
from datetime import datetime


@pytest.fixture
def sample_bronze_record():
    """Sample bronze layer job listing."""
    return {
        "source_id": "ST12345",
        "title": "Senior Data Engineer",
        "company": "Tech Corp",
        "location": "Berlin, Germany",
        "url": "https://example.com/job/12345",
        "posted_date": "2024-01-15",
        "salary_text": "€65,000 - €85,000",
        "description_html": "<p>Job description here</p>",
        "metadata": {
            "page_number": 1,
            "position": 3,
            "total_results": 150
        },
        "scrape_timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_silver_record():
    """Sample silver layer job listing."""
    return {
        "job_id": "md5_hash_here",
        "title": "Senior Data Engineer",
        "company": "Tech Corp",
        "location": "Berlin, Germany",
        "url": "https://example.com/job/12345",
        "posting_date": datetime(2024, 1, 15),
        "salary_min": 65000.0,
        "salary_max": 85000.0,
        "skills": ["Python", "AWS", "Spark"],
        "experience_years_min": 5,
        "experience_years_max": 8,
        "employment_type": "Full-time",
        "description": "Job description here",
        "source": "StepStone",
        "scrape_timestamp": datetime.utcnow(),
        "processed_timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_job_metrics():
    """Sample job count metrics."""
    return {
        "date": datetime(2024, 1, 15),
        "total_jobs": 100,
        "jobs_by_company": {
            "Tech Corp": 30,
            "Data Ltd": 40,
            "AI Solutions": 30
        },
        "jobs_by_location": {
            "Berlin": 50,
            "Hamburg": 30,
            "Munich": 20
        },
        "jobs_by_role": {
            "Data Engineer": 40,
            "Data Scientist": 35,
            "ML Engineer": 25
        }
    }


@pytest.fixture
def sample_skills_data():
    """Sample skills analytics data."""
    return {
        "skill": "Python",
        "frequency": 500,
        "growth_rate": 0.15,
        "roles": ["Data Engineer", "Data Scientist"],
        "avg_salary": 75000.0
    }


@pytest.fixture
def sample_salary_data():
    """Sample salary trends data."""
    return {
        "role": "Data Engineer",
        "location": "Berlin",
        "avg_salary": 75000.0,
        "median_salary": 72000.0,
        "salary_range": (60000.0, 90000.0),
        "sample_size": 100
    }