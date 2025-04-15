"""Integration tests for the job scraping pipeline."""

from datetime import datetime

import pytest
from src.data_processing.data_saver import DataSaver
from src.data_processing.job_data_processor import JobDataProcessor
from src.scrapers.stepstone_scraper import StepStoneScraper


@pytest.fixture
def scraper():
    """Initialize scraper with test configuration."""
    return StepStoneScraper(
        search_term="python developer", location="Berlin", max_pages=1, headless=True
    )


@pytest.fixture
def processor():
    """Initialize data processor."""
    return JobDataProcessor()


@pytest.fixture
def data_saver():
    """Initialize data saver with test paths."""
    return DataSaver(
        bronze_path="data/test/bronze",
        silver_path="data/test/silver",
        gold_path="data/test/gold",
    )


def test_end_to_end_scraping():
    """Test complete scraping pipeline."""
    # Initialize components
    scraper = StepStoneScraper(
        search_term="python developer", location="Berlin", max_pages=1, headless=True
    )
    processor = JobDataProcessor()
    data_saver = DataSaver(
        bronze_path="data/test/bronze",
        silver_path="data/test/silver",
        gold_path="data/test/gold",
    )

    try:
        # Step 1: Scrape job listings
        raw_listings = scraper.scrape_jobs()
        assert len(raw_listings) > 0, "No job listings were scraped"

        # Step 2: Process data
        processed_listings = processor.process_listings(raw_listings)
        assert len(processed_listings) == len(raw_listings), (
            "Data lost during processing"
        )

        # Step 3: Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bronze_saved = data_saver.save_bronze_data(raw_listings, timestamp)
        silver_saved = data_saver.save_silver_data(processed_listings, timestamp)

        assert bronze_saved, "Failed to save bronze data"
        assert silver_saved, "Failed to save silver data"

    finally:
        # Cleanup
        scraper.close()
