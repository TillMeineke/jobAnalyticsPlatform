# 🏠 Local Development Environment

This directory contains all components needed for local development and testing of the Job Analytics Platform.

## 📂 Directory Structure

- `src/` - Source code for data collection and processing
- `data/` - Medallion architecture data (🥉 Bronze, 🥈 Silver, 🥇 Gold)
- `dbt/` - dbt transformation models
- `kestra/` - Kestra orchestration config
- `metabase/` - Metabase dashboard config
- `flows/` - Kestra workflow YAMLs
- `tests/` - Python tests

## 🚀 Quickstart

```bash
cd 01_local
make setup-local
make run-local
```

- Access Kestra: <http://localhost:8080>
- Access Metabase: <http://localhost:3000>

## 🧪 Testing

```bash
cd 01_local
make test-local
```

## 🛠️ Troubleshooting

- If you see `make import-flows` errors, ensure you have YAML files in `01_local/flows` and Kestra is running.
- For database connection issues, check Postgres logs and ensure the container is healthy.
- For port conflicts, stop other services using 5432, 3000, or 8080.

## 🧹 Codebase Consolidation Checklist

- [ ] Review `data/` and `src/` for duplicate scripts or data
- [ ] Move reusable code to `src/` and update imports
- [ ] Remove/archive old or duplicate files
- [ ] Update this README and subfolder READMEs after changes

---

For more details, see the README.md in each subfolder.
