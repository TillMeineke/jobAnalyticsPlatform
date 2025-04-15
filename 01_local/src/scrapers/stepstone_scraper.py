"""
Stepstone Job Scraper.

This module provides a class to scrape job listings from Stepstone.de.
"""

import logging
import time
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup

from .job_parser import JobParser
from .utils.helpers import setup_logger


class StepstoneScraper:
    """
    A class to scrape job listings from Stepstone.de.
    
    This scraper can search for jobs based on role and location and extract
    detailed information about each job posting.
    
    Attributes:
        base_url (str): Base URL for Stepstone job search
        headers (Dict): HTTP headers for requests
        logger (logging.Logger): Logger for the scraper
        parser (JobParser): Parser to extract structured data from job listings
    """
    
    def __init__(
        self, 
        log_level: int = logging.INFO,
        request_delay: float = 1.0
    ) -> None:
        """
        Initialize the StepstoneScraper.
        
        Args:
            log_level: Logging level (default: logging.INFO)
            request_delay: Delay between requests in seconds (default: 1.0)
        """
        self.base_url = "https://www.stepstone.de/jobs"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        self.logger = setup_logger("stepstone_scraper", log_level)
        self.parser = JobParser()
        self.request_delay = request_delay
        
    def search_jobs(
        self, 
        role: str, 
        location: str, 
        radius: int = 30,
        max_pages: int = 1
    ) -> List[Dict]:
        """
        Search for jobs based on role and location.
        
        Args:
            role: Job role/title to search for
            location: Location to search in
            radius: Search radius in km (default: 30)
            max_pages: Maximum number of pages to scrape (default: 1)
            
        Returns:
            List of job listings as dictionaries
        """
        job_listings = []
        
        # Format the search URL
        role_formatted = role.replace(" ", "-").lower()
        location_formatted = location.lower()
        search_url = f"{self.base_url}/{role_formatted}/in-{location_formatted}?radius={radius}"
        
        self.logger.info(f"Searching for '{role}' jobs in '{location}' (radius: {radius}km)")
        self.logger.info(f"Search URL: {search_url}")
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}&page={page}" if page > 1 else search_url
            self.logger.info(f"Scraping page {page} of {max_pages}")
            
            try:
                response = self._make_request(page_url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract job listings from the page
                page_listings = self._extract_job_listings(soup)
                self.logger.info(f"Found {len(page_listings)} job listings on page {page}")
                
                job_listings.extend(page_listings)
                
                # Respect the website by adding a delay between requests
                if page < max_pages:
                    time.sleep(self.request_delay)
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
        
        self.logger.info(f"Total job listings found: {len(job_listings)}")
        return job_listings
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make an HTTP request with error handling.
        
        Args:
            url: URL to request
            
        Returns:
            Response object if successful, None otherwise
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response
            else:
                self.logger.error(f"Request failed with status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            return None
    
    def _extract_job_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract job listings from a BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of job listings as dictionaries
        """
        job_listings = []
        
        # Find all job listing elements on the page
        job_elements = soup.find_all("a", attrs={"data-at": "job-item-title"})
        
        for job_element in job_elements:
            try:
                # Extract basic job information
                job_data = self.parser.parse_job_card(job_element)
                
                if job_data:
                    job_listings.append(job_data)
                    
            except Exception as e:
                self.logger.error(f"Error extracting job data: {str(e)}")
        
        return job_listings
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific job posting.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary containing job details if successful, None otherwise
        """
        if not job_url.startswith("http"):
            job_url = f"https://www.stepstone.de{job_url}"
            
        self.logger.info(f"Getting details for job at: {job_url}")
        
        try:
            response = self._make_request(job_url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract detailed job information
            job_details = self.parser.parse_job_details(soup)
            
            return job_details
            
        except Exception as e:
            self.logger.error(f"Error getting job details: {str(e)}")
            return None