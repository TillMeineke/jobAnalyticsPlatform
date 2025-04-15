"""Tests for bronze layer data validation."""

from datetime import datetime

import pytest
from pydantic import BaseModel


class BronzeJobListing(BaseModel):
    """Schema for raw job listings."""

    source_id: str
    title: str
    company: str
    location: str
    url: str
    posted_date: str
    salary_text: str | None
    description_html: str
    metadata: dict
    scrape_timestamp: datetime


def test_validate_bronze_record(sample_bronze_record):
    """Test that a bronze record matches the expected schema."""
    try:
        BronzeJobListing(**sample_bronze_record)
    except Exception as e:
        pytest.fail(f"Bronze record validation failed: {e}")


def test_required_fields_present(sample_bronze_record):
    """Test that all required fields are present."""
    required_fields = {
        "source_id",
        "title",
        "company",
        "location",
        "url",
        "posted_date",
        "description_html",
        "metadata",
        "scrape_timestamp",
    }
    assert all(field in sample_bronze_record for field in required_fields)
