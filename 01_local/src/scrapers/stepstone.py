"""StepStone job scraper implementation."""

import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

# Configure logging with colors
import colorlog
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class StepStoneScraper:
    """StepStone job scraper class."""

    BASE_URL = "https://www.stepstone.de"
    SEARCH_URL = f"{BASE_URL}/jobs"
    LOGIN_URL = f"{BASE_URL}/5/login"

    def __init__(
        self,
        max_results: int = 100,
        headless: bool = True,
        login: bool = True,  # Default to True for login
        max_runtime_seconds: Optional[int] = None,
        sort_order: str = "desc",
    ):
        self.max_results = max_results
        self.headless = headless
        self.should_login = login
        self.max_runtime_seconds = max_runtime_seconds
        self.sort_order = sort_order.lower()
        self.driver = self._setup_driver()

        if self.should_login:
            self._login()

    def _setup_driver(self) -> webdriver.Firefox:
        """Set up the Firefox web driver."""
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")

        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")

        driver = webdriver.Firefox(options=firefox_options)
        return driver

    def _login(self) -> bool:
        """Log in to StepStone account."""
        email = os.getenv("STEPSTONE_EMAIL")
        password = os.getenv("STEPSTONE_PASSWORD")

        if not email or not password:
            logger.warning(
                "STEPSTONE_EMAIL or STEPSTONE_PASSWORD not set, skipping login"
            )
            return False

        logger.info("Logging in to StepStone...")
        self.driver.get(self.LOGIN_URL)

        try:
            # Accept cookies if prompted
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
                ).click()
                logger.info("Accepted cookies")
            except (TimeoutException, NoSuchElementException):
                logger.debug("No cookie banner found")

            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.send_keys(email)

            # Find and click continue button
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            continue_button.click()

            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.send_keys(password)

            # Find and click login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()

            # Wait for login to complete
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: any(
                        path in driver.current_url
                        for path in ["/dashboard", "/jobs", "/profile"]
                    )
                )
                logger.info("Successfully logged in to StepStone")
                return True
            except TimeoutException:
                logger.error("Login failed - could not verify successful login")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def search(
        self, job_titles: List[str], location: str
    ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Search for jobs and return results with related terms."""
        start_time = time.time()
        all_jobs = []
        all_related_terms = []

        for job_title in job_titles:
            logger.info(f"Searching for {job_title} in {location}...")

            sort_param = "date" if self.sort_order == "desc" else "date_asc"
            search_query = (
                f"?what={quote(job_title)}&where={quote(location)}&sort={sort_param}"
            )
            url = f"{self.SEARCH_URL}{search_query}"

            self.driver.get(url)

            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
                ).click()
            except (TimeoutException, NoSuchElementException):
                pass

            total_jobs = self._extract_total_jobs()
            logger.info(f"Found {total_jobs} total jobs")

            jobs, related_terms = self._parse_search_results()

            logger.info(f"Extracted {len(jobs)} job listings")
            all_jobs.extend(jobs)
            all_related_terms.extend(related_terms)

            if (
                self.max_runtime_seconds
                and (time.time() - start_time) > self.max_runtime_seconds
            ):
                logger.info(
                    f"Reached maximum runtime of {self.max_runtime_seconds} seconds"
                )
                break

        return all_jobs, all_related_terms

    def _extract_total_jobs(self) -> int:
        """Extract the total number of jobs found."""
        try:
            # Wait for either the legacy or new selector
            WebDriverWait(self.driver, 10).until(
                lambda d: len(
                    d.find_elements(
                        By.CSS_SELECTOR,
                        "[data-at='searchbar-jobs-count'], [data-at='found-jobs-count']",
                    )
                )
                > 0
            )

            # Try both selectors
            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-at='searchbar-jobs-count'], [data-at='found-jobs-count']",
            )

            if elements:
                total_text = elements[0].text
                # Extract number from text like "1.251 Treffer"
                return int(total_text.split()[0].replace(".", ""))
            return 0
        except Exception as e:
            logger.warning(f"Could not extract total jobs count: {e}")
            return 0

    def _parse_search_results(
        self,
    ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Parse the search results page."""
        jobs = []
        page = 1
        total_jobs = 0

        while True:
            try:
                job_elements = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "[data-at='job-item']")
                    )
                )

                if not job_elements:
                    break

                logger.info(f"Found {len(job_elements)} job listings on page {page}")

                for job_element in job_elements:
                    try:
                        job_info = self._extract_job_info(job_element)
                        if job_info:
                            jobs.append(job_info)
                            total_jobs += 1

                        if total_jobs >= self.max_results:
                            logger.info(
                                f"Reached maximum number of results: {self.max_results}"
                            )
                            break
                    except Exception as e:
                        logger.error(f"Error extracting job info: {e}")
                        continue

                if total_jobs >= self.max_results:
                    break

                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "[data-at='pagination-next']:not([disabled])",
                            )
                        )
                    )
                    next_button.click()
                    page += 1
                    time.sleep(2)
                except TimeoutException:
                    logger.info("No more pages available")
                    break

            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break

        related_terms = self._extract_related_terms()
        return jobs, related_terms

    def _extract_job_info(self, job_element) -> Optional[Dict[str, str]]:
        """Extract information from a job listing element."""
        try:
            # Extract base information
            title = job_element.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-title']"
            ).text.strip()
            company = job_element.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-company-name']"
            ).text.strip()
            location = job_element.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-location']"
            ).text.strip()

            # Get job URL and ID
            url_element = job_element.find_element(
                By.CSS_SELECTOR, "a[data-at='job-item-title']"
            )
            url = url_element.get_attribute("href")
            job_id = url.split("/")[-1].split("?")[0]

            # Get additional information if available
            try:
                salary = job_element.find_element(
                    By.CSS_SELECTOR, "[data-at='job-item-salary-info']"
                ).text.strip()
            except NoSuchElementException:
                salary = None

            try:
                posted = job_element.find_element(
                    By.CSS_SELECTOR, "[data-at='job-item-timeago']"
                ).text.strip()
            except NoSuchElementException:
                posted = None

            return {
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "salary": salary,
                "posted": posted,
                "source": "StepStone",
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error extracting job info: {e}")
            return None

    def _extract_related_terms(self) -> List[Dict[str, str]]:
        """Extract related search terms."""
        related_terms = []
        try:
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-at='similar-searches'] a"
            )
            for element in elements:
                title = element.text.strip()
                url = element.get_attribute("href")
                related_terms.append(
                    {"title": title, "url": url, "type": "related_search"}
                )
        except Exception as e:
            logger.warning(f"Error extracting related terms: {e}")
        return related_terms

    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def __del__(self):
        """Destructor to ensure the web driver is closed."""
        self.close()


