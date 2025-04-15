"""StepStone job scraper implementation."""

import logging
from typing import Any, Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.scrapers.details_retriever import DetailsRetriever
from src.scrapers.job_parser import JobParser
from src.scrapers.search_retriever import SearchRetriever


class StepStoneScraper:
    """Scraper for StepStone job listings."""

    def __init__(
        self, search_term: str, location: str, max_pages: int = 1, headless: bool = True
    ):
        """Initialize the scraper.

        Args:
            search_term: Job search term
            location: Location to search in
            max_pages: Maximum number of pages to scrape
            headless: Whether to run browser in headless mode
        """
        self.search_term = search_term
        self.location = location
        self.max_pages = max_pages

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        self.search_retriever = SearchRetriever(self.driver)
        self.details_retriever = DetailsRetriever(self.driver)
        self.job_parser = JobParser()
        self.logger = logging.getLogger(__name__)

    def scrape_jobs(self) -> List[Dict[str, Any]]:
        """Scrape job listings from StepStone.

        Returns:
            List of job listings with detailed information
        """
        try:
            job_listings = []

            # Get job URLs from search pages
            job_urls = self.search_retriever.get_job_urls(
                self.search_term, self.location, self.max_pages
            )

            # Get details for each job
            for url in job_urls:
                try:
                    details = self.details_retriever.get_job_details(url)
                    if details:
                        parsed_job = self.job_parser.parse_job(details)
                        if parsed_job:
                            job_listings.append(parsed_job)
                except Exception as e:
                    self.logger.error(f"Error scraping job details from {url}: {e}")
                    continue

            return job_listings

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return []

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
