# 🔄 Kestra Workflows

This directory contains the workflow definitions (YAML) for the Kestra orchestration platform.

## 📄 Workflow Files

- Place all Kestra flow YAMLs here (e.g., `job_scraper_flow.yml`).
- Each file should be named descriptively and follow naming conventions.

## 🚀 Usage

- Flows in this directory can be imported into Kestra via the UI or API.
- To import all flows at once:

  ```bash
  cd 01_local
  make import-flows
  ```

## 🛠️ Troubleshooting

- If flows do not appear in Kestra, check for YAML syntax errors and ensure the import command ran successfully.
- For API import errors, see the troubleshooting section in `kestra/README.md`.

## 🔗 Integration Points

These workflows connect with:

- **Job Scraper** (Python)
- **S3 Storage**
- **Data Quality Checks**
- **dbt Transformations**
- **Metabase** (final output)

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated flows
- [ ] Ensure all flows are documented and follow naming conventions

---

See the README.md in `kestra/` for orchestration setup and in `src/` for code called by flows.
