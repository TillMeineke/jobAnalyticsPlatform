# ☁️ Cloud Deployment (AWS)

This directory contains all configurations to deploy the Job Analytics Platform to AWS using Terraform and related tools.

## 📂 Directory Structure

- `terraform/` - Infrastructure as code (main.tf, variables.tf, etc.)
- `dlt_pipelines/` - Cloud-specific dlt configs
- `dbt_project/` - Cloud-specific dbt configs
- `tests/` - Cloud environment tests

## 🚀 Deployment Instructions

### Prerequisites

- AWS CLI installed and configured
- Terraform installed (v1.0+)
- Valid AWS credentials

### Setup Steps

```bash
cd 02_cloud/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

- After deployment, Terraform will output:
  - Metabase URL
  - Database connection details
  - S3 bucket names

## 🧪 Validation

```bash
cd 02_cloud
make validate-cloud
```

## 🛠️ Troubleshooting

- For AWS permission errors, check IAM roles and credentials.
- For resource conflicts, destroy old resources:

  ```bash
  cd 02_cloud/terraform
  terraform destroy
  ```

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated Terraform modules/configs
- [ ] Ensure all cloud configs are documented
- [ ] Add/Update automation scripts as needed

---

See the README.md in each subfolder for more details on pipelines, dbt, and tests.
