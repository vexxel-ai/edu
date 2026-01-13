# RDS PostgreSQL Database for staging/production
# Local development uses Docker PostgreSQL

resource "aws_db_subnet_group" "app" {
  count      = var.use_rds ? 1 : 0
  name       = "${var.project_name}-${var.environment}-db-subnet"
  subnet_ids = local.db_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet"
  }
}

resource "aws_security_group" "rds" {
  count       = var.use_rds ? 1 : 0
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = local.vpc_id

  # Allow PostgreSQL from EC2 security group
  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  # No outbound restrictions
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

resource "aws_db_instance" "postgres" {
  count      = var.use_rds ? 1 : 0
  identifier = "${var.project_name}-${var.environment}"

  # Engine
  engine         = "postgres"
  engine_version = "15.4"

  # Instance
  instance_class        = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # Database
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.app[0].name
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  publicly_accessible    = false

  # Backups
  backup_retention_period = var.db_backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # High Availability (for production)
  multi_az = var.environment == "prod" ? true : false

  # Performance Insights
  performance_insights_enabled = var.environment == "prod" ? true : false

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = var.environment == "prod" ? 60 : 0
  monitoring_role_arn             = var.environment == "prod" ? aws_iam_role.rds_monitoring[0].arn : null

  # Deletion protection
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "prod" ? false : true
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Auto minor version upgrades
  auto_minor_version_upgrade = true

  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }
}

# IAM role for RDS enhanced monitoring (production only)
resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-monitoring"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.environment == "prod" ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
