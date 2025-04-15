#!/usr/bin/env python3
"""
Debug script for investigating scraper issues.
This script checks file paths, dependencies, and basic scraper functionality.
"""

import os
import sys
import importlib
import logging
import colorama
from colorama import Fore, Style

# Initialize colorama for colored terminal output
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def log_success(message: str) -> None:
    """Log a success message with green color."""
    logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def log_warning(message: str) -> None:
    """Log a warning message with yellow color."""
    logger.warning(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def log_error(message: str) -> None:
    """Log an error message with red color."""
    logger.error(f"{Fore.RED}{message}{Style.RESET_ALL}")


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists at the given path."""
    exists = os.path.exists(file_path)
    if exists:
        log_success(f"File exists: {file_path}")
    else:
        log_error(f"File does not exist: {file_path}")
    return exists


def check_dependencies() -> bool:
    """Check if required Python packages are installed."""
    required_packages = ["requests", "beautifulsoup4", "pandas", "colorama"]
    all_dependencies_installed = True
    
    log_warning("Checking required Python packages...")
    for package in required_packages:
        try:
            importlib.import_module(package)
            log_success(f"Package installed: {package}")
        except ImportError:
            log_error(f"Package not installed: {package}")
            all_dependencies_installed = False
    
    return all_dependencies_installed


def check_scraper_structure() -> bool:
    """Check the structure of the scraper module."""
    # Paths to check
    paths_to_check = [
        "src/run_scraper.py",
        "src/scraper/stepstone_scraper.py",
        "src/scraper/job_parser.py",
        "src/data_processing/data_saver.py",
    ]
    
    all_files_exist = True
    for path in paths_to_check:
        if not check_file_exists(path):
            all_files_exist = False
    
    return all_files_exist


def check_directory_structure() -> None:
    """Check the directory structure and print out key directories."""
    log_warning("Current directory: " + os.getcwd())
    log_warning("Directory contents:")
    
    try:
        # List the main directory contents
        for item in os.listdir('.'):
            if os.path.isdir(item):
                log_warning(f"  DIR: {item}/")
            else:
                log_warning(f"  FILE: {item}")
        
        # Check src directory if it exists
        if os.path.isdir('src'):
            log_warning("\nsrc/ directory contents:")
            for item in os.listdir('src'):
                log_warning(f"  {item}")
    except Exception as e:
        log_error(f"Error listing directory contents: {str(e)}")


def main() -> None:
    """Main function to run the debugging steps."""
    log_warning("=== Scraper Debugging Script ===")
    
    # Check current directory and structure
    check_directory_structure()
    
    # Check if required Python packages are installed
    dependencies_ok = check_dependencies()
    if not dependencies_ok:
        log_error("Missing required Python packages. Install them with pip before continuing.")
    
    # Check scraper file structure
    structure_ok = check_scraper_structure()
    if not structure_ok:
        log_error("Scraper structure issues detected. Some files are missing.")
    
    # Show Makefile scraper command
    try:
        with open('Makefile', 'r') as file:
            makefile_content = file.read()
            scraper_section = makefile_content.split('scrape-data:')[1].split('\n\n')[0]
            log_warning("\nMakefile scrape-data section:")
            log_warning(scraper_section)
    except Exception as e:
        log_error(f"Error reading Makefile: {str(e)}")
    
    # Summary
    if dependencies_ok and structure_ok:
        log_success("\nBasic checks passed. The issue might be in the scraper code execution.")
        log_success("Try running the scraper directly with:")
        log_success("python src/run_scraper.py --search-term \"data engineer\" --location \"Hamburg\" --max-pages 2 --fetch-details --debug")
    else:
        log_error("\nIssues detected with dependencies or file structure.")
        log_error("Fix these issues before running the scraper.")


if __name__ == "__main__":
    main()