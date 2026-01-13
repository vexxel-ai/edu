"""
Main FastAPI application for edu.vexxel.ai

Provides:
- Public routes for browsing modules and content
- Admin CMS integration
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
from app.models import MediaAsset, MediaType, Post, PostTag, Tag
from app.routers import analytics, auth, tags, users

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
app.include_router(tags.router)
app.include_router(users.router)
app.include_router(analytics.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


# ==================== Helper Functions ====================


def get_hierarchical_tags(session: Session) -> list[dict]:
    """Get tags organized hierarchically."""
    root_tags = session.exec(select(Tag).where(Tag.parent_id.is_(None)).order_by(Tag.name)).all()

    hierarchical = []
    for root_tag in root_tags:
        # Get children
        children = session.exec(
            select(Tag).where(Tag.parent_id == root_tag.id).order_by(Tag.name)
        ).all()

        hierarchical.append({"tag": root_tag, "children": children})

    return hierarchical


def sort_media_assets(assets: list[MediaAsset]) -> dict[str, list[MediaAsset]]:
    """Sort media assets by type and order."""
    sorted_assets = {"slides": [], "images": [], "youtube": [], "blog_links": [], "html": []}

    for asset in sorted(assets, key=lambda x: x.order):
        if asset.type == MediaType.SLIDE:
            sorted_assets["slides"].append(asset)
        elif asset.type == MediaType.IMAGE:
            sorted_assets["images"].append(asset)
        elif asset.type == MediaType.YOUTUBE:
            sorted_assets["youtube"].append(asset)
        elif asset.type == MediaType.BLOG_LINK:
            sorted_assets["blog_links"].append(asset)
        elif asset.type == MediaType.HTML:
            sorted_assets["html"].append(asset)

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
    request: Request, tag_id: Optional[int] = None, session: Session = Depends(get_session)
):
    """
    All modules page with tag sidebar and module grid.

    Supports filtering by tag via query parameter.
    """
    # Get hierarchical tags for sidebar
    hierarchical_tags = get_hierarchical_tags(session)

    # Get posts (filtered by tag if provided)
    if tag_id:
        # Get posts associated with this tag
        post_tags = session.exec(select(PostTag).where(PostTag.tag_id == tag_id)).all()
        post_ids = [pt.post_id for pt in post_tags]

        posts = session.exec(
            select(Post).where(Post.id.in_(post_ids)).order_by(Post.created_at.desc())
        ).all()

        selected_tag = session.get(Tag, tag_id)
    else:
        # Get all posts
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()
        selected_tag = None

    return templates.TemplateResponse(
        "modules.html",
        {
            "request": request,
            "posts": posts,
            "hierarchical_tags": hierarchical_tags,
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
    - Custom HTML (if present)
    - Markdown description (always)
    """
    # Get post by slug
    post = session.exec(select(Post).where(Post.slug == slug)).first()

    if not post:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    # Get post tags (optimized to avoid N+1 queries)
    post_tag_relations = session.exec(select(PostTag).where(PostTag.post_id == post.id)).all()
    tag_ids = [pt.tag_id for pt in post_tag_relations]
    post_tags = []
    if tag_ids:
        post_tags = list(session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all())

    # Build breadcrumb hierarchy from the most specific (deepest) tag
    breadcrumb_tags = []
    if post_tags:
        # Find the deepest tag (one with a parent)
        deepest_tag = None
        for tag in post_tags:
            if tag.parent_id:
                deepest_tag = tag
                break

        # If no child tag found, use the first root tag
        if not deepest_tag and post_tags:
            deepest_tag = post_tags[0]

        # Build hierarchy from deepest to root
        if deepest_tag:
            current = deepest_tag
            breadcrumb_tags.insert(0, current)
            while current.parent_id:
                parent = session.get(Tag, current.parent_id)
                if parent:
                    breadcrumb_tags.insert(0, parent)
                    current = parent
                else:
                    break

    # Extract subtopic from title (e.g., "An Introduction" from "GNN: An Introduction")
    post_subtopic = post.title
    if ":" in post.title:
        # Use the part after the colon, stripped
        post_subtopic = post.title.split(":", 1)[1].strip()
    elif post_tags:
        # If no colon, check if title contains the tag name
        for tag in post_tags:
            if tag.name in post.title:
                # Remove the tag name from the title for the subtopic
                post_subtopic = post.title.replace(tag.name, "").strip()
                # Remove leading/trailing punctuation
                post_subtopic = post_subtopic.strip(": -")
                break

    # Sort media assets by type
    sorted_assets = sort_media_assets(post.media_assets)

    # Convert markdown to HTML (thread-safe)
    description_html = render_markdown(post.description) if post.description else ""

    return templates.TemplateResponse(
        "module_detail.html",
        {
            "request": request,
            "post": post,
            "post_tags": post_tags,
            "breadcrumb_tags": breadcrumb_tags,
            "post_subtopic": post_subtopic,
            "slides": sorted_assets["slides"],
            "images": sorted_assets["images"],
            "youtube_videos": sorted_assets["youtube"],
            "blog_links": sorted_assets["blog_links"],
            "html_content": sorted_assets["html"],
            "description_html": description_html,
        },
    )


@app.get("/api/modules", response_class=HTMLResponse)
async def filter_modules(
    request: Request, tag_id: Optional[int] = None, session: Session = Depends(get_session)
):
    """
    HTMX endpoint for filtering modules by tag.

    Returns HTML partial with filtered posts and title.
    """
    selected_tag = None

    if tag_id:
        # Get posts associated with this tag
        post_tags = session.exec(select(PostTag).where(PostTag.tag_id == tag_id)).all()
        post_ids = [pt.post_id for pt in post_tags]

        posts = session.exec(
            select(Post).where(Post.id.in_(post_ids)).order_by(Post.created_at.desc())
        ).all()

        selected_tag = session.get(Tag, tag_id)
    else:
        # Get all posts
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()

    return templates.TemplateResponse(
        "partials/module_content.html",
        {"request": request, "posts": posts, "selected_tag": selected_tag},
    )


# ==================== Error Handlers ====================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
