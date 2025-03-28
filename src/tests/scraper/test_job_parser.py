"""
Tests for the JobParser class.
"""

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup, Tag

from src.scraper.job_parser import JobParser


class TestJobParser(unittest.TestCase):
    """Test cases for the JobParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = JobParser()
        
        # Sample HTML for job card testing
        self.job_card_html = """
            <a class="res-1foik6i" data-at="job-item-title" href="/stellenangebote--Data-Scientist-Hamburg-Test-Company--123456-inline.html">
                <div class="res-1ewaude">
                    <div class="res-vurnku">
                        <div class="res-nehv70">Data Scientist (m/w/d)</div>
                    </div>
                </div>
            </a>
        """
        self.job_card = BeautifulSoup(self.job_card_html, "html.parser").find("a")
        
        # Sample HTML for parent article
        self.article_html = """
            <article>
                <a class="res-1foik6i" data-at="job-item-title" href="/stellenangebote--Data-Scientist-Hamburg-Test-Company--123456-inline.html">
                    <div>Data Scientist (m/w/d)</div>
                </a>
                <div data-at="job-item-company-name">Test Company GmbH</div>
                <div data-at="job-item-location">Hamburg</div>
                <span data-at="job-item-timeago">
                    <time>vor 3 Tagen</time>
                </span>
            </article>
        """
        self.article = BeautifulSoup(self.article_html, "html.parser").find("article")
        
        # Sample HTML for job details page
        self.job_details_html = """
            <html>
                <body>
                    <h1>Senior Data Scientist (m/w/d)</h1>
                    <span data-at="job-header-company">Test Company GmbH</span>
                    <div data-at="job-description">
                        Looking for a data scientist with Python, SQL, and machine learning experience.
                        Required skills: Python, pandas, scikit-learn, SQL, Docker.
                        Nice to have: AWS, Spark
                    </div>
                    <span data-at="job-header-salary">€60.000 - €75.000 pro Jahr</span>
                    <span data-at="job-header-employment-type">Vollzeit</span>
                </body>
            </html>
        """
        self.job_details_soup = BeautifulSoup(self.job_details_html, "html.parser")
    
    def test_extract_job_id(self):
        """Test extracting job ID from URL."""
        # Test normal case
        url = "/stellenangebote--Data-Scientist-Hamburg-Test-Company--123456-inline.html"
        job_id = self.parser._extract_job_id(url)
        self.assertEqual(job_id, "123456")
        
        # Test edge case without ID pattern
        url = "/jobs/data-scientist-hamburg.html"
        job_id = self.parser._extract_job_id(url)
        self.assertEqual(job_id, "data-scientist-hamburg")
        
    def test_find_parent_article(self):
        """Test finding parent article element."""
        # Setup: Create a nested structure
        soup = BeautifulSoup(self.article_html, "html.parser")
        job_element = soup.find("a")
        
        # Call method
        parent = self.parser._find_parent_article(job_element)
        
        # Assert
        self.assertIsNotNone(parent)
        self.assertEqual(parent.name, "article")
        
    def test_extract_company_name(self):
        """Test extracting company name from article."""
        # Call method
        company_name = self.parser._extract_company_name(self.article)
        
        # Assert
        self.assertEqual(company_name, "Test Company GmbH")
        
    def test_extract_location(self):
        """Test extracting job location from article."""
        # Call method
        location = self.parser._extract_location(self.article)
        
        # Assert
        self.assertEqual(location, "Hamburg")
        
    def test_extract_posting_date(self):
        """Test extracting posting date from article."""
        # Call method
        posting_date = self.parser._extract_posting_date(self.article)
        
        # Assert
        self.assertEqual(posting_date, "vor 3 Tagen")
        
    @patch("src.scraper.job_parser.JobParser._find_parent_article")
    def test_parse_job_card(self, mock_find_parent):
        """Test parsing a job card."""
        # Setup mock
        mock_find_parent.return_value = self.article
        
        # Call method
        job_data = self.parser.parse_job_card(self.job_card)
        
        # Assert
        self.assertIsNotNone(job_data)
        self.assertEqual(job_data["job_title"], "Data Scientist (m/w/d)")
        self.assertEqual(job_data["job_url"], "/stellenangebote--Data-Scientist-Hamburg-Test-Company--123456-inline.html")
        self.assertEqual(job_data["company_name"], "Test Company GmbH")
        self.assertEqual(job_data["location"], "Hamburg")
        self.assertEqual(job_data["posting_date"], "vor 3 Tagen")
        
    def test_extract_skills(self):
        """Test extracting skills from job description."""
        # Test with various skill mentions
        description = """
        We are looking for a Data Scientist with:
        - Python and pandas experience
        - SQL knowledge
        - Experience with machine learning
        - Docker and Kubernetes 
        """
        
        # Call method
        skills = self.parser._extract_skills(description)
        
        # Assert skills are found
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertIn("machine learning", skills)
        self.assertIn("docker", skills)
        self.assertIn("kubernetes", skills)
        
    def test_parse_salary(self):
        """Test parsing salary text into structured data."""
        # Test with salary range in EUR per year
        salary_text = "€60.000 - €75.000 pro Jahr"
        
        # Call method
        salary_data = self.parser._parse_salary(salary_text)
        
        # Assert
        self.assertEqual(salary_data["raw"], salary_text)
        self.assertEqual(salary_data["min_salary"], 60000.0)
        self.assertEqual(salary_data["max_salary"], 75000.0)
        self.assertEqual(salary_data["avg_salary"], 67500.0)
        self.assertEqual(salary_data["currency"], "€")
        self.assertEqual(salary_data["frequency"], "yearly")
        
    def test_parse_job_details(self):
        """Test parsing a job details page."""
        # Call method
        job_details = self.parser.parse_job_details(self.job_details_soup)
        
        # Assert
        self.assertIsNotNone(job_details)
        self.assertEqual(job_details["job_title"], "Senior Data Scientist (m/w/d)")
        self.assertEqual(job_details["company_name"], "Test Company GmbH")
        self.assertTrue("description" in job_details)
        self.assertTrue("skills" in job_details)
        self.assertTrue("python" in job_details["skills"])
        self.assertTrue("sql" in job_details["skills"])
        self.assertTrue("docker" in job_details["skills"])
        self.assertEqual(job_details["employment_type"], "Vollzeit")
        
        # Check salary parsing
        self.assertEqual(job_details["salary"]["min_salary"], 60000.0)
        self.assertEqual(job_details["salary"]["max_salary"], 75000.0)


if __name__ == "__main__":
    unittest.main()