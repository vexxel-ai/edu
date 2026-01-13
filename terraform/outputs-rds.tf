# Additional outputs for RDS

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = var.use_rds ? aws_db_instance.postgres[0].endpoint : null
}

output "rds_address" {
  description = "RDS instance address (hostname)"
  value       = var.use_rds ? aws_db_instance.postgres[0].address : null
}

output "rds_port" {
  description = "RDS instance port"
  value       = var.use_rds ? aws_db_instance.postgres[0].port : null
}

output "database_url" {
  description = "Full database connection URL"
  value       = var.use_rds ? "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres[0].endpoint}/${var.db_name}" : null
  sensitive   = true
}

output "connection_command" {
  description = "Command to connect to RDS from EC2"
  value       = var.use_rds ? "psql -h ${aws_db_instance.postgres[0].address} -U ${var.db_username} -d ${var.db_name}" : null
}
