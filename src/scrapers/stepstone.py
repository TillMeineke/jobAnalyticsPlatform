"""StepStone job scraper implementation."""

import datetime
import logging
import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from src.scrapers.base import BaseScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StepStoneScraper(BaseScraper):
    """StepStone job platform scraper."""

    BASE_URL = "https://www.stepstone.de"
    SEARCH_URL = f"{BASE_URL}/jobs"

    def __init__(
        self, max_results: int = 100, days_back: int = 30, headless: bool = True
    ):
        """Initialize the StepStone scraper.

        Args:
            max_results: Maximum number of job listings to fetch
            days_back: How far back to search (in days)
            headless: Whether to run the browser in headless mode
        """
        super().__init__(max_results=max_results, days_back=days_back)
        self.headless = headless
        self._setup_browser()

    def _setup_browser(self):
        """Set up the Firefox/Gecko browser for scraping."""
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")

        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options,
        )

    def search(
        self,
        job_titles: List[str],
        location: str,
        max_results: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> List[Dict]:
        """Search for job listings on StepStone.

        Args:
            job_titles: List of job titles to search for
            location: Location to search within
            max_results: Maximum number of results to fetch (overrides init value)
            days_back: How far back to search (overrides init value)

        Returns:
            List of job listings as dictionaries
        """
        max_results = max_results or self.max_results
        days_back = days_back or self.days_back

        all_jobs = []

        # Search for each job title
        for job_title in job_titles:
            logger.info(f"Searching for '{job_title}' in '{location}'")

            # Construct the search URL
            search_query = f"{job_title} {location}"
            encoded_query = search_query.replace(" ", "+")
            url = f"{self.SEARCH_URL}?q={encoded_query}"

            # Use selenium to handle JavaScript-rendered content
            self.driver.get(url)

            # Accept cookies if prompted
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ccmgt_explicit_accept"))
                ).click()
                logger.info("Accepted cookies prompt")
            except Exception as e:
                logger.debug(f"No cookie prompt appeared or couldn't click: {e}")

            # Get all job listings
            jobs = self._extract_job_listings(max_results, days_back)
            all_jobs.extend(jobs)
            logger.info(f"Found {len(jobs)} jobs for '{job_title}' in '{location}'")

            # Limit total results
            if len(all_jobs) >= max_results:
                all_jobs = all_jobs[:max_results]
                break

        return all_jobs

    def _extract_job_listings(self, max_results: int, days_back: int) -> List[Dict]:
        """Extract job listings from search results.

        Args:
            max_results: Maximum number of results to fetch
            days_back: How far back to search (in days)

        Returns:
            List of job listings as dictionaries
        """
        jobs = []
        page_num = 1
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)

        while len(jobs) < max_results:
            # Wait for job listings to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sc-fXqpFg"))
                )
            except Exception as e:
                logger.error(f"Failed to load job listings: {e}")
                break

            # Extract job listings from current page
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            job_elements = soup.select("article.sc-fXqpFg")

            if not job_elements:
                logger.info("No job listings found on this page")
                break

            # Process each job listing
            for job_element in job_elements:
                if len(jobs) >= max_results:
                    break

                try:
                    # Extract job data
                    job_data = self._extract_job_data(job_element)

                    # Check if job is within the time range
                    if job_data.get("published_at"):
                        pub_date = datetime.datetime.fromisoformat(
                            job_data["published_at"]
                        )
                        if pub_date < cutoff_date:
                            logger.debug(
                                f"Skipping job published before cutoff date: {pub_date}"
                            )
                            continue

                    # Add job to the list
                    jobs.append(job_data)

                except Exception as e:
                    logger.error(f"Error extracting job data: {e}")
                    continue

            # Check if there are more pages
            next_button = soup.select_one("button[aria-label='Next']")
            if not next_button or "disabled" in next_button.attrs:
                logger.info("No more pages available")
                break

            # Go to next page
            page_num += 1
            next_url = f"{self.driver.current_url}&page={page_num}"
            self.driver.get(next_url)
            time.sleep(2)  # Wait for page to load

        return jobs

    def _extract_job_data(self, job_element) -> Dict:
        """Extract job data from a job listing element.

        Args:
            job_element: BeautifulSoup element containing job data

        Returns:
            Dictionary containing job data
        """
        # Extract job ID
        job_id = job_element.get("id", "")
        if not job_id:
            link = job_element.select_one("a")
            if link and "href" in link.attrs:
                job_id = link["href"].split("/")[-1].split("?")[0]

        # Extract job title
        title_element = job_element.select_one("h2")
        title = title_element.get_text().strip() if title_element else ""

        # Extract company
        company_element = job_element.select_one("span[data-testid='company-name']")
        company = company_element.get_text().strip() if company_element else ""

        # Extract location
        location_element = job_element.select_one("span[data-testid='job-location']")
        location = location_element.get_text().strip() if location_element else ""

        # Extract URL
        url_element = job_element.select_one("a")
        relative_url = (
            url_element["href"] if url_element and "href" in url_element.attrs else ""
        )
        url = f"{self.BASE_URL}{relative_url}" if relative_url else ""

        # Extract published date
        date_element = job_element.select_one("time")
        published_at = ""
        if date_element and "datetime" in date_element.attrs:
            published_at = date_element["datetime"]
        else:
            # Try to parse from text
            date_text = date_element.get_text().strip() if date_element else ""
            if "today" in date_text.lower():
                published_at = datetime.datetime.now().isoformat()
            elif "yesterday" in date_text.lower():
                published_at = (
                    datetime.datetime.now() - datetime.timedelta(days=1)
                ).isoformat()

        # Create job data dictionary
        job_data = {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "published_at": published_at,
            "scraped_at": datetime.datetime.now().isoformat(),
            "platform": "stepstone",
        }

        return self._normalize_job_data(job_data)

    def get_job_details(self, job_id: str) -> Dict:
        """Get detailed information about a specific job.

        Args:
            job_id: Unique identifier for the job

        Returns:
            Dictionary containing job details
        """
        url = f"{self.BASE_URL}/job/{job_id}"
        logger.info(f"Getting details for job {job_id} from {url}")

        # Load the job page
        self.driver.get(url)

        # Wait for job details to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sc-cjibBx"))
            )
        except Exception as e:
            logger.error(f"Failed to load job details: {e}")
            return {}

        # Parse the page content
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Extract job details
        title_element = soup.select_one("h1")
        title = title_element.get_text().strip() if title_element else ""

        company_element = soup.select_one("span[data-testid='company-name']")
        company = company_element.get_text().strip() if company_element else ""

        location_element = soup.select_one("span[data-testid='job-location']")
        location = location_element.get_text().strip() if location_element else ""

        # Extract job description
        description_element = soup.select_one("div.sc-cjibBx")
        description = (
            description_element.get_text().strip() if description_element else ""
        )

        # Extract published date
        date_element = soup.select_one("time")
        published_at = ""
        if date_element and "datetime" in date_element.attrs:
            published_at = date_element["datetime"]

        # Create job data dictionary
        job_data = {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "published_at": published_at,
            "scraped_at": datetime.datetime.now().isoformat(),
            "platform": "stepstone",
        }

        # Extract additional details
        job_details_items = soup.select(
            "dl.job-listing-details__list dt, dl.job-listing-details__list dd"
        )

        for i in range(0, len(job_details_items) - 1, 2):
            if i + 1 < len(job_details_items):
                key = job_details_items[i].get_text().strip().lower().replace(" ", "_")
                value = job_details_items[i + 1].get_text().strip()
                job_data[key] = value

        return self._normalize_job_data(job_data)

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except:
                pass
