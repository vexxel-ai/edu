# Deployment Guide for edu.vexxel.ai

Complete guide for deploying the multi-user learning platform to AWS EC2 with PostgreSQL and Supabase Auth.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              AWS EC2 t4g.micro                  │
│              (ARM Graviton)                      │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         Docker Compose                     │ │
│  │                                            │ │
│  │  ┌─────────┐  ┌──────┐  ┌────────────┐   │ │
│  │  │ Nginx   │→ │ App  │→ │ PostgreSQL │   │ │
│  │  │ (proxy) │  │(API) │  │ (data)     │   │ │
│  │  └─────────┘  └──────┘  └────────────┘   │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                     ↕
         ┌───────────────────────┐
         │   Supabase (Cloud)    │
         │   Authentication      │
         └───────────────────────┘
```

## Cost Breakdown

- **EC2 t4g.micro**: $6.14/month (ARM Graviton, 1 vCPU, 1GB RAM)
- **EBS Storage (20GB)**: $2.00/month
- **Supabase Auth**: FREE (up to 50K MAU)
- **Backups to S3** (optional): ~$0.10/month

**Total: ~$8/month**

## Prerequisites

1. **AWS Account** with IAM user credentials
2. **Supabase Account** (free tier at https://supabase.com)
3. **SSH Key Pair** (create in AWS EC2 Console)
4. **Domain Name** (optional, for SSL)
5. **Terraform** installed locally (`brew install terraform` on macOS)
6. **Local Development**: Python 3.10+, Docker, uv package manager

## Part 1: Local Development Setup

### 1.1 Initial Setup

```bash
# Clone repository
cd /path/to/edu

# Run local setup script
./scripts/local-setup.sh
```

The script will:
- Create `.env` from `.env.dev.example`
- Install `uv` package manager
- Install Python dependencies
- Optionally start PostgreSQL with Docker
- Run database migration

### 1.2 Manual Setup (Alternative)

```bash
# Install dependencies
uv sync

# Create environment file
cp .env.dev.example .env

# Edit .env with your Supabase credentials
# Get these from: https://app.supabase.com/project/_/settings/api
nano .env
```

Update `.env`:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPER_ADMIN_EMAIL=admin@vexxel.ai
SUPER_ADMIN_PASSWORD=change-me-now
```

### 1.3 Start Local Development Server

**Option A: SQLite (simplest)**
```bash
# DATABASE_URL in .env should be: sqlite:///./database.db
uvicorn app.main:app --reload --port 8000
```

**Option B: PostgreSQL with Docker**
```bash
# Start PostgreSQL
docker-compose -f docker-compose.dev.yml up -d postgres

# Update .env
# DATABASE_URL=postgresql://eduuser:devpassword@localhost:5432/edu_vexxel_dev

# Start app
uvicorn app.main:app --reload --port 8000
```

### 1.4 Run Migration

```bash
python migrations/migrate_to_multiuser.py
# Type 'RESET' when prompted
```

### 1.5 Verify Setup

Visit http://localhost:8000/docs and test:

```bash
# Sign in as admin
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@vexxel.ai", "password": "change-me-now"}'
```

## Part 2: Supabase Setup

### 2.1 Create Supabase Project

1. Go to https://supabase.com and sign up
2. Create a new project
3. Wait for project to be provisioned (~2 minutes)

### 2.2 Get Credentials

Navigate to **Settings → API**:
- Copy **Project URL** → `SUPABASE_URL`
- Copy **anon public** key → `SUPABASE_ANON_KEY`

Navigate to **Settings → API → JWT Settings**:
- Copy **JWT Secret** → `SUPABASE_JWT_SECRET`

### 2.3 Configure Email Authentication

1. Go to **Authentication → Providers**
2. Ensure **Email** is enabled
3. Optionally configure email templates
4. For production, set up custom SMTP (optional)

## Part 3: AWS Infrastructure Setup

### 3.1 Configure AWS Credentials

```bash
# Install AWS CLI
brew install awscli  # macOS
# or: apt-get install awscli  # Linux

# Configure credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1)
```

### 3.2 Create SSH Key Pair

```bash
# In AWS Console: EC2 → Key Pairs → Create key pair
# Name: edu-vexxel-key
# Type: RSA
# Format: .pem
# Download and save to ~/.ssh/

# Set permissions
chmod 400 ~/.ssh/edu-vexxel-key.pem
```

