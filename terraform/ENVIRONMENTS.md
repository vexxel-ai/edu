# Environment Management Quick Reference

## TL;DR: How to Differentiate Staging vs Prod

**Key Differences:**
1. **Resource Names**: Tagged with environment (e.g., `edu-vexxel-staging` vs `edu-vexxel-prod`)
2. **State Files**: Separate Terraform state for each environment
3. **Instance Size**: Dev uses t4g.nano, staging/prod use t4g.micro
4. **Supabase Project**: Separate project per environment
5. **Domain**: Different subdomains (staging.vexxel.ai vs edu.vexxel.ai)

## Quick Setup: Multiple Environments

### Using Terraform Workspaces (Recommended for Small Teams)

```bash
cd terraform

# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Deploy dev
terraform workspace select dev
terraform apply -var-file=terraform.tfvars.dev

# Deploy staging
terraform workspace select staging
terraform apply -var-file=terraform.tfvars.staging

# Deploy prod
terraform workspace select prod
terraform apply -var-file=terraform.tfvars.prod

# See current workspace
terraform workspace show

# List all workspaces
terraform workspace list
```

### File Structure

```
terraform/
├── main.tf
├── variables.tf
├── ec2.tf
├── security-groups.tf
├── user-data.sh
├── outputs.tf
├── terraform.tfvars.dev.example
├── terraform.tfvars.staging.example
├── terraform.tfvars.prod.example
├── terraform.tfvars.dev           # Your dev config
├── terraform.tfvars.staging       # Your staging config
└── terraform.tfvars.prod          # Your prod config
```

## Environment Comparison

| Feature | Dev | Staging | Production |
|---------|-----|---------|------------|
| Instance | t4g.nano | t4g.micro | t4g.micro |
| Cost/mo | $3 | $8 | $8 |
| SSH | Open (dev only) | Your IP | Your IP |
| SSL | Optional | Yes | Required |
| Domain | dev.vexxel.ai | staging.vexxel.ai | edu.vexxel.ai |
| Supabase | Dev project | Staging project | Prod project |
| Backups | No | 3 days | 7 days |
| Uptime | As needed | 24/7 | 24/7 |

## Identifying Resources in AWS Console

Resources are tagged with environment:

**EC2 Instances:**
- Name: `edu-vexxel-dev`
- Name: `edu-vexxel-staging`
- Name: `edu-vexxel-prod`

**Security Groups:**
- Name: `edu-vexxel-dev-sg`
- Name: `edu-vexxel-staging-sg`
- Name: `edu-vexxel-prod-sg`

**Tags on all resources:**
```
Environment: dev | staging | prod
Project: edu-vexxel
ManagedBy: Terraform
```

## Deployment Workflow

```bash
# 1. Create environment configs
cp terraform.tfvars.dev.example terraform.tfvars.dev
cp terraform.tfvars.staging.example terraform.tfvars.staging
cp terraform.tfvars.prod.example terraform.tfvars.prod

# Edit each file with environment-specific values

# 2. Deploy infrastructure for each environment
terraform workspace new dev && terraform workspace select dev
terraform apply -var-file=terraform.tfvars.dev

terraform workspace new staging && terraform workspace select staging
terraform apply -var-file=terraform.tfvars.staging

terraform workspace new prod && terraform workspace select prod
terraform apply -var-file=terraform.tfvars.prod

# 3. Get IPs for each environment
DEV_IP=$(terraform workspace select dev && terraform output -raw instance_public_ip)
STAGING_IP=$(terraform workspace select staging && terraform output -raw instance_public_ip)
PROD_IP=$(terraform workspace select prod && terraform output -raw instance_public_ip)

# 4. Deploy application to each
../scripts/deploy.sh $DEV_IP      # Update script to accept env param
../scripts/deploy.sh $STAGING_IP
../scripts/deploy.sh $PROD_IP
```

## Separate State Files

Each workspace gets its own state file:

**Local State:**
```
terraform.tfstate.d/
├── dev/
│   └── terraform.tfstate
├── staging/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

**S3 Backend (if configured):**
```
s3://edu-vexxel-terraform-state/
├── env:/dev/terraform.tfstate
├── env:/staging/terraform.tfstate
└── env:/prod/terraform.tfstate
```

## How to Check Current Environment

```bash
# Current workspace
terraform workspace show

