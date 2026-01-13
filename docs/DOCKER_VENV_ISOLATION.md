# Docker .venv Isolation

## Problem

When mounting the entire project directory into Docker, the container's virtual environment can contaminate your local `.venv`, causing:
- Python version mismatches
- Package conflicts
- IDE/linting issues

## Solution

Our `docker-compose.yml` uses **selective volume mounting** to keep Docker's `.venv` completely isolated from your local environment.

## How It Works

### Docker Setup

```yaml
volumes:
  # Only mount necessary files/directories
  - ./app:/app/app
  - ./migrations_scripts:/app/migrations_scripts
  - ./static:/app/static
  - ./tests:/app/tests
  - ./pyproject.toml:/app/pyproject.toml
  - ./uv.lock:/app/uv.lock
  # Docker's .venv lives in a named volume (isolated)
  - venv-data:/app/.venv
```

### What This Means

```
Your Machine:                    Docker Container:
├── app/                         ├── app/           (mounted from host)
├── migrations_scripts/          ├── migrations_scripts/ (mounted from host)
├── static/                      ├── static/        (mounted from host)
├── tests/                       ├── tests/         (mounted from host)
├── pyproject.toml               ├── pyproject.toml (mounted from host)
├── uv.lock                      ├── uv.lock        (mounted from host)
├── .venv/ (YOUR venv)           └── .venv/         (Docker volume, ISOLATED)
└── [other files]                    └── [not accessible]
```

## Benefits

1. **No Local Contamination**: Docker can't write to your local `.venv`
2. **Works Without Local .venv**: You don't need `.venv` to exist locally for Docker to work
3. **Independent Environments**: Run different Python versions locally vs Docker
4. **Fast Reloads**: Code changes still trigger `--reload` since source is mounted

## Usage

### First Time Setup

```bash
# No need to create local .venv first!
# Just start Docker
make up

# Docker will create its own isolated .venv automatically
```

### Optional: Local Development (Outside Docker)

If you want to run code locally (for IDE, linting, etc.):

```bash
# Create your own local .venv
python3.13 -m venv .venv  # Use whatever Python version you prefer
source .venv/bin/activate

# Install dependencies
uv sync

# Now you can use your IDE, run linters, etc.
# This is completely separate from Docker's environment
```

### Development Workflow

```bash
# Work with Docker (uses Docker's isolated .venv)
make up
make shell  # Opens shell in Docker with Docker's Python

# OR work locally (uses your local .venv)
source .venv/bin/activate
python app/main.py

# Both environments are completely independent!
```

## Verification

### Check Docker's Environment

```bash
# Check Docker's Python version
docker-compose exec app python --version

# Check Docker's packages
docker-compose exec app uv pip list

# Check where Docker's .venv is
docker-compose exec app ls -la /app/.venv
```

### Check Local Environment (if you created one)

```bash
# Check local Python version
source .venv/bin/activate
python --version

# Check local packages
uv pip list

# Check local .venv location
ls -la .venv
```

## Troubleshooting

### "Module not found" in Docker

```bash
# Rebuild Docker image and recreate volumes
make rebuild

# Or manually:
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Local .venv was contaminated before the fix

```bash
# Remove contaminated local .venv
rm -rf .venv

# Recreate clean local environment
python3 -m venv .venv
source .venv/bin/activate
uv sync
```

### Need to update dependencies

```bash
# Update uv.lock
uv lock

# Rebuild Docker to use new lock file
make rebuild
```

## Files Involved

- **docker-compose.yml**: Defines volume mounts and isolation
- **.dockerignore**: Prevents `.venv` from being copied during build
- **.gitignore**: Keeps `.venv` out of git
- **Dockerfile**: Installs dependencies into container's `.venv`

## Best Practices

1. **Never commit `.venv` to git** (already in `.gitignore`)
2. **Use Docker for running the app** (`make up`)
3. **Use local .venv only for IDE/linting** (optional)
4. **Always use `uv lock` to update dependencies**, then rebuild Docker
5. **Don't manually modify `.venv`** in either environment
