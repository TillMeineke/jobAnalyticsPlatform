"""
Tests for the StepstoneScraper class.
"""

import unittest
from unittest.mock import patch, MagicMock

import requests
from bs4 import BeautifulSoup

from src.scraper.stepstone_scraper import StepstoneScraper


class TestStepstoneScraper(unittest.TestCase):
    """Test cases for the StepstoneScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = StepstoneScraper()
    
    def test_init(self):
        """Test the initialization of the StepstoneScraper."""
        self.assertEqual(self.scraper.base_url, "https://www.stepstone.de/jobs")
        self.assertIsNotNone(self.scraper.headers)
        self.assertIsNotNone(self.scraper.logger)
        self.assertIsNotNone(self.scraper.parser)
        
    @patch("src.scraper.stepstone_scraper.requests.get")
    def test_make_request(self, mock_get):
        """Test the _make_request method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.scraper._make_request("https://www.stepstone.de/jobs/test")
        
        # Assert the result
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with(
            "https://www.stepstone.de/jobs/test", 
            headers=self.scraper.headers, 
            timeout=10
        )
        
    @patch("src.scraper.stepstone_scraper.requests.get")
    def test_make_request_error(self, mock_get):
        """Test the _make_request method with an error."""
        # Setup mock response
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        
        # Call the method
        result = self.scraper._make_request("https://www.stepstone.de/jobs/test")
        
        # Assert the result
        self.assertIsNone(result)
        
    @patch("src.scraper.stepstone_scraper.StepstoneScraper._make_request")
    @patch("src.scraper.stepstone_scraper.StepstoneScraper._extract_job_listings")
    def test_search_jobs(self, mock_extract_listings, mock_make_request):
        """Test the search_jobs method."""
        # Setup mocks
        mock_response = MagicMock()
        mock_make_request.return_value = mock_response
        
        mock_listings = [
            {"job_id": "1", "job_title": "Test Job 1"},
            {"job_id": "2", "job_title": "Test Job 2"}
        ]
        mock_extract_listings.return_value = mock_listings
        
        # Call the method
        result = self.scraper.search_jobs("data-scientist", "hamburg", max_pages=1)
        
        # Assert the result
        self.assertEqual(result, mock_listings)
        mock_make_request.assert_called_once()
        mock_extract_listings.assert_called_once()
        
    @patch("src.scraper.stepstone_scraper.BeautifulSoup")
    @patch("src.scraper.stepstone_scraper.StepstoneScraper._make_request")
    def test_get_job_details(self, mock_make_request, mock_bs):
        """Test the get_job_details method."""
        # Setup mocks
        mock_response = MagicMock()
        mock_make_request.return_value = mock_response
        
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        
        mock_job_details = {"job_title": "Test Job", "company_name": "Test Company"}
        self.scraper.parser.parse_job_details = MagicMock(return_value=mock_job_details)
        
        # Call the method
        result = self.scraper.get_job_details("/test-job-url")
        
        # Assert the result
        self.assertEqual(result, mock_job_details)
        mock_make_request.assert_called_once_with("https://www.stepstone.de/test-job-url")


if __name__ == "__main__":
    unittest.main()