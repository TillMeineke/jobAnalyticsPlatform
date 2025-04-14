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
        # Set a larger window size to ensure all elements are visible
        self.driver.set_window_size(1920, 1080)

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

            # Sleep a bit to ensure page loads
            time.sleep(3)

            # Accept cookies if prompted
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
                )
                cookie_button.click()
                logger.info("Accepted cookies prompt")
                time.sleep(1)  # Wait for cookie banner to disappear
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

        # Try to get the total number of results
        try:
            total_results_element = self.driver.find_element(
                By.CSS_SELECTOR, "h1[data-testid='search-results-count']"
            )
            total_text = total_results_element.text
            logger.info(f"Search results header: {total_text}")
        except Exception as e:
            logger.warning(f"Could not find total results count: {e}")

        while len(jobs) < max_results:
            # Take a screenshot for debugging
            screenshot_file = f"search_page_{page_num}.png"
            try:
                self.driver.save_screenshot(screenshot_file)
                logger.info(f"Saved screenshot to {screenshot_file}")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {e}")

            # Wait for job listings to load - try different potential selectors
            try:
                # Look for job listings container - try multiple possible selectors
                for selector in [
                    "article.job-element",
                    "div[data-testid='job-item']",
                    "div.sc-iBdmCd",
                    "li.sc-jrcTuL",
                    "article",
                    "[data-testid='job-item']",
                ]:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"Found job listings with selector: {selector}")
                        job_elements_selector = selector
                        break
                    except Exception:
                        continue
                else:
                    # If no selector worked, log the page source for debugging
                    logger.error("Could not find job elements with any known selector")
                    logger.debug(f"Page source: {self.driver.page_source[:1000]}...")
                    break
            except Exception as e:
                logger.error(f"Failed to load job listings: {e}")
                break

            # Extract job listings from current page
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Try multiple selectors to find job listings
            job_elements = []
            for selector in [
                "article.job-element",
                "div[data-testid='job-item']",
                "div.sc-iBdmCd",
                "li.sc-jrcTuL",
                "article",
                "[data-testid='job-item']",
            ]:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    logger.info(
                        f"Found {len(elements)} job elements with selector: {selector}"
                    )
                    break

            if not job_elements:
                logger.warning("No job listings found on this page")
                # Let's try to find any potential job elements for debugging
                for tag in ["article", "div", "li"]:
                    elements = soup.find_all(tag)
                    logger.debug(f"Found {len(elements)} {tag} elements")
                    # Look at first few elements to see if they might contain job info
                    for i, elem in enumerate(elements[:5]):
                        if i == 0:
                            logger.debug(
                                f"Sample {tag} classes: {elem.get('class', [])}"
                            )
                break

            # Process each job listing
            for job_element in job_elements:
                if len(jobs) >= max_results:
                    break

                try:
                    # Extract job data
                    job_data = self._extract_job_data(job_element)

                    # Skip jobs without an ID
                    if not job_data.get("id"):
                        logger.warning("Skipping job without ID")
                        continue

                    # Check if job is within the time range
                    if job_data.get("published_at"):
                        try:
                            pub_date = datetime.datetime.fromisoformat(
                                job_data["published_at"]
                            )
                            if pub_date < cutoff_date:
                                logger.debug(
                                    f"Skipping job published before cutoff date: {pub_date}"
                                )
                                continue
                        except ValueError:
                            # If we can't parse the date, still include the job
                            pass

                    # Add job to the list
                    jobs.append(job_data)
                    logger.debug(
                        f"Added job: {job_data['title']} at {job_data['company']}"
                    )

                except Exception as e:
                    logger.error(f"Error extracting job data: {e}")
                    continue

            if len(jobs) >= max_results:
                break

            # Look for next page button
            try:
                # Try different selectors for pagination
                next_button = None
                for next_selector in [
                    "button[aria-label='Next']",
                    "a[data-at='pagination-next']",
                    "li.next a",
                    "a[rel='next']",
                    "[aria-label='Next page']",
                ]:
                    next_buttons = soup.select(next_selector)
                    if next_buttons and "disabled" not in next_buttons[0].attrs:
                        next_button = next_buttons[0]
                        logger.info(f"Found next button with selector: {next_selector}")
                        break

                if not next_button or "disabled" in next_button.attrs:
                    logger.info("No more pages available")
                    break

                # Go to next page
                page_num += 1
                if "href" in next_button.attrs:
                    next_url = next_button["href"]
                    if not next_url.startswith("http"):
                        next_url = f"{self.BASE_URL}{next_url}"
                else:
                    next_url = f"{self.driver.current_url}&page={page_num}"

                logger.info(f"Going to next page: {page_num}, URL: {next_url}")
                self.driver.get(next_url)
                time.sleep(3)  # Wait for page to load

            except Exception as e:
                logger.error(f"Error navigating to next page: {e}")
                break

        return jobs

    def _extract_job_data(self, job_element) -> Dict:
        """Extract job data from a job listing element.

        Args:
            job_element: BeautifulSoup element containing job data

        Returns:
            Dictionary containing job data
        """
        # Debugging
        element_classes = job_element.get("class", [])
        element_id = job_element.get("id", "")
        logger.debug(
            f"Processing job element with classes: {element_classes}, id: {element_id}"
        )

        # Extract job ID from various possible sources
        job_id = element_id
        if not job_id:
            # Try to get ID from data attribute
            job_id = job_element.get("data-job-id", "")

        if not job_id:
            # Try to extract from URL in link
            link = job_element.select_one("a")
            if link and "href" in link.attrs:
                href = link["href"]
                # Extract job ID from URL patterns like /job/12345 or ?jobId=12345
                if "/job/" in href:
                    job_id = href.split("/job/")[-1].split("/")[0].split("?")[0]
                elif "jobId=" in href:
                    job_id = href.split("jobId=")[-1].split("&")[0]

        # Extract job title using various selectors
        title = ""
        for title_selector in [
            "h2",
            "h3",
            "[data-testid='job-title']",
            ".job-title",
            ".listing-title",
        ]:
            title_element = job_element.select_one(title_selector)
            if title_element:
                title = title_element.get_text().strip()
                break

        # Extract company
        company = ""
        for company_selector in [
            "span[data-testid='company-name']",
            ".company-name",
            "[data-testid='company']",
            ".listing-company",
        ]:
            company_element = job_element.select_one(company_selector)
            if company_element:
                company = company_element.get_text().strip()
                break

        # Extract location
        location = ""
        for location_selector in [
            "span[data-testid='job-location']",
            ".job-location",
            "[data-testid='location']",
            ".listing-location",
        ]:
            location_element = job_element.select_one(location_selector)
            if location_element:
                location = location_element.get_text().strip()
                break

        # Extract URL
        url = ""
        url_element = job_element.select_one("a")
        if url_element and "href" in url_element.attrs:
            relative_url = url_element["href"]
            # Check if it's a relative or absolute URL
            if relative_url.startswith("http"):
                url = relative_url
            else:
                url = f"{self.BASE_URL}{relative_url}"

        # Extract published date
        published_at = ""
        for date_selector in [
            "time",
            "[data-testid='job-date']",
            ".job-date",
            ".listing-date",
        ]:
            date_element = job_element.select_one(date_selector)
            if date_element:
                if date_element.get("datetime"):
                    published_at = date_element["datetime"]
                    break
                else:
                    # Try to parse from text
                    date_text = date_element.get_text().strip()
                    if date_text:
                        if "today" in date_text.lower():
                            published_at = datetime.datetime.now().isoformat()
                            break
                        elif "yesterday" in date_text.lower():
                            published_at = (
                                datetime.datetime.now() - datetime.timedelta(days=1)
                            ).isoformat()
                            break
                        else:
                            published_at = date_text  # Store as text if we can't parse

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

        logger.debug(f"Extracted job data: {job_data}")
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
        time.sleep(2)  # Wait for page to load

        # Wait for job details to load - try different potential selectors
        try:
            for selector in [
                "div.job-detail",
                "div[data-testid='job-details']",
                "article.job-element",
                "div.job-description",
            ]:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found job details with selector: {selector}")
                    break
                except Exception:
                    continue
            else:
                logger.error("Could not find job details with any known selector")
        except Exception as e:
            logger.error(f"Failed to load job details: {e}")
            return {}

        # Save screenshot for debugging
        try:
            self.driver.save_screenshot(f"job_detail_{job_id}.png")
        except Exception as e:
            logger.warning(f"Could not save screenshot: {e}")

        # Parse the page content
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Extract job details - try different selectors for each field

        # Title
        title = ""
        for title_selector in ["h1", "h1[data-testid='job-title']", ".job-title"]:
            title_element = soup.select_one(title_selector)
            if title_element:
                title = title_element.get_text().strip()
                break

        # Company
        company = ""
        for company_selector in [
            "span[data-testid='company-name']",
            ".company-name",
            "div[data-testid='company']",
        ]:
            company_element = soup.select_one(company_selector)
            if company_element:
                company = company_element.get_text().strip()
                break

        # Location
        location = ""
        for location_selector in [
            "span[data-testid='job-location']",
            ".job-location",
            "div[data-testid='location']",
        ]:
            location_element = soup.select_one(location_selector)
            if location_element:
                location = location_element.get_text().strip()
                break

        # Description
        description = ""
        for desc_selector in [
            "div.job-description",
            "div[data-testid='job-description']",
            "div.job-detail-description",
            "section[data-testid='description']",
        ]:
            description_element = soup.select_one(desc_selector)
            if description_element:
                description = description_element.get_text().strip()
                break

        # Published date
        published_at = ""
        for date_selector in ["time", "span[data-testid='job-date']", ".job-date"]:
            date_element = soup.select_one(date_selector)
            if date_element:
                if date_element.get("datetime"):
                    published_at = date_element["datetime"]
                    break
                else:
                    date_text = date_element.get_text().strip()
                    if "today" in date_text.lower():
                        published_at = datetime.datetime.now().isoformat()
                        break
                    elif "yesterday" in date_text.lower():
                        published_at = (
                            datetime.datetime.now() - datetime.timedelta(days=1)
                        ).isoformat()
                        break

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

        # Extract additional details - try different selectors
        for details_selector in [
            "dl.job-listing-details__list",
            "div.job-facts",
            "div[data-testid='job-facts']",
        ]:
            job_details_items = soup.select(
                f"{details_selector} dt, {details_selector} dd"
            )

            if job_details_items:
                logger.info(
                    f"Found job details items with selector: {details_selector}"
                )
                for i in range(0, len(job_details_items) - 1, 2):
                    if i + 1 < len(job_details_items):
                        key = (
                            job_details_items[i]
                            .get_text()
                            .strip()
                            .lower()
                            .replace(" ", "_")
                        )
                        value = job_details_items[i + 1].get_text().strip()
                        job_data[key] = value
                break

        return self._normalize_job_data(job_data)

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except:
                pass
