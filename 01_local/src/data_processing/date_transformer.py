import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DateTransformer:
    """
    A utility class for transforming German date phrases like 'vor 1 Tag' into 
    actual datetime objects and ISO formatted date strings.
    """
    
    def __init__(self):
        # German time unit patterns with singular and plural forms
        self.patterns = {
            r'vor\s+(\d+)\s+Stunde[n]?': lambda x: timedelta(hours=int(x)),
            r'vor\s+(\d+)\s+Tag[en]?': lambda x: timedelta(days=int(x)),
            r'vor\s+(\d+)\s+Woche[n]?': lambda x: timedelta(weeks=int(x)),
            r'vor\s+(\d+)\s+Monat[en]?': lambda x: timedelta(days=int(x) * 30),  # Approximation
        }
    
    def german_posting_date_to_datetime(self, posting_date, scrape_date=None):
        """
        Convert a German posting date phrase to a Python datetime object.
        
        Args:
            posting_date (str): The German posting date phrase (e.g., 'vor 1 Tag')
            scrape_date (str, optional): The scrape date as reference point. 
                                        If None, current time is used.
                                        
        Returns:
            datetime: The calculated datetime object
        """
        if not posting_date:
            return None
        
        # Use scrape_date if provided, otherwise use current time
        if scrape_date and isinstance(scrape_date, str):
            try:
                reference_date = datetime.fromisoformat(scrape_date.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Could not parse scrape_date: {scrape_date}")
                reference_date = datetime.now()
        else:
            reference_date = datetime.now()
            
        # Try to match the posting date string against our patterns
        for pattern, time_func in self.patterns.items():
            match = re.match(pattern, posting_date)
            if match:
                time_value = match.group(1)
                delta = time_func(time_value)
                return reference_date - delta
        
        # Return None if no pattern matches
        logger.warning(f"Could not parse posting date: {posting_date}")
        return None
    
    def transform_job_posting(self, job_posting):
        """
        Add a new field with the calculated actual posting date to a job posting.
        
        Args:
            job_posting (dict): A job posting dictionary
            
        Returns:
            dict: The job posting with an added 'actual_posting_date' field
        """
        if not job_posting.get('posting_date'):
            job_posting['actual_posting_date'] = None
            return job_posting
            
        posting_datetime = self.german_posting_date_to_datetime(
            job_posting.get('posting_date'),
            job_posting.get('scrape_date')
        )
        
        if posting_datetime:
            # Store as ISO format string
            job_posting['actual_posting_date'] = posting_datetime.isoformat()
        else:
            job_posting['actual_posting_date'] = None
            
        return job_posting
