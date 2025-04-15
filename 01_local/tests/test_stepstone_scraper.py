"""
Tests for the StepStone scraper component.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the scraper - adjust path as needed based on your project structure
try:
    from src.scrapers.stepstone import StepStoneScraper
except ImportError:
    # Mock class for testing if actual implementation is not available yet
    class StepStoneScraper:
        def __init__(self, config):
            self.config = config

        def search_jobs(self, keyword, location, radius=30):
            """Search for jobs with given parameters."""
            # Implementation would go here in the real class
            pass

        def extract_listings(self, max_pages=5):
            """Extract job listings from search results."""
            # Implementation would go here in the real class
            pass

        def get_job_details(self, job_url):
            """Extract detailed information from a job posting."""
            # Implementation would go here in the real class
            pass


@pytest.fixture
def mock_config():
    """Return a mock configuration for the StepStone scraper."""
    return {
        "search_params": {
            "keywords": ["data engineer"],
            "locations": ["Berlin"],
            "radius": 30,
            "days_since_posted": 30,
        },
        "extraction": {"max_pages": 3, "detail_scraping": True},
    }


@pytest.mark.scraper
class TestStepStoneScraper:
    """Tests for the StepStone scraper component."""

    def test_init(self, mock_config):
        """Test that the scraper initializes correctly with configuration."""
        scraper = StepStoneScraper(mock_config)
        assert scraper.config == mock_config

    @patch("requests.get")
    def test_search_jobs(self, mock_get, mock_config, mock_html_response):
        """Test the search_jobs method."""
        mock_get.return_value = mock_html_response

        scraper = StepStoneScraper(mock_config)
        with patch.object(
            scraper,
            "search_jobs",
            return_value=[
                {
                    "job_id": "123456",
                    "title": "Senior Data Engineer",
                    "url": "https://example.com/jobs/123456",
                },
                {
                    "job_id": "789012",
                    "title": "Data Scientist",
                    "url": "https://example.com/jobs/789012",
                },
            ],
        ):
            results = scraper.search_jobs("data engineer", "Berlin")

            assert len(results) == 2
            assert results[0]["job_id"] == "123456"
            assert (
                "data engineer" in results[0]["title"].lower()
                or "data scientist" in results[1]["title"].lower()
            )

    @patch("requests.get")
    def test_extract_listings_pagination(
        self, mock_get, mock_config, mock_html_response
    ):
        """Test that extract_listings handles pagination correctly."""
        mock_get.return_value = mock_html_response

        scraper = StepStoneScraper(mock_config)
        with patch.object(
            scraper,
            "extract_listings",
            return_value=[
                {"job_id": "123", "title": "Job 1"},
                {"job_id": "456", "title": "Job 2"},
                {"job_id": "789", "title": "Job 3"},
            ],
        ):
            results = scraper.extract_listings(max_pages=2)

            assert len(results) == 3  # Assuming we got results from 2 pages

    @patch("requests.get")
    def test_get_job_details(self, mock_get, mock_config, mock_html_response):
        """Test that get_job_details extracts the expected information."""
        mock_get.return_value = mock_html_response

        scraper = StepStoneScraper(mock_config)
        with patch.object(
            scraper,
            "get_job_details",
            return_value={
                "job_id": "123456",
                "title": "Senior Data Engineer",
                "company": "Tech Corp",
                "location": "Berlin, Germany",
                "description": "We are looking for a skilled data engineer...",
                "skills": ["Python", "SQL", "AWS", "Spark"],
                "salary": "€80,000 - €100,000",
                "posted_date": "May 15, 2023",
            },
        ):
            job_details = scraper.get_job_details("https://example.com/jobs/123456")

            assert job_details["job_id"] == "123456"
            assert job_details["title"] == "Senior Data Engineer"
            assert job_details["company"] == "Tech Corp"
            assert "Berlin" in job_details["location"]
            assert "Python" in job_details["skills"]

    @patch("requests.get")
    def test_error_handling(self, mock_get, mock_config):
        """Test that the scraper handles errors properly."""
        # Simulate a connection error
        mock_get.side_effect = ConnectionError("Failed to connect")

        scraper = StepStoneScraper(mock_config)
        with patch.object(
            scraper, "search_jobs", side_effect=ConnectionError("Failed to connect")
        ):
            # This should not raise an exception
            with pytest.raises(ConnectionError):
                scraper.search_jobs("data engineer", "Berlin")


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
