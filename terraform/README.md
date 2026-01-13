# Terraform Infrastructure for edu.vexxel.ai

This directory contains Terraform configuration for deploying the edu.vexxel.ai platform to AWS.

## Architecture

- **Compute**: EC2 t4g.micro (ARM Graviton) - $6.14/month
- **Storage**: 20GB EBS gp3 - $2.00/month
- **Database**: PostgreSQL 15 on Docker (same EC2)
- **Auth**: Supabase (external, free tier)
- **Networking**: Elastic IP, Security Group

**Total Cost: ~$8/month**

## Prerequisites

1. AWS CLI configured with credentials
2. Terraform >= 1.5 installed
3. SSH key pair created in AWS EC2 Console
4. Supabase project created

## Quick Start

```bash
# 1. Copy example variables
cp terraform.tfvars.example terraform.tfvars

# 2. Edit with your values
nano terraform.tfvars

# 3. Initialize Terraform
terraform init

# 4. Review plan
terraform plan

# 5. Deploy
terraform apply
```

## Configuration

### Required Variables (terraform.tfvars)

```hcl
# AWS Configuration
aws_region     = "us-east-1"
environment    = "prod"
instance_type  = "t4g.micro"
ssh_key_name   = "your-ssh-key-name"

# Security - Restrict SSH to your IP!
allowed_ssh_cidr = ["YOUR_IP/32"]

# Supabase
supabase_url        = "https://xxxxx.supabase.co"
supabase_anon_key   = "your-anon-key"
supabase_jwt_secret = "your-jwt-secret"

# Admin
super_admin_email    = "admin@vexxel.ai"
super_admin_password = "secure-password"

# Database
db_password = "secure-db-password"
```

## Files

- `main.tf` - Provider configuration, data sources
- `variables.tf` - Input variable definitions
- `ec2.tf` - EC2 instance and Elastic IP
- `security-groups.tf` - Firewall rules
- `user-data.sh` - Bootstrap script (installs Docker)
- `outputs.tf` - Output values (IP, SSH command)
- `terraform.tfvars` - Your configuration (NOT in git)

## Outputs

After `terraform apply`, you'll get:

```bash
instance_id          = "i-xxxxx"
instance_public_ip   = "54.123.45.67"
instance_public_dns  = "ec2-54-123-45-67.compute-1.amazonaws.com"
ssh_command          = "ssh -i ~/.ssh/your-key.pem ubuntu@54.123.45.67"
security_group_id    = "sg-xxxxx"
```

## Security Best Practices

### 1. Restrict SSH Access

Update `allowed_ssh_cidr` to your IP only:
```hcl
allowed_ssh_cidr = ["203.0.113.10/32"]  # Your public IP
```

Find your IP:
```bash
curl ifconfig.me
```

### 2. Use IAM Roles (Advanced)

Instead of IAM user credentials, attach an IAM role to EC2 for AWS service access.

### 3. Enable Encryption

Root EBS volume is already encrypted in the configuration.

### 4. Secrets Management

- Never commit `terraform.tfvars` to git (already in .gitignore)
- For production, use AWS Secrets Manager or Parameter Store
- Rotate passwords regularly

## Multi-Environment Setup

To manage dev/staging/prod separately:

```bash
terraform/
├── environments/
│   ├── dev/
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── terraform.tfvars
│   └── prod/
│       └── terraform.tfvars
└── modules/  # shared configs
```

Deploy each:
```bash
cd environments/dev
terraform init
terraform apply

cd ../staging
terraform init
terraform apply
```

## Remote State (Recommended for Teams)

To store state in S3:

1. Create S3 bucket and DynamoDB table:
```bash
aws s3 mb s3://edu-vexxel-terraform-state
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

2. Uncomment backend in `main.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "edu-vexxel-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

3. Initialize:
```bash
terraform init -migrate-state
```

## Cost Optimization

### Stop Instance When Not in Use (Dev)

```bash
# Stop (you still pay for EBS)
aws ec2 stop-instances --instance-ids $(terraform output -raw instance_id)

# Start
aws ec2 start-instances --instance-ids $(terraform output -raw instance_id)
```

### Use Spot Instances (Advanced)

For dev/staging, use spot instances to save ~70%:
```hcl
# In ec2.tf
resource "aws_spot_instance_request" "app" {
  ami           = data.aws_ami.ubuntu_arm.id
  instance_type = var.instance_type
  spot_price    = "0.003"  # ~$2/month
  # ... rest of config
}
```

### Reserved Instances (Production)

For production with 1-year commitment, save ~30%.

## Troubleshooting

### Error: UnauthorizedOperation

AWS credentials not configured or lack permissions.
```bash
aws configure
aws sts get-caller-identity
```

### Error: InvalidKeyPair.NotFound

SSH key doesn't exist in AWS.
```bash
# List keys
aws ec2 describe-key-pairs

# Create key
aws ec2 create-key-pair --key-name edu-vexxel-key --query 'KeyMaterial' --output text > ~/.ssh/edu-vexxel-key.pem
chmod 400 ~/.ssh/edu-vexxel-key.pem
```

### Error: Instance failed status checks

View system log:
```bash
aws ec2 get-console-output --instance-id $(terraform output -raw instance_id)
```

### Cannot SSH to instance

1. Check security group allows your IP:
```bash
curl ifconfig.me  # Get your IP
```

2. Update `terraform.tfvars` with correct IP

3. Apply changes:
```bash
terraform apply
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
# Type 'yes' to confirm
```

⚠️ This will permanently delete:
- EC2 instance
- EBS volumes
- Elastic IP
- Security groups
- All data on the instance

## Next Steps

After infrastructure is deployed:

1. Deploy application: `../scripts/deploy.sh <EC2_IP>`
2. Set up SSL: `../scripts/setup-ssl.sh <DOMAIN> <EMAIL> <EC2_IP>`
3. Configure monitoring and backups

See `../DEPLOYMENT.md` for complete deployment guide.

## Support

For issues:
- Check AWS CloudWatch logs
- Review user-data script execution: `cat /var/log/cloud-init-output.log`
- Verify security groups and network connectivity
