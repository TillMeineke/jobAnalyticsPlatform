"""
Job Parser for Stepstone.

This module provides functionality to parse and extract structured data
from Stepstone job listings.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from bs4 import BeautifulSoup, Tag


class JobParser:
    """
    A class to parse job listings from Stepstone.de.
    
    This parser extracts structured data from job listing HTML elements.
    It provides methods for parsing both job cards (search results) and
    detailed job pages.
    """
    
    def parse_job_card(self, job_element: Tag) -> Optional[Dict[str, Any]]:
        """
        Parse a job card element from the search results page.
        
        Args:
            job_element: BeautifulSoup Tag object representing a job card
            
        Returns:
            Dictionary containing extracted job data or None if parsing fails
        """
        try:
            # Extract job title and URL
            job_title = job_element.get_text(strip=True)
            job_url = job_element.get("href", "")
            
            # Create job listing dictionary with basic information
            job_data = {
                "job_id": self._extract_job_id(job_url),
                "job_title": job_title,
                "job_url": job_url,
                "scrape_date": datetime.now().isoformat(),
            }
            
            # Find the parent article that contains additional information
            parent_article = self._find_parent_article(job_element)
            if parent_article:
                # Extract additional data from the parent article
                company_name = self._extract_company_name(parent_article)
                location = self._extract_location(parent_article)
                posting_date = self._extract_posting_date(parent_article)
                
                # Add additional information to the job data
                if company_name:
                    job_data["company_name"] = company_name
                if location:
                    job_data["location"] = location
                if posting_date:
                    job_data["posting_date"] = posting_date
            
            return job_data
            
        except Exception as e:
            print(f"Error parsing job card: {str(e)}")
            return None
            
    def parse_job_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parse the detailed job page to extract comprehensive information.
        
        Args:
            soup: BeautifulSoup object of the job detail page
            
        Returns:
            Dictionary containing detailed job information
        """
        job_details = {}
        
        try:
            # Extract job title
            title_element = soup.find("h1")
            if title_element:
                job_details["job_title"] = title_element.get_text(strip=True)
            
            # Extract company name
            company_element = soup.find("span", {"data-at": "job-header-company"})
            if company_element:
                job_details["company_name"] = company_element.get_text(strip=True)
            
            # Extract company details if available
            company_details = self._extract_company_details(soup)
            if company_details:
                job_details["company_details"] = company_details
            
            # Extract job description
            description_element = soup.find("div", {"data-at": "job-description"})
            if description_element:
                job_details["description"] = description_element.get_text(strip=True)
                
                # Extract skills from the description
                job_details["skills"] = self._extract_skills(description_element.get_text())
            
            # Extract salary information if available
            salary_element = soup.find("span", {"data-at": "job-header-salary"})
            if salary_element:
                job_details["salary"] = self._parse_salary(salary_element.get_text(strip=True))
            
            # Extract employment type
            employment_type_element = soup.find("span", {"data-at": "job-header-employment-type"})
            if employment_type_element:
                job_details["employment_type"] = employment_type_element.get_text(strip=True)
                
            # Extract similar/related job titles
            related_jobs = self._extract_related_jobs(soup)
            if related_jobs:
                job_details["related_jobs"] = related_jobs
                
            # Extract job requirements and qualifications
            requirements = self._extract_requirements(soup)
            if requirements:
                job_details["requirements"] = requirements
            
        except Exception as e:
            print(f"Error parsing job details: {str(e)}")
        
        return job_details
    
    def _extract_job_id(self, job_url: str) -> str:
        """
        Extract the job ID from the URL.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Job ID as a string
        """
        try:
            # Extract job ID from URL pattern
            match = re.search(r"--(\d+)-", job_url)
            if match:
                return match.group(1)
            else:
                return job_url.split("/")[-1].split(".")[0]
        except Exception:
            return f"unknown-{datetime.now().timestamp()}"
    
    def _find_parent_article(self, element: Tag) -> Optional[Tag]:
        """
        Find the parent article element containing additional job information.
        
        Args:
            element: BeautifulSoup Tag object
            
        Returns:
            Parent article Tag if found, None otherwise
        """
        parent = element
        max_levels = 5  # Limit search to 5 levels up to avoid infinite loops
        
        for _ in range(max_levels):
            if parent is None:
                return None
            
            if parent.name == "article":
                return parent
            
            parent = parent.parent
            
        return None
    
    def _extract_company_name(self, article: Tag) -> Optional[str]:
        """
        Extract the company name from the article element.
        
        Args:
            article: Article Tag object
            
        Returns:
            Company name as a string if found, None otherwise
        """
        company_element = article.find(attrs={"data-at": "job-item-company-name"})
        if company_element:
            return company_element.get_text(strip=True)
        return None
    
    def _extract_location(self, article: Tag) -> Optional[str]:
        """
        Extract the job location from the article element.
        
        Args:
            article: Article Tag object
            
        Returns:
            Location as a string if found, None otherwise
        """
        location_element = article.find(attrs={"data-at": "job-item-location"})
        if location_element:
            return location_element.get_text(strip=True)
        return None
    
    def _extract_posting_date(self, article: Tag) -> Optional[str]:
        """
        Extract the posting date from the article element.
        
        Args:
            article: Article Tag object
            
        Returns:
            Posting date as a string if found, None otherwise
        """
        date_element = article.find("span", {"data-at": "job-item-timeago"})
        if date_element and date_element.find("time"):
            return date_element.find("time").get_text(strip=True)
        return None
        
    def _extract_company_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract detailed information about the company.
        
        Args:
            soup: BeautifulSoup object of the job detail page
            
        Returns:
            Dictionary containing company details
        """
        company_details = {}
        
        try:
            # Look for company size
            company_size_elements = soup.find_all(string=re.compile(r"Company size|Employees|Mitarbeiter"))
            for element in company_size_elements:
                parent = element.parent
                if parent and parent.next_sibling:
                    company_details["company_size"] = parent.next_sibling.get_text(strip=True)
                    break
            
            # Look for company industry
            industry_elements = soup.find_all(string=re.compile(r"Industry|Branche"))
            for element in industry_elements:
                parent = element.parent
                if parent and parent.next_sibling:
                    company_details["industry"] = parent.next_sibling.get_text(strip=True)
                    break
                    
            # Look for company website
            website_elements = soup.find_all("a", href=re.compile(r"^https?://"))
            for element in website_elements:
                if "Website" in element.get_text() or "website" in element.get_text():
                    company_details["website"] = element.get("href")
                    break
            
            # Look for company location
            company_location_elements = soup.find_all(string=re.compile(r"Headquarters|Hauptsitz"))
            for element in company_location_elements:
                parent = element.parent
                if parent and parent.next_sibling:
                    company_details["headquarters"] = parent.next_sibling.get_text(strip=True)
                    break
                    
        except Exception as e:
            print(f"Error extracting company details: {str(e)}")
            
        return company_details
    
    def _extract_related_jobs(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract similar or related job titles.
        
        Args:
            soup: BeautifulSoup object of the job detail page
            
        Returns:
            List of related job titles and their URLs
        """
        related_jobs = []
        
        try:
            # Look for "Similar Jobs" or "Related Jobs" section
            related_job_sections = soup.find_all("div", string=re.compile(r"Similar Jobs|Related Jobs|Ähnliche Jobs"))
            
            for section in related_job_sections:
                job_links = section.parent.find_all("a")
                for link in job_links:
                    job_title = link.get_text(strip=True)
                    job_url = link.get("href")
                    if job_title and job_url and not job_title.lower() in ["similar jobs", "related jobs", "ähnliche jobs"]:
                        related_jobs.append({
                            "title": job_title,
                            "url": job_url if job_url.startswith("http") else f"https://www.stepstone.de{job_url}"
                        })
            
            # If no dedicated section found, try to find "You might also be interested in" section
            if not related_jobs:
                interested_sections = soup.find_all("h2", string=re.compile(r"might also be interested|könnte auch interessieren"))
                for section in interested_sections:
                    job_links = section.parent.find_all("a")
                    for link in job_links:
                        job_title = link.get_text(strip=True)
                        job_url = link.get("href")
                        if job_title and job_url:
                            related_jobs.append({
                                "title": job_title,
                                "url": job_url if job_url.startswith("http") else f"https://www.stepstone.de{job_url}"
                            })
        
        except Exception as e:
            print(f"Error extracting related jobs: {str(e)}")
            
        return related_jobs
    
    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract job requirements and qualifications.
        
        Args:
            soup: BeautifulSoup object of the job detail page
            
        Returns:
            List of job requirements
        """
        requirements = []
        
        try:
            # Look for requirements section
            req_headers = soup.find_all(string=re.compile(r"Requirements|Qualifications|Anforderungen|Qualifikationen"))
            
            for header in req_headers:
                parent = header.parent
                if parent:
                    # Look for list elements after the header
                    ul_elements = parent.find_all_next("ul", limit=2)  # Limit to avoid parsing unrelated lists
                    for ul in ul_elements:
                        li_elements = ul.find_all("li")
                        for li in li_elements:
                            requirement = li.get_text(strip=True)
                            if requirement:
                                requirements.append(requirement)
            
            # If no requirements found through headers, try to find common requirement patterns in the description
            if not requirements:
                description_element = soup.find("div", {"data-at": "job-description"})
                if description_element:
                    requirements = self._extract_requirements_from_text(description_element.get_text())
        
        except Exception as e:
            print(f"Error extracting requirements: {str(e)}")
            
        return requirements
    
    def _extract_requirements_from_text(self, text: str) -> List[str]:
        """
        Extract requirements from job description text.
        
        Args:
            text: Job description text
            
        Returns:
            List of requirements
        """
        requirements = []
        
        # Common requirement indicators
        requirement_sections = [
            r"Requirements:", r"Qualifications:", r"Anforderungen:", r"Qualifikationen:",
            r"You should have:", r"You must have:", r"You need:", r"We require:",
            r"Skills required:", r"Minimum qualifications:", r"What you'll need:"
        ]
        
        # Try to find requirement sections and extract points
        for indicator in requirement_sections:
            if indicator in text:
                section_start = text.find(indicator) + len(indicator)
                # Find the next section header (often starts with a newline and uppercase)
                section_end_matches = re.search(r"\n[A-Z][a-zA-Z\s]+:", text[section_start:])
                if section_end_matches:
                    section_end = section_start + section_end_matches.start()
                else:
                    section_end = len(text)
                
                section_text = text[section_start:section_end].strip()
                # Split by newlines or bullet points
                points = re.split(r"\n+|•|\*|\-|\d+\.", section_text)
                for point in points:
                    point = point.strip()
                    if point and len(point) > 10:  # Avoid very short fragments
                        requirements.append(point)
                
                # If we found at least one requirement, stop looking
                if requirements:
                    break
        
        return requirements
    
    def _extract_skills(self, description: str) -> List[str]:
        """
        Extract mentioned skills from job description.
        
        This is an enhanced implementation that looks for common data science,
        technology, and soft skills in the description text.
        
        Args:
            description: Job description text
            
        Returns:
            List of identified skills
        """
        skills = []
        description_lower = description.lower()
        
        # Common technical skills
        tech_skill_patterns = [
            # Programming languages
            r"python", r"sql", r"r\s+language", r"\br\b", r"java\b", r"javascript", r"typescript",
            r"c\+\+", r"c#", r"scala", r"php", r"perl", r"ruby", r"go\b", r"golang", r"swift",
            r"kotlin", r"rust", r"bash", r"shell", r"powershell",
            
            # Web development
            r"html", r"css", r"react", r"vue", r"angular", r"node\.?js", r"express\.?js", 
            r"django", r"flask", r"fastapi", r"spring\s+boot", r"asp\.net", r"laravel",
            
            # Data engineering
            r"etl", r"data\s+pipeline", r"data\s+warehouse", r"data\s+lake", r"data\s+mesh",
            r"airflow", r"luigi", r"dagster", r"prefect", r"dbt", r"fivetran", r"stitch",
            r"datadog", r"databricks", r"snowflake", r"redshift", r"bigquery", r"synapse",
            
            # Big data
            r"hadoop", r"spark", r"kafka", r"flink", r"hive", r"storm", r"cassandra", r"hbase",
            r"elasticsearch", r"solr", r"pig", r"impala", r"druid", r"presto", r"trino",
            
            # Cloud
            r"aws", r"azure", r"gcp", r"google\s+cloud", r"cloud", r"s3", r"ec2", r"lambda",
            r"dynamodb", r"rds", r"aurora", r"sqs", r"sns", r"kinesis", r"cloudformation",
            r"terraform", r"pulumi", r"cloudflare", r"netlify", r"vercel", r"heroku",
            
            # Container & orchestration
            r"docker", r"kubernetes", r"k8s", r"openshift", r"rancher", r"helm", r"istio",
            r"prometheus", r"grafana", r"argo", r"jenkins", r"gitlab\s+ci", r"github\s+actions",
            
            # Data science & ML
            r"pandas", r"numpy", r"scikit.learn", r"scipy", r"matplotlib", r"seaborn",
            r"tensorflow", r"pytorch", r"keras", r"hugging\s+face", r"transformers", r"spacy", r"nltk",
            r"machine\s+learning", r"deep\s+learning", r"nlp", r"natural\s+language\s+processing",
            r"computer\s+vision", r"reinforcement\s+learning", r"generative\s+ai", r"llm",
            r"large\s+language\s+model", r"gpt", r"bert", r"neural\s+network", 
            
            # BI & visualization
            r"data\s+visualization", r"tableau", r"power\s+bi", r"looker", r"qlik",
            r"data\s+studio", r"metabase", r"superset", r"redash", r"mode", r"domo",
            
            # Database
            r"mysql", r"postgresql", r"sql\s+server", r"oracle", r"mongodb", r"couchdb",
            r"redis", r"neo4j", r"graphql", r"dax", r"mdx", r"olap", r"oltp",
            
            # Version control & dev tools
            r"git", r"github", r"gitlab", r"bitbucket", r"jira", r"confluence", r"agile",
            r"scrum", r"kanban", r"ci/cd", r"continuous\s+integration", r"continuous\s+delivery",
            
            # Other technical skills
            r"restful\s+api", r"graphql", r"microservices", r"serverless",
            r"oauth", r"authentication", r"authorization", r"security", r"encryption",
            r"regression\s+testing", r"unit\s+testing", r"e2e\s+testing", r"selenium",
            r"cypress", r"jest", r"pytest", r"junit"
        ]
        
        # Soft skills
        soft_skill_patterns = [
            r"communication", r"teamwork", r"leadership", r"problem.solving", r"critical\s+thinking",
            r"time\s+management", r"project\s+management", r"analytical\s+skills", r"creativity",
            r"adaptability", r"flexibility", r"attention\s+to\s+detail", r"collaboration",
            r"interpersonal\s+skills", r"presentation\s+skills", r"decision.making",
            r"conflict\s+resolution", r"emotional\s+intelligence", r"negotiation",
            r"mentoring", r"coaching", r"stakeholder\s+management"
        ]
        
        # Find matching technical skills in the description
        for pattern in tech_skill_patterns:
            if re.search(pattern, description_lower):
                # Convert pattern to readable skill name
                skill = pattern.replace(r"\s+", " ")
                skill = skill.replace(r"\b", "")
                skill = skill.replace(r"\.", ".")
                skill = skill.replace(r"\+", "+")
                skill = skill.replace(r"\?", "?")
                
                # Add the skill to our list
                skills.append(skill)
        
        # Find matching soft skills and add them with a 'soft skill:' prefix
        for pattern in soft_skill_patterns:
            if re.search(pattern, description_lower):
                skill = pattern.replace(r"\s+", " ")
                skill = f"soft skill: {skill}"
                skills.append(skill)
        
        return skills
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """
        Parse salary information into a structured format.
        
        Args:
            salary_text: Text containing salary information
            
        Returns:
            Dictionary containing structured salary data
        """
        salary_data = {"raw": salary_text}
        
        try:
            # Extract salary range if present
            range_match = re.search(r"(\d+[\.,]\d+)\s*-\s*(\d+[\.,]\d+)", salary_text)
            if range_match:
                min_salary = float(range_match.group(1).replace(".", "").replace(",", "."))
                max_salary = float(range_match.group(2).replace(".", "").replace(",", "."))
                
                salary_data["min_salary"] = min_salary
                salary_data["max_salary"] = max_salary
                salary_data["avg_salary"] = (min_salary + max_salary) / 2
            
            # Extract currency
            currency_match = re.search(r"(€|\$|£|EUR|USD|GBP)", salary_text)
            if currency_match:
                salary_data["currency"] = currency_match.group(1)
            
            # Extract frequency (yearly, monthly, etc.)
            if re.search(r"year|yearly|annual|p\.a\.|per\s+annum", salary_text, re.IGNORECASE):
                salary_data["frequency"] = "yearly"
            elif re.search(r"month|monthly", salary_text, re.IGNORECASE):
                salary_data["frequency"] = "monthly"
            elif re.search(r"hour|hourly", salary_text, re.IGNORECASE):
                salary_data["frequency"] = "hourly"
            elif re.search(r"day|daily", salary_text, re.IGNORECASE):
                salary_data["frequency"] = "daily"
            else:
                salary_data["frequency"] = "unknown"
                
        except Exception:
            # If parsing fails, just keep the raw text
            pass
            
        return salary_data