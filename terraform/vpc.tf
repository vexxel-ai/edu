# VPC and networking configuration
# Uses default VPC for simplicity and cost savings

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Locals for VPC configuration
locals {
  vpc_id        = var.vpc_id != null ? var.vpc_id : data.aws_vpc.default.id
  db_subnet_ids = length(var.db_subnet_ids) > 0 ? var.db_subnet_ids : data.aws_subnets.default.ids
}
