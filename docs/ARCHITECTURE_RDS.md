# Architecture with RDS

Updated architecture using **RDS for staging/production** and **local PostgreSQL for development**.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   LOCAL DEVELOPMENT                          │
└─────────────────────────────────────────────────────────────┘

    Docker Compose
    ┌────────────────────────────────────┐
    │  PostgreSQL (container)            │
    │  ↕                                 │
    │  FastAPI App (container)           │
    └────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              STAGING / PRODUCTION (AWS)                      │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │   EC2 t4g.micro     │
    │   (FastAPI only)    │
    └──────────┬──────────┘
               │
               ↓
    ┌─────────────────────┐
    │   RDS PostgreSQL    │
    │   (Managed DB)      │
    │   - Auto backups    │
    │   - Multi-AZ (prod) │
    │   - Monitoring      │
    └─────────────────────┘

    ┌─────────────────────┐
    │   Supabase Auth     │
    │   (External)        │
    └─────────────────────┘

    ┌─────────────────────┐
    │   Frontend          │
    │   (TBD)             │
    └─────────────────────┘
```

## Cost Breakdown

### Local Development: $0/month
- PostgreSQL: Docker container (free)
- FastAPI: Docker container (free)

### Staging: ~$20/month
- EC2 t4g.micro: $6.14/month
- RDS db.t4g.micro (Single-AZ): $12.41/month
- Storage (20GB): $2.30/month
- Supabase: FREE
- **Total: ~$21/month**

### Production: ~$35/month
- EC2 t4g.micro: $6.14/month
- RDS db.t4g.micro (Multi-AZ): $24.82/month
- Storage (20GB): $4.60/month
- Supabase: FREE
- **Total: ~$36/month**

### Production (Scaled): ~$50/month
- EC2 t4g.small: $12.28/month
- RDS db.t4g.small (Multi-AZ): $49.64/month (or ~$25 single-AZ)
- Storage (50GB): $11.50/month
- **Total: ~$50-74/month**

## Benefits of RDS

### ✅ Automated Backups
- Daily automated backups
- Point-in-time recovery
- Configurable retention (7-35 days)
- No manual backup scripts needed

### ✅ High Availability
- Multi-AZ deployment for production
- Automatic failover
- Read replicas for scaling

### ✅ Managed Maintenance
- Automated OS and PostgreSQL patches
- Configurable maintenance windows
- No downtime for minor updates

### ✅ Monitoring
- CloudWatch integration
- Performance Insights
- Automated alerting

### ✅ Security
- Encryption at rest and in transit
- VPC isolation
- IAM database authentication
- Automated security updates

### ✅ Scalability
- Easy instance resizing
- Storage auto-scaling
- Read replicas

## Environment Comparison

| Feature | Local Dev | Staging | Production |
|---------|-----------|---------|------------|
| **Database** | Docker PostgreSQL | RDS Single-AZ | RDS Multi-AZ |
| **EC2** | None | t4g.micro | t4g.micro/small |
| **Backups** | None | 7 days | 30 days |
| **Multi-AZ** | N/A | No | Yes |
| **Monitoring** | Logs only | CloudWatch | Enhanced Monitoring |
| **Cost** | $0 | ~$21/mo | ~$36/mo |

## Terraform Configuration

### Staging Configuration

```hcl
# terraform/environments/staging/terraform.tfvars

environment    = "staging"
instance_type  = "t4g.micro"

# RDS Configuration
use_rds                   = true
db_instance_class         = "db.t4g.micro"
db_allocated_storage      = 20
db_backup_retention_days  = 7
db_password               = "staging-secure-password"
```

### Production Configuration

```hcl
# terraform/environments/prod/terraform.tfvars

environment    = "prod"
instance_type  = "t4g.micro"  # or t4g.small

# RDS Configuration
use_rds                   = true
db_instance_class         = "db.t4g.micro"  # or db.t4g.small
db_allocated_storage      = 20
db_max_allocated_storage  = 100
db_backup_retention_days  = 30
db_password               = "prod-very-secure-password"
```

## Deployment

### 1. Deploy Infrastructure

```bash
cd terraform

# Staging
terraform workspace select staging
terraform apply -var-file=terraform.tfvars.staging

# Production
terraform workspace select prod
terraform apply -var-file=terraform.tfvars.prod
```

### 2. Get Database Connection

```bash
# RDS endpoint
terraform output rds_endpoint

