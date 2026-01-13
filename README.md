# edu.vexxel.ai

A modern, minimalist learning platform for engineering notes and resources. Browse hierarchical topics, view handwritten notes with an immersive viewer, and access curated learning materials.

## Features

- **Immersive Note Viewer**: Full-screen portrait note viewing with magnification
- **Hierarchical Topics**: Tag-based organization with nested categories
- **Multiple Content Types**: Handwritten notes, Google Slides, videos, and blog links
- **Markdown Support**: Rich content descriptions with syntax highlighting
- **Theme System**: Modern/Terminal modes with Light/Dark themes
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **i18n Ready**: English and Portuguese translations

## Tech Stack

- **Backend**: FastAPI + SQLModel + SQLite
- **Frontend**: Jinja2 templates + HTMX + TailwindCSS (CDN)
- **Syntax Highlighting**: highlight.js
- **Infrastructure**: Docker + docker-compose

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/vexxel-ai/edu.git
cd edu

# Start with docker-compose
docker-compose up --build

# Access at http://localhost:8000
```

### Local Development

```bash
# Install dependencies with uv
uv sync

# Seed the database with example content
uv run python seed.py

# Run the development server
uvicorn app.main:app --reload --port 8000

# Access at http://localhost:8000
```

## Project Structure

```
edu/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # SQLModel database models
│   ├── database.py          # Database connection and session
│   ├── routers/             # Route modules
│   │   └── admin.py         # Admin CMS routes
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template with nav/footer
│       ├── index.html       # Homepage
│       ├── modules.html     # Module listing page
│       ├── module_detail.html # Module viewer
│       ├── admin/           # Admin CMS templates
│       └── partials/        # HTMX partials
├── static/
│   ├── css/                 # Stylesheets
│   │   ├── base.css         # Theme system and variables
│   │   ├── components.css   # Reusable UI components
│   │   └── module-viewer.css # Module viewer layouts
│   ├── js/                  # JavaScript modules
│   │   ├── theme.js         # Theme switching logic
│   │   ├── i18n.js          # Translations
│   │   └── module-viewer.js # Slide viewer and magnifier
│   ├── content/             # Static content assets
│   └── uploads/             # User-uploaded files
├── seed.py                  # Database seeding script
├── pyproject.toml           # uv project configuration
├── requirements.txt         # pip dependencies (generated)
├── Dockerfile               # Container definition
└── docker-compose.yml       # Service orchestration
```

## Database Models

**Post** - Learning module with title, slug, description (markdown)
**Tag** - Hierarchical categories (parent_id for nesting)
**PostTag** - Many-to-many relationship between posts and tags
**MediaAsset** - Attachments (images, slides, videos, links, HTML)

MediaAsset types: `IMAGE`, `SLIDE`, `YOUTUBE`, `BLOG_LINK`, `HTML`

## Development

### Code Formatting

```bash
# Format code
ruff format .

# Lint
ruff check . --fix
```

### Adding Content

Edit `seed.py` to add new modules, tags, or media assets, then run:

```bash
rm -f database.db
uv run python seed.py
```

### Admin Panel

Access the CMS at `/admin` to create and manage content via a web interface.

## Environment Variables

Create a `.env` file (see `.env.example`):

```env
DATABASE_URL=sqlite:///./database.db
SECRET_KEY=your-secret-key-here
```

## Deployment

### Docker Production

```bash
docker-compose up -d
```

### Manual Deployment

1. Set environment variables
2. Install dependencies: `uv sync`
3. Seed database: `uv run python seed.py`
4. Run with gunicorn: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`

## Links

- **GitHub**: https://github.com/vexxel-ai/edu
- **Twitter**: https://x.com/vexxelai

## License

See project documentation for license information.
