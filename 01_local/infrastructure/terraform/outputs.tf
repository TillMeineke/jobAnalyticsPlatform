output "s3_bucket_name" {
  description = "Name of the S3 bucket for raw data"
  value       = aws_s3_bucket.raw_data.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for raw data"
  value       = aws_s3_bucket.raw_data.arn
}

output "athena_workgroup" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.job_analysis.name
}

output "athena_database" {
  description = "Name of the Athena database"
  value       = aws_athena_database.job_database.name
}

output "redshift_cluster_endpoint" {
  description = "Endpoint of the Redshift cluster"
  value       = aws_redshift_cluster.job_warehouse.endpoint
}

output "redshift_connection_string" {
  description = "JDBC connection string for the Redshift cluster"
  value       = "jdbc:redshift://${aws_redshift_cluster.job_warehouse.endpoint}/${aws_redshift_cluster.job_warehouse.database_name}"
}
