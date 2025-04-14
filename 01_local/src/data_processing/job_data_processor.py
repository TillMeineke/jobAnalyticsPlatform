import os
import json
import logging
from pathlib import Path
from .date_transformer import DateTransformer

logger = logging.getLogger(__name__)

class JobDataProcessor:
    """
    Process job posting data from bronze to silver, enhancing and standardizing fields.
    """
    
    def __init__(self, bronze_dir=None, silver_dir=None):
        """
        Initialize the processor with directories for bronze and silver data.
        
        Args:
            bronze_dir (str, optional): Directory for bronze/raw data
            silver_dir (str, optional): Directory for silver/processed data
        """
        self.date_transformer = DateTransformer()
        
        # Set default directories if not provided
        base_dir = Path('/Users/tillmeineke/ML/DE_Zoomcamp2025_hw/capstone_project_1/data')
        self.bronze_dir = bronze_dir or base_dir / 'raw/bronze'
        self.silver_dir = silver_dir or base_dir / 'processed/silver'
        
        # Ensure directories exist
        os.makedirs(self.silver_dir, exist_ok=True)
    
    def process_job_file(self, input_file, output_file=None):
        """
        Process a single job posting file, adding standardized dates.
        
        Args:
            input_file (str): Path to the input JSON file
            output_file (str, optional): Path to write the processed data.
                                        If None, will use input filename in silver directory.
                                        
        Returns:
            str: Path to the processed output file
        """
        try:
            # Default output filename if not specified
            if not output_file:
                input_path = Path(input_file)
                output_file = self.silver_dir / input_path.name
            
            # Read input data
            with open(input_file, 'r', encoding='utf-8') as f:
                job_postings = json.load(f)
            
            # Process each job posting
            processed_postings = []
            for posting in job_postings:
                # Apply date transformation
                enhanced_posting = self.date_transformer.transform_job_posting(posting)
                processed_postings.append(enhanced_posting)
                
            # Write processed data to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_postings, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Processed {len(processed_postings)} job postings to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing file {input_file}: {e}")
            raise
    
    def process_all_files(self):
        """
        Process all job posting files from bronze to silver.
        
        Returns:
            list: Paths to all processed output files
        """
        processed_files = []
        
        # Find all JSON files in bronze directory
        for file_path in Path(self.bronze_dir).glob('*.json'):
            output_file = self.process_job_file(file_path)
            processed_files.append(output_file)
            
        return processed_files
