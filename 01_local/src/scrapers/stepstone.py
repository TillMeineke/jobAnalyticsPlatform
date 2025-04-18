#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StepStone Job Scraper

This module provides functionality to scrape job listings from StepStone.de.
It extracts job details such as title, company, location, and more.
"""

import argparse
import csv
import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored
from webdriver_manager.firefox import GeckoDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StepStoneScraper:
    """Scraper for StepStone job listings using Firefox/GeckoDriver."""

    BASE_URL = "https://www.stepstone.de"
    SEARCH_URL = "https://www.stepstone.de/jobs/{}/in-{}?radius=30&sort=2"
    LOGIN_URL = "https://www.stepstone.de/anmelden"

    # Path to the logins CSV file relative to the project root
    DEFAULT_LOGINS_PATH = os.path.join("config", "logins.csv")

    def __init__(self, headless: bool = False, logins_path: Optional[str] = None):
        """
        Initialize the StepStone scraper.

        Args:
            headless: Whether to run the browser in headless mode
            logins_path: Path to CSV file with login credentials (default: config/logins.csv)
        """
        self.driver = None
        self.headless = headless
        self.logins_path = logins_path or self.DEFAULT_LOGINS_PATH
        self.logins = []
        self.current_login = None
        self.is_logged_in = False
        self._load_logins()

    def _load_logins(self) -> None:
        """Load login credentials from CSV file."""
        try:
            # Check both absolute path and relative to project root
            if os.path.isfile(self.logins_path):
                logins_file = self.logins_path
            else:
                # Try relative to project root
                project_root = Path(__file__).parent.parent.parent
                logins_file = os.path.join(project_root, self.logins_path)

                # If still not found, check for template and copy it
                if not os.path.isfile(logins_file):
                    template_path = os.path.join(
                        project_root, f"{self.logins_path}.template"
                    )
                    if os.path.isfile(template_path):
                        # Create directories if they don't exist
                        os.makedirs(os.path.dirname(logins_file), exist_ok=True)

                        # Copy template to actual file
                        with (
                            open(template_path, "r") as template,
                            open(logins_file, "w") as target,
                        ):
                            target.write(template.read())

                        logger.warning(
                            colored(
                                f"Created logins file from template at {logins_file}. "
                                f"Please fill in your actual credentials.",
                                "yellow",
                            )
                        )

            if os.path.isfile(logins_file):
                with open(logins_file, "r") as f:
                    reader = csv.DictReader(f)
                    self.logins = list(reader)

                logger.info(
                    colored(f"Loaded {len(self.logins)} login credentials", "green")
                )
            else:
                logger.warning(
                    colored(f"Logins file not found at {self.logins_path}", "yellow")
                )

        except Exception as e:
            logger.error(colored(f"Error loading login credentials: {str(e)}", "red"))

    def _get_login_for_task(
        self, task_type: str = "search"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get login credentials for a specific task type.

        Args:
            task_type: Type of task ("search" or "details")

        Returns:
            Tuple of (email, password) or (None, None) if no suitable login found
        """
        if not self.logins:
            return None, None

        # Filter logins by method
        suitable_logins = [
            login
            for login in self.logins
            if login.get("method", "").lower() == task_type.lower()
        ]

        # If no suitable logins found, use any available login
        if not suitable_logins:
            suitable_logins = self.logins

        # If we've already used a login in this session, try to reuse it
        if self.current_login and self.current_login in suitable_logins:
            return self.current_login["emails"], self.current_login["passwords"]

        # Otherwise pick the first suitable login
        if suitable_logins:
            self.current_login = suitable_logins[0]
            return self.current_login["emails"], self.current_login["passwords"]

        return None, None

    def _setup_driver(self) -> None:
        """Set up the Selenium WebDriver."""
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=1920,1080")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options,
        )

    def _close_driver(self) -> None:
        """Close the Selenium WebDriver if it exists."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info(colored("WebDriver closed", "green"))
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

    def _accept_cookies(self) -> None:
        """Accept cookies on the website if the dialog appears."""
        try:
            # Try different selectors for cookie consent
            selectors = [
                "button[data-testid='button-allow-essential']",
                "button[data-testid='accept-button']",
                "button.btn-cookie-consent-accept",
                "button.accept-all-cookies",
            ]

            for selector in selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_button.click()
                    logger.info(
                        colored("Accepted cookies using selector: " + selector, "green")
                    )
                    time.sleep(1)
                    return
                except TimeoutException:
                    continue

            logger.info("No cookie consent dialog found")
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {e}")

    def login(self, task_type: str = "search") -> bool:
        """
        Login to StepStone account using credentials from the CSV file.

        Args:
            task_type: Type of task for which login is needed ("search" or "details")

        Returns:
            Boolean indicating whether login was successful
        """
        if not self.driver:
            self._setup_driver()

        # Get login credentials for the task
        email, password = self._get_login_for_task(task_type)

        if not email or not password:
            logger.warning(
                colored(
                    f"No login credentials found for task type: {task_type}", "yellow"
                )
            )
            return False

        try:
            logger.info(colored(f"Attempting to login with email {email}", "blue"))

            # Navigate to login page
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)

            # Accept cookies if needed
            self._accept_cookies()

            # Find and fill in the login form with explicit waits
            try:
                # Email field - try multiple potential selectors
                email_selectors = [
                    "input[data-testid='loginform-email-field']",
                    "input[name='email']",
                    "input[id='email']",
                    "input[type='email']",
                ]

                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if email_field:
                            break
                    except:
                        continue

                if not email_field:
                    logger.error(colored("Could not find email input field", "red"))
                    return False

                email_field.clear()
                email_field.send_keys(email)
                logger.info(colored("Email entered successfully", "green"))

                # Password field - try multiple potential selectors
                password_selectors = [
                    "input[data-testid='loginform-password-field']",
                    "input[name='password']",
                    "input[id='password']",
                    "input[type='password']",
                ]

                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if password_field:
                            break
                    except:
                        continue

                if not password_field:
                    logger.error(colored("Could not find password input field", "red"))
                    return False

                password_field.clear()
                password_field.send_keys(password)
                logger.info(colored("Password entered successfully", "green"))

                # Submit login form - try multiple potential selectors
                submit_selectors = [
                    "button[data-testid='submit-button']",
                    "button[type='submit']",
                    "input[type='submit']",
                    "button.login-button",
                ]

                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if submit_button:
                            break
                    except:
                        continue

                if not submit_button:
                    logger.error(colored("Could not find login submit button", "red"))
                    return False

                submit_button.click()
                logger.info(colored("Login form submitted", "green"))

                # Wait for login to complete and verify success
                time.sleep(5)

                # Check if login was successful by looking for elements that indicate logged-in state
                success_indicators = [
                    "a[data-testid='user-menu-toggle']",
                    "div.user-menu",
                    "a.user-menu-link",
                    "a[href*='meine-bewerbungen']",
                ]

                for indicator in success_indicators:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        self.is_logged_in = True
                        logger.info(
                            colored(
                                f"Successfully logged in to StepStone with {email}",
                                "green",
                            )
                        )
                        return True
                    except:
                        continue

                # If no success indicators found, check for error messages
                error_selectors = ["div.error", "p.error-message", "div.alert-danger"]
                for selector in error_selectors:
                    try:
                        error_element = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        error_text = error_element.text.strip()
                        logger.error(colored(f"Login failed: {error_text}", "red"))
                        return False
                    except:
                        continue

                # If no error message found but also no success indicators
                logger.warning(
                    colored(
                        "Login status unclear - no success indicators or error messages found",
                        "yellow",
                    )
                )
                return False

            except Exception as e:
                logger.error(colored(f"Error during login process: {str(e)}", "red"))
                return False

        except Exception as e:
            logger.error(colored(f"Login attempt failed: {str(e)}", "red"))
            return False

    # ... rest of the class methods (search_jobs, etc.) ...


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
    parser.add_argument("--logins-path", help="Path to CSV file with login credentials")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    scraper = StepStoneScraper(headless=args.headless, logins_path=args.logins_path)
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
