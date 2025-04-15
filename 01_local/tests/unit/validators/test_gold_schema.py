"""Tests for gold layer data validation."""

from datetime import datetime
from typing import Dict, List

import pytest
from pydantic import BaseModel


class JobCountMetrics(BaseModel):
    """Schema for job count aggregations."""

    date: datetime
    total_jobs: int
    jobs_by_company: Dict[str, int]
    jobs_by_location: Dict[str, int]
    jobs_by_role: Dict[str, int]


class SkillsAnalytics(BaseModel):
    """Schema for skills analysis."""

    skill: str
    frequency: int
    growth_rate: float
    roles: List[str]
    avg_salary: float


class SalaryTrends(BaseModel):
    """Schema for salary analytics."""

    role: str
    location: str
    avg_salary: float
    median_salary: float
    salary_range: tuple[float, float]
    sample_size: int


def test_job_count_metrics(sample_job_metrics):
    """Test job count metrics schema."""
    try:
        JobCountMetrics(**sample_job_metrics)
    except Exception as e:
        pytest.fail(f"Job metrics validation failed: {e}")


def test_skills_analytics(sample_skills_data):
    """Test skills analytics schema."""
    try:
        SkillsAnalytics(**sample_skills_data)
    except Exception as e:
        pytest.fail(f"Skills analytics validation failed: {e}")


def test_salary_trends(sample_salary_data):
    """Test salary trends schema."""
    try:
        SalaryTrends(**sample_salary_data)
    except Exception as e:
        pytest.fail(f"Salary trends validation failed: {e}")


def test_metrics_consistency(sample_job_metrics):
    """Test that job count metrics are consistent."""
    total = sample_job_metrics["total_jobs"]
    by_company = sum(sample_job_metrics["jobs_by_company"].values())
    by_location = sum(sample_job_metrics["jobs_by_location"].values())
    assert total == by_company == by_location
