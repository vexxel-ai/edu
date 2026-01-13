variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.micro" # ARM-based, $6.14/month
}

variable "volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 20
}

variable "ssh_key_name" {
  description = "Name of the SSH key pair for EC2 access"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "edu-vexxel"
}

variable "allowed_ssh_cidr" {
  description = "CIDR blocks allowed to SSH (your IP)"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Restrict this in production!
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
  sensitive   = true
}

variable "supabase_anon_key" {
  description = "Supabase anon key"
  type        = string
  sensitive   = true
}

variable "supabase_jwt_secret" {
  description = "Supabase JWT secret"
  type        = string
  sensitive   = true
}

variable "super_admin_email" {
  description = "Super admin email"
  type        = string
  default     = "admin@vexxel.ai"
}

variable "super_admin_password" {
  description = "Super admin password"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}
