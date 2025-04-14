"""Base scraper class for job platforms."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseScraper(ABC):
    """Base scraper class with common interface for all job platform scrapers."""

    def __init__(self, max_results: int = 100, days_back: int = 30):
        """Initialize the base scraper.

        Args:
            max_results: Maximum number of job listings to fetch
            days_back: How far back to search (in days)
        """
        self.max_results = max_results
        self.days_back = days_back

    @abstractmethod
    def search(
        self,
        job_titles: List[str],
        location: str,
        max_results: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> List[Dict]:
        """Search for job listings.

        Args:
            job_titles: List of job titles to search for
            location: Location to search within
            max_results: Maximum number of results to fetch (overrides init value)
            days_back: How far back to search (overrides init value)

        Returns:
            List of job listings as dictionaries
        """
        pass

    @abstractmethod
    def get_job_details(self, job_id: str) -> Dict:
        """Get detailed information about a specific job.

        Args:
            job_id: Unique identifier for the job

        Returns:
            Dictionary containing job details
        """
        pass

    def _normalize_job_data(self, raw_job_data: Dict) -> Dict:
        """Normalize job data to a standard format.

        Args:
            raw_job_data: Raw job data from the platform

        Returns:
            Normalized job data
        """
        # Standard fields that should be present in all job listings
        normalized_data = {
            "id": raw_job_data.get("id", ""),
            "title": raw_job_data.get("title", ""),
            "company": raw_job_data.get("company", ""),
            "location": raw_job_data.get("location", ""),
            "description": raw_job_data.get("description", ""),
            "url": raw_job_data.get("url", ""),
            "published_at": raw_job_data.get("published_at", ""),
            "scraped_at": raw_job_data.get("scraped_at", ""),
            "platform": self.__class__.__name__.replace("Scraper", "").lower(),
            "raw_data": raw_job_data,  # Store the original data for reference
        }
        return normalized_data
