# 🔄 Job Analytics Flows

This directory contains Kestra flows for the Job Analytics Platform.

## 🌊 Available Flows

1. `job_scraper` - Scrapes job listings from StepStone
   - Runs daily at midnight
   - Collects data for multiple job titles
   - Saves raw data to bronze layer

2. `data_processor` - Processes and transforms job data
   - Runs daily at 1 AM
   - Transforms raw data into structured format
   - Runs dbt models for analytics

## 🚀 Running Flows

```bash
# Start the platform (note: Kestra takes 60-90 seconds to fully initialize)
cd /Users/tillmeineke/ML/jobAnalyticsPlatform/01_local
docker compose down
docker compose up -d

# Wait at least 60-90 seconds for Kestra to fully initialize before importing flows
sleep 90

# Import flows into Kestra
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/job_scraper_flow.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/data_processing_flow.yaml
```

> ⚠️ **Important**: The Kestra container takes more than 60 seconds to fully initialize. If you try to import flows too early, you may get connection errors or flows may not appear in the UI. Wait at least 1-2 minutes after starting the container before importing flows.

## 🔧 Troubleshooting

### Kestra Issues:

1. **Flows not appearing in UI after import:**
   - Check if Kestra is running: `docker ps`
   - Ensure you're using the correct Python task type: `io.kestra.core.tasks.scripts.Python` 
   - Restart Kestra to apply changes:
   ```bash
   cd /Users/tillmeineke/ML/jobAnalyticsPlatform/01_local
   docker compose down
   docker compose up -d
   ```
   - Wait 60-90 seconds before importing flows

2. **Connection errors:**
   - Check Kestra logs: `docker logs job-analytics-kestra`
   - Ensure PostgreSQL is running and healthy

### Metabase Issues:

1. **If Metabase shows encryption warnings:**
   - Make sure `MB_ENCRYPTION_SECRET_KEY` is set in docker-compose.yml
   - Restart Metabase: `docker restart job-analytics-metabase`

2. **If Metabase shows Java version warnings:**
   - These can be safely ignored - Metabase is showing the full version including build info
   - Metabase is using Java 21, which is correct

## 📝 Flow Development Guidelines

1. **Use proper task types:**
   - For Python scripts: `io.kestra.core.tasks.scripts.Python`
   - For Shell commands: `io.kestra.plugin.scripts.shell.Commands`
   - For Log messages: `io.kestra.core.tasks.log.Log`

2. **Python requirements:**
   - Always include `kestra` in requirements to use the Kestra outputs API
   - Example usage:
   ```python
   from kestra import Kestra
   Kestra.outputs({'status': 'completed', 'count': 42})
   ```
