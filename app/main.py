"""
Main FastAPI application for edu.vexxel.ai

Provides:
- Public routes for browsing modules and content
- Section/Subsection based organization
- HTMX-powered filtering
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import markdown
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import create_db_and_tables, get_session
from app.models import MediaAsset, MediaType, Post, PostTag, Section, Subsection, Tag
from app.routers import auth, sections, tags, users

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== Lifespan Events ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting up edu.vexxel.ai...")

    # Validate environment variables
    try:
        from app.config import validate_environment

        validate_environment()
    except Exception as e:
        logger.error(f"Failed to validate environment: {e}")
        raise

    # Create database tables
    create_db_and_tables()
    logger.info("Database tables created successfully")

    logger.info("✓ Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down edu.vexxel.ai...")


# Initialize FastAPI app
app = FastAPI(
    title="edu.vexxel.ai",
    description="Learning platform for engineering notes and resources",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth.router)
app.include_router(sections.router)
app.include_router(tags.router)
app.include_router(users.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


# ==================== Helper Functions ====================


def get_sections_with_subsections(session: Session) -> list[dict]:
    """Get sections with their subsections organized hierarchically."""
    sections = session.exec(select(Section).order_by(Section.name)).all()

    result = []
    for section in sections:
        # Get subsections for this section
        subsections = session.exec(
            select(Subsection)
            .where(Subsection.section_id == section.id)
            .order_by(Subsection.name)
        ).all()

        result.append({"section": section, "subsections": subsections})

    return result


def sort_media_assets(assets: list[MediaAsset]) -> dict[str, list[MediaAsset]]:
    """Sort media assets by type and order."""
    sorted_assets = {
        "slides": [],
        "notes": [],
        "youtube": [],
        "blog_links": [],
        "code_snippets": [],
        "exercises": [],
    }

    for asset in sorted(assets, key=lambda x: x.order):
        if asset.type == MediaType.SLIDE:
            sorted_assets["slides"].append(asset)
        elif asset.type == MediaType.IMAGE:
            sorted_assets["notes"].append(asset)
        elif asset.type == MediaType.YOUTUBE:
            sorted_assets["youtube"].append(asset)
        elif asset.type == MediaType.BLOG_LINK:
            sorted_assets["blog_links"].append(asset)
        elif asset.type == MediaType.CODE_SNIPPET:
            sorted_assets["code_snippets"].append(asset)
        elif asset.type == MediaType.EXERCISE:
            sorted_assets["exercises"].append(asset)

    return sorted_assets


def render_markdown(text: str) -> str:
    """
    Render markdown to HTML.

    Creates a new Markdown instance for each call to ensure thread-safety.
    """
    md = markdown.Markdown(extensions=["fenced_code", "codehilite", "tables"])
    return md.convert(text)


# ==================== Public Routes ====================


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, session: Session = Depends(get_session)):
    """
    Homepage with hero section and featured modules.

    Shows only the top 2 modules as featured content.
    """
    # Get only the first 2 posts for the homepage
    posts = session.exec(select(Post).order_by(Post.created_at.desc()).limit(2)).all()

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.get("/modules", response_class=HTMLResponse)
async def modules_page(
    request: Request,
    section_id: Optional[int] = None,
    subsection_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """
    All modules page with section/subsection sidebar and module grid.

    Supports filtering by section, subsection, or tag via query parameters.
    """
    # Get sections with subsections for sidebar
    sections_hierarchy = get_sections_with_subsections(session)

    # Get all tags for optional filtering
    all_tags = session.exec(select(Tag).order_by(Tag.name)).all()

    # Get posts (filtered if needed)
    selected_section = None
    selected_subsection = None
    selected_tag = None

    if tag_id:
        # Filter by tag
        selected_tag = session.get(Tag, tag_id)
        if selected_tag:
            # Get posts with this tag
            post_tag_relations = session.exec(select(PostTag).where(PostTag.tag_id == tag_id)).all()
            post_ids = [pt.post_id for pt in post_tag_relations]
            if post_ids:
                posts = list(
                    session.exec(
                        select(Post).where(Post.id.in_(post_ids)).order_by(Post.created_at.desc())
                    ).all()
                )
            else:
                posts = []
        else:
            posts = []
    elif subsection_id:
        # Filter by subsection (most specific)
        posts = session.exec(
            select(Post)
            .where(Post.subsection_id == subsection_id)
            .order_by(Post.created_at.desc())
        ).all()
        selected_subsection = session.get(Subsection, subsection_id)
        if selected_subsection:
            selected_section = session.get(Section, selected_subsection.section_id)
    elif section_id:
        # Filter by section
        posts = session.exec(
            select(Post).where(Post.section_id == section_id).order_by(Post.created_at.desc())
        ).all()
        selected_section = session.get(Section, section_id)
    else:
        # Get all posts
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()

    return templates.TemplateResponse(
        "modules.html",
        {
            "request": request,
            "posts": posts,
            "sections_hierarchy": sections_hierarchy,
            "selected_section": selected_section,
            "selected_subsection": selected_subsection,
            "all_tags": all_tags,
            "selected_tag": selected_tag,
        },
    )


@app.get("/modules/{slug}", response_class=HTMLResponse)
async def module_detail(slug: str, request: Request, session: Session = Depends(get_session)):
    """
    Module detail page with conditional rendering of media assets.

    Displays:
    - Google Slides (if present)
    - TikTok-style scroll for images (if present)
    - YouTube videos (if present)
    - Blog links (if present)
    - Markdown description (always)
    """
    # Get post by slug
    post = session.exec(select(Post).where(Post.slug == slug)).first()

    if not post:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    # Get section and subsection (required)
    section = session.get(Section, post.section_id)
    subsection = session.get(Subsection, post.subsection_id)

    # Get optional tags
    post_tag_relations = session.exec(select(PostTag).where(PostTag.post_id == post.id)).all()
    tag_ids = [pt.tag_id for pt in post_tag_relations]
    post_tags = []
    if tag_ids:
        post_tags = list(session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all())

    # Build breadcrumb (Section > Subsection > Post)
    breadcrumbs = []
    if section:
        breadcrumbs.append({"name": section.name, "url": f"/modules?section_id={section.id}"})
    if subsection:
        breadcrumbs.append(
            {"name": subsection.name, "url": f"/modules?subsection_id={subsection.id}"}
        )

    # Sort media assets by type
    sorted_assets = sort_media_assets(post.media_assets)

    # Convert markdown to HTML (thread-safe)
    description_html = render_markdown(post.description) if post.description else ""

    # Render markdown for exercises content
    exercises_with_html = []
    for exercise in sorted_assets["exercises"]:
        exercise_dict = {
            "title": exercise.title,
            "url": exercise.url,
            "order": exercise.order,
            "content": render_markdown(exercise.content) if exercise.content else "",
        }
        exercises_with_html.append(exercise_dict)

    return templates.TemplateResponse(
        "module_detail.html",
        {
            "request": request,
            "post": post,
            "section": section,
            "subsection": subsection,
            "post_tags": post_tags,
            "breadcrumbs": breadcrumbs,
            "slides": sorted_assets["slides"],
            "notes": sorted_assets["notes"],
            "youtube_videos": sorted_assets["youtube"],
            "blog_links": sorted_assets["blog_links"],
            "code_snippets": sorted_assets["code_snippets"],
            "exercises": exercises_with_html,
            "description_html": description_html,
        },
    )


@app.get("/api/modules", response_class=HTMLResponse)
async def filter_modules(
    request: Request,
    section_id: Optional[int] = None,
    subsection_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """
    HTMX endpoint for filtering modules by section/subsection.

    Returns HTML partial with filtered posts and title.
    """
    selected_section = None
    selected_subsection = None

    if subsection_id:
        # Filter by subsection
        posts = session.exec(
            select(Post)
            .where(Post.subsection_id == subsection_id)
            .order_by(Post.created_at.desc())
        ).all()
        selected_subsection = session.get(Subsection, subsection_id)
        if selected_subsection:
            selected_section = session.get(Section, selected_subsection.section_id)
    elif section_id:
        # Filter by section
        posts = session.exec(
            select(Post).where(Post.section_id == section_id).order_by(Post.created_at.desc())
        ).all()
        selected_section = session.get(Section, section_id)
    else:
        # Get all posts
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()

    return templates.TemplateResponse(
        "partials/module_content.html",
        {
            "request": request,
            "posts": posts,
            "selected_section": selected_section,
            "selected_subsection": selected_subsection,
        },
    )


# ==================== Error Handlers ====================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
