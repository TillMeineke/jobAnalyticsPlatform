"""
Configuration module for the job market data pipeline.

This module provides configuration settings for different environments
(dev, test, prod) and components of the pipeline.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ScraperConfig:
    """Configuration for the web scraper."""
    
    request_delay: float = 1.0  # Delay between requests in seconds
    max_retries: int = 3  # Maximum number of retries for failed requests
    timeout: int = 10  # Request timeout in seconds
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    roles: list = field(default_factory=lambda: ["data-scientist", "data-engineer", "data-analyst"])
    locations: list = field(default_factory=lambda: ["hamburg", "berlin", "munich"])
    search_radius: int = 30  # Search radius in km
    max_pages_per_search: int = 5  # Maximum number of pages to scrape per search


@dataclass
class StorageConfig:
    """Configuration for data storage."""
    
    local_data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    
    # S3 storage configuration
    s3_bucket: Optional[str] = None
    s3_prefix: str = "raw/stepstone"


@dataclass
class Config:
    """Main configuration class for the pipeline."""
    
    environment: str
    scraper: ScraperConfig
    storage: StorageConfig
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.
        
        Returns:
            Config object initialized from environment variables
        """
        # Get environment or default to development
        environment = os.getenv("ENVIRONMENT", "dev")
        
        # Initialize with default configurations
        scraper_config = ScraperConfig()
        storage_config = StorageConfig()
        
        # Override with environment-specific settings
        if environment == "prod":
            # Production settings
            s3_bucket = os.getenv("PROD_S3_BUCKET")
            storage_config.s3_bucket = s3_bucket
            storage_config.raw_data_dir = "data/prod/raw"
            storage_config.processed_data_dir = "data/prod/processed"
            
            # More conservative scraping in production
            scraper_config.request_delay = 2.0
            
        elif environment == "test":
            # Test settings
            storage_config.raw_data_dir = "data/test/raw"
            storage_config.processed_data_dir = "data/test/processed"
            
            # Minimal scraping for tests
            scraper_config.max_pages_per_search = 1
            
        # Development settings are already the defaults
        
        return cls(
            environment=environment,
            scraper=scraper_config,
            storage=storage_config,
        )


# Default configuration instance
config = Config.from_env()

def get_config() -> Dict[str, Any]:
    """
    Get configuration as a dictionary.
    
    This function provides easy access to the configuration settings
    for scripts that don't need the full Config object.
    
    Returns:
        Dictionary representation of the configuration
    """
    return {
        "environment": config.environment,
        "scraper": {
            "request_delay": config.scraper.request_delay,
            "max_retries": config.scraper.max_retries,
            "timeout": config.scraper.timeout,
            "user_agent": config.scraper.user_agent,
            "roles": config.scraper.roles,
            "locations": config.scraper.locations,
            "search_radius": config.scraper.search_radius,
            "max_pages_per_search": config.scraper.max_pages_per_search
        },
        "storage": {
            "local_data_dir": config.storage.local_data_dir,
            "raw_data_dir": config.storage.raw_data_dir,
            "processed_data_dir": config.storage.processed_data_dir,
            "s3_bucket": config.storage.s3_bucket,
            "s3_prefix": config.storage.s3_prefix
        }
    }