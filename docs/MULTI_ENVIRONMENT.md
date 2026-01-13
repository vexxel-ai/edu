# Multi-Environment Setup Guide

How to manage dev, staging, and production environments separately.

## Current Setup vs Multi-Environment

**Current Setup**: Single environment (production)
```
terraform/
├── main.tf
├── variables.tf
├── ec2.tf
└── terraform.tfvars  # Your production config
```

**Multi-Environment Setup**: Separate environments
```
terraform/
├── modules/                    # Shared infrastructure code
│   └── app-server/
│       ├── main.tf
│       ├── variables.tf
│       ├── ec2.tf
│       ├── security-groups.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf             # Uses module
│   │   ├── terraform.tfvars    # Dev-specific config
│   │   └── backend.tf          # Dev state file
│   ├── staging/
│   │   ├── main.tf             # Uses module
│   │   ├── terraform.tfvars    # Staging-specific config
│   │   └── backend.tf          # Staging state file
│   └── prod/
│       ├── main.tf             # Uses module
│       ├── terraform.tfvars    # Prod-specific config
│       └── backend.tf          # Prod state file
```

## Key Differences Between Environments

| Aspect | Dev | Staging | Production |
|--------|-----|---------|------------|
| **Instance Type** | t4g.nano | t4g.micro | t4g.micro → t4g.small |
| **Monthly Cost** | $3 | $6 | $6-12 |
| **Running Hours** | On-demand (stop when not in use) | 24/7 | 24/7 |
| **Domain** | dev.vexxel.ai | staging.vexxel.ai | edu.vexxel.ai |
| **SSL** | Optional | Yes | Yes (required) |
| **Backups** | No | Daily (3 days) | Daily (7 days) |
| **DB Password** | Simple | Moderate | Strong |
| **SSH Access** | Your IP | Your IP + Team | Bastion host only |
| **Monitoring** | Basic logs | CloudWatch | CloudWatch + Alerts |
| **Data** | Fake/seed data | Production-like | Real data |
| **Purpose** | Feature development | Pre-production testing | Live users |

## Option 1: Quick Multi-Environment (Same Structure)

Keep current structure but use different `terraform.tfvars` files:

```bash
terraform/
├── main.tf
├── variables.tf
├── ec2.tf
├── security-groups.tf
├── outputs.tf
├── terraform.tfvars.dev
├── terraform.tfvars.staging
└── terraform.tfvars.prod
```

### Deploy Different Environments

```bash
# Development
terraform apply -var-file=terraform.tfvars.dev

# Staging
terraform apply -var-file=terraform.tfvars.staging

# Production
terraform apply -var-file=terraform.tfvars.prod
```

### Example terraform.tfvars.dev

```hcl
aws_region     = "us-east-1"
environment    = "dev"
instance_type  = "t4g.nano"  # Smaller/cheaper
volume_size    = 10           # Less storage
ssh_key_name   = "edu-vexxel-dev-key"

allowed_ssh_cidr = ["0.0.0.0/0"]  # More relaxed for dev

supabase_url        = "https://dev-xxxxx.supabase.co"
supabase_anon_key   = "dev-anon-key"
supabase_jwt_secret = "dev-jwt-secret"

super_admin_email    = "admin@vexxel.ai"
super_admin_password = "dev-password"

db_password = "dev-db-password"
```

### Example terraform.tfvars.staging

```hcl
aws_region     = "us-east-1"
environment    = "staging"
instance_type  = "t4g.micro"  # Same as prod
volume_size    = 20
ssh_key_name   = "edu-vexxel-staging-key"

allowed_ssh_cidr = ["YOUR_IP/32"]  # Restricted

supabase_url        = "https://staging-xxxxx.supabase.co"
supabase_anon_key   = "staging-anon-key"
supabase_jwt_secret = "staging-jwt-secret"

super_admin_email    = "admin@vexxel.ai"
super_admin_password = "staging-password"

db_password = "staging-db-password"
```

### Example terraform.tfvars.prod

```hcl
aws_region     = "us-east-1"
environment    = "prod"
instance_type  = "t4g.micro"  # Or t4g.small for more power
volume_size    = 20
ssh_key_name   = "edu-vexxel-prod-key"

allowed_ssh_cidr = ["YOUR_IP/32"]  # Very restricted

supabase_url        = "https://prod-xxxxx.supabase.co"
supabase_anon_key   = "prod-anon-key"
supabase_jwt_secret = "prod-jwt-secret"

super_admin_email    = "admin@vexxel.ai"
super_admin_password = "VERY_SECURE_PASSWORD"

db_password = "VERY_SECURE_DB_PASSWORD"
```

## Option 2: Separate Workspaces (Recommended)

Terraform workspaces keep separate state for each environment:

