#!/usr/bin/env python3
import os
import logging
import argparse
from pathlib import Path
from src.data_processing.job_data_processor import JobDataProcessor

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process job posting data from bronze to silver.')
    parser.add_argument('--bronze-dir', type=str, help='Directory containing bronze/raw data')
    parser.add_argument('--silver-dir', type=str, help='Directory to write silver/processed data')
    parser.add_argument('--file', type=str, help='Process a specific file instead of all files')
    return parser.parse_args()

def main():
    """Main entry point for the script"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    args = parse_arguments()
    
    # Initialize the processor
    processor = JobDataProcessor(
        bronze_dir=args.bronze_dir,
        silver_dir=args.silver_dir
    )
    
    if args.file:
        # Process a specific file
        input_path = Path(args.file)
        if not input_path.exists():
            logger.error(f"File not found: {args.file}")
            return 1
            
        try:
            output_file = processor.process_job_file(input_path)
            logger.info(f"Successfully processed {args.file} to {output_file}")
        except Exception as e:
            logger.error(f"Failed to process {args.file}: {e}")
            return 1
    else:
        # Process all files
        try:
            processed_files = processor.process_all_files()
            logger.info(f"Successfully processed {len(processed_files)} files")
            for file in processed_files:
                logger.info(f"  - {file}")
        except Exception as e:
            logger.error(f"Error during batch processing: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
