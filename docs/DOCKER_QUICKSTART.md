# Docker Quick Start

Run everything through Docker - no loose commands needed!

## Prerequisites

- Docker and Docker Compose installed
- Supabase account (free at https://supabase.com)

## Quick Start (3 steps)

### 1. Initial Setup

```bash
make setup
```

This creates your `.env` file from the template.

Edit `.env` and add your Supabase credentials:
```bash
nano .env
```

### 2. Initialize Database

```bash
make db-setup
```

Type `SETUP` when prompted. This creates all tables and the super admin user.

### 3. Start Services

```bash
make up
```

That's it! Visit http://localhost:8000/docs

## Available Commands

### Essentials

```bash
make setup      # Initial project setup (creates .env)
make db-setup   # Initialize database (run once)
make up         # Start all services
make down       # Stop all services
make logs       # View logs
```

### Development

```bash
make dev        # Start services and follow logs
make restart    # Restart all services
make shell      # Open shell in app container
make db-shell   # Open PostgreSQL shell
```

### Database

```bash
make db-setup   # Initial database setup
make db-reset   # Reset database (WARNING: deletes all data)
```

### Code Quality

```bash
make format     # Format code with ruff
make lint       # Check code style
make lint-fix   # Auto-fix linting issues
make test       # Run tests
```

### Maintenance

```bash
make build      # Rebuild Docker images
make rebuild    # Rebuild and restart
make status     # Show service status
make clean      # Remove containers and volumes
```

## Common Workflows

### First Time Setup

```bash
# 1. Setup project
make setup

# 2. Edit .env with Supabase credentials
nano .env

# 3. Initialize database
make db-setup

# 4. Start services
make up

# 5. Open browser
open http://localhost:8000/docs
```

### Daily Development

```bash
# Start and watch logs
make dev

# In another terminal - make changes to code
# App auto-reloads thanks to --reload flag

# View specific logs
make logs-app   # or make logs-db

# Stop when done
make down
```

### Testing API

```bash
# Services must be running
make up

# Sign in as admin
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vexxel.ai",
    "password": "change-me"
  }'

# Or use the interactive docs
open http://localhost:8000/docs
```

### Reset Everything

```bash
# If you mess something up
make clean      # Remove all containers and volumes
make setup      # Recreate .env
make db-setup   # Reinitialize database
make up         # Start fresh
```

## Docker Compose Commands (Alternative)

If you prefer docker-compose directly:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run database setup
docker-compose run --rm app python migrations/initial_setup.py

# Open shell
docker-compose exec app /bin/sh

# Run tests
docker-compose run --rm app pytest

# Format code
docker-compose run --rm app ruff format .
```

## What's Running?

When you run `make up` or `docker-compose up`, you get:

1. **PostgreSQL** - Database on port 5432
2. **FastAPI App** - API on port 8000 with hot reload

Check status:
```bash
make status
```

## Environment Variables

All environment variables come from `.env`:

```env
# Database
DB_PASSWORD=devpassword

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Admin
SUPER_ADMIN_EMAIL=admin@vexxel.ai
SUPER_ADMIN_PASSWORD=change-me

# Environment
ENVIRONMENT=development
```

## Volumes

Data persists in Docker volumes:

- `postgres-data` - Database files

To completely wipe data:
```bash
make clean
```

## Logs

View logs for all services:
```bash
make logs
```

View specific service:
```bash
make logs-app   # App logs only
make logs-db    # PostgreSQL logs only
```

Follow logs (real-time):
```bash
docker-compose logs -f app
```

## Troubleshooting

### Port already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it or use different port in docker-compose.yml
```

### Database connection errors

```bash
# Check PostgreSQL is running
make status

# View database logs
make logs-db

# Restart services
make restart
```

### Can't connect to Supabase

```bash
# Verify credentials in .env
cat .env | grep SUPABASE

# Make sure Supabase project is active
# Visit: https://app.supabase.com
```

### Need to rebuild

```bash
# After changing Dockerfile or dependencies
make rebuild
```

### Permission errors

```bash
# If you get permission errors with volumes
sudo chown -R $USER:$USER .
```

## Tips

1. **Use `make help`** to see all available commands
2. **Use `make dev`** for development (starts + follows logs)
3. **Use `make shell`** to run commands inside the container
4. **Use `make db-shell`** to access PostgreSQL directly
5. **Changes auto-reload** - just edit files and save

## Next Steps

- Read `SETUP_MULTIUSER.md` for API details
- Read `DEPLOYMENT.md` for production deployment
- Use `make help` to see all commands

---

**Everything runs in Docker - no loose commands needed!** 🐳