# Full connection URL (sensitive)
terraform output database_url
```

### 3. Update EC2 Environment

SSH to EC2 and update `.env`:
```env
DATABASE_URL=postgresql://eduadmin:password@rds-endpoint:5432/edu_vexxel
```

### 4. Run Database Setup

```bash
# On EC2
cd /opt/edu-vexxel
docker-compose run --rm app python migrations/initial_setup.py
```

## Frontend Hosting Options

You mentioned you're still deciding on frontend hosting. Here are the best options:

### Option 1: Vercel (Recommended for Next.js/React)
**Pros:**
- ✅ FREE for personal projects
- ✅ Automatic deployments from git
- ✅ Global CDN
- ✅ Built-in SSL
- ✅ Perfect for Next.js

**Cons:**
- ❌ Vendor lock-in
- ❌ Cold starts on free tier

**Cost:** FREE (hobby), $20/month (pro)

### Option 2: Cloudflare Pages (Best for Static Sites)
**Pros:**
- ✅ FREE unlimited
- ✅ Global CDN
- ✅ Built-in SSL
- ✅ R2 storage integration
- ✅ Fast performance

**Cons:**
- ❌ Limited build time
- ❌ No server-side rendering

**Cost:** FREE

### Option 3: AWS Amplify
**Pros:**
- ✅ Full AWS integration
- ✅ Same ecosystem as backend
- ✅ CDN included
- ✅ SSL included

**Cons:**
- ❌ More expensive ($5-15/month)
- ❌ Complex setup

**Cost:** ~$5-15/month

### Option 4: S3 + CloudFront (Most Control)
**Pros:**
- ✅ Full control
- ✅ Very cheap (~$1-5/month)
- ✅ Terraform manageable
- ✅ Global CDN

**Cons:**
- ❌ Manual setup
- ❌ No automatic deployments
- ❌ More configuration

**Cost:** ~$1-5/month

### Option 5: Same EC2 as API
**Pros:**
- ✅ No additional cost
- ✅ Simple deployment
- ✅ Same server

**Cons:**
- ❌ Not ideal for static assets
- ❌ No CDN benefits
- ❌ Single point of failure

**Cost:** $0 extra

### Recommendation

For your use case, I recommend:

1. **For MVP/Development**: **Vercel** (FREE, easy, fast)
2. **For Production**: **Cloudflare Pages** or **S3 + CloudFront**
   - Cloudflare: Easier, FREE, fast
   - S3 + CloudFront: More control, cheap, integrates with AWS

## Complete Stack Recommendation

```
Development:
- Backend: Docker (local)
- Database: PostgreSQL (Docker)
- Frontend: Vite dev server
Cost: $0/month

Staging:
- Backend: EC2 t4g.micro
- Database: RDS db.t4g.micro (Single-AZ)
- Frontend: Cloudflare Pages (or Vercel)
Cost: ~$21/month

Production:
- Backend: EC2 t4g.micro
- Database: RDS db.t4g.micro (Multi-AZ)
- Frontend: Cloudflare Pages + CDN
Cost: ~$36/month
```

## Migration from Old Architecture

If you've already deployed the old architecture (PostgreSQL on EC2):

### 1. Backup Current Data

```bash
# On old EC2
pg_dump -h localhost -U eduuser -d edu_vexxel > backup.sql
```

### 2. Deploy New Infrastructure

```bash
# Deploy with RDS
terraform apply -var-file=terraform.tfvars.prod
```

### 3. Restore to RDS

```bash
# From EC2 to RDS
psql -h <rds-endpoint> -U eduadmin -d edu_vexxel < backup.sql
```

### 4. Update Application

```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://eduadmin:password@<rds-endpoint>:5432/edu_vexxel

# Restart app
docker-compose restart
```

## Monitoring

### RDS Metrics (CloudWatch)
- CPU Utilization
- Database Connections
- Free Storage Space
- Read/Write IOPS
- Read/Write Latency

### Set Up Alerts

```bash
# Example: Alert when CPU > 80%
aws cloudwatch put-metric-alarm \
  --alarm-name rds-cpu-high \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --period 300 \
  --statistic Average \
  --threshold 80
```

## Summary

**Architecture:**
- ✅ Local: Docker PostgreSQL
- ✅ Staging/Prod: RDS PostgreSQL
- ✅ EC2: API only
- ✅ Frontend: Vercel/Cloudflare/S3

**Benefits:**
- ✅ No backup management
- ✅ High availability
- ✅ Automated maintenance
- ✅ Better monitoring
- ✅ Scalable

**Cost:**
- Local: $0
- Staging: ~$21/month
- Production: ~$36/month

**Next Steps:**
1. Choose frontend hosting
2. Deploy with RDS
3. Set up monitoring
4. Configure backups
5. Test failover (prod)
