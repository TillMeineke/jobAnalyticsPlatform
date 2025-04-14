variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1" # Frankfurt region, change as needed
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "job-market-pipeline"
}

# S3 Variables
variable "raw_data_bucket_name" {
  description = "Name of the S3 bucket for raw data"
  type        = string
  default     = "stepstone-raw-data"
}

# EC2 Variables
variable "ec2_ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
  default     = "ami-04e601abe3e1a910f" # Ubuntu 22.04 LTS in eu-central-1
}

variable "ec2_instance_type" {
  description = "Instance type for the EC2 instance"
  type        = string
  default     = "t3.medium" # 2 vCPU, 4 GiB RAM
}

variable "ec2_key_name" {
  description = "Key pair name for SSH access to the EC2 instance"
  type        = string
  # No default, must be specified in terraform.tfvars or via command line
}

# Example of other variables
variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
}
