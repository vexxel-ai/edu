"""
Initial database setup for edu.vexxel.ai multi-user platform.

This script:
1. Creates all database tables from scratch
2. Creates super admin user in Supabase
3. Syncs super admin to local database
4. Verifies setup completed successfully

Run this once when setting up the project for the first time.

⚠️  WARNING: This will DROP ALL TABLES if they exist!
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, select, text

from app.auth.supabase_client import get_supabase_client, settings
from app.database import engine
from app.models import (
    PendingTag,
    Post,
    SQLModel,
    Tag,
    TagActivity,
    User,
    UserRole,
)


def reset_database():
    """Drop all existing tables and recreate from scratch."""
    print("Resetting database (dropping all tables)...")
    SQLModel.metadata.drop_all(engine)
    print("✓ All tables dropped")

    print("Creating tables from scratch...")
    SQLModel.metadata.create_all(engine)
    print("✓ All tables created successfully")


def create_super_admin(session: Session) -> User:
    """
    Create super admin user in both Supabase and local database.

    Args:
        session: Database session

    Returns:
        Created super admin user
    """
    print(f"\nCreating super admin user: {settings.super_admin_email}")

    # Check if super admin already exists in local DB
    existing_user = session.exec(
        select(User).where(User.email == settings.super_admin_email)
    ).first()
    if existing_user:
        print(f"✓ Super admin already exists with ID: {existing_user.id}")
        return existing_user

    try:
        # Create user in Supabase Auth
        supabase = get_supabase_client()
        print("  - Creating user in Supabase...")

        auth_response = supabase.auth.admin.create_user(
            {
                "email": settings.super_admin_email,
                "password": settings.super_admin_password,
                "email_confirm": True,  # Auto-confirm email
            }
        )

        if not auth_response.user:
            raise Exception("Failed to create user in Supabase")

        print(f"  - Supabase user created with ID: {auth_response.user.id}")

        # Create user in local database
        user = User(
            supabase_id=auth_response.user.id,
            email=settings.super_admin_email,
            full_name="Super Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"✓ Super admin created successfully with ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Password: {settings.super_admin_password}")
        print("  ⚠️  IMPORTANT: Change this password in production!")

        return user

    except Exception as e:
        print(f"✗ Failed to create super admin: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that Supabase credentials in .env are correct")
        print("2. Verify Supabase project is active")
        print(
            "3. Check that SUPABASE_JWT_SECRET matches your Supabase project settings"
        )
        print("4. For manual creation, use Supabase dashboard and sync to local DB")
        raise




def verify_migration(session: Session):
    """
    Verify that setup completed successfully.

    Args:
        session: Database session

    Returns:
        True if verification passed, False otherwise
    """
    print("\nVerifying setup...")

    errors = []

    # Check super admin exists
    admin = session.exec(select(User).where(User.role == UserRole.ADMIN)).first()
    if not admin:
        errors.append("No admin user found")
    else:
        print(f"✓ Admin user found: {admin.email}")

    # Check tables exist
    try:
        session.exec(select(User)).first()
        print("✓ User table accessible")
    except Exception as e:
        errors.append(f"User table error: {str(e)}")

    try:
        session.exec(select(PendingTag)).first()
        print("✓ PendingTag table accessible")
    except Exception as e:
        errors.append(f"PendingTag table error: {str(e)}")

    try:
        session.exec(select(TagActivity)).first()
        print("✓ TagActivity table accessible")
    except Exception as e:
        errors.append(f"TagActivity table error: {str(e)}")

    if errors:
        print("\n✗ Setup verification failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("\n✓ Setup verification passed!")
    return True


def main():
    """Run the initial database setup."""
    print("=" * 60)
    print("Initial Database Setup")
    print("=" * 60)

    # Check environment variables
    print("\nChecking environment variables...")
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"\n✗ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these in your .env file:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_ANON_KEY=your-anon-key")
        print("  SUPABASE_JWT_SECRET=your-jwt-secret")
        print("\nYou can find these in your Supabase project settings:")
        print("  https://app.supabase.com/project/_/settings/api")
        sys.exit(1)

    print("✓ Environment variables found")

    # Confirm before proceeding
    print("\n" + "=" * 60)
    print("⚠️  WARNING: This will:")
    print("  1. DROP ALL EXISTING TABLES (if any)")
    print("  2. Create fresh database schema")
    print("  3. Create super admin user in Supabase and local DB")
    print("=" * 60)

    response = input("\n⚠️  Are you sure? Type 'SETUP' to proceed: ")
    if response != "SETUP":
        print("Setup cancelled")
        sys.exit(0)

    try:
        with Session(engine) as session:
            # Step 1: Reset database (drop and recreate all tables)
            reset_database()

            # Step 2: Create super admin
            admin_user = create_super_admin(session)

            # Step 3: Verify setup
            if verify_migration(session):
                print("\n" + "=" * 60)
                print("✓ Database setup completed successfully!")
                print("=" * 60)
                print("\nNext steps:")
                print("  1. Start services: docker-compose up")
                print("  2. Or use: make up")
                print("  3. Visit: http://localhost:8000/docs")
                print("  4. Sign in with:")
                print(f"     Email: {settings.super_admin_email}")
                print(f"     Password: {settings.super_admin_password}")
                print("  5. Change password in production!")
                print("=" * 60)
            else:
                print("\n✗ Setup completed with warnings")
                print("Please review the errors above and fix manually if needed")
                sys.exit(1)

    except Exception as e:
        print(f"\n✗ Setup failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