# List all workspaces (* marks current)
terraform workspace list

# Show resources in current workspace
terraform state list

# Get outputs from specific workspace
terraform workspace select staging
terraform output instance_public_ip
```

## Cost Breakdown by Setup

**Single Environment (Current):**
- Prod only: **$8/month**

**Dev + Prod:**
- Dev (stopped 16h/day): $4/month
- Prod (24/7): $8/month
- **Total: $12/month**

**Dev + Staging + Prod:**
- Dev (stopped 16h/day): $4/month
- Staging (24/7): $8/month
- Prod (24/7): $8/month
- **Total: $20/month**

## Stop/Start Dev Environment

Save costs by stopping dev when not in use:

```bash
# Get instance ID
terraform workspace select dev
INSTANCE_ID=$(terraform output -raw instance_id)

# Stop instance (keeps data, still pay for storage ~$2/mo)
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Start instance when needed
aws ec2 start-instances --instance-ids $INSTANCE_ID

# Wait for it to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get new IP (Elastic IP stays the same if you set one up)
terraform output instance_public_ip
```

## Environment-Specific Configs

Each environment needs its own config files:

```bash
# Terraform configs
terraform/terraform.tfvars.dev
terraform/terraform.tfvars.staging
terraform/terraform.tfvars.prod

# Application configs
.env.dev
.env.staging
.env.prod

# Supabase projects
Dev: https://dev-xxxxx.supabase.co
Staging: https://staging-xxxxx.supabase.co
Prod: https://prod-xxxxx.supabase.co
```

## Quick Commands

```bash
# Deploy specific environment
terraform workspace select <env>
terraform apply -var-file=terraform.tfvars.<env>

# Destroy specific environment
terraform workspace select <env>
terraform destroy -var-file=terraform.tfvars.<env>

# Get outputs from specific environment
terraform workspace select <env>
terraform output

# View resources in specific environment
terraform workspace select <env>
terraform state list

# Switch between environments
terraform workspace select dev
terraform workspace select staging
terraform workspace select prod
```

## Promotion Workflow

Typical development flow:

```
1. Feature branch → Deploy to dev
2. Test in dev environment
3. Merge to staging branch → Deploy to staging
4. QA testing in staging
5. Merge to main → Manual deploy to prod
```

```bash
# Update dev
git checkout feature-branch
terraform workspace select dev
terraform apply -var-file=terraform.tfvars.dev
../scripts/deploy.sh $DEV_IP

# Update staging after testing
git checkout staging
terraform workspace select staging
../scripts/deploy.sh $STAGING_IP

# Update prod after approval
git checkout main
terraform workspace select prod
../scripts/deploy.sh $PROD_IP
```

## Troubleshooting

**Wrong environment deployed?**
```bash
# Check current workspace
terraform workspace show

# Switch to correct one
terraform workspace select prod
```

**Can't find resources?**
```bash
# Make sure you're in the right workspace
terraform workspace list

# Resources only visible in their workspace
terraform workspace select staging
terraform state list
```

**Need to destroy one environment?**
```bash
# Safe - only destroys resources in current workspace
terraform workspace select dev
terraform destroy -var-file=terraform.tfvars.dev

# Other environments unaffected
terraform workspace select prod
terraform state list  # Still shows prod resources
```

## Best Practice Checklist

- [ ] Use separate Supabase projects per environment
- [ ] Use different SSH keys per environment
- [ ] Tag all resources with environment name
- [ ] Use workspaces or separate directories
- [ ] Document which environment is which
- [ ] Restrict SSH access in staging/prod
- [ ] Use SSL in staging/prod
- [ ] Stop dev environment when not in use
- [ ] Test changes in dev before staging
- [ ] Never deploy directly to prod without staging test

## See Also

- `MULTI_ENVIRONMENT.md` - Detailed multi-environment guide
- `README.md` - Terraform basics
- `../DEPLOYMENT.md` - Deployment guide
