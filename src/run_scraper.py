#!/usr/bin/env python
"""
Script to run the Stepstone job scraper.

This script runs the StepstoneScraper to collect job data including:
- Basic job information
- Company details
- Skills mentioned in job descriptions
- Similar/related job titles
- Salary data (when available, may be behind authentication)

Usage:
    python -m src.run_scraper --role "Data Engineer" --location "Berlin" --max-pages 5 --output job_data.json
"""
import argparse
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List

import pandas as pd

# Fix the imports to work properly when run as a module
from src.scraper.stepstone_scraper import StepstoneScraper
from src.config.config import get_config


def setup_argparse() -> argparse.Namespace:
    """
    Set up the command line argument parser.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Run Stepstone job scraper")
    
    parser.add_argument(
        "--role",
        type=str,
        required=True,
        help="Job role/title to search for (e.g., 'Data Engineer')"
    )
    
    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help="Location to search jobs in (e.g., 'Berlin')"
    )
    
    parser.add_argument(
        "--radius",
        type=int,
        default=30,
        help="Search radius in km (default: 30)"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of search result pages to scrape (default: 5)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file path (default: auto-generated based on search parameters)"
    )
    
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=None,
        help="Limit number of job listings to get detailed information for (default: all)"
    )
    
    parser.add_argument(
        "--request-delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    return parser.parse_args()


def configure_logging(log_level: str) -> logging.Logger:
    """
    Configure logging for the script.
    
    Args:
        log_level: Logging level as string
        
    Returns:
        Configured logger
    """
    # Map string log levels to numeric values
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    numeric_level = level_map.get(log_level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger("run_scraper")
    logger.setLevel(numeric_level)
    
    # Create console handler and set level
    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def generate_output_path(role: str, location: str, output_dir: str = "data/raw") -> str:
    """
    Generate output file path based on search parameters.
    
    Args:
        role: Job role/title
        location: Location
        output_dir: Directory to store output files
        
    Returns:
        Generated file path
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Format role and location for filename
    role_formatted = role.lower().replace(" ", "_")
    location_formatted = location.lower().replace(" ", "_")
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{role_formatted}_{location_formatted}_{timestamp}.json"
    
    return os.path.join(output_dir, filename)


def save_data(data: List[Dict], output_path: str, logger: logging.Logger) -> None:
    """
    Save the job data to disk.
    
    Args:
        data: List of job data dictionaries
        output_path: Path to save the data to
        logger: Logger instance
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Data saved to {output_path}")
    
    # Also save as CSV for easy viewing
    csv_path = output_path.replace(".json", ".csv")
    
    try:
        # Flatten job data for CSV
        flattened_data = []
        for job in data:
            flat_job = {}
            # Extract top level fields
            for key, value in job.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    flat_job[key] = value
                elif key == "skills" and isinstance(value, list):
                    flat_job["skills"] = ", ".join(value)
                elif key == "salary" and isinstance(value, dict):
                    for salary_key, salary_value in value.items():
                        flat_job[f"salary_{salary_key}"] = salary_value
            
            flattened_data.append(flat_job)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(flattened_data)
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Data also saved as CSV to {csv_path}")
    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")


def main():
    """Main function to run the scraper."""
    # Parse command line arguments
    args = setup_argparse()
    
    # Configure logging
    logger = configure_logging(args.log_level)
    
    # Get numeric log level for the scraper
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    scraper_log_level = level_map.get(args.log_level, logging.INFO)
    
    # Get config
    try:
        config = get_config()
        env = config.get("environment", "dev")
        logger.info(f"Running in {env} environment")
    except Exception as e:
        logger.warning(f"Failed to load config: {str(e)}. Using default values.")
        env = "dev"
    
    # Initialize scraper
    scraper = StepstoneScraper(
        log_level=scraper_log_level,
        request_delay=args.request_delay
    )
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Generate output path based on search parameters
        if env == "dev":
            output_dir = "data/raw/bronze"
        elif env == "test":
            output_dir = "data/raw/silver"
        else:  # prod
            output_dir = "data/raw/gold"
        
        output_path = generate_output_path(args.role, args.location, output_dir)
    
    logger.info(f"Starting job search for '{args.role}' in '{args.location}'")
    
    # Search for jobs
    job_listings = scraper.search_jobs(
        role=args.role,
        location=args.location,
        radius=args.radius,
        max_pages=args.max_pages
    )
    
    logger.info(f"Found {len(job_listings)} job listings")
    
    # Get detailed information for each job
    jobs_with_details = []
    job_count = len(job_listings)
    detail_limit = args.detail_limit if args.detail_limit is not None else job_count
    
    logger.info(f"Fetching detailed information for up to {detail_limit} jobs...")
    
    for i, job in enumerate(job_listings[:detail_limit], 1):
        try:
            logger.info(f"Processing job {i}/{min(detail_limit, job_count)}: {job.get('job_title', 'Unknown')}")
            
            # Get detailed information
            job_url = job.get("job_url")
            if job_url:
                job_details = scraper.get_job_details(job_url)
                
                if job_details:
                    # Merge the job data
                    job_data = {**job, **job_details}
                    jobs_with_details.append(job_data)
                else:
                    # If we couldn't get details, just use the basic information
                    logger.warning(f"Could not get details for job {i}, using basic information only")
                    jobs_with_details.append(job)
            else:
                logger.warning(f"No URL found for job {i}, using basic information only")
                jobs_with_details.append(job)
                
            # Add delay between requests
            if i < min(detail_limit, job_count):
                time.sleep(args.request_delay)
                
        except Exception as e:
            logger.error(f"Error processing job {i}: {str(e)}")
            jobs_with_details.append(job)
    
    # Save the data
    save_data(jobs_with_details, output_path, logger)
    
    # Print summary
    logger.info("Job search completed successfully")
    logger.info(f"Total jobs found: {job_count}")
    logger.info(f"Jobs with detailed information: {len(jobs_with_details)}")
    logger.info(f"Data saved to: {output_path}")


if __name__ == "__main__":
    main()