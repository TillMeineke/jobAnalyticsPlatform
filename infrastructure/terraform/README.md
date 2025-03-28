# Terraform Infrastructure

This directory contains the Terraform configuration for setting up the infrastructure for the job market data pipeline.

## Resources Created

- S3 bucket for raw data storage
- Athena workgroup and database for querying raw data
- Redshift cluster for data warehousing
- IAM roles and security groups

## Usage

### Prerequisites

- Terraform installed (v1.0.0+)
- AWS CLI installed and configured
- AWS credentials set up

### Deployment Steps

1. Initialize Terraform:

```bash
terraform init
```

2. Create a terraform.tfvars file (not tracked in git) with sensitive values:

```
redshift_master_password = "YourStrongPassword123!"
```

3. Preview the changes:

```bash
terraform plan
```

4. Apply the changes:

```bash
terraform apply
```

5. To destroy the infrastructure:

```bash
terraform destroy
```

### Environment Variables

You can also provide variables using environment variables:

```bash
export TF_VAR_redshift_master_password="YourStrongPassword123!"
terraform apply
```

## Modifying the Configuration

- Update variable values in `variables.tf` or by providing a `.tfvars` file
- For production deployment, update security settings and resource sizing
