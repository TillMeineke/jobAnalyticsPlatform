#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StepStone Job Scraper

This module provides functionality to scrape job listings from StepStone.de.
It extracts job details such as title, company, location, and more.
"""

import argparse
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StepStoneScraper:
    """Scraper for StepStone job listings."""

    BASE_URL = "https://www.stepstone.de"
    SEARCH_URL = "https://www.stepstone.de/jobs/{}/in-{}?radius=30&sort=2"

    def __init__(self, headless: bool = False):
        """
        Initialize the StepStone scraper.

        Args:
            headless: Whether to run the browser in headless mode
        """
        self.driver = None
        self.headless = headless

    def _setup_driver(self) -> None:
        """Set up the Selenium WebDriver."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def _close_driver(self) -> None:
        """Close the Selenium WebDriver if it exists."""
        if self.driver:
            self.driver.quit()
            logger.info(colored("WebDriver closed", "green"))

    def _accept_cookies(self) -> None:
        """Accept cookies on the website if the dialog appears."""
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-testid='button-allow-essential']")
                )
            )
            cookie_button.click()
            time.sleep(1)
        except Exception:
            logger.debug("No cookie dialog found or it could not be closed.")

    def search_jobs(
        self, job_title: str, location: str, max_results: int = 100, max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs with the given title and location.

        Args:
            job_title: The job title to search for
            location: The location to search jobs in
            max_results: Maximum number of job listings to retrieve
            max_pages: Maximum number of pages to scrape

        Returns:
            A list of job listings as dictionaries
        """
        if not self.driver:
            self._setup_driver()

        # Format the job title for the URL (replace spaces with hyphens)
        formatted_job_title = job_title.lower().replace(" ", "-")
        search_url = self.SEARCH_URL.format(formatted_job_title, location)

        logger.info(colored(f"Searching for {job_title} in {location}...", "green"))
        self.driver.get(search_url)
        time.sleep(5)  # Allow page to load

        self._accept_cookies()

        # Get total jobs count
        try:
            total_jobs_element = self.driver.find_element(
                By.CSS_SELECTOR, "h1.res-1fgoj9l"
            )
            total_jobs_text = total_jobs_element.text
            total_jobs_match = re.search(r"(\d+(?:\.\d+)?)", total_jobs_text)
            total_jobs = (
                int(total_jobs_match.group(1).replace(".", ""))
                if total_jobs_match
                else None
            )
            if total_jobs:
                logger.info(
                    colored(
                        f"Found {total_jobs} total jobs from results counter", "green"
                    )
                )
        except Exception as e:
            logger.warning(f"Could not extract total jobs count: {str(e)}")
            total_jobs = None

        job_listings = []
        current_page = 1

        while current_page <= max_pages and len(job_listings) < max_results:
            logger.info(colored(f"Processing page {current_page}", "green"))

            # Extract job listings from current page
            page_listings = self._extract_job_listings_from_page()

            if not page_listings:
                logger.info("No more job listings found.")
                break

            logger.info(
                colored(
                    f"Found {len(page_listings)} job listings on page {current_page}",
                    "green",
                )
            )
            job_listings.extend(page_listings)

            if len(job_listings) >= max_results:
                logger.info(
                    colored(
                        f"Reached maximum number of results: {max_results}", "green"
                    )
                )
                break

            # Go to next page if available
            try:
                next_button = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-at='pagination-next-link']"
                )
                if "disabled" in next_button.get_attribute("class"):
                    logger.info("No more pages available.")
                    break

                next_button.click()
                time.sleep(3)  # Wait for the next page to load
                current_page += 1
            except Exception as e:
                logger.info(f"Could not navigate to next page: {str(e)}")
                break

        # Trim excess results
        job_listings = job_listings[:max_results]

        logger.info(
            colored(
                f"Found {len(job_listings)} job listings for '{job_title}' in '{location}'",
                "green",
            )
        )
        return job_listings

    def _extract_job_listings_from_page(self) -> List[Dict[str, Any]]:
        """
        Extract job listings from the current page.

        Returns:
            A list of job listings from the current page
        """
        job_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "article[data-genesis-element='CARD'][data-at='job-item']"
        )

        job_listings = []
        for job_element in job_elements:
            try:
                # Extract job ID
                job_id = job_element.get_attribute("id").replace("job-item-", "")

                # Extract job title
                title_element = job_element.find_element(
                    By.CSS_SELECTOR,
                    "div[data-genesis-element='BASE'] a[data-at='job-item-title']",
                )
                title = title_element.text.strip()

                # Extract job URL
                url = urljoin(self.BASE_URL, title_element.get_attribute("href"))

                # Extract company name
                company = job_element.find_element(
                    By.CSS_SELECTOR, "span[data-at='job-item-company-name']"
                ).text.strip()

                # Extract location
                location = job_element.find_element(
                    By.CSS_SELECTOR, "span[data-at='job-item-location']"
                ).text.strip()

                # Extract posted date
                posted_element = job_element.find_element(
                    By.CSS_SELECTOR, "span[data-at='job-item-timeago'] time"
                )
                posted = posted_element.text.strip()

                # Extract company logo URL (if available)
                try:
                    company_logo = job_element.find_element(
                        By.CSS_SELECTOR,
                        "img[data-genesis-element='COMPANY_LOGO_IMAGE']",
                    ).get_attribute("src")
                except:
                    company_logo = None

                # Extract home office options (if available)
                try:
                    homeoffice_element = job_element.find_element(
                        By.CSS_SELECTOR, "span[data-at='job-item-work-from-home']"
                    )
                    homeoffice = homeoffice_element.text.strip()
                except:
                    homeoffice = None

                # Check for fast application badge
                try:
                    fast_application_element = job_element.find_element(
                        By.CSS_SELECTOR, "div[data-at='job-item-badge']"
                    )
                    fast_application = (
                        "Schnelle Bewerbung" in fast_application_element.text
                    )
                except:
                    fast_application = False

                # Extract salary information (if available)
                salary = None
                try:
                    salary_elements = job_element.find_elements(
                        By.CSS_SELECTOR, "span[data-at='job-item-salary']"
                    )
                    if salary_elements:
                        salary = salary_elements[0].text.strip()
                except:
                    pass

                # Create job listing dictionary
                job_listing = {
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "posted": posted,
                    "url": url,
                    "company_logo_url": company_logo,
                    "homeoffice_options": homeoffice,
                    "fast_application": fast_application,
                    "salary": salary,
                    "scraped_at": datetime.now().isoformat(),
                }

                job_listings.append(job_listing)

            except Exception as e:
                logger.warning(f"Error extracting job listing: {str(e)}")
                continue

        return job_listings

    def scrape_job_details(self, url: str) -> Dict[str, Any]:
        """
        Scrape detailed information about a specific job.

        Args:
            url: URL of the job listing

        Returns:
            Dictionary containing job details
        """
        if not self.driver:
            self._setup_driver()

        self.driver.get(url)
        time.sleep(3)

        self._accept_cookies()

        try:
            # Extract job description
            description_element = self.driver.find_element(
                By.CSS_SELECTOR, "div[data-at='job-description']"
            )
            description = description_element.text

            # Extract requirements (if separately available)
            requirements = None
            try:
                requirements_element = self.driver.find_element(
                    By.CSS_SELECTOR, "div[data-at='job-requirements']"
                )
                requirements = requirements_element.text
            except:
                pass

            # Extract additional information
            details = {
                "description": description,
                "requirements": requirements,
                "url": url,
                "scraped_at": datetime.now().isoformat(),
            }

            return details

        except Exception as e:
            logger.error(f"Error scraping job details: {str(e)}")
            return {"url": url, "error": str(e)}

    def run(
        self,
        job_title: str,
        location: str,
        max_results: int = 100,
        max_pages: int = 10,
        scrape_details: bool = False,
        output_path: Optional[str] = None,
        first_n: Optional[int] = None,
        last_n: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Run the complete scraping process.

        Args:
            job_title: The job title to search for
            location: The location to search jobs in
            max_results: Maximum number of job listings to retrieve
            max_pages: Maximum number of pages to scrape
            scrape_details: Whether to scrape detailed information for each job
            output_path: Path to save the results CSV file
            first_n: Show only first N results in the output
            last_n: Show only last N results in the output

        Returns:
            DataFrame with job listings
        """
        try:
            self._setup_driver()
            job_listings = self.search_jobs(
                job_title, location, max_results=max_results, max_pages=max_pages
            )

            if scrape_details:
                for job in job_listings:
                    details = self.scrape_job_details(job["url"])
                    job.update(details)

            # Create DataFrame
            df = pd.DataFrame(job_listings)

            # Save to CSV if output path is provided
            if output_path:
                df.to_csv(output_path, index=False)
                logger.info(colored(f"Saved results to {output_path}", "green"))

            # Print results summary
            total_jobs = len(job_listings)
            print("\n" + "=" * 80)
            print(
                f"StepStone reports a total of {df['job_id'].nunique()} available jobs for '{job_title}' in '{location}'"
            )
            print("=" * 80 + "\n")

            print(
                f"Retrieved {total_jobs} job listings from the first {min(max_pages, (total_jobs + 24) // 25)} page(s)\n"
            )

            # Display sample results
            sample_jobs = []
            if first_n and not last_n:
                sample_jobs = job_listings[:first_n]
            elif last_n and not first_n:
                sample_jobs = job_listings[-last_n:]
            elif first_n and last_n:
                first_jobs = job_listings[:first_n]
                last_jobs = job_listings[-last_n:]
                sample_jobs = first_jobs + last_jobs
            else:
                sample_jobs = job_listings[:5]  # Default show first 5

            print("Sample job listings:\n")
            for i, job in enumerate(sample_jobs, 1):
                print(f"--- Job {i} ---")
                print(f"Title: {job['title']}")
                print(f"Company: {job['company']}")
                print(f"Location: {job['location']}")
                print(f"Posted: {job['posted']}")
                print(f"URL: {job['url']}")
                print()

            return df

        except Exception as e:
            logger.error(colored(f"Error during scraping: {str(e)}", "red"))
            raise
        finally:
            self._close_driver()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Scrape job listings from StepStone")
    parser.add_argument("--job-title", required=True, help="Job title to search for")
    parser.add_argument("--location", required=True, help="Location to search in")
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to retrieve",
    )
    parser.add_argument(
        "--max-pages", type=int, default=10, help="Maximum number of pages to scrape"
    )
    parser.add_argument("--output", help="Path to save the results CSV file")
    parser.add_argument(
        "--scrape-details",
        action="store_true",
        help="Scrape detailed information for each job",
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument(
        "--first-n", type=int, help="Show only first N results in the output"
    )
    parser.add_argument(
        "--last-n", type=int, help="Show only last N results in the output"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    scraper = StepStoneScraper(headless=args.headless)
    scraper.run(
        job_title=args.job_title,
        location=args.location,
        max_results=args.max_results,
        max_pages=args.max_pages,
        scrape_details=args.scrape_details,
        output_path=args.output,
        first_n=args.first_n,
        last_n=args.last_n,
    )
