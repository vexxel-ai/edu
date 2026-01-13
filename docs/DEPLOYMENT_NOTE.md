# Deployment Simplification Note

## Important Change

The deployment documentation (DEPLOYMENT.md) was written for the old architecture where PostgreSQL ran in Docker on EC2.

**We now use RDS**, so the deployment is simpler:

### New Deployment (with RDS):
```bash
# 1. Deploy infrastructure (EC2 + RDS)
cd terraform
terraform apply

# 2. Build and push Docker image
docker build -t edu-vexxel .

# 3. Run on EC2 (single container)
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@rds-endpoint/db \
  -e SUPABASE_URL=... \
  -p 8000:8000 \
  edu-vexxel
```

No docker-compose needed on EC2!

**DEPLOYMENT.md needs to be rewritten for the RDS architecture.**

For now, use ARCHITECTURE_RDS.md for the correct setup.
