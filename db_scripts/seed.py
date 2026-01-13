"""
Seed script to populate the database with sample data.

This script reads post examples from the posts_examples/ folder and creates:
- Sections (top-level categories)
- Subsections (second-level categories within sections)
- Posts with markdown content loaded from external files
- Various media assets (slides, images, YouTube links, blog links)
- Optional tags for filtering

Each post example folder should contain:
- content.md: The markdown content for the post
- metadata.json: Post metadata including title, slug, section, subsection, tags, and media assets

Run this script to populate the database:
    python migrations_scripts/seed.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import MediaAsset, MediaType, Post, PostTag, Section, Subsection, Tag


def create_sections_and_subsections(session: Session) -> tuple[dict[str, Section], dict[tuple[str, str], Subsection]]:
    """
    Create sections and subsections.

    Returns:
        Tuple of (section_slug_map, subsection_key_map)
        where subsection_key_map uses (section_slug, subsection_slug) as key
    """
    sections_data = [
        {
            "name": "Reinforcement Learning",
            "slug": "reinforcement-learning",
            "description": "Learning through interaction with an environment",
        },
        {
            "name": "Deep Learning",
            "slug": "deep-learning",
            "description": "Neural networks and deep architectures",
        },
        {
            "name": "Algorithms",
            "slug": "algorithms",
            "description": "Fundamental algorithms and data structures",
        },
        {
            "name": "Computer Science",
            "slug": "computer-science",
            "description": "Core computer science concepts",
        },
        {
            "name": "Leetcode",
            "slug": "leetcode",
            "description": "Coding interview problems and patterns",
        },
    ]

    subsections_data = [
        # Reinforcement Learning subsections
        {
            "name": "The RL Problem",
            "slug": "the-rl-problem",
            "section_slug": "reinforcement-learning",
            "description": "Understanding the reinforcement learning problem",
        },
        {
            "name": "Q-Learning",
            "slug": "q-learning",
            "section_slug": "reinforcement-learning",
            "description": "Q-learning and value-based methods",
        },
        {
            "name": "Policy Gradients",
            "slug": "policy-gradients",
            "section_slug": "reinforcement-learning",
            "description": "Policy gradient methods",
        },
        # Deep Learning subsections
        {
            "name": "Graph Neural Networks",
            "slug": "graph-neural-networks",
            "section_slug": "deep-learning",
            "description": "Neural networks for graph-structured data",
        },
        {
            "name": "CNNs",
            "slug": "cnns",
            "section_slug": "deep-learning",
            "description": "Convolutional Neural Networks",
        },
        # Algorithms subsections
        {
            "name": "Dynamic Programming",
            "slug": "dynamic-programming",
            "section_slug": "algorithms",
            "description": "Dynamic programming techniques",
        },
        {
            "name": "Greedy Algorithms",
            "slug": "greedy-algorithms",
            "section_slug": "algorithms",
            "description": "Greedy algorithmic approaches",
        },
        # Computer Science subsections
        {
            "name": "Theory",
            "slug": "theory",
            "section_slug": "computer-science",
            "description": "Theoretical computer science",
        },
        # Leetcode subsections
        {
            "name": "Dynamic Programming",
            "slug": "dynamic-programming-leetcode",
            "section_slug": "leetcode",
            "description": "DP patterns for coding interviews",
        },
        {
            "name": "Sorting & Searching",
            "slug": "sorting-searching",
            "section_slug": "leetcode",
            "description": "Sorting and searching problem patterns",
        },
        {
            "name": "General Patterns",
            "slug": "general-patterns",
            "section_slug": "leetcode",
            "description": "Common problem-solving patterns",
        },
    ]

    # Create sections
    section_slug_map = {}
    for section_data in sections_data:
        section = Section(
            name=section_data["name"],
            slug=section_data["slug"],
            description=section_data["description"],
        )
        session.add(section)
        session.commit()
        session.refresh(section)
        section_slug_map[section.slug] = section

    print(f"✅ Created {len(section_slug_map)} sections")

    # Create subsections
    subsection_key_map = {}
    for subsection_data in subsections_data:
        section_slug = subsection_data["section_slug"]
        if section_slug not in section_slug_map:
            print(f"⚠️  Warning: Section '{section_slug}' not found for subsection '{subsection_data['name']}'")
            continue

        section = section_slug_map[section_slug]
        subsection = Subsection(
            name=subsection_data["name"],
            slug=subsection_data["slug"],
            section_id=section.id,
            description=subsection_data["description"],
        )
        session.add(subsection)
        session.commit()
        session.refresh(subsection)

        # Key is (section_slug, subsection_slug) for lookups
        subsection_key_map[(section_slug, subsection.slug)] = subsection

    print(f"✅ Created {len(subsection_key_map)} subsections")

    return section_slug_map, subsection_key_map


def create_tags(session: Session) -> dict[str, Tag]:
    """
    Create optional flat tags for filtering.

    Tags don't have hierarchy and don't require approval.
    """
    tags_data = [
        {"name": "Neural Networks", "slug": "neural-networks"},
        {"name": "Optimization", "slug": "optimization"},
        {"name": "Python", "slug": "python"},
        {"name": "Theory", "slug": "theory"},
        {"name": "Practice", "slug": "practice"},
        {"name": "Hash Map", "slug": "hash-map"},
        {"name": "Arrays", "slug": "arrays"},
        {"name": "Dynamic Programming", "slug": "dynamic-programming"},
        {"name": "Binary Search", "slug": "binary-search"},
        {"name": "Intervals", "slug": "intervals"},
        {"name": "Sorting", "slug": "sorting"},
    ]

    tag_slug_map = {}
    for tag_data in tags_data:
        tag = Tag(
            name=tag_data["name"],
            slug=tag_data["slug"],
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
        tag_slug_map[tag.slug] = tag

    print(f"✅ Created {len(tag_slug_map)} tags")
    return tag_slug_map


def load_post_from_folder(folder_path: Path) -> dict:
    """
    Load post content and metadata from a folder.

    Args:
        folder_path: Path to the post example folder

    Returns:
        Dictionary with 'content' (markdown string) and 'metadata' (dict)
    """
    content_file = folder_path / "content.md"
    metadata_file = folder_path / "metadata.json"

    if not content_file.exists():
        raise FileNotFoundError(f"Content file not found: {content_file}")
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

    # Read markdown content
    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Read metadata JSON
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return {"content": content, "metadata": metadata}


def create_post_from_data(
    session: Session,
    post_data: dict,
    section_slug_map: dict[str, Section],
    subsection_key_map: dict[tuple[str, str], Subsection],
    tag_slug_map: dict[str, Tag],
) -> Post:
    """
    Create a post with media assets from loaded data.

    Args:
        session: Database session
        post_data: Dictionary with 'content' and 'metadata'
        section_slug_map: Mapping of section slugs to Section objects
        subsection_key_map: Mapping of (section_slug, subsection_slug) to Subsection objects
        tag_slug_map: Mapping of tag slugs to Tag objects

    Returns:
        Created Post object
    """
    metadata = post_data["metadata"]
    content = post_data["content"]

    # Get required section and subsection
    section_slug = metadata.get("section")
    subsection_slug = metadata.get("subsection")

    if not section_slug:
        raise ValueError(f"Post '{metadata['title']}' is missing required 'section' field")
    if not subsection_slug:
        raise ValueError(f"Post '{metadata['title']}' is missing required 'subsection' field")

    if section_slug not in section_slug_map:
        raise ValueError(f"Section '{section_slug}' not found for post '{metadata['title']}'")

    subsection_key = (section_slug, subsection_slug)
    if subsection_key not in subsection_key_map:
        raise ValueError(
            f"Subsection '{subsection_slug}' not found in section '{section_slug}' "
            f"for post '{metadata['title']}'"
        )

    section = section_slug_map[section_slug]
    subsection = subsection_key_map[subsection_key]

    # Create post (approved by default for seed data)
    post = Post(
        title=metadata["title"],
        slug=metadata["slug"],
        description=content,
        section_id=section.id,
        subsection_id=subsection.id,
        is_approved=True,  # Seed data is pre-approved
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    # Add optional tags
    for tag_slug in metadata.get("tags", []):
        if tag_slug in tag_slug_map:
            session.add(PostTag(post_id=post.id, tag_id=tag_slug_map[tag_slug].id))
        else:
            print(f"⚠️  Warning: Tag '{tag_slug}' not found for post '{metadata['title']}'")

    # Add media assets
    for asset_data in metadata.get("media_assets", []):
        media_type = MediaType(asset_data["type"])

        # Create media asset
        # For code_snippet and exercise: content field stores the code/markdown
        # For code_snippet: url field stores the language (e.g., "python", "javascript")
        # For other types: url field stores the actual URL
        media_asset = MediaAsset(
            post_id=post.id,
            type=media_type,
            url=asset_data.get("url") or asset_data.get("language"),
            content=asset_data.get("content"),
            title=asset_data.get("title"),
            order=asset_data.get("order", 0),
        )
        session.add(media_asset)

    session.commit()
    print(f"✅ Created post: {metadata['title']}")
    return post


def create_posts_from_examples(
    session: Session,
    section_slug_map: dict[str, Section],
    subsection_key_map: dict[tuple[str, str], Subsection],
    tag_slug_map: dict[str, Tag],
) -> None:
    """
    Load and create all posts from the posts_examples folder.

    Args:
        session: Database session
        section_slug_map: Mapping of section slugs to Section objects
        subsection_key_map: Mapping of (section_slug, subsection_slug) to Subsection objects
        tag_slug_map: Mapping of tag slugs to Tag objects
    """
    examples_dir = Path(__file__).parent / "posts_examples"

    if not examples_dir.exists():
        print(f"⚠️  Posts examples directory not found: {examples_dir}")
        return

    # Get all subdirectories in posts_examples
    post_folders = [
        d for d in examples_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]

    # Filter out example_notes folder
    post_folders = [d for d in post_folders if d.name != "example_notes"]

    if not post_folders:
        print("⚠️  No post example folders found")
        return

    print(f"📝 Found {len(post_folders)} post example(s)")

    for post_folder in sorted(post_folders):
        try:
            post_data = load_post_from_folder(post_folder)
            create_post_from_data(
                session, post_data, section_slug_map, subsection_key_map, tag_slug_map
            )
        except Exception as e:
            print(f"✗ Failed to load post from {post_folder.name}: {e}")


def main():
    """Main seeding function."""
    print("🌱 Starting database seed...")

    # Create tables
    print("📋 Creating database tables...")
    create_db_and_tables()

    with Session(engine) as session:
        # Check if data already exists
        existing_posts = session.exec(select(Post)).first()
        if existing_posts:
            print("⚠️  Database already contains data. Skipping seed.")
            print("   To reseed, run: make db-reset")
            return

        # Create sections and subsections
        print("\n🏷️  Creating sections and subsections...")
        section_slug_map, subsection_key_map = create_sections_and_subsections(session)

        # Create optional tags
        print("\n🔖 Creating optional tags...")
        tag_slug_map = create_tags(session)

        # Create posts from examples folder
        print("\n📝 Loading posts from examples...")
        create_posts_from_examples(session, section_slug_map, subsection_key_map, tag_slug_map)

    print("\n✨ Database seeding completed!")


if __name__ == "__main__":
    main()
