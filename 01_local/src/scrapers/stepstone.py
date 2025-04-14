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
            continue_selectors = [
                "button[type='submit']",
                "[data-testid='button-continue']",
                ".at-login-email-button",
            ]
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
            login_selectors = [
                "button[type='submit']",
                "[data-testid='button-login']",
                ".at-login-password-button",
            ]
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
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-at='user-menu']")
                    )
                )
                logger.info("Login successful")
                return True
            except TimeoutException:
                logger.error("Login failed")
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def search(self, job_title: str, location: str) -> Tuple[List[Dict[str, str]], int]:
        """Search for jobs on StepStone.

        Args:
            job_title: Job title to search for
            location: Location to search in

        Returns:
            A tuple containing:
                - A list of job listings dictionaries
                - The total number of jobs found
        """
        start_time = time.time()

        logger.info(f"Searching for {job_title} in {location}...")

        # Build search URL with parameters
        sort_param = "date" if self.sort_order == "desc" else "date_asc"
        search_query = (
            f"?what={quote(job_title)}&where={quote(location)}&sort={sort_param}"
        )
        url = f"{self.SEARCH_URL}{search_query}"

        # Navigate to search page
        self.driver.get(url)

        # Accept cookies if prompted
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
            ).click()
            logger.debug("Accepted cookies")
        except (TimeoutException, NoSuchElementException):
            logger.debug("No cookie banner found")

        # Wait for search results to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-at='job-item']")
                )
            )
        except TimeoutException:
            logger.warning("Timed out waiting for search results to load")

        # Extract total number of jobs
        total_jobs = self._extract_total_jobs()

        # Parse the search results and extract job listings
        jobs, related_terms = self._parse_search_results()

        logger.info(f"Found {len(jobs)} job listings for '{job_title}' in '{location}'")

        return jobs, total_jobs

    def _extract_total_jobs(self) -> int:
        """Extract the total number of jobs found."""
        try:
            # Wait for page to load enough to find job count
            time.sleep(2)

            # Try more specific selectors for the job count
            selectors = [
                # Main search results header with count
                "h1.at-search-composition-header-headline",
                "h1.at-listing-search-header-title",
                # Data attributes specifically for job counts
                "[data-at='searchbar-jobs-count']",
                "[data-at='found-jobs-count']",
                # Fallback to any element containing "Treffer"
                ".at-listing-search-header",
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        total_text = element.text.strip()
                        logger.debug(f"Found potential job count text: '{total_text}'")

                        # Look for patterns like "1.251 Treffer" or "1251 Jobs"
                        if "Treffer" in total_text or "Jobs" in total_text:
                            # Try to extract the number part
                            import re

                            number_match = re.search(r"([\d.]+)", total_text)
                            if number_match:
                                count_str = number_match.group(1).replace(".", "")
                                count = int(count_str)
                                logger.info(f"Extracted job count: {count}")
                                return count
                except Exception as inner_e:
                    logger.debug(f"Selector {selector} failed: {inner_e}")
                    continue

            # If all selectors fail, try scraping the title
            try:
                title = self.driver.title
                if "Treffer" in title:
                    import re

                    number_match = re.search(r"([\d.]+)", title)
                    if number_match:
                        count_str = number_match.group(1).replace(".", "")
                        count = int(count_str)
                        logger.info(f"Extracted job count from title: {count}")
                        return count
            except Exception as e:
                logger.debug(f"Title extraction failed: {e}")

            # Last resort: try to use the number of job items found on the page
            try:
                job_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-at='job-item']"
                )
                if job_elements:
                    logger.info(
                        f"Using job elements count as fallback: {len(job_elements)}"
                    )
                    return len(job_elements)
            except Exception as e:
                logger.debug(f"Job elements count failed: {e}")

            logger.warning("Could not find job count with any method")
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

    def get_job_details(self, job_id: str) -> dict:
        """Get detailed information about a job listing.

        Args:
            job_id: The job listing ID

        Returns:
            A dictionary containing detailed job information
        """
        logger.info(f"Getting details for job ID: {job_id}")

        # Construct job URL
        job_url = f"{self.BASE_URL}/{job_id}"

        try:
            # Navigate to job detail page
            self.driver.get(job_url)

            # Wait for job details to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-at='job-detail-description']")
                    )
                )
            except TimeoutException:
                logger.warning(
                    f"Timed out waiting for job details page to load: {job_id}"
                )
                return {}

            # Extract job description
            description = ""
            try:
                description_element = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-at='job-detail-description']"
                )
                description = description_element.get_attribute("innerHTML")
                logger.debug("Successfully extracted job description")
            except NoSuchElementException:
                logger.warning("Could not find job description element")

            # Extract skills (if available)
            skills = []
            try:
                skill_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-at='skills'] li"
                )
                skills = [skill.text.strip() for skill in skill_elements]
                logger.debug(f"Extracted {len(skills)} skills")
            except:
                logger.debug("No skills section found")

            # Extract company info
            company_info = {}
            try:
                company_element = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-at='job-company-description']"
                )
                company_info["description"] = company_element.get_attribute("innerHTML")
                logger.debug("Successfully extracted company description")
            except NoSuchElementException:
                logger.debug("No company description found")

            # Extract requirements
            requirements = {}
            try:
                sections = self.driver.find_elements(
                    By.CSS_SELECTOR, ".at-section-text-with-header"
                )
                for section in sections:
                    try:
                        header = (
                            section.find_element(By.CSS_SELECTOR, "h2, h3")
                            .text.strip()
                            .lower()
                        )
                        content = section.find_element(
                            By.CSS_SELECTOR, "div"
                        ).get_attribute("innerHTML")
                        requirements[header] = content
                        logger.debug(f"Extracted section: {header}")
                    except:
                        continue
            except:
                logger.debug("No requirement sections found")

            # Extract metadata (employment type, location details, etc.)
            metadata = {}
            try:
                meta_items = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-at='job-detail-meta-box'] li"
                )
                for item in meta_items:
                    try:
                        text = item.text.strip()
                        if ":" in text:
                            key, value = text.split(":", 1)
                            metadata[key.strip().lower()] = value.strip()
                    except:
                        continue
                logger.debug(f"Extracted {len(metadata)} metadata items")
            except:
                logger.debug("No metadata found")

            # Compile all job details
            job_details = {
                "job_id": job_id,
                "url": job_url,
                "description": description,
                "skills": skills,
                "company_info": company_info,
                "requirements": requirements,
                "metadata": metadata,
                "scraped_at": datetime.now().isoformat(),
            }

            return job_details

        except Exception as e:
            logger.error(f"Error retrieving job details for {job_id}: {str(e)}")
            return {}

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
        jobs, total_jobs = scraper.search(args.job_title, args.location)

        logger.info(
            f"\nFound {total_jobs} jobs for '{args.job_title}' in '{args.location}'"
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
