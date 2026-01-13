# Documentation Index

Quick reference to all documentation for edu.vexxel.ai

## 📖 Getting Started

### For Development
1. **[Docker Quick Start](DOCKER_QUICKSTART.md)** - Run locally with Docker (recommended)
   - Initial setup
   - All make commands
   - Local development workflow

### For Deployment
2. **[Deployment Guide](DEPLOYMENT.md)** - Deploy to AWS
   - Complete deployment walkthrough
   - Terraform setup
   - SSL configuration
   - Cost breakdown

### For Understanding the System
3. **[Multi-User API Guide](SETUP_MULTIUSER.md)** - API endpoints and features
   - Authentication
   - Tag approval workflow
   - User management
   - Analytics

## 🏗️ Architecture

4. **[Architecture with RDS](ARCHITECTURE_RDS.md)** - Infrastructure overview
   - Local vs Staging vs Production
   - RDS configuration
   - Cost breakdown
   - Frontend hosting options

5. **[Multi-Environment Setup](MULTI_ENVIRONMENT.md)** - Dev/Staging/Prod
   - Environment differences
   - Terraform workspaces
   - Separate configurations

## 📋 Quick Reference

### Local Development
```bash
make setup      # Initial setup
make db-setup   # Initialize database
make up         # Start services
make dev        # Start and follow logs
```

### Deployment
```bash
cd terraform
terraform apply -var-file=terraform.tfvars.staging
../scripts/deploy.sh $EC2_IP
```

### API
- Docs: http://localhost:8000/docs
- Sign in: POST /auth/signin
- Create user: POST /auth/signup

## 🗂️ File Organization

```
docs/
├── README.md                 # This file
├── DOCKER_QUICKSTART.md      # Local development guide
├── DEPLOYMENT.md             # Production deployment
├── SETUP_MULTIUSER.md        # API reference
├── ARCHITECTURE_RDS.md       # Infrastructure design
└── MULTI_ENVIRONMENT.md      # Environment management
```

## 🎯 Common Tasks

**Run locally:**
→ See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

**Deploy to AWS:**
→ See [DEPLOYMENT.md](DEPLOYMENT.md)

**Understand API:**
→ See [SETUP_MULTIUSER.md](SETUP_MULTIUSER.md)

**Scale infrastructure:**
→ See [ARCHITECTURE_RDS.md](ARCHITECTURE_RDS.md)

**Manage environments:**
→ See [MULTI_ENVIRONMENT.md](MULTI_ENVIRONMENT.md)

---

**Start here:** [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for local development
