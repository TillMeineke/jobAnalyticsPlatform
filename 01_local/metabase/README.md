# 📊 Metabase Dashboards

This directory contains Metabase dashboard configurations for visualizing job market analytics.

## 🚀 Quickstart

- Metabase runs at <http://localhost:3000> when started via Docker Compose.
- Default database connection: Postgres (`jobanalytics`/`jobanalytics`)

## 🔧 Setup Instructions

### Local Setup

```bash
cd 01_local
make run-local
# Access Metabase at http://localhost:3000
```

### Automating Setup

- Use the [Metabase API](https://www.metabase.com/docs/latest/api-documentation.html) to automate database connections, users, and dashboard imports.
- Example: Add a database via API

  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Job Analytics Postgres",
      "engine": "postgres",
      "details": {
        "host": "postgres",
        "port": 5432,
        "dbname": "jobanalytics",
        "user": "jobanalytics",
        "password": "jobanalytics"
      }
    }' \
    http://localhost:3000/api/database
  ```

## 🛠️ Troubleshooting

- If Metabase is stuck on "initializing", check Postgres container logs and ensure the database is ready.
- For port conflicts, stop other services using 3000.

## 🧹 Codebase Consolidation Checklist

- [ ] Remove outdated dashboard configs
- [ ] Ensure all dashboards are documented
- [ ] Add/Update automation scripts as needed

---

See the README.md in `dbt/` for details on the data models powering these dashboards.
