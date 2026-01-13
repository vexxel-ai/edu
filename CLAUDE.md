# edu.vexxel.ai - Multi-User Learning Platform

## Purpose

A multi-user learning platform for sharing engineering notes, slides, and educational content. Features authentication, role-based access control, tag approval workflows, and analytics.

## Tech Stack

- **Backend**: FastAPI + SQLModel + PostgreSQL (SQLite for local dev)
- **Auth**: Supabase (OAuth, JWT)
- **Frontend**: Jinja2 + HTMX + TailwindCSS (CDN)
- **Syntax Highlighting**: highlight.js (CDN)
- **Infrastructure**: Docker + docker-compose + Terraform (AWS)
- **Migrations**: Alembic

## Project Structure

```
├── app/
│   ├── main.py           # FastAPI app, public routes
│   ├── models.py         # SQLModel definitions
│   ├── database.py       # DB connection, session
│   ├── auth/             # Authentication module
│   │   ├── dependencies.py    # JWT validation, role checks
│   │   ├── supabase_client.py # Supabase integration
│   │   └── utils.py           # Auth utilities
│   ├── routers/          # API routers
│   │   ├── auth.py       # Signup, signin, signout
│   │   ├── tags.py       # Tag requests, approval
│   │   ├── users.py      # User management (admin)
│   │   └── analytics.py  # Tag activity analytics
│   └── templates/        # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── modules.html
│       ├── module_detail.html
│       └── partials/     # HTMX partials
├── migrations/           # Database migrations
│   └── initial_setup.py  # Initial DB setup script
├── static/               # Static assets
├── docs/                 # Documentation
├── terraform/            # AWS infrastructure
├── seed.py               # DB seed script
├── Dockerfile
├── docker-compose.yml
├── Makefile              # Development commands
├── pyproject.toml
└── uv.lock
```

## Commands

```bash
# Setup (uses Makefile)
make setup      # Create .env file
make db-setup   # Initialize database
make up         # Start Docker services
make dev        # Start and follow logs

# Dependencies
uv sync

# Run locally (without Docker)
uvicorn app.main:app --reload --port 8000

# Format & Lint
make format     # or: ruff format .
make lint       # or: ruff check .
make lint-fix   # or: ruff check . --fix

# Tests
make test       # or: pytest

# Docker
make build      # Rebuild images
make shell      # Open app shell
make db-shell   # Open PostgreSQL shell
```

## Data Model

Seven tables with relationships:

- **User**: Platform users with roles (admin, sub_admin, user)
- **Post**: Content modules with markdown, media assets, tags
- **Tag**: Hierarchical tags (self-referential parent_id)
- **PendingTag**: Tag requests requiring approval
- **PostTag**: Many-to-many junction (Post ↔ Tag)
- **MediaAsset**: Images, slides, videos, links, HTML (1:N with Post)
- **TagActivity**: Analytics data for tags

MediaAsset.type enum: `image` | `slide` | `youtube` | `blog_link` | `html`

## User Roles & Permissions

- **Admin**: Full access (user management, all content, approve tags)
- **Sub-Admin**: Can approve tags, manage content (no user management)
- **User**: Can create content, request new tags

## Post Structure

Every post has:

1. Title and slug (unique URL identifier)
2. Markdown description with code syntax highlighting
3. Author (User relationship)
4. Media assets:
   - Images (handwritten notes)
   - Google Slides embeds
   - YouTube videos
   - Blog/article links
   - Custom HTML content
5. Tags (hierarchical, many-to-many)
6. Timestamps (created_at, updated_at)

## Key UI Patterns

1. **Tag Sidebar**: Hierarchical tree, HTMX-powered filtering (`hx-get`, `hx-target`)
2. **Scroll Snap Container**: Use `snap-y snap-mandatory h-screen overflow-y-scroll` on parent, `snap-start` on children
3. **Google Slides**: Embed via iframe with `pub?embedded=true` URL format

## Code Conventions

- Use `async def` for all route handlers
- SQLModel for ORM (not raw SQLAlchemy)
- Return `HTMLResponse` with `templates.TemplateResponse()`
- HTMX partials go in `templates/partials/`
- All Tailwind via CDN (no build step)

## Testing Changes

1. Run `ruff check .` — must pass with no errors
2. Run `mypy app/` — no type errors
3. Start server and manually verify UI works
4. If Docker changes: `docker-compose up --build` must succeed

## Git Practices

- Commit messages: imperative mood, <50 chars subject
- No co-authored-by or tool attribution in commits
- One logical change per commit