def main():
    """Run the scraper from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="StepStone Job Scraper")
    parser.add_argument(
        "--job-title", default="Data Engineer", help="Job title to search for"
    )
    parser.add_argument("--location", default="Hamburg", help="Location to search in")
    parser.add_argument(
        "--max-results", type=int, default=25, help="Maximum number of results to fetch"
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--login", action="store_true", help="Login to StepStone")
    parser.add_argument("--max-runtime", type=int, help="Maximum runtime in seconds")
    parser.add_argument(
        "--sort",
        choices=["asc", "desc"],
        default="desc",
        help="Sort order (asc or desc by date)",
    )
    parser.add_argument(
        "--first-n", type=int, default=0, help="Get details for first N jobs"
    )
    parser.add_argument(
        "--last-n", type=int, default=0, help="Get details for last N jobs"
    )

    args = parser.parse_args()

    scraper = StepStoneScraper(
        max_results=args.max_results,
        headless=args.headless,
        login=args.login,
        max_runtime_seconds=args.max_runtime,
        sort_order=args.sort,
    )

    try:
        jobs, related_terms = scraper.search([args.job_title], args.location)

        logger.info(
            f"\nFound {len(jobs)} jobs for '{args.job_title}' in '{args.location}'"
        )

        if jobs:
            print("\nSample job listings:")
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n--- Job {i} ---")
                print(f"Title: {job['title']}")
                print(f"Company: {job['company']}")
                print(f"Location: {job['location']}")
                if job.get("salary"):
                    print(f"Salary: {job['salary']}")
                if job.get("posted"):
                    print(f"Posted: {job['posted']}")
                print(f"URL: {job['url']}")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
