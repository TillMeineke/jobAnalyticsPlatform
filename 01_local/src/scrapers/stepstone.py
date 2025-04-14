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
        """Log in to StepStone account.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        email = os.environ.get("STEPSTONE_EMAIL")
        password = os.environ.get("STEPSTONE_PASSWORD")

        if not email or not password:
            logger.warning("STEPSTONE_EMAIL or STEPSTONE_PASSWORD not set, skipping login")
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
                
            # StepStone has multiple login page variants, try different selectors
            email_selectors = ["#email", "#loginEmail", "[name='email']"]
            for selector in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    email_input.send_keys(email)
                    logger.debug(f"Found email input with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                logger.error("Could not find email input field")
                return False

            # Find and click continue button - try different selectors
            continue_selectors = ["button[type='submit']", "[data-testid='button-continue']", ".at-login-email-button"]
            for selector in continue_selectors:
                try:
                    continue_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    continue_button.click()
                    logger.debug(f"Found continue button with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                logger.error("Could not find continue button")
                return False

            # Wait for password field to appear
            time.sleep(1)  # Small delay for page transition
            
            # Try different selectors for password field
            password_selectors = ["#password", "#loginPassword", "[name='password']"]
            for selector in password_selectors:
                try:
                    password_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    password_input.send_keys(password)
                    logger.debug(f"Found password input with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                logger.error("Could not find password input field")
                return False

            # Find and click login button - try different selectors
            login_selectors = ["button[type='submit']", "[data-testid='button-login']", ".at-login-password-button"]
            for selector in login_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    login_button.click()
                    logger.debug(f"Found login button with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            else:
                logger.error("Could not find login button")
                return False

            # Wait for login to complete
            try:
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
