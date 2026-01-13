"""
Tests for main application routes.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Post, Tag


def test_homepage(client: TestClient):
    """Test homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "edu.vexxel.ai" in response.text or "vexxel" in response.text.lower()


def test_modules_page(client: TestClient):
    """Test modules page loads successfully."""
    response = client.get("/modules")
    assert response.status_code == 200


def test_module_detail_not_found(client: TestClient):
    """Test module detail returns 404 for non-existent module."""
    response = client.get("/modules/non-existent-slug")
    assert response.status_code == 404


def test_render_markdown():
    """Test markdown rendering helper function."""
    from app.main import render_markdown

    # Test basic markdown
    result = render_markdown("# Hello World")
    assert "<h1>Hello World</h1>" in result

    # Test code block
    result = render_markdown("```python\nprint('hello')\n```")
    assert "codehilite" in result or "fenced" in result or "print" in result

    # Test empty string
    result = render_markdown("")
    assert result == ""


def test_sort_media_assets():
    """Test media assets sorting helper function."""
    from app.main import sort_media_assets
    from app.models import MediaAsset, MediaType

    # Create test assets
    assets = [
        MediaAsset(id=1, post_id=1, type=MediaType.IMAGE, order=2, url="/test1.jpg"),
        MediaAsset(id=2, post_id=1, type=MediaType.SLIDE, order=1, url="/test2"),
        MediaAsset(id=3, post_id=1, type=MediaType.YOUTUBE, order=3, url="/test3"),
    ]

    sorted_assets = sort_media_assets(assets)

    # Check structure
    assert "images" in sorted_assets
    assert "slides" in sorted_assets
    assert "youtube" in sorted_assets
    assert "blog_links" in sorted_assets
    assert "html" in sorted_assets

    # Check sorting by order
    assert len(sorted_assets["slides"]) == 1
    assert len(sorted_assets["images"]) == 1
    assert len(sorted_assets["youtube"]) == 1


def test_hierarchical_tags(session: Session):
    """Test hierarchical tags helper function."""
    from app.main import get_hierarchical_tags

    # Create test tags
    parent_tag = Tag(name="Parent", slug="parent")
    session.add(parent_tag)
    session.commit()
    session.refresh(parent_tag)

    child_tag = Tag(name="Child", slug="child", parent_id=parent_tag.id)
    session.add(child_tag)
    session.commit()

    # Get hierarchical structure
    hierarchical = get_hierarchical_tags(session)

    assert len(hierarchical) > 0
    assert hierarchical[0]["tag"].name == "Parent"
    assert len(hierarchical[0]["children"]) == 1
    assert hierarchical[0]["children"][0].name == "Child"