### 3.3 Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Update `terraform.tfvars`:
```hcl
aws_region     = "us-east-1"
environment    = "prod"
instance_type  = "t4g.micro"
ssh_key_name   = "edu-vexxel-key"

# Restrict to your IP for security
allowed_ssh_cidr = ["YOUR_IP_ADDRESS/32"]

# Supabase credentials
supabase_url        = "https://xxxxx.supabase.co"
supabase_anon_key   = "your-anon-key"
supabase_jwt_secret = "your-jwt-secret"

# Admin credentials
super_admin_email    = "admin@vexxel.ai"
super_admin_password = "SECURE_PASSWORD_HERE"

# Database password
db_password = "SECURE_DB_PASSWORD_HERE"
```

### 3.4 Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy
terraform apply
# Type 'yes' when prompted

# Save outputs
terraform output > ../ec2-info.txt
```

This creates:
- EC2 t4g.micro instance with Ubuntu 22.04 ARM64
- Security group with ports 22, 80, 443 open
- Elastic IP for consistent public IP
- Installs Docker and Docker Compose
- Creates application directories

### 3.5 Verify EC2 Instance

```bash
# Get EC2 IP from output
EC2_IP=$(terraform output -raw instance_public_ip)

# Test SSH connection
ssh -i ~/.ssh/edu-vexxel-key.pem ubuntu@$EC2_IP

# Verify Docker is installed
docker --version
docker-compose --version

# Exit
exit
```

## Part 4: Application Deployment

### 4.1 Prepare Production Environment File

```bash
cd /path/to/edu
cp .env.prod.example .env.prod
nano .env.prod
```

Update `.env.prod`:
```env
DATABASE_URL=postgresql://eduuser:YOUR_DB_PASSWORD@postgres:5432/edu_vexxel
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPER_ADMIN_EMAIL=admin@vexxel.ai
SUPER_ADMIN_PASSWORD=your-secure-password
DB_PASSWORD=your-secure-db-password  # Same as terraform.tfvars
ENVIRONMENT=production
```

### 4.2 Deploy Application

```bash
# Get EC2 IP
cd terraform
EC2_IP=$(terraform output -raw instance_public_ip)
cd ..

# Run deployment script
./scripts/deploy.sh $EC2_IP
```

The script will:
1. Copy application files to EC2
2. Copy `.env.prod` to EC2
3. Build Docker containers
4. Start all services (PostgreSQL, FastAPI, Nginx)
5. Run database migration
6. Create super admin user

### 4.3 Verify Deployment

```bash
# Check services are running
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml ps'

# View logs
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml logs -f app'
# Press Ctrl+C to exit logs

# Test API
curl http://$EC2_IP/docs
```

Visit in browser:
- API: http://YOUR_EC2_IP
- Docs: http://YOUR_EC2_IP/docs

### 4.4 Test Authentication

```bash
# Sign in as admin
curl -X POST http://$EC2_IP/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vexxel.ai",
    "password": "your-password-from-env-prod"
  }'

# Should return access_token and user info
```

## Part 5: SSL/TLS Setup (Production)

### 5.1 Configure Domain DNS

Point your domain to the EC2 Elastic IP:
```
Type: A
Name: edu (or @)
Value: YOUR_EC2_IP
TTL: 300
```

Wait for DNS propagation (~5-30 minutes):
```bash
dig edu.vexxel.ai
```

### 5.2 Obtain SSL Certificate

```bash
./scripts/setup-ssl.sh edu.vexxel.ai admin@vexxel.ai $EC2_IP
```

### 5.3 Update Nginx Configuration

```bash
nano nginx.conf
```

Uncomment the HTTPS server block and update:
```nginx
server {
    listen 443 ssl http2;
    server_name edu.vexxel.ai;  # Update this

    ssl_certificate /etc/letsencrypt/live/edu.vexxel.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/edu.vexxel.ai/privkey.pem;
    # ... rest of config
}
```

Also update the HTTP redirect:
```nginx
server {
    listen 80;
    server_name edu.vexxel.ai;  # Update this

    location / {
        return 301 https://$host$request_uri;  # Uncomment this
    }
}
```

### 5.4 Redeploy

```bash
./scripts/deploy.sh $EC2_IP
```

### 5.5 Verify HTTPS

Visit https://edu.vexxel.ai and verify the SSL certificate is valid.

## Part 6: Monitoring and Maintenance

### 6.1 View Logs

```bash
# All services
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml logs -f'

