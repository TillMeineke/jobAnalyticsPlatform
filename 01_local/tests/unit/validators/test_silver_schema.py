"""Tests for silver layer data validation."""

from datetime import datetime
from typing import List

import pytest
from pydantic import BaseModel


class SilverJobListing(BaseModel):
    """Schema for processed job listings."""

    job_id: str
    title: str
    company: str
    location: str
    url: str
    posting_date: datetime
    salary_min: float | None
    salary_max: float | None
    skills: List[str]
    experience_years_min: int | None
    experience_years_max: int | None
    employment_type: str
    description: str
    source: str
    scrape_timestamp: datetime
    processed_timestamp: datetime


def test_validate_silver_record(sample_silver_record):
    """Test that a silver record matches the expected schema."""
    try:
        SilverJobListing(**sample_silver_record)
    except Exception as e:
        pytest.fail(f"Silver record validation failed: {e}")


def test_salary_range_valid(sample_silver_record):
    """Test that salary ranges are valid when present."""
    if sample_silver_record.get("salary_min") and sample_silver_record.get(
        "salary_max"
    ):
        assert sample_silver_record["salary_min"] <= sample_silver_record["salary_max"]


def test_experience_range_valid(sample_silver_record):
    """Test that experience ranges are valid when present."""
    if sample_silver_record.get("experience_years_min") and sample_silver_record.get(
        "experience_years_max"
    ):
        assert (
            sample_silver_record["experience_years_min"]
            <= sample_silver_record["experience_years_max"]
        )
