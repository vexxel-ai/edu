# Knowledge Sharing Platform

## Purpose

A personal knowledge sharing platform for engineering notes. Users browse hierarchical tags, view posts with embedded Google Slides, and scroll through handwritten note images a very aestehtic and readable format.

## Tech Stack

- **Backend**: FastAPI + SQLModel + SQLite
- **Frontend**: Jinja2 + HTMX + TailwindCSS (CDN)
- **Syntax Highlighting**: highlight.js (CDN)
- **Infrastructure**: Docker + docker-compose

## Project Structure

```
├── app/
│   ├── main.py           # FastAPI app, routes
│   ├── models.py         # SQLModel definitions
│   ├── database.py       # DB connection, session
│   └── templates/        # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── post_detail.html
│       └── partials/     # HTMX partials
├── static/               # Static assets
├── seed.py               # DB seed script
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Commands

```bash
# Dependencies
uv sync 

# Run locally
uvicorn app.main:app --reload --port 8000

# Format & Lint
ruff format .
ruff check . --fix

# Type check
mypy app/

# Docker
docker-compose up --build

# Seed database
python seed.py
```

## Data Model

Four tables with these relationships:

- `Post` → has many `MediaAsset` (1:N)
- `Post` ↔ `Tag` via `PostTag` (M:N)
- `Tag` → self-referential `parent_id` for hierarchy

MediaAsset.type is an enum: `image` | `slide`

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
