# Additional variables for RDS configuration

variable "vpc_id" {
  description = "VPC ID for RDS deployment (use default VPC for simplicity)"
  type        = string
  default     = null # Will use default VPC if not specified
}

variable "db_subnet_ids" {
  description = "List of subnet IDs for RDS (must be in different AZs)"
  type        = list(string)
  default     = [] # Will use default VPC subnets if empty
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro" # ARM-based, cheapest option
}

variable "db_allocated_storage" {
  description = "Initial storage size in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage size for autoscaling in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "edu_vexxel"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "eduadmin"
}

variable "db_backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "use_rds" {
  description = "Whether to create RDS instance (false for local dev)"
  type        = bool
  default     = true
}
