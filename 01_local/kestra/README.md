# Kestra Orchestration 🚀

This directory contains the configuration files for [Kestra](https://kestra.io/), which orchestrates our data pipelines.

## Overview

Kestra is used to orchestrate the following workflows:

1. **Job Scraping Flow** - Automates the job data collection and processing pipeline:
   - Runs the StepstoneScraper to collect job listings
   - Processes the collected data with DLT
   - Scheduled to run daily at midnight

2. **Data Quality Flow** - Monitors the quality of the job data:
   - Checks the completeness and validity of job data
   - Triggers alerts if data quality falls below thresholds
   - Runs daily at noon and after each successful job scraping run

## Configuration

The `configuration.yml` file contains the Kestra server configuration:

- Uses PostgreSQL for state management
- Uses ElasticSearch for flow execution storage
- Exposes the UI on port 8080

## Usage

### Accessing the UI

Once the containers are running, you can access the Kestra UI at:

```
http://localhost:8080
```

### Managing Workflows

Workflows are defined in YAML files located in the `/flows` directory. To deploy a new workflow:

1. Create a new YAML file in `/flows` following Kestra's flow syntax
2. Use the Kestra UI to upload the flow or restart the containers

### Monitoring Executions

The Kestra UI provides a dashboard to monitor:

- Workflow executions
- Task statuses
- Logs and error messages

## Troubleshooting

Common issues:

1. **Container startup failures**: Check the logs using `docker-compose logs kestra-server`
2. **Missing dependencies**: Ensure Python modules are installed in the Docker image
3. **Path issues**: Ensure paths in flow files match the Docker container paths
