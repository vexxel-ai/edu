# edu.vexxel.ai

A multi-user learning platform for sharing engineering notes, slides, and educational content.

## Quick Start

```bash
make setup      # Create .env file
make db-setup   # Initialize database (type SETUP)
make up         # Start services
```

Visit: **http://localhost:8000/docs**

## Features

- 🔐 Multi-user authentication (Supabase)
- 👥 Role-based access (Admin, Sub-Admin, User)
- ✅ Tag approval workflow
- 📊 Analytics dashboard
- 🚀 Production-ready (~$21-36/month on AWS)

## Tech Stack

- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Auth**: Supabase (free tier)
- **Infrastructure**: Docker + Terraform + AWS
- **Database**: Local PostgreSQL (dev) / RDS (staging/prod)

## Commands

```bash
make help       # Show all commands
make dev        # Start and follow logs
make shell      # Open app shell
make test       # Run tests
make format     # Format code
make lint       # Check code style
```

## Documentation

- **[Docker Quick Start](docs/DOCKER_QUICKSTART.md)** - Local development
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deploy to AWS
- **[API Reference](docs/SETUP_MULTIUSER.md)** - API endpoints
- **[Architecture](docs/ARCHITECTURE_RDS.md)** - Infrastructure design
- **[Full Docs Index](docs/README.md)** - All documentation

## Project Structure

```
├── app/                # FastAPI application
│   ├── main.py
│   ├── models.py
│   ├── auth/
│   └── routers/
├── migrations/         # Database setup
├── terraform/          # AWS infrastructure
├── docs/              # Documentation
├── docker-compose.yml # Docker setup
└── Makefile          # Commands
```

## Environment Variables

Required in `.env`:

```env
# Supabase (https://supabase.com)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Admin
SUPER_ADMIN_EMAIL=admin@vexxel.ai
SUPER_ADMIN_PASSWORD=change-me

# Database (Docker)
DB_PASSWORD=devpassword
```

## Cost Breakdown

| Environment | Monthly Cost |
|-------------|--------------|
| Local Dev | $0 |
| Staging | ~$21 |
| Production | ~$36 |

## API Endpoints

- `POST /auth/signup` - Register user
- `POST /auth/signin` - Login
- `GET /auth/me` - Get current user
- `POST /tags/request` - Request new tag
- `GET /tags/pending` - View pending requests (Sub-Admin+)
- `GET /users` - List users (Admin only)

Full API docs: http://localhost:8000/docs

## Development

```bash
# Start development
make dev

# Make changes to code (auto-reloads)

# Run tests
make test

# Format code
make format
```

## Deployment

```bash
cd terraform
terraform apply -var-file=terraform.tfvars.staging
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete guide.

## Support

- 📚 Documentation: [docs/](docs/)
- 🐛 Issues: GitHub Issues
- 💬 API Docs: http://localhost:8000/docs

---

Built with FastAPI, Supabase, and PostgreSQL 🚀
