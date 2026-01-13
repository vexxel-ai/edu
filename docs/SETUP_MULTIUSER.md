# Multi-User Platform Setup Guide

This guide covers the setup and configuration of the new multi-user authentication system with role-based access control.

## Overview

The platform now supports:
- **Multi-user authentication** via Supabase Auth
- **Three user roles**: Admin, Sub-Admin, and User
- **Tag approval workflow**: Users request tags, admins approve
- **User management**: Admin dashboard for managing users and roles
- **Analytics**: GitHub-like contribution tracking for tags

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI App                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  Auth Routes    (/auth)                       │  │
│  │  - signup, signin, signout, me, refresh       │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Tag Routes     (/tags)                       │  │
│  │  - request, approve, reject, create-direct    │  │
│  ├───────────────────────────────────────────────┤  │
│  │  User Routes    (/users)                      │  │
│  │  - list, get, update role, deactivate         │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Analytics      (/analytics)                  │  │
│  │  - tag activity, top tags, top contributors   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
           │                           │
           v                           v
    ┌─────────────┐            ┌──────────────┐
    │  Supabase   │            │   SQLite     │
    │    Auth     │            │   Database   │
    │   (JWT)     │            │              │
    └─────────────┘            │  - User      │
                               │  - Post      │
                               │  - Tag       │
                               │  - PendingTag│
                               │  - TagActivity│
                               └──────────────┘
```

## Prerequisites

1. **Supabase Account**
   - Sign up at https://supabase.com
   - Create a new project
   - Note your project URL, anon key, and JWT secret

2. **Python 3.10+**
   - Install from https://python.org or use `pyenv`

3. **uv Package Manager** (recommended)
   - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Step 1: Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
uv sync
```

New dependencies added:
- `pyjwt>=2.10.1` - JWT token validation
- `supabase>=2.24.0` - Already installed, now used for auth

## Step 2: Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Super Admin Configuration
SUPER_ADMIN_EMAIL=admin@vexxel.ai
SUPER_ADMIN_PASSWORD=change-this-in-production

# Database
DATABASE_URL=sqlite:///./database.db
```

### Finding Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
4. Navigate to **Settings** → **API** → **JWT Settings**
5. Copy **JWT Secret** → `SUPABASE_JWT_SECRET`

## Step 3: Run Migration

⚠️  **WARNING**: This will delete all existing data!

```bash
python migrations/migrate_to_multiuser.py
```

The migration will:
1. Drop all existing tables
2. Create fresh database schema with all new tables
3. Create super admin user in Supabase and local DB
4. Verify the migration completed successfully

When prompted, type `RESET` to confirm.

Expected output:
```
============================================================
Multi-User Platform Migration
============================================================

Checking environment variables...
✓ Environment variables found

⚠️  WARNING: This migration will:
  1. DROP ALL EXISTING TABLES (all data will be lost!)
  2. Create fresh database schema with new tables
  3. Create super admin user in Supabase and local DB
============================================================

⚠️  Are you sure? Type 'RESET' to proceed: RESET

Resetting database (dropping all tables)...
✓ All tables dropped
Creating tables from scratch...
✓ All tables created successfully

Creating super admin user: admin@vexxel.ai
  - Creating user in Supabase...
  - Supabase user created with ID: xxx-xxx-xxx
✓ Super admin created successfully with ID: 1
  Email: admin@vexxel.ai
  Password: change-this-in-production
  ⚠️  IMPORTANT: Change this password in production!

Verifying migration...
✓ Admin user found: admin@vexxel.ai
✓ User table accessible
✓ PendingTag table accessible
✓ TagActivity table accessible

✓ Migration verification passed!

============================================================
✓ Migration completed successfully!
============================================================

Next steps:
  1. Start the server: uvicorn app.main:app --reload
  2. Sign in with super admin credentials
     Email: admin@vexxel.ai
     Password: change-this-in-production
  3. Change the super admin password in production!
  4. Create additional admin/sub-admin users as needed
  5. Optionally run seed.py to add sample data
============================================================
```

## Step 4: Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 5: Test Authentication

### Sign In as Super Admin

```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vexxel.ai",
    "password": "change-this-in-production"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@vexxel.ai",
    "full_name": "Super Administrator",
    "role": "admin",
    "is_active": true
  }
}
```

Save the `access_token` for authenticated requests.

### Create a New User

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password",
    "full_name": "John Doe"
  }'
```

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/signin` | Sign in with email/password | No |
| POST | `/auth/signout` | Sign out current user | No |
| GET | `/auth/me` | Get current user info | Yes |
| POST | `/auth/refresh` | Refresh access token | No |

### Tags (`/tags`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/tags/request` | Request new tag/subtag | Yes | User |
| GET | `/tags/my-requests` | View own tag requests | Yes | User |
| GET | `/tags/pending` | List pending tag requests | Yes | Sub-Admin+ |
| POST | `/tags/approve/{id}` | Approve/reject tag request | Yes | Sub-Admin+ |
| POST | `/tags/create-direct` | Create tag without approval | Yes | Sub-Admin+ |

