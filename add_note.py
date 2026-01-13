"""
Quick script to add example_x.jpg as a note to an existing module.
"""

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import MediaAsset, MediaType, Post


def add_example_note():
    """Add the example handwritten note to an existing module."""
    with Session(engine) as session:
        # Get all posts to see what's available
        posts = session.exec(select(Post)).all()

        if not posts:
            print("❌ No posts found! Run seed.py first to create sample modules.")
            return

        # List available posts
        print("\nAvailable modules:")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.title} ({post.slug})")

        # Add to the first post (you can change this)
        post = posts[0]

        print(f"\n✨ Adding handwritten note to: '{post.title}'")

        # Create the media asset
        note_image = MediaAsset(
            title="Books on Shelves Problem",
            type=MediaType.IMAGE,
            url="/static/uploads/example_x.jpg",
            order=len(post.media_assets) + 1,  # Add at the end
            post_id=post.id
        )

        session.add(note_image)
        session.commit()

        print(f"✅ Added handwritten note successfully!")
        print(f"📝 View at: http://localhost:8000/modules/{post.slug}")


if __name__ == "__main__":
    print("🔧 Setting up database...")
    create_db_and_tables()

    print("📸 Adding example note to module...")
    add_example_note()
