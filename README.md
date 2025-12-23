# edu.vexxel - Learn with Purpose

A minimal working example of an educational platform built with modern web technologies focused on backend/infrastructure learning.

## Tech Stack

**Backend:**
- **FastAPI** - Modern Python web framework (async, high-performance)
- **PostgreSQL** - Relational database for user data and progress tracking
- **SQLAlchemy** - ORM for database operations

**Frontend:**
- **htmx** - Dynamic HTML without JavaScript complexity
- **AlpineJS** - Lightweight JavaScript for client-side interactivity
- **TailwindCSS** - Utility-first CSS framework

**Infrastructure:**
- **Docker & Docker Compose** - Containerized development environment
- **Uvicorn** - ASGI server for FastAPI

## Project Structure

```
edu/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & routes
│   │   ├── models.py            # SQLAlchemy database models
│   │   ├── database.py          # Database configuration
│   │   └── templates/           # Jinja2 HTML templates
│   │       ├── base.html        # Base template with htmx/Alpine/Tailwind
│   │       ├── index.html       # Homepage
│   │       ├── courses.html     # Course listing
│   │       └── course_detail.html  # Course detail with lessons
│   ├── Dockerfile               # FastAPI container image
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variables template
├── content/
│   └── courses/
│       └── intro-to-leetcode/
│           ├── metadata.json    # Course metadata
│           ├── lesson-1.md      # Markdown lesson content
│           └── lesson-2.md
├── docker-compose.yml           # Multi-container setup
└── README.md                    # This file
```

## Features Demonstrated

### 1. **htmx in Action**
- Dynamic course loading without page refresh
- Lesson content loaded on-demand
- Seamless navigation between lessons

### 2. **AlpineJS Interactivity**
- Mobile menu toggle
- Lesson completion checkboxes
- Show/hide tips section
- Smooth transitions and animations

### 3. **FastAPI Backend**
- RESTful API endpoints
- Database integration with SQLAlchemy
- Jinja2 template rendering
- Markdown to HTML conversion

### 4. **PostgreSQL Database**
- User accounts
- Course and lesson management
- Progress tracking
- Relational data modeling

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** (to clone the repository)
- **Modern web browser**

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd edu
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the FastAPI application container
   - Start PostgreSQL database
   - Create database tables
   - Load sample course data
   - Start the development server

3. **Access the application:**

   Open your browser and visit: **http://localhost:8000**

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

   To remove volumes (database data):
   ```bash
   docker-compose down -v
   ```

## Usage Guide

### Exploring the Demo

1. **Homepage** (`/`)
   - See the hero section with CTA buttons
   - Features section explaining the platform
   - Courses loaded dynamically via htmx

2. **Course Listing**
   - Click "Browse Courses" to see available courses
   - Sample course: "Introduction to LeetCode"

3. **Course Detail Page**
   - Click "Start Learning" on a course
   - Left sidebar: Lesson list with checkboxes
   - Right panel: Lesson content area
   - Click any lesson to load content (htmx)
   - Check boxes to mark lessons complete (AlpineJS + API)

### Key Interactions to Test

**htmx (Server Communication):**
- Click "Start with Lesson 1" → loads content from server
- Click any lesson in sidebar → fetches content dynamically
- Watch the network tab: only HTML is transferred, no JSON APIs

**AlpineJS (Client-Side):**
- Toggle mobile menu (responsive navbar)
- Check/uncheck lesson completion boxes
- Click "Show/Hide Tips" button
- Notice smooth transitions and instant feedback

**TailwindCSS:**
- Responsive design (try resizing browser)
- Hover effects on buttons and cards
- Consistent spacing and colors

## Architecture Highlights

### How htmx + AlpineJS Work Together

```html
<!-- Example: Lesson with htmx (server) + Alpine (client) -->
<div x-data="{ completed: false }">
  <!-- htmx: Fetch content from server -->
  <button
    hx-get="/lessons/1/content"
    hx-target="#lesson-content"
    class="lesson-btn"
  >
    <!-- Alpine: Client-side checkbox toggle -->
    <input
      type="checkbox"
      x-model="completed"
      @change="fetch('/lessons/1/complete', { method: 'POST' })"
    />
    <span>Lesson Title</span>
  </button>
</div>
```

**Division of responsibility:**
- **htmx**: Load lesson content, navigate pages, submit forms
- **Alpine**: Toggle UI elements, manage local state, animations
- **Tailwind**: Style everything consistently

### Database Schema

**Users** → Track learners
- `id`, `email`, `username`, `created_at`

**Courses** → Educational content
- `id`, `slug`, `title`, `description`, `goal`

**Lessons** → Course chapters
- `id`, `course_id`, `slug`, `title`, `content`, `order`

**Progress** → Track completion
- `id`, `user_id`, `lesson_id`, `completed`, `completed_at`

## Development Workflow

### Adding a New Course

1. **Create course directory:**
   ```bash
   mkdir content/courses/your-course-slug
   ```

2. **Add metadata.json:**
   ```json
   {
     "slug": "your-course-slug",
     "title": "Your Course Title",
     "description": "Course description",
     "goal": "Learning goal",
     "lessons": [
       {"slug": "lesson-1", "title": "Lesson 1", "file": "lesson-1.md"}
     ]
   }
   ```

3. **Create lesson files:**
   ```bash
   touch content/courses/your-course-slug/lesson-1.md
   ```

4. **Restart the application:**
   ```bash
   docker-compose restart web
   ```

### Modifying the Frontend

- **Templates** are in `backend/app/templates/`
- Edit HTML files and refresh the browser
- Changes are reflected immediately (hot reload enabled)

### Modifying the Backend

- **Python files** are in `backend/app/`
- Changes trigger automatic reload (Uvicorn `--reload` flag)
- Watch the terminal for reload confirmations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage |
| GET | `/courses` | List all courses |
| GET | `/courses/{slug}` | Course detail page |
| GET | `/lessons/{id}/content` | Get lesson content (htmx) |
| POST | `/lessons/{id}/complete` | Mark lesson complete/incomplete |
| GET | `/health` | Health check |

## What's Next?

This minimal example demonstrates the core architecture. To build the full platform, you would add:

### Authentication (Week 3-4)
- Integrate Supabase Auth or AWS Cognito
- User registration and login
- Protected routes
- Session management

### Progress Tracking (Week 5-6)
- User dashboard with progress overview
- Course enrollment system
- Completion certificates
- Analytics

### Content Management (Week 7-8)
- Admin panel for course creation
- PDF upload and storage (S3)
- Video integration (YouTube API)
- Jupyter notebook rendering

### Infrastructure (Ongoing)
- Terraform for AWS deployment
- CI/CD pipeline (GitHub Actions)
- Monitoring and logging (Sentry, CloudWatch)
- Caching layer (Redis)

## Troubleshooting

**Database connection errors:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db
```

**Port already in use:**
```bash
# Stop any services using port 8000 or 5432
lsof -ti:8000 | xargs kill -9
lsof -ti:5432 | xargs kill -9
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up --build
```

## Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **htmx**: https://htmx.org/examples/
- **AlpineJS**: https://alpinejs.dev/start-here
- **TailwindCSS**: https://tailwindcss.com/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org/

## Project Goals

This minimal example serves to:

1. ✅ Demonstrate htmx + AlpineJS + TailwindCSS integration
2. ✅ Show FastAPI backend with database
3. ✅ Prove the architecture works for educational content
4. ✅ Provide a foundation for scaling to production

**Built by vexxel.ai** - Delivering cool solutions, making great projects, spreading knowledge.
