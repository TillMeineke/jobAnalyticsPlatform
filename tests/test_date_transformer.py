import unittest
from datetime import datetime, timedelta
from src.data_processing.date_transformer import DateTransformer

class TestDateTransformer(unittest.TestCase):
    
    def setUp(self):
        self.transformer = DateTransformer()
        # Fixed reference date for testing
        self.reference_date = datetime(2025, 3, 14, 9, 26, 20)
        
    def test_german_date_patterns(self):
        # Define test cases with German date strings and expected timedeltas
        test_cases = [
            ("vor 1 Tag", timedelta(days=1)),
            ("vor 2 Tagen", timedelta(days=2)),
            ("vor 1 Woche", timedelta(weeks=1)),
            ("vor 3 Wochen", timedelta(weeks=3)),
            ("vor 8 Stunden", timedelta(hours=8)),
            ("vor 1 Monat", timedelta(days=30)),
            ("vor 2 Monaten", timedelta(days=60))
        ]
        
        for german_date, expected_delta in test_cases:
            # Create a fake job posting with our reference date
            job_posting = {
                "posting_date": german_date,
                "scrape_date": self.reference_date.isoformat()
            }
            
            # Transform the job posting
            transformed = self.transformer.transform_job_posting(job_posting)
            
            # Parse the resulting date
            actual_date = datetime.fromisoformat(transformed["actual_posting_date"])
            
            # Calculate the expected date
            expected_date = self.reference_date - expected_delta
            
            # Assert that the dates match
            self.assertEqual(actual_date.date(), expected_date.date())
            
    def test_unparseable_date(self):
        # Test with an invalid date string
        job_posting = {
            "posting_date": "unparseable date",
            "scrape_date": self.reference_date.isoformat()
        }
        
        transformed = self.transformer.transform_job_posting(job_posting)
        self.assertIsNone(transformed["actual_posting_date"])
        
if __name__ == '__main__':
    unittest.main()
