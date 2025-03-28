# S3 bucket for raw data
resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-${var.raw_data_bucket_name}-${var.environment}"

  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning for the bucket (optional but recommended)
resource "aws_s3_bucket_versioning" "raw_data_versioning" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket folder structure
resource "aws_s3_object" "raw_folder" {
  bucket = aws_s3_bucket.raw_data.id
  key    = "raw/"
  content_type = "application/x-directory"
}

resource "aws_s3_object" "stepstone_folder" {
  bucket = aws_s3_bucket.raw_data.id
  key    = "raw/stepstone/"
  content_type = "application/x-directory"
}

# Athena workgroup
resource "aws_athena_workgroup" "job_analysis" {
  name = "${var.project_name}-${var.environment}"

  configuration {
    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.raw_data.bucket}/athena-results/"
    }
  }
}

# Athena database
resource "aws_athena_database" "job_database" {
  name   = "${replace(var.project_name, "-", "_")}_${var.environment}"
  bucket = aws_s3_bucket.raw_data.bucket
}

# S3 buckets for data layers
resource "aws_s3_bucket" "bronze_layer" {
  bucket = "kestra-data-zoomcamp"
  tags = {
    Environment = var.environment
    Layer       = "bronze"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "silver_layer" {
  bucket = "${var.project_name}-silver-${var.environment}"
  tags = {
    Environment = var.environment
    Layer       = "silver"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "gold_layer" {
  bucket = "${var.project_name}-gold-${var.environment}"
  tags = {
    Environment = var.environment
    Layer       = "gold"
  }
  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning for all buckets
resource "aws_s3_bucket_versioning" "bronze_versioning" {
  bucket = aws_s3_bucket.bronze_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "silver_versioning" {
  bucket = aws_s3_bucket.silver_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "gold_versioning" {
  bucket = aws_s3_bucket.gold_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Setup for Athena
resource "aws_s3_object" "athena_results" {
  bucket       = aws_s3_bucket.bronze_layer.id
  key          = "athena-results/"
  content_type = "application/x-directory"
}

# Athena databases for each layer
resource "aws_athena_database" "bronze_database" {
  name   = "${replace(var.project_name, "-", "_")}_bronze_${var.environment}"
  bucket = aws_s3_bucket.bronze_layer.bucket
}

resource "aws_athena_database" "silver_database" {
  name   = "${replace(var.project_name, "-", "_")}_silver_${var.environment}"
  bucket = aws_s3_bucket.silver_layer.bucket
}

resource "aws_athena_database" "gold_database" {
  name   = "${replace(var.project_name, "-", "_")}_gold_${var.environment}"
  bucket = aws_s3_bucket.gold_layer.bucket
}

# EC2 instance for processing
resource "aws_security_group" "ec2_security_group" {
  name        = "${var.project_name}-ec2-sg-${var.environment}"
  description = "Security group for EC2 instance"

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # In production, restrict to your IP
  }

  # HTTP access for Kestra web UI
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # In production, restrict to your IP
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-ec2-sg-${var.environment}"
    Environment = var.environment
  }
}

# IAM role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Policy for S3 access
resource "aws_iam_policy" "s3_access" {
  name        = "${var.project_name}-s3-access-policy-${var.environment}"
  description = "Policy for EC2 to access S3 buckets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.bronze_layer.arn,
          "${aws_s3_bucket.bronze_layer.arn}/*",
          aws_s3_bucket.silver_layer.arn,
          "${aws_s3_bucket.silver_layer.arn}/*",
          aws_s3_bucket.gold_layer.arn,
          "${aws_s3_bucket.gold_layer.arn}/*"
        ]
      }
    ]
  })
}

# Policy for Athena access
resource "aws_iam_policy" "athena_access" {
  name        = "${var.project_name}-athena-access-policy-${var.environment}"
  description = "Policy for EC2 to access Athena"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup",
          "athena:BatchGetQueryExecution",
          "athena:GetDataCatalog",
          "athena:GetDatabase",
          "athena:GetTableMetadata",
          "athena:ListDatabases",
          "athena:ListDataCatalogs",
          "athena:ListTableMetadata"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach policies to role
resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_role_policy_attachment" "athena_access_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.athena_access.arn
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile-${var.environment}"
  role = aws_iam_role.ec2_role.name
}

# EC2 instance
resource "aws_instance" "processing_instance" {
  ami                    = var.ec2_ami_id
  instance_type          = var.ec2_instance_type
  key_name               = var.ec2_key_name
  vpc_security_group_ids = [aws_security_group.ec2_security_group.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name        = "${var.project_name}-ec2-${var.environment}"
    Environment = var.environment
  }

  user_data = <<-EOF
              #!/bin/bash
              # Update and install Docker
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker

              # Create directories for Kestra
              mkdir -p /opt/kestra/conf
              mkdir -p /opt/kestra/plugins
              mkdir -p /opt/kestra/data

              # Create docker-compose.yml for Kestra
              cat > /opt/kestra/docker-compose.yml <<EOL
              version: '3'
              services:
                kestra:
                  image: kestra/kestra:latest-full
                  restart: unless-stopped
                  ports:
                    - "8080:8080"
                  environment:
                    - KESTRA_CONFIGURATION=/app/kestra/conf/application.yml
                  volumes:
                    - ./conf:/app/kestra/conf
                    - ./plugins:/app/kestra/plugins
                    - ./data:/app/kestra/data
              EOL

              # Create Kestra configuration
              cat > /opt/kestra/conf/application.yml <<EOL
              kestra:
                repository:
                  type: filesystem
                  filesystem:
                    base-path: /app/kestra/data
                storage:
                  type: local
                  local:
                    base-path: /app/kestra/data
                queue:
                  type: in-memory
              EOL

              # Start Kestra
              cd /opt/kestra
              docker-compose up -d
              EOF
}
