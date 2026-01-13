"""
Admin router for CMS functionality.

Provides:
- Simple password-based authentication
- CRUD operations for modules (posts)
- CRUD operations for tags
- CRUD operations for resources (media assets)
- File upload handling
"""

import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import AdminSession, MediaAsset, MediaType, Post, PostTag, Tag


router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Upload configuration
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ==================== Authentication ====================


def get_admin_password() -> str:
    """Get admin password from environment variable."""
    import os
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    return password


def create_session_token(session: Session) -> str:
    """Create a new admin session token."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    admin_session = AdminSession(token=token, expires_at=expires_at)
    session.add(admin_session)
    session.commit()

    return token


def verify_session_token(
    session: Session,
    admin_token: Optional[str] = Cookie(None)
) -> bool:
    """Verify admin session token from cookie."""
    if not admin_token:
        return False

    stmt = select(AdminSession).where(AdminSession.token == admin_token)
    admin_session = session.exec(stmt).first()

    if not admin_session:
        return False

    # Check if token is expired
    if admin_session.expires_at < datetime.now(timezone.utc):
        return False

    return True


def require_admin(
    session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(None)
):
    """Dependency to require admin authentication."""
    if not verify_session_token(session, admin_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


# ==================== Authentication Routes ====================


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display admin login page."""
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )


@router.post("/login")
async def login(
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    """Process admin login."""
    correct_password = get_admin_password()

    if password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Create session token
    token = create_session_token(session)

    # Redirect to dashboard with cookie
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        samesite="lax"
    )

    return response


@router.get("/logout")
async def logout():
    """Log out admin user."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("admin_token")
    return response


# ==================== Dashboard ====================


@router.get("", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def dashboard(
    request: Request,
    session: Session = Depends(get_session)
):
    """Admin dashboard."""
    # Get all posts
    posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()

    # Get all tags (hierarchical)
    root_tags = session.exec(
        select(Tag).where(Tag.parent_id.is_(None)).order_by(Tag.name)
    ).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "posts": posts,
            "root_tags": root_tags
        }
    )


# ==================== Module (Post) Management ====================


@router.get("/modules/new", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def new_module_page(
    request: Request,
    session: Session = Depends(get_session)
):
    """Display form to create a new module."""
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    return templates.TemplateResponse(
        "admin/module_form.html",
        {
            "request": request,
            "tags": tags,
            "post": None
        }
    )


@router.post("/modules", dependencies=[Depends(require_admin)])
async def create_module(
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    tag_ids: list[int] = Form(default=[]),
    session: Session = Depends(get_session)
):
    """Create a new module."""
    # Create post
    post = Post(
        title=title,
        slug=slug,
        description=description
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    # Add tags
    for tag_id in tag_ids:
        post_tag = PostTag(post_id=post.id, tag_id=tag_id)
        session.add(post_tag)

    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/modules/{post_id}/edit", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def edit_module_page(
    post_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Display form to edit a module."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    tags = session.exec(select(Tag).order_by(Tag.name)).all()

    # Get current tag IDs for this post
    current_tag_ids = [pt.tag_id for pt in session.exec(
        select(PostTag).where(PostTag.post_id == post_id)
    ).all()]

    return templates.TemplateResponse(
        "admin/module_form.html",
        {
            "request": request,
            "tags": tags,
            "post": post,
            "current_tag_ids": current_tag_ids
        }
    )


@router.post("/modules/{post_id}/edit", dependencies=[Depends(require_admin)])
async def update_module(
    post_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    tag_ids: list[int] = Form(default=[]),
    session: Session = Depends(get_session)
):
    """Update a module."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update post
    post.title = title
    post.slug = slug
    post.description = description
    post.updated_at = datetime.now(timezone.utc)

    # Update tags (remove old, add new)
    session.exec(select(PostTag).where(PostTag.post_id == post_id)).all()
    for pt in session.exec(select(PostTag).where(PostTag.post_id == post_id)).all():
        session.delete(pt)

    for tag_id in tag_ids:
        post_tag = PostTag(post_id=post.id, tag_id=tag_id)
        session.add(post_tag)

    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/modules/{post_id}/delete", dependencies=[Depends(require_admin)])