### Users (`/users`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/users` | List all users (paginated) | Yes | Admin |
| GET | `/users/{id}` | Get user details | Yes | Admin |
| PATCH | `/users/{id}/role` | Update user role | Yes | Admin |
| PATCH | `/users/{id}/status` | Activate/deactivate user | Yes | Admin |
| DELETE | `/users/{id}` | Delete user (soft delete) | Yes | Admin |
| GET | `/users/stats/summary` | Get user statistics | Yes | Admin |

### Analytics (`/analytics`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/analytics/tags/{id}/activity` | Tag activity over time | Optional |
| GET | `/analytics/tags/top` | Most active tags | Optional |
| GET | `/analytics/contributors/top` | Top contributors | Optional |
| GET | `/analytics/tags/stats` | Overall tag statistics | Optional |

## User Roles & Permissions

### Admin
- Full system access
- Manage users (create, update roles, deactivate)
- Approve/reject tag requests
- Create tags directly
- Create and publish posts

### Sub-Admin
- Approve/reject tag requests
- Create tags directly
- Create and publish posts
- Cannot manage users

### User
- Create and publish posts
- Request new tags (requires approval)
- View own content and tag requests

## Workflow: Tag Approval

### As a User:

1. **Request a new tag**:
```bash
curl -X POST http://localhost:8000/tags/request \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Information Theory",
    "slug": "information-theory",
    "parent_id": null
  }'
```

2. **Check request status**:
```bash
curl -X GET http://localhost:8000/tags/my-requests \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### As a Sub-Admin/Admin:

1. **View pending requests**:
```bash
curl -X GET http://localhost:8000/tags/pending \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. **Approve a request**:
```bash
curl -X POST http://localhost:8000/tags/approve/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true
  }'
```

3. **Reject a request**:
```bash
curl -X POST http://localhost:8000/tags/approve/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "rejection_reason": "Too generic, please be more specific"
  }'
```

## Database Schema

### New Tables

**User**
- `id` (Primary Key)
- `supabase_id` (Unique, links to Supabase Auth)
- `email` (Unique)
- `full_name`
- `role` (admin | sub_admin | user)
- `is_active`
- `created_at`

**PendingTag**
- `id` (Primary Key)
- `name`, `slug`, `parent_id`
- `requested_by_id` → User
- `status` (pending | approved | rejected)
- `reviewed_by_id` → User
- `reviewed_at`
- `rejection_reason`
- `created_at`

**TagActivity**
- `id` (Primary Key)
- `tag_id` → Tag
- `date`
- `post_count`
- `contributor_count`
- `created_at`

### Updated Tables

**Post**
- Added: `author_id` → User (nullable for backward compatibility)

## Troubleshooting

### Migration fails with "Invalid token" error
- Verify `SUPABASE_JWT_SECRET` matches your Supabase project settings
- Check that you copied the JWT Secret, not the anon key

### "User not found in database" after sign in
- The user exists in Supabase but not in local DB
- This should auto-sync on sign in, but you can manually create:
```python
# In Python shell
from app.database import engine
from app.models import User, UserRole
from sqlmodel import Session

with Session(engine) as session:
    user = User(
        supabase_id="user-supabase-id",
        email="user@example.com",
        role=UserRole.USER,
        is_active=True
    )
    session.add(user)
    session.commit()
```

### Cannot approve tags
- Verify your user role is `sub_admin` or `admin`
- Check the JWT token is valid and not expired
- Ensure `Authorization: Bearer TOKEN` header is present

## Next Steps

1. **Update Admin UI** (Phase 7)
   - Create login/signup pages
   - Add user management dashboard
   - Build tag approval interface
   - Add analytics visualizations

2. **Testing** (Phase 9)
   - Write unit tests for auth flows
   - Test role-based access control
   - Test tag approval workflow
   - Integration tests with Supabase

3. **Production Deployment**
   - Set up Supabase production project
   - Configure environment variables
   - Set up proper secrets management
   - Enable Supabase email verification
   - Configure OAuth providers (optional)
   - Set up monitoring and logging

## Support

For issues or questions:
- Check the FastAPI docs at http://localhost:8000/docs
- Review Supabase Auth documentation
- Check the GitHub repository issues

---

**Built with FastAPI, Supabase, and SQLModel**
