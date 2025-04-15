"""DLT pipeline for ingesting job data into the bronze layer."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterator, List

import dlt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def enrich_job_data(job: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich job data with metadata and ensure required fields."""
    enriched_job = job.copy()

    # Add metadata
    enriched_job["search_term"] = metadata.get("search_term", "unknown")
    enriched_job["search_location"] = metadata.get("location", "unknown")
    enriched_job["scrape_date"] = metadata.get("timestamp", datetime.now().isoformat())
    enriched_job["source"] = metadata.get("source", "stepstone")

    # Ensure job_id exists
    if "job_id" not in enriched_job:
        if "url" in enriched_job:
            url_parts = enriched_job["url"].split("--")
            if len(url_parts) > 1:
                enriched_job["job_id"] = (
                    url_parts[-1].split(".")[0].replace("-inline", "")
                )
            else:
                enriched_job["job_id"] = (
                    f"{enriched_job.get('company', 'unknown')}_{enriched_job.get('title', 'job')}".lower().replace(
                        " ", "_"
                    )
                )
        else:
            enriched_job["job_id"] = (
                f"{enriched_job.get('company', 'unknown')}_{enriched_job.get('title', 'job')}".lower().replace(
                    " ", "_"
                )
            )

    return enriched_job


def job_listings_resource(jobs: List[Dict], metadata: Dict[str, Any]) -> Iterator[Dict]:
    """DLT resource that yields enriched job listings.

    Args:
        jobs: List of job listings
        metadata: Search metadata (search term, location, etc.)

    Yields:
        Enriched job listings as dictionaries
    """
    logger.info(f"Processing {len(jobs)} job listings with metadata: {metadata}")

    try:
        for job in jobs:
            enriched_job = enrich_job_data(job, metadata)
            yield enriched_job

    except Exception as e:
        logger.error(f"Error in job_listings_resource: {e}")
    finally:
        logger.info("Finished processing job listings")


def create_bronze_pipeline(destination: str = "postgres") -> dlt.Pipeline:
    """Create a DLT pipeline for ingesting job data into the bronze layer.

    Args:
        destination: Destination type ('postgres' or 's3')

    Returns:
        DLT pipeline instance
    """
    pipeline = dlt.pipeline(
        pipeline_name="jobs_bronze", destination=destination, dataset_name="jobs_raw"
    )

    # Configure the destination
    if destination == "postgres":
        pipeline.default_schema = "bronze"
        pipeline.ensure_destination_config(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "jobanalytics"),
            password=os.getenv("DB_PASSWORD", "jobanalytics"),
            database=os.getenv("DB_NAME", "jobanalytics"),
        )
    elif destination == "s3":
        pipeline.default_schema = "bronze"
        pipeline.ensure_destination_config(
            bucket_name=os.getenv("S3_BRONZE_BUCKET"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region=os.getenv("AWS_REGION", "eu-central-1"),
        )
    else:
        raise ValueError(f"Unsupported destination: {destination}")

    return pipeline


def verify_data_quality(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify the quality of job data.

    Args:
        jobs: List of job dictionaries to check

    Returns:
        Dictionary with quality metrics
    """
    metrics = {
        "total_jobs": len(jobs),
        "jobs_with_missing_title": 0,
        "jobs_with_missing_company": 0,
        "jobs_with_missing_location": 0,
        "jobs_with_complete_data": 0,
    }

    for job in jobs:
        missing_fields = []

        if not job.get("title"):
            metrics["jobs_with_missing_title"] += 1
            missing_fields.append("title")

        if not job.get("company"):
            metrics["jobs_with_missing_company"] += 1
            missing_fields.append("company")

        if not job.get("location"):
            metrics["jobs_with_missing_location"] += 1
            missing_fields.append("location")

        if not missing_fields:
            metrics["jobs_with_complete_data"] += 1

    # Calculate percentages
    metrics["complete_data_percentage"] = round(
        (metrics["jobs_with_complete_data"] / metrics["total_jobs"]) * 100
        if metrics["total_jobs"] > 0
        else 0,
        2,
    )

    logger.info(f"Data quality metrics: {metrics}")
    return metrics


def run_pipeline(jobs: List[Dict[str, Any]], metadata: Dict[str, Any]):
    """Run the job listings pipeline with provided data.

    Args:
        jobs: List of job listings to process
        metadata: Search metadata (search term, location, etc.)
    """
    try:
        # Create the pipeline
        pipeline = create_bronze_pipeline()

        # Verify data quality
        quality_metrics = verify_data_quality(jobs)
        logger.info(f"Data quality check complete: {quality_metrics}")

        # Run the pipeline
        info = pipeline.run(
            job_listings_resource(jobs, metadata),
            table_name="job_listings",
            write_disposition="append",
        )

        logger.info(f"Pipeline completed successfully. Load info: {info}")
        return info

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    test_jobs = [
        {"title": "Data Engineer", "company": "Test Corp", "location": "Berlin"},
    ]
    test_metadata = {
        "search_term": "data engineer",
        "location": "berlin",
        "timestamp": datetime.now().isoformat(),
    }
    run_pipeline(test_jobs, test_metadata)