async def delete_module(
    post_id: int,
    session: Session = Depends(get_session)
):
    """Delete a module."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    session.delete(post)
    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


# ==================== Tag Management ====================


@router.get("/tags/new", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def new_tag_page(
    request: Request,
    session: Session = Depends(get_session)
):
    """Display form to create a new tag."""
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    return templates.TemplateResponse(
        "admin/tag_form.html",
        {
            "request": request,
            "tags": tags,
            "tag": None
        }
    )


@router.post("/tags", dependencies=[Depends(require_admin)])
async def create_tag(
    name: str = Form(...),
    slug: str = Form(...),
    parent_id: Optional[int] = Form(None),
    session: Session = Depends(get_session)
):
    """Create a new tag."""
    tag = Tag(
        name=name,
        slug=slug,
        parent_id=parent_id if parent_id else None
    )
    session.add(tag)
    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tags/{tag_id}/edit", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def edit_tag_page(
    tag_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Display form to edit a tag."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Get all tags except this one (to prevent circular references)
    tags = session.exec(
        select(Tag).where(Tag.id != tag_id).order_by(Tag.name)
    ).all()

    return templates.TemplateResponse(
        "admin/tag_form.html",
        {
            "request": request,
            "tags": tags,
            "tag": tag
        }
    )


@router.post("/tags/{tag_id}/edit", dependencies=[Depends(require_admin)])
async def update_tag(
    tag_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    parent_id: Optional[int] = Form(None),
    session: Session = Depends(get_session)
):
    """Update a tag."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.name = name
    tag.slug = slug
    tag.parent_id = parent_id if parent_id else None

    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tags/{tag_id}/delete", dependencies=[Depends(require_admin)])
async def delete_tag(
    tag_id: int,
    session: Session = Depends(get_session)
):
    """Delete a tag."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


# ==================== Resource Management ====================


@router.get("/modules/{post_id}/resources/add", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def add_resource_page(
    post_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Display form to add a resource to a module."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        "admin/resource_form.html",
        {
            "request": request,
            "post": post,
            "media_types": [t.value for t in MediaType]
        }
    )


@router.post("/modules/{post_id}/resources", dependencies=[Depends(require_admin)])
async def add_resource(
    post_id: int,
    resource_type: str = Form(...),
    title: str = Form(...),
    url: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    order: int = Form(0),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Add a resource to a module."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Handle file upload for images
    if resource_type == MediaType.IMAGE.value and file:
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
            )

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Save file
        filename = f"{secrets.token_urlsafe(16)}{file_ext}"
        file_path = UPLOAD_DIR / filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

        url = f"/static/uploads/{filename}"

    # Create media asset
    media_asset = MediaAsset(
        post_id=post_id,
        type=MediaType(resource_type),
        url=url,
        content=content,
        title=title,
        order=order
    )
    session.add(media_asset)
    session.commit()

    return RedirectResponse(
        url=f"/admin/modules/{post_id}/edit",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/resources/{resource_id}/delete", dependencies=[Depends(require_admin)])
async def delete_resource(
    resource_id: int,
    session: Session = Depends(get_session)
):
    """Delete a resource."""
    resource = session.get(MediaAsset, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    post_id = resource.post_id

    # Delete file if it's an uploaded image
    if resource.type == MediaType.IMAGE and resource.url:
        file_path = Path(resource.url.lstrip("/"))
        if file_path.exists():
            file_path.unlink()

    session.delete(resource)
    session.commit()

    return RedirectResponse(
        url=f"/admin/modules/{post_id}/edit",
        status_code=status.HTTP_303_SEE_OTHER
    )


# ==================== File Upload Helper ====================


@router.post("/upload", dependencies=[Depends(require_admin)])
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return its URL."""
    # Validate file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Save file
    filename = f"{secrets.token_urlsafe(16)}{file_ext}"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"url": f"/static/uploads/{filename}"}