# Specific service
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml logs -f app'
```

### 6.2 Restart Services

```bash
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml restart'
```

### 6.3 Database Backups

Backups run automatically daily. To verify:

```bash
# List backups
ssh ubuntu@$EC2_IP 'ls -lh /opt/edu-vexxel/backups'

# Manual backup
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml exec backup /backup.sh'
```

To restore a backup:
```bash
# On EC2 instance
cd /opt/edu-vexxel
gunzip -c backups/backup_YYYYMMDD_HHMMSS.sql.gz | \
  sudo docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U eduuser -d edu_vexxel
```

### 6.4 Update Application

```bash
# Pull latest changes
git pull origin main

# Redeploy
./scripts/deploy.sh $EC2_IP
```

## Part 7: Troubleshooting

### Cannot SSH to EC2

```bash
# Check security group allows your IP
# Update terraform/terraform.tfvars with your current IP
cd terraform
terraform apply

# Verify key permissions
chmod 400 ~/.ssh/edu-vexxel-key.pem
```

### Docker containers not starting

```bash
# SSH to EC2
ssh ubuntu@$EC2_IP

# Check Docker status
sudo systemctl status docker

# Check container logs
cd /opt/edu-vexxel
sudo docker-compose -f docker-compose.prod.yml logs
```

### Database connection errors

```bash
# Verify PostgreSQL is running
ssh ubuntu@$EC2_IP 'cd /opt/edu-vexxel && sudo docker-compose -f docker-compose.prod.yml ps postgres'

# Check .env file has correct DB_PASSWORD
ssh ubuntu@$EC2_IP 'cat /opt/edu-vexxel/.env | grep DB_PASSWORD'
```

### Supabase authentication errors

- Verify `SUPABASE_JWT_SECRET` matches your Supabase project
- Check Supabase project is active
- Verify email/password provider is enabled in Supabase Auth settings

### 502 Bad Gateway

- App container may not be running or crashed
- Check app logs: `sudo docker-compose logs app`
- Restart containers: `sudo docker-compose restart`

## Part 8: Multi-Environment Setup

To set up dev/staging/prod environments:

### 8.1 Directory Structure

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf → ../../main.tf (symlink)
│   │   ├── variables.tf → ../../variables.tf (symlink)
│   │   ├── ec2.tf → ../../ec2.tf (symlink)
│   │   ├── security-groups.tf → ../../security-groups.tf (symlink)
│   │   ├── outputs.tf → ../../outputs.tf (symlink)
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── ... (same structure)
│   └── prod/
│       └── ... (same structure)
```

### 8.2 Deploy Multiple Environments

```bash
# Dev
cd terraform/environments/dev
terraform init
terraform apply

# Staging
cd ../staging
terraform init
terraform apply

# Prod
cd ../prod
terraform init
terraform apply
```

## Cost Optimization Tips

1. **Stop dev/staging when not in use**:
   ```bash
   aws ec2 stop-instances --instance-ids i-xxxxx
   ```

2. **Use Reserved Instances for production** (1-year commitment):
   - Saves ~30% compared to on-demand

3. **Monitor with AWS Cost Explorer**:
   - Set up billing alerts

4. **Use S3 for backups** (cheaper than EBS snapshots):
   ```bash
   # Sync backups to S3
   aws s3 sync /opt/edu-vexxel/backups s3://your-backup-bucket/
   ```

## Scaling Considerations

When you need to scale (>1000 users):

1. **Separate PostgreSQL**: Migrate to RDS ($15-30/month)
2. **Load Balancer**: Add ALB for multiple EC2 instances
3. **Auto Scaling**: Set up ASG for EC2 instances
4. **CDN**: Use CloudFront for static assets
5. **Monitoring**: Add CloudWatch or Datadog

---

**Setup Complete!** 🎉

Your multi-user learning platform is now deployed and ready for production use.

For questions or issues, refer to:
- `QUICKSTART.md` - Quick setup reference
- `SETUP_MULTIUSER.md` - Multi-user features guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
