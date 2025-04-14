# 📊 Metabase Dashboards

This directory contains Metabase dashboard configurations for visualizing job market analytics.

## 🏗️ Dashboard Architecture

The dashboards are built on top of the gold layer tables and views, following the medallion architecture (Bronze 🥉 → Silver 🥈 → Gold 🥇).

## 📊 Available Dashboards

### 1. Job Market Overview Dashboard

This dashboard provides a high-level overview of the job market:

- **Job Count by Time**: Line chart showing job posting trends over time
- **Job Distribution by Company**: Bar chart of top companies by job count
- **Job Distribution by Location**: Map or bar chart of jobs by location
- **Job Title Word Cloud**: Visual representation of common job titles

### 2. Skill Demand Analysis Dashboard

This dashboard focuses on skill requirements and keyword analysis:

- **Top Skills in Demand**: Bar chart of most requested skills
- **Skill Trends Over Time**: Line chart showing changing skill demands
- **Education Requirements**: Breakdown of education levels requested
- **Experience Requirements**: Distribution of years of experience required

## 🔄 Data Refresh

Dashboards are refreshed according to the pipeline schedule:

- **Local Environment**: Data refreshes when the pipeline is manually triggered
- **Cloud Environment**: Automatic daily refresh at 2 AM UTC

## 🔧 Setup Instructions

### Local Setup

1. Start the Docker environment:
   ```bash
   cd 01_local
   docker-compose up -d
   ```

2. Access Metabase at `http://localhost:3000`

3. Login with default credentials:
   - Username: `admin@jobanalytics.com`
   - Password: `metabase123`

4. Set up a new database connection:
   - Name: `Job Analytics DB`
   - Engine: `PostgreSQL`
   - Host: `postgres`
   - Port: `5432`
   - Database Name: `jobanalytics`
   - Username: `jobanalytics`
   - Password: `jobanalytics`

5. Import dashboard configurations from the `.metabase` files in this directory

### Importing Dashboards

Pre-configured dashboards can be imported using the Metabase admin interface:

1. Go to `Admin settings` → `Databases`
2. Ensure your database is connected and synchronized
3. Navigate to `Dashboard` → `Import` 
4. Select the `.metabase` file you wish to import

## 📱 Dashboard Examples

### Job Count by Time
![Job Count by Time](../docs/images/job_count_time.png)

### Job Distribution by Location
![Job Distribution by Location](../docs/images/job_location.png)

## 🔒 Access Control

By default, all users have view access to the dashboards. To modify access:

1. Go to `Admin settings` → `Permissions`
2. Configure access controls as needed for your organization

## 🔄 Customization

To customize dashboards:

1. Clone an existing dashboard using the "Copy" function
2. Modify visualizations, filters, and layout as needed
3. Save with a new name to preserve the original template