```bash
cd terraform

# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch between workspaces
terraform workspace select dev
terraform apply -var-file=terraform.tfvars.dev

terraform workspace select staging
terraform apply -var-file=terraform.tfvars.staging

terraform workspace select prod
terraform apply -var-file=terraform.tfvars.prod

# List workspaces
terraform workspace list
```

Benefits:
- ✅ Separate state files automatically
- ✅ Can't accidentally affect wrong environment
- ✅ Simple to switch between environments

## Option 3: Separate Directories (Best for Teams)

Most production-ready approach:

### Step 1: Reorganize Structure

```bash
cd terraform

# Create modules directory
mkdir -p modules/app-server

# Move main infrastructure to module
mv main.tf modules/app-server/
mv ec2.tf modules/app-server/
mv security-groups.tf modules/app-server/
mv user-data.sh modules/app-server/
mv outputs.tf modules/app-server/
mv variables.tf modules/app-server/

# Create environment directories
mkdir -p environments/{dev,staging,prod}
```

### Step 2: Create Module (modules/app-server/main.tf)

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Rest of your infrastructure code
# (ec2.tf, security-groups.tf content goes here)
```

### Step 3: Create Environment Configs

**environments/dev/main.tf**
```hcl
terraform {
  required_version = ">= 1.5"
  backend "s3" {
    bucket = "edu-vexxel-terraform-state"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = "dev"
      ManagedBy   = "Terraform"
      Project     = "edu-vexxel"
    }
  }
}

module "app_server" {
  source = "../../modules/app-server"

  environment          = "dev"
  instance_type        = "t4g.nano"
  volume_size          = 10
  ssh_key_name         = var.ssh_key_name
  allowed_ssh_cidr     = var.allowed_ssh_cidr

  supabase_url         = var.supabase_url
  supabase_anon_key    = var.supabase_anon_key
  supabase_jwt_secret  = var.supabase_jwt_secret

  super_admin_email    = var.super_admin_email
  super_admin_password = var.super_admin_password
  db_password          = var.db_password
}

output "instance_public_ip" {
  value = module.app_server.instance_public_ip
}
```

**environments/staging/main.tf**
```hcl
# Same structure, but:
backend "s3" {
  key = "staging/terraform.tfstate"
}
default_tags {
  Environment = "staging"
}
module "app_server" {
  environment   = "staging"
  instance_type = "t4g.micro"
  volume_size   = 20
  # ... staging values
}
```

**environments/prod/main.tf**
```hcl
# Same structure, but:
backend "s3" {
  key = "prod/terraform.tfstate"
}
default_tags {
  Environment = "prod"
}
module "app_server" {
  environment   = "prod"
  instance_type = "t4g.micro"  # or t4g.small
  volume_size   = 20
  # ... prod values
}
```

### Step 4: Deploy Each Environment

```bash
# Development
cd environments/dev
terraform init
terraform apply

# Staging
cd ../staging
terraform init
terraform apply

# Production
cd ../prod
terraform init
terraform apply
```

## How Resources Are Differentiated

### 1. Resource Naming

All resources are tagged with environment:

```hcl
# In your Terraform
resource "aws_instance" "app" {
  tags = {
    Name        = "${var.project_name}-${var.environment}"  # edu-vexxel-dev
    Environment = var.environment                            # dev
  }
}
```

Results in:
- Dev: `edu-vexxel-dev`
- Staging: `edu-vexxel-staging`
- Prod: `edu-vexxel-prod`

### 2. Separate State Files

Each environment has its own state:
```
s3://edu-vexxel-terraform-state/
├── dev/terraform.tfstate
├── staging/terraform.tfstate
└── prod/terraform.tfstate
```

### 3. Different Security Groups

```hcl
resource "aws_security_group" "app_sg" {
  name = "${var.project_name}-${var.environment}-sg"
  # dev: edu-vexxel-dev-sg
  # staging: edu-vexxel-staging-sg
  # prod: edu-vexxel-prod-sg
}
```

### 4. Separate Supabase Projects

- Dev: `https://dev-xxxxx.supabase.co`
- Staging: `https://staging-xxxxx.supabase.co`
- Prod: `https://prod-xxxxx.supabase.co`

### 5. Different Domains (with SSL)

- Dev: `dev.vexxel.ai`
- Staging: `staging.vexxel.ai`
- Prod: `edu.vexxel.ai`

## AWS Console View

When you log into AWS Console, you'll see resources tagged:

**EC2 Instances**:
```
Name                    Instance Type   State     Environment
edu-vexxel-dev         t4g.nano        stopped   dev
edu-vexxel-staging     t4g.micro       running   staging
edu-vexxel-prod        t4g.micro       running   prod
```

