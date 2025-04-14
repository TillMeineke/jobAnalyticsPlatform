# ☁️ Cloud Deployment (AWS)

This directory contains all the necessary configurations to deploy the Job Analytics Platform to AWS using Terraform.

## 🏗️ Architecture

The cloud deployment uses the following AWS services:

- **S3**: For storing raw data (bronze layer)
- **AWS Glue**: For data cataloging and ETL workflows (silver layer)
- **Amazon RDS (PostgreSQL)**: For storing analytics-ready data (gold layer)
- **EC2**: For hosting Metabase dashboard
- **IAM**: For access management and permissions
- **CloudWatch**: For monitoring and logging

## 📂 Directory Structure

```
.
├── terraform/                  # Infrastructure as code
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Variable definitions
│   ├── outputs.tf              # Output definitions
│   ├── s3.tf                   # S3 bucket configurations
│   ├── rds.tf                  # RDS database configurations
│   ├── ec2.tf                  # EC2 instance configurations
│   ├── glue.tf                 # AWS Glue configurations
│   ├── iam.tf                  # IAM role configurations
│   └── README.md               # Terraform documentation
├── dlt_pipelines/              # Cloud-specific dlt configurations
│   └── README.md               # Cloud DLT documentation
└── dbt_project/                # Cloud-specific dbt configurations
    └── README.md               # Cloud DBT documentation
```

## 🚀 Deployment Instructions

### Prerequisites

- AWS CLI installed and configured
- Terraform installed (version 1.0+)
- Valid AWS credentials with appropriate permissions

### Setup Steps

1. **Configure AWS credentials**

   ```bash
   aws configure
   ```

2. **Initialize Terraform**

   ```bash
   cd 02_cloud/terraform
   terraform init
   ```

3. **Plan the deployment**

   ```bash
   terraform plan -out=tfplan
   ```

4. **Apply the configuration**

   ```bash
   terraform apply tfplan
   ```

5. **Access the deployed resources**
   After successful deployment, Terraform will output:
   - Metabase URL
   - Database connection details
   - S3 bucket names

## ⚙️ Configuration

### Environment Variables

Create a `terraform.tfvars` file with the following variables:

```hcl
aws_region     = "us-east-1"
environment    = "production"
db_username    = "admin"  # Change this
db_password    = "password123"  # Change this
```

### Scaling Configuration

Modify the `variables.tf` file to adjust instance sizes, database configurations, and other scaling parameters.

## 🧪 Validation

After deployment, validate the infrastructure:

```bash
# This will be implemented in the Makefile
make validate-cloud
```

## 🔄 Update Process

To update the cloud infrastructure:

1. Make changes to Terraform files
2. Run `terraform plan` to preview changes
3. Run `terraform apply` to apply changes

## 💰 Cost Management

The deployed resources will incur AWS charges. Use the following command to estimate costs:

```bash
# This will be implemented in the Makefile
make estimate-cost
```

To destroy all resources when they're no longer needed:

```bash
cd 02_cloud/terraform
terraform destroy
```

## 📚 Additional Documentation

- [Terraform Configuration Details](./terraform/README.md)
- [Cloud DLT Pipeline](./dlt_pipelines/README.md)
- [Cloud DBT Project](./dbt_project/README.md)
