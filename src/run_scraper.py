#!/usr/bin/env python3
"""
Job data scraper module for Stepstone.

This module provides functionality to scrape job listings from Stepstone
and save the data for further processing.
"""

import os
import sys
import argparse
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scraper.stepstone_scraper import StepstoneScraper
from src.data_processing.data_saver import DataSaver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def setup_arg_parser() -> argparse.ArgumentParser:
    """
    Set up command line argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Scrape job postings from Stepstone.'
    )
    
    parser.add_argument(
        '--search-term',
        type=str,
        default='data scientist',
        help='Job title or search term (default: "data scientist")'
    )
    
    parser.add_argument(
        '--location',
        type=str,
        default='hamburg',
        help='Job location (default: "hamburg")'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=1,
        help='Maximum number of search results pages to scrape (default: 1)'
    )
    
    parser.add_argument(
        '--fetch-details',
        action='store_true',
        help='Fetch detailed job information for each listing (slower)'
    )
    
    parser.add_argument(
        '--output-formats',
        type=str,
        default='json,csv',
        help='Comma-separated list of output formats: json,csv,parquet (default: json,csv)'
    )
    
    parser.add_argument(
        '--use-s3',
        action='store_true',
        help='Save output to S3 instead of local filesystem'
    )
    
    parser.add_argument(
        '--s3-bucket',
        type=str,
        help='S3 bucket name (required if --use-s3 is specified)'
    )
    
    parser.add_argument(
        '--output-path',
        type=str,
        default='data/raw/bronze',
        help='Output directory path (default: data/raw/bronze)'
    )
    
    return parser


def run_scraper(search_term: str, location: str, max_pages: int = 1, 
               fetch_details: bool = False) -> List[Dict[Any, Any]]:
    """
    Run the job scraper with the specified parameters.

    Args:
        search_term: Job search term
        location: Job location
        max_pages: Maximum number of search results pages to scrape
        fetch_details: Whether to fetch detailed job information

    Returns:
        List of job dictionaries
    """
    logger.info(f"Starting scraper for '{search_term}' jobs in '{location}'")
    
    scraper = StepstoneScraper()
    jobs = scraper.search_jobs(search_term, location, max_pages=max_pages)
    
    if fetch_details and jobs:
        logger.info(f"Fetching details for {len(jobs)} job listings")
        for i, job in enumerate(jobs):
            if "job_url" in job:
                try:
                    logger.info(f"Fetching details for job {i+1}/{len(jobs)}: {job['job_title']}")
                    job_details = scraper.get_job_details(job["job_url"])
                    if job_details:
                        # Update the job with detailed information
                        job.update(job_details)
                except Exception as e:
                    logger.error(f"Error fetching job details for {job['job_title']}: {str(e)}")
    
    logger.info(f"Scraper finished. Total job listings found: {len(jobs)}")
    return jobs


def main():
    """Main function to run the scraper."""
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # Parse output formats
    output_formats = [fmt.strip().lower() for fmt in args.output_formats.split(',')]
    
    try:
        # Run the scraper to get job data
        jobs = run_scraper(
            args.search_term, 
            args.location,
            max_pages=args.max_pages,
            fetch_details=args.fetch_details
        )
        
        if not jobs:
            logger.warning("No jobs found. Nothing to save.")
            return
        
        # Configure data saver
        data_saver = DataSaver(
            base_path=args.output_path,
            use_s3=args.use_s3,
            s3_bucket=args.s3_bucket if args.use_s3 else None
        )
        
        # Save the data in requested formats
        timestamp = datetime.now()
        save_results = data_saver.save_data(
            jobs, 
            args.search_term, 
            args.location, 
            formats=output_formats,
            timestamp=timestamp
        )
        
        # Report results
        logger.info(f"Job data saved successfully:")
        for fmt, path in save_results.items():
            logger.info(f"  - {fmt.upper()}: {path}")
        
    except Exception as e:
        logger.error(f"Error running scraper: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()