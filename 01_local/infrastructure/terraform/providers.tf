terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure backend for state if needed
  # backend "s3" {
  #   bucket = "terraform-state-job-pipeline"
  #   key    = "terraform.tfstate"
  #   region = "eu-central-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Job-Market-Pipeline"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