**Security Groups**:
```
Name                    Ports
edu-vexxel-dev-sg      22, 80, 443
edu-vexxel-staging-sg  22, 80, 443
edu-vexxel-prod-sg     22, 80, 443
```

## Environment Configuration Files

Each environment needs separate config files:

```bash
# .env files for each environment
.env.dev
.env.staging
.env.prod

# Terraform configs
terraform/environments/dev/terraform.tfvars
terraform/environments/staging/terraform.tfvars
terraform/environments/prod/terraform.tfvars
```

## Deployment Scripts for Each Environment

Update deployment scripts to handle environments:

**scripts/deploy.sh** (updated)
```bash
#!/bin/bash
set -e

ENVIRONMENT=$1
EC2_IP=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$EC2_IP" ]; then
  echo "Usage: ./scripts/deploy.sh <environment> <ec2_ip>"
  echo "Example: ./scripts/deploy.sh dev 54.123.45.67"
  exit 1
fi

if [ ! -f ".env.$ENVIRONMENT" ]; then
  echo "Error: .env.$ENVIRONMENT not found!"
  exit 1
fi

echo "Deploying $ENVIRONMENT environment to $EC2_IP..."

# Copy environment-specific .env
scp ".env.$ENVIRONMENT" ubuntu@$EC2_IP:/opt/edu-vexxel/.env

# Rest of deployment...
```

Usage:
```bash
# Deploy dev
./scripts/deploy.sh dev $DEV_IP

# Deploy staging
./scripts/deploy.sh staging $STAGING_IP

# Deploy prod
./scripts/deploy.sh prod $PROD_IP
```

## Cost Management

### Stop Dev Environment When Not in Use

```bash
# Stop dev instance (still pay for storage ~$2/mo)
aws ec2 stop-instances --instance-ids $(terraform output -raw instance_id)

# Start when needed
aws ec2 start-instances --instance-ids $(terraform output -raw instance_id)
```

### Monthly Costs by Setup

**Single Environment (Current)**
- Production only: ~$8/month

**Dev + Prod**
- Dev (t4g.nano, stopped 16h/day): ~$4/month
- Prod (t4g.micro, 24/7): ~$8/month
- **Total**: ~$12/month

**Dev + Staging + Prod**
- Dev (t4g.nano, stopped 16h/day): ~$4/month
- Staging (t4g.micro, 24/7): ~$8/month
- Prod (t4g.micro, 24/7): ~$8/month
- **Total**: ~$20/month

## Best Practices

### 1. Use Workspaces for Small Teams
- ✅ Simple to set up
- ✅ Single codebase
- ✅ Good for 1-3 developers

### 2. Use Separate Directories for Large Teams
- ✅ Complete isolation
- ✅ Different approval workflows
- ✅ Team-specific access control
- ✅ Good for 5+ developers

### 3. Promotion Workflow

```
Dev → Staging → Production

1. Develop feature in dev
2. Test locally
3. Deploy to dev for testing
4. Merge to staging branch → auto-deploy to staging
5. QA testing on staging
6. Manual promotion to prod
```

### 4. Infrastructure Drift Prevention

```bash
# Regular check for drift
terraform plan -var-file=terraform.tfvars.prod

# If drift detected, review changes and apply
terraform apply -var-file=terraform.tfvars.prod
```

## Recommended Setup for You

Given your requirements (cost-effective, starting out), I recommend:

**Phase 1: Single Environment (Now)**
```
prod only → $8/month
```

**Phase 2: Add Dev (When actively developing)**
```
dev + prod → $12/month
Use workspaces or -var-file
```

**Phase 3: Add Staging (When you have users)**
```
dev + staging + prod → $20/month
Use separate directories
```

## Quick Start: Add Dev Environment Now

```bash
cd terraform

# Create dev config
cp terraform.tfvars.example terraform.tfvars.dev

# Edit for dev settings
nano terraform.tfvars.dev
# - Change environment = "dev"
# - Use t4g.nano
# - Use dev Supabase project

# Deploy dev
terraform workspace new dev
terraform workspace select dev
terraform apply -var-file=terraform.tfvars.dev

# Get dev IP
DEV_IP=$(terraform output -raw instance_public_ip)

# Create dev .env
cp .env.prod.example .env.dev
# Edit with dev settings

# Deploy app to dev
./scripts/deploy.sh dev $DEV_IP
```

## Summary

**Current Setup**: Single environment, production-focused

**To Differentiate Environments**:
1. Use `environment` variable in Terraform
2. Separate `.tfvars` files per environment
3. Use workspaces or separate directories
4. Tag all resources with environment name
5. Use different Supabase projects
6. Use different domain names

**Simplest Approach**: Use Terraform workspaces + separate `.tfvars` files

**Most Robust Approach**: Separate directories with modules

Choose based on your team size and complexity needs!
