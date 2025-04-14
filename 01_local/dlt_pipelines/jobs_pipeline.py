"""DLT pipeline for ingesting job data into the bronze layer."""

import datetime
import logging
import os
from typing import Dict, List, Iterator

import dlt
from dotenv import load_dotenv

from src.scrapers.stepstone import StepStoneScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def job_listings_resource(
    job_titles: List[str] = ["Data Engineer", "Data Scientist"],
    location: str = "Berlin",
    max_results: int = 100,
    days_back: int = 30
) -> Iterator[Dict]:
    """DLT resource that yields job listings from StepStone.
    
    Args:
        job_titles: List of job titles to search for
        location: Location to search within
        max_results: Maximum number of results to fetch
        days_back: How far back to search (in days)
        
    Yields:
        Job listings as dictionaries
    """
    logger.info(f"Fetching job listings for {job_titles} in {location}")
    
    try:
        # Initialize the scraper
        scraper = StepStoneScraper(
            max_results=max_results,
            days_back=days_back,
            headless=True
        )
        
        # Search for job listings
        jobs = scraper.search(
            job_titles=job_titles,
            location=location,
            max_results=max_results,
            days_back=days_back
        )
        
        # Yield each job
        for job in jobs:
            yield job
            
            # Fetch detailed job info if we have an ID
            if job.get("id"):
                try:
                    detailed_job = scraper.get_job_details(job["id"])
                    if detailed_job:
                        # Replace the job with the detailed version
                        yield detailed_job
                except Exception as e:
                    logger.error(f"Error fetching details for job {job['id']}: {e}")
    
    except Exception as e:
        logger.error(f"Error in job_listings_resource: {e}")
    
    finally:
        logger.info("Finished fetching job listings")


def create_bronze_pipeline(
    destination: str = "postgres"
) -> dlt.Pipeline:
    """Create a DLT pipeline for ingesting job data into the bronze layer.
    
    Args:
        destination: Destination type ('postgres' or 's3')
        
    Returns:
        DLT pipeline instance
    """
    # Create the pipeline with the specified destination
    pipeline = dlt.pipeline(
        pipeline_name="jobs_bronze",
        destination=destination,
        dataset_name="jobs_raw"
    )
    
    # Configure the destination connection
    if destination == "postgres":
        # Local PostgreSQL destination
        pipeline.default_schema = "bronze"
        pipeline.ensure_destination_config(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "jobanalytics"),
            password=os.getenv("DB_PASSWORD", "jobanalytics"),
            database=os.getenv("DB_NAME", "jobanalytics")
        )
    elif destination == "s3":
        # AWS S3 destination
        pipeline.default_schema = "bronze"
        pipeline.ensure_destination_config(
            bucket_name=os.getenv("S3_BRONZE_BUCKET"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region=os.getenv("AWS_REGION")
        )
    else:
        raise ValueError(f"Unsupported destination: {destination}")
    
    return pipeline


def run_pipeline():
    """Run the job listings pipeline."""
    # Create the pipeline
    pipeline = create_bronze_pipeline()
    
    # Add the job listings resource
    pipeline.run(
        job_listings_resource(
            job_titles=["Data Engineer", "Data Scientist"],  # Default job titles
            location="Berlin",  # Default location
            max_results=100,  # Default max results
            days_back=30  # Default days back
        ),
        table_name="job_listings",
        write_disposition="append"  # Append to existing data
    )
    
    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()