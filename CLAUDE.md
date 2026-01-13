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
├── migrations_scripts/   # Database setup and seeding
│   ├── initial_setup.py # Initial DB setup script
│   ├── seed.py          # DB seed script
│   └── posts_examples/  # Example posts for seeding
│       ├── example_notes/    # Shared example images
│       └── [post-slug]/      # Each post folder contains:
│           ├── content.md    # Markdown content
│           └── metadata.json # Post metadata (title, tags, media)
├── static/               # Static assets
├── docs/                 # Documentation
├── terraform/            # AWS infrastructure
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

Core tables with relationships:

- **User**: Platform users with roles (admin, sub_admin, user)
- **Section**: Top-level categories (e.g., "Reinforcement Learning", "Deep Learning")
- **Subsection**: Second-level categories within a Section (e.g., "Q-Learning", "CNNs")
- **Post**: Content modules (REQUIRED: section_id + subsection_id)
- **Tag**: Optional flat tags for filtering (no hierarchy, no approval needed)
- **PostTag**: Many-to-many junction (Post ↔ Tag, optional)
- **MediaAsset**: Images, slides, videos, links (1:N with Post)
- **PendingSection**: Section creation requests requiring admin approval
- **PendingSubsection**: Subsection creation requests requiring admin approval

MediaAsset.type enum: `image` | `slide` | `youtube` | `blog_link`

### Key Relationships

- Every **Post** MUST have exactly ONE Section and ONE Subsection
- **Subsections** belong to a Section (many-to-one)
- **Tags** are optional (many-to-many via PostTag)
- **Subsection slugs** are unique within a section (not globally)

## User Roles & Permissions

- **Admin**: Full access (user management, all content, approve sections/subsections)
- **Sub-Admin**: Can approve sections/subsections, manage content (no user management)
- **User**: Can create content, create tags (no approval), request new sections/subsections

## Post Structure

Every post has:

1. Title and slug (unique URL identifier)
2. Markdown description with code syntax highlighting
3. **Section** (REQUIRED): Top-level category
4. **Subsection** (REQUIRED): Second-level category
5. Author (User relationship, optional)
6. Media assets:
   - Images (handwritten notes)
   - Google Slides embeds
   - YouTube videos
   - Blog/article links
7. Tags (optional, flat, many-to-many)
8. Timestamps (created_at, updated_at)

## Adding New Post Examples

To add a new post example for seeding:

1. Create a folder in `migrations_scripts/posts_examples/[post-slug]/`
2. Add `content.md` with the markdown content
3. Add `metadata.json` with:
   - `title`: Post title
   - `slug`: URL-friendly slug
   - `section`: Section slug (REQUIRED, must exist in seed.py)
   - `subsection`: Subsection slug (REQUIRED, must exist in seed.py)
   - `tags`: Array of tag slugs (OPTIONAL, must exist in seed.py)
   - `media_assets`: Array of media objects with `type`, `url`, `title`, `order`
4. Run `make seed` to populate the database

Example metadata.json:
```json
{
  "title": "Introduction to Q-Learning",
  "slug": "intro-q-learning",
  "section": "reinforcement-learning",
  "subsection": "q-learning",
  "tags": ["neural-networks", "python"],
  "media_assets": [
    {
      "type": "image",
      "url": "/migrations_scripts/posts_examples/example_notes/example_0.jpg",
      "title": "Example Image",
      "order": 1
    }
  ]
}
```

## Key UI Patterns

1. **Section/Subsection Sidebar**: Two-level navigation, HTMX-powered filtering (`hx-get`, `hx-target`)
2. **Breadcrumbs**: Section > Subsection > Post Title
3. **Scroll Snap Container**: Use `snap-y snap-mandatory h-screen overflow-y-scroll` on parent, `snap-start` on children
4. **Google Slides**: Embed via iframe with `pub?embedded=true` URL format

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
