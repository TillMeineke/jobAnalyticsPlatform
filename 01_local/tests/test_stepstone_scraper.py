"""
Tests for the StepStone scraper component.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the scraper - using the existing implementation
from src.scrapers.stepstone import StepStoneScraper


@pytest.fixture
def mock_html_response():
    """Return a mock HTML response object for testing."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <div class="search-results">
                <article id="job-item-123456" data-genesis-element="CARD" data-at="job-item">
                    <div data-genesis-element="BASE">
                        <a data-at="job-item-title" href="/jobs/senior-data-engineer--123456">Senior Data Engineer</a>
                    </div>
                    <span data-at="job-item-company-name">Tech Corp</span>
                    <span data-at="job-item-location">Berlin, Germany</span>
                    <span data-at="job-item-timeago"><time>vor 3 Tagen</time></span>
                </article>
            </div>
        </body>
    </html>
    """
    return mock_response


@pytest.fixture
def mock_job_detail_response():
    """Return a mock job detail response object for testing."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <div data-at="job-description">
                We are looking for a skilled data engineer with Python and AWS experience.
            </div>
        </body>
    </html>
    """
    return mock_response


class TestStepStoneScraper:
    """Tests for the StepStone scraper component."""

    @patch("selenium.webdriver.Chrome")
    def test_init(self, mock_chrome):
        """Test that the scraper initializes correctly."""
        scraper = StepStoneScraper()
        assert scraper.BASE_URL == "https://www.stepstone.de"
        assert scraper.driver is not None

    @patch("selenium.webdriver.Chrome")
    @patch("selenium.webdriver.Chrome.get")
    @patch("selenium.webdriver.Chrome.find_elements", return_value=[MagicMock()])
    def test_search_jobs(self, mock_find_elements, mock_get, mock_chrome):
        """Test the search_jobs method returns job listings."""
        # Setup mock elements to return job data
        mock_job_element = MagicMock()
        mock_job_element.get_attribute.side_effect = (
            lambda attr: "job-item-123456" if attr == "id" else ""
        )

        mock_title_element = MagicMock()
        mock_title_element.text = "Senior Data Engineer"
        mock_title_element.get_attribute.return_value = (
            "/jobs/senior-data-engineer--123456"
        )

        mock_company_element = MagicMock()
        mock_company_element.text = "Tech Corp"

        mock_location_element = MagicMock()
        mock_location_element.text = "Berlin, Germany"

        mock_posted_element = MagicMock()
        mock_posted_element.find_element.return_value.text = "vor 3 Tagen"

        # Configure mock find_element to return appropriate elements
        mock_job_element.find_element.side_effect = lambda by, value: {
            "div[data-genesis-element='BASE'] a[data-at='job-item-title']": mock_title_element,
            "span[data-at='job-item-company-name']": mock_company_element,
            "span[data-at='job-item-location']": mock_location_element,
            "span[data-at='job-item-timeago']": mock_posted_element,
        }.get(value, MagicMock())

        # Configure the main find_elements to return our mock job element
        mock_find_elements.return_value = [mock_job_element]

        scraper = StepStoneScraper(headless=True)
        job_listings = scraper.search_jobs("data engineer", "Berlin", max_pages=1)

        assert len(job_listings) > 0
        assert job_listings[0]["title"] == "Senior Data Engineer"
        assert job_listings[0]["company"] == "Tech Corp"
        assert "Berlin" in job_listings[0]["location"]

    @patch("selenium.webdriver.Chrome")
    @patch("selenium.webdriver.Chrome.get")
    @patch("selenium.webdriver.Chrome.find_element")
    def test_scrape_job_details(self, mock_find_element, mock_get, mock_chrome):
        """Test that scrape_job_details extracts job description."""
        # Setup mock description element
        mock_desc_element = MagicMock()
        mock_desc_element.text = (
            "We are looking for a skilled data engineer with Python and AWS experience."
        )
        mock_find_element.return_value = mock_desc_element

        scraper = StepStoneScraper(headless=True)
        job_details = scraper.scrape_job_details(
            "https://www.stepstone.de/jobs/data-engineer--123456"
        )

        assert "description" in job_details
        assert "Python" in job_details["description"]
        assert "AWS" in job_details["description"]

    @patch("selenium.webdriver.Chrome")
    @patch("selenium.webdriver.Chrome.quit")
    def test_close(self, mock_quit, mock_chrome):
        """Test that the close method properly closes the driver."""
        scraper = StepStoneScraper(headless=True)
        scraper.close()
        mock_quit.assert_called_once()


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
