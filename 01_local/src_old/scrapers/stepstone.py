"""StepStone job scraper implementation."""

import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StepStoneScraper:
    """StepStone job scraper class."""

    BASE_URL = "https://www.stepstone.de"
    SEARCH_URL = f"{BASE_URL}/jobs"
    LOGIN_URL = f"{BASE_URL}/5/login"

    def __init__(
        self,
        max_results: int = 100,
        headless: bool = True,
        login: bool = False,
        max_runtime_seconds: Optional[int] = None,
        sort_order: str = "desc",
    ):
        """Initialize the StepStone scraper.

        Args:
            max_results: Maximum number of job listings to scrape
            headless: Whether to run the browser in headless mode
            login: Whether to login to StepStone
            max_runtime_seconds: Maximum runtime in seconds before stopping
            sort_order: Sort order for job listings ('asc' or 'desc' by date)
        """
        self.max_results = max_results
        self.headless = headless
        self.should_login = login
        self.max_runtime_seconds = max_runtime_seconds
        self.sort_order = sort_order.lower()

        if self.sort_order not in ["asc", "desc"]:
            logger.warning(f"Invalid sort_order: {sort_order}, defaulting to 'desc'")
            self.sort_order = "desc"

        self.driver = self._setup_driver()

        if self.should_login:
            self._login()

    def _setup_driver(self) -> webdriver.Firefox:
        """Set up the Firefox web driver.

        Returns:
            A configured Firefox web driver instance
        """
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")

        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")

        # Use geckodriver from PATH
        driver = webdriver.Firefox(options=firefox_options)
        return driver

    def _login(self) -> None:
        """Log in to StepStone account."""
        email = os.environ.get("STEPSTONE_EMAIL")
        password = os.environ.get("STEPSTONE_PASSWORD")

        if not email or not password:
            logger.warning(
                "STEPSTONE_EMAIL or STEPSTONE_PASSWORD not set, skipping login"
            )
            return

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
                logger.info("No cookie banner found")

            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "loginEmail"))
            )
            email_input.send_keys(email)

            # Find and click continue button
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@data-testid='button-continue']")
                )
            )
            continue_button.click()

            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "loginPassword"))
            )
            password_input.send_keys(password)

            # Find and click login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@data-testid='button-login']")
                )
            )
            login_button.click()

            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                lambda driver: "stepstone.de/5/dashboard" in driver.current_url
                or "stepstone.de/jobs" in driver.current_url
            )

            logger.info("Successfully logged in to StepStone")

        except Exception as e:
            logger.error(f"Error logging in: {e}")
            raise

    def search(
        self,
        job_titles: List[str],
        location: str,
        get_first_n: int = 0,
        get_last_n: int = 0,
    ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Search for jobs on StepStone.

        Args:
            job_titles: List of job titles to search for
            location: Location to search in
            get_first_n: Number of first jobs to get details for
            get_last_n: Number of last jobs to get details for

        Returns:
            A tuple containing:
                - A list of job listings dictionaries
                - A list of related job terms dictionaries
        """
        start_time = time.time()
        all_jobs = []
        all_related_terms = []

        for job_title in job_titles:
            logger.info(f"Searching for {job_title} in {location}...")

            # Construct search URL with sort parameter
            sort_param = "date" if self.sort_order == "desc" else "date_asc"
            search_query = (
                f"?what={quote(job_title)}&where={quote(location)}&sort={sort_param}"
            )
            url = f"{self.SEARCH_URL}{search_query}"

            self.driver.get(url)

            # Accept cookies if prompted
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "ccmgt_explicit_accept"))
                ).click()
            except (TimeoutException, NoSuchElementException):
                pass

            jobs, related_terms = self._parse_search_results()

            # Log progress
            logger.info(
                f"Found {len(jobs)} job listings for '{job_title}' in '{location}'"
            )

            all_jobs.extend(jobs)
            all_related_terms.extend(related_terms)

            # Check if we exceeded max runtime
            if (
                self.max_runtime_seconds
                and (time.time() - start_time) > self.max_runtime_seconds
            ):
                logger.info(
                    f"Reached maximum runtime of {self.max_runtime_seconds} seconds"
                )
                break

        # Filter out jobs with synthetic IDs which can't be used for detail lookup
        valid_jobs = [job for job in all_jobs if not job["id"].startswith("synthetic-")]

        # Process the first N and last N jobs if requested
        processed_jobs = []

        if get_first_n > 0 and valid_jobs:
            first_n = valid_jobs[: min(get_first_n, len(valid_jobs))]
            logger.info(f"Getting details for first {len(first_n)} jobs")

            for job in first_n:
                if job.get("id"):
                    details = self.get_job_details(job["id"])
                    processed_jobs.append({**job, "details": details})

                    # Check if we exceeded max runtime
                    if (
                        self.max_runtime_seconds
                        and (time.time() - start_time) > self.max_runtime_seconds
                    ):
                        logger.info(
                            f"Reached maximum runtime of {self.max_runtime_seconds} seconds"
                        )
                        break

        if get_last_n > 0 and valid_jobs:
            last_n = valid_jobs[-min(get_last_n, len(valid_jobs)) :]
            logger.info(f"Getting details for last {len(last_n)} jobs")

            for job in last_n:
                if job.get("id"):
                    details = self.get_job_details(job["id"])
                    processed_jobs.append({**job, "details": details})

                    # Check if we exceeded max runtime
                    if (
                        self.max_runtime_seconds
                        and (time.time() - start_time) > self.max_runtime_seconds
                    ):
                        logger.info(
                            f"Reached maximum runtime of {self.max_runtime_seconds} seconds"
                        )
                        break

        # If no specific jobs were requested for processing, return the raw list
        if get_first_n == 0 and get_last_n == 0:
            return all_jobs, all_related_terms
        else:
            return processed_jobs, all_related_terms

    def _extract_total_jobs(self) -> int:
        """Extract the total number of jobs found."""
        try:
            # Wait for the element to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='found-jobs-count']")
                )
            )
            total_element = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='found-jobs-count']"
            )
            total_text = total_element.text
            # Extract number from text like "1.251 Treffer"
            return int(total_text.split()[0].replace(".", ""))
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
        start_time = time.time()

        # Get total number of jobs first
        total_available_jobs = self._extract_total_jobs()
        logger.info(f"Total jobs available: {total_available_jobs}")

        while True:
            # Wait for job listings to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='job-item']")
                    )
                )
                time.sleep(1)  # Small delay to ensure all items are loaded

                job_listings = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-testid='job-item']"
                )

                if not job_listings:
                    logger.warning("No job listings found on current page")
                    break

                logger.info(f"Found {len(job_listings)} job listings on page {page}")

                for job_element in job_listings:
                    try:
                        job = self._extract_job_info(job_element)
                        jobs.append(job)
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

                # Check runtime
                if (
                    self.max_runtime_seconds
                    and (time.time() - start_time) > self.max_runtime_seconds
                ):
                    logger.info(
                        f"Reached maximum runtime of {self.max_runtime_seconds} seconds"
                    )
                    break

                # Try to go to next page
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "[data-testid='next-page-button']:not([disabled])",
                            )
                        )
                    )
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", next_button
                    )
                    time.sleep(0.5)
                    next_button.click()
                    page += 1
                    time.sleep(2)  # Wait for new page to load
                except TimeoutException:
                    logger.info("No more pages available")
                    break
                except Exception as e:
                    logger.error(f"Error navigating to next page: {e}")
                    break

            except TimeoutException:
                logger.warning("Timeout waiting for job listings")
                break
            except Exception as e:
                logger.error(f"Error parsing search results: {e}")
                break

        # Extract related search terms
        related_terms = self._extract_related_terms()

        return jobs, related_terms

    def _extract_job_info(self, job_element) -> Dict[str, str]:
        """Extract job information from a job listing element.

        Args:
            job_element: The job listing HTML element

        Returns:
            A dictionary containing job information
        """
        # Extract job title
        try:
            title_element = job_element.find_element(
                By.CSS_SELECTOR, "h2[data-testid='job-element-title']"
            )
            title = title_element.text.strip()
        except NoSuchElementException:
            title = "Unknown Title"

        # Extract company name
        try:
            company_element = job_element.find_element(
                By.CSS_SELECTOR, "span[data-testid='job-element-company']"
            )
            company = company_element.text.strip()
        except NoSuchElementException:
            company = "Unknown Company"

        # Extract location
        try:
            location_element = job_element.find_element(
                By.CSS_SELECTOR, "span[data-testid='job-element-location']"
            )
            location = location_element.text.strip()
        except NoSuchElementException:
            location = "Unknown Location"

        # Extract job URL and ID
        try:
            url_element = job_element.find_element(
                By.CSS_SELECTOR, "a[data-testid='job-element-link']"
            )
            url = url_element.get_attribute("href")
            # Extract the ID from the URL
            job_id = url.split("/")[-1].split("?")[0]

            # Skip synthetic IDs
            if not job_id or len(job_id) < 5:
                job_id = f"synthetic-{uuid.uuid4()}"

        except NoSuchElementException:
            url = None
            job_id = f"synthetic-{uuid.uuid4()}"

        # Extract posting date if available
        try:
            date_element = job_element.find_element(
                By.CSS_SELECTOR, "span[data-testid='job-element-date']"
            )
            posting_date = date_element.text.strip()
        except NoSuchElementException:
            posting_date = "Unknown"

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "posting_date": posting_date,
            "source": "StepStone",
            "scraped_at": datetime.now().isoformat(),
        }

    def _extract_related_terms(self) -> List[Dict[str, str]]:
        """Extract related search terms.

        Returns:
            A list of related search terms dictionaries
        """
        related_terms = []

        try:
            related_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='serp-similar-searches'] a"
            )

            for element in related_elements:
                title = element.text.strip()
                url = element.get_attribute("href")

                related_terms.append(
                    {"title": title, "url": url, "type": "related_search"}
                )

        except Exception as e:
            logger.warning(f"Error extracting related terms: {e}")

        return related_terms

    def _extract_job_details(self, job_card):
        """Extract detailed information from a job card."""
        try:
            title = job_card.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-title']"
            ).text
            company = job_card.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-company-name']"
            ).text
            location = job_card.find_element(
                By.CSS_SELECTOR, "[data-at='job-item-location']"
            ).text

            # Get the job link
            link = job_card.find_element(
                By.CSS_SELECTOR, "a[data-at='job-item-title']"
            ).get_attribute("href")

            # Try to get salary if available
            try:
                salary = job_card.find_element(
                    By.CSS_SELECTOR, "[data-at='job-item-salary-info']"
                ).text
            except NoSuchElementException:
                salary = "Not specified"

            # Try to get posting date
            try:
                posted = job_card.find_element(
                    By.CSS_SELECTOR, "[data-at='job-item-timeago']"
                ).text
            except NoSuchElementException:
                posted = "Not specified"

            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "posted": posted,
                "link": link,
            }
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            return None

    def scrape(self):
        """Main scraping method."""
        jobs_found = []
        for page in range(1, self.max_results + 1):
            try:
                job_cards = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-at='job-item']"
                )
                logger.info(f"Found {len(job_cards)} job listings on page {page}")

                # Process first_n and last_n if specified
                if self.first_n or self.last_n:
                    if self.first_n:
                        first_cards = job_cards[: self.first_n]
                        for card in first_cards:
                            details = self._extract_job_details(card)
                            if details:
                                jobs_found.append(details)

                    if self.last_n:
                        last_cards = job_cards[-self.last_n :]
                        for card in last_cards:
                            details = self._extract_job_details(card)
                            if details:
                                jobs_found.append(details)
                else:
                    for card in job_cards:
                        details = self._extract_job_details(card)
                        if details:
                            jobs_found.append(details)

            except Exception as e:
                logger.error(f"Error on page {page}: {str(e)}")
                break

        logger.info(
            f"\nFound {len(jobs_found)} jobs for '{self.job_title}' in '{self.location}'"
        )
        print(f"\nRetrieved details for {len(jobs_found)} jobs")

        # Print detailed job information
        for job in jobs_found:
            print("\n-------------------")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Salary: {job['salary']}")
            print(f"Posted: {job['posted']}")
            print(f"Link: {job['link']}")

        return jobs_found

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information about a job listing.

        Args:
            job_id: The job listing ID

        Returns:
            A dictionary containing detailed job information
        """
        logger.info(f"Getting details for job ID: {job_id}")

        # Skip synthetic IDs
        if job_id.startswith("synthetic-"):
            logger.warning(f"Skipping synthetic job ID: {job_id}")
            return {"error": "Synthetic job ID"}

        # Construct job URL
        job_url = f"{self.BASE_URL}/stellenangebote/{job_id}"
        self.driver.get(job_url)

        # Wait for job details to load
        try:
            WebDriverWait(self.driver, 15).until(  # Increased timeout
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='job-detail-page']")
                )
            )
        except TimeoutException:
            logger.error("Timeout waiting for job details to load")
            return {"error": "Timeout loading job details"}

        job_details = {}

        # Extract basic information
        try:
            job_details["title"] = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='job-detail-title']"
            ).text.strip()
        except NoSuchElementException:
            job_details["title"] = "Unknown Title"

        try:
            job_details["company"] = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='job-detail-company']"
            ).text.strip()
        except NoSuchElementException:
            job_details["company"] = "Unknown Company"

        try:
            job_details["location"] = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='job-detail-location']"
            )
            job_details["location"] = job_details["location"].text.strip()
        except NoSuchElementException:
            job_details["location"] = "Unknown Location"

        # Extract job description
        try:
            description_element = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='job-detail-description']"
            )
            job_details["description"] = description_element.get_attribute("innerHTML")
        except NoSuchElementException:
            job_details["description"] = ""

        # Extract additional information if available
        try:
            # Extract salary if available
            salary_elements = self.driver.find_elements(
                By.XPATH, "//dt[contains(text(), 'Gehalt')]/following-sibling::dd[1]"
            )
            if salary_elements:
                job_details["salary"] = salary_elements[0].text.strip()

            # Extract employment type if available
            type_elements = self.driver.find_elements(
                By.XPATH,
                "//dt[contains(text(), 'Beschäftigungsart')]/following-sibling::dd[1]",
            )
            if type_elements:
                job_details["employment_type"] = type_elements[0].text.strip()

            # Extract additional metadata from the job description page
            metadata_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "dl.at-section-description-list dt, dl.at-section-description-list dd",
            )

            # Process metadata elements in pairs
            for i in range(0, len(metadata_elements), 2):
                if i + 1 < len(metadata_elements):
                    key = metadata_elements[i].text.strip().lower().replace(" ", "_")
                    value = metadata_elements[i + 1].text.strip()
                    job_details[key] = value

        except Exception as e:
            logger.warning(f"Error extracting additional details: {e}")

        # Extract application deadline if available
        try:
            deadline_elements = self.driver.find_elements(
                By.XPATH,
                "//dt[contains(text(), 'Bewerbungsfrist')]/following-sibling::dd[1]",
            )
            if deadline_elements:
                job_details["application_deadline"] = deadline_elements[0].text.strip()
        except Exception:
            pass

        # Add metadata
        job_details["id"] = job_id
        job_details["url"] = job_url
        job_details["source"] = "StepStone"
        job_details["scraped_at"] = datetime.now().isoformat()

        return job_details

    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def __del__(self):
        """Destructor to ensure the web driver is closed."""
        self.close()


def main():
    """Run the scraper for testing purposes."""
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
        jobs, related_terms = scraper.search(
            [args.job_title],
            args.location,
            get_first_n=args.first_n,
            get_last_n=args.last_n,
        )

        print(f"\nFound {len(jobs)} jobs for '{args.job_title}' in '{args.location}'")

        if args.first_n > 0 or args.last_n > 0:
            print(f"\nRetrieved details for {len(jobs)} jobs")
            for i, job in enumerate(jobs, 1):
                print(f"\n--- Job {i} ---")
                print(f"Title: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company', 'N/A')}")
                print(f"Location: {job.get('location', 'N/A')}")
                if "details" in job:
                    print(
                        f"Description length: {len(job['details'].get('description', ''))}"
                    )
                    if "salary" in job["details"]:
                        print(f"Salary: {job['details']['salary']}")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
