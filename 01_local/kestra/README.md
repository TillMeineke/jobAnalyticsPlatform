# 🔄 Kestra Orchestration

This directory contains configuration and instructions for [Kestra](https://kestra.io/), the workflow orchestration tool for the Job Analytics Platform.

## 🚀 Quickstart

```bash
cd 01_local
make run-local
# Access Kestra UI at http://localhost:8080
```

## 📄 Managing Flows

- Place your YAML flows in `01_local/flows/`.
- Import all flows via Makefile:

  ```bash
  cd 01_local
  make import-flows
  ```

- Or import individual flows via API:

  ```bash
  curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/your_flow.yml
  ```

## 🛠️ Troubleshooting

- If `make import-flows` fails, ensure:
  - Kestra is running and accessible at <http://localhost:8080>
  - There are valid `.yml` files in `01_local/flows/`
  - The API endpoint is correct
- For database issues, check the Postgres container logs.

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated flows
- [ ] Ensure all flows follow naming conventions
- [ ] Document any manual changes here

---

See the README.md in `flows/` for more on workflow YAMLs and in `src/` for code called by flows.
