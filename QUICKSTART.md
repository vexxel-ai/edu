# Quick Start Guide

Get edu.vexxel running in 2 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Terminal/Command line access

## Start the Application

```bash
# Navigate to project
cd edu

# Start everything (first time will take 2-3 minutes to build)
docker-compose up --build
```

Wait for this message:
```
vexxel_edu_web | INFO:     Application startup complete.
```

## Access the App

Open your browser: **http://localhost:8000**

## Test the Features

1. **Homepage**: See the landing page with features
2. **Browse Courses**: Click to see course listing
3. **Open Course**: Click "Start Learning" on "Introduction to LeetCode"
4. **Test htmx**: Click any lesson in the sidebar → content loads without page refresh
5. **Test Alpine**:
   - Toggle mobile menu (resize browser)
   - Check lesson completion boxes
   - Click "Show/Hide Tips"

## Stop the Application

```bash
# Press Ctrl+C in terminal, then:
docker-compose down
```

## Reset Everything

```bash
# Remove all data and start fresh
docker-compose down -v
docker-compose up --build
```

## Common Issues

**Port 8000 already in use?**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Database connection errors?**
```bash
# Check logs
docker-compose logs db
```

## What's Included?

- ✅ FastAPI backend with 5 API endpoints
- ✅ PostgreSQL database with sample data
- ✅ 1 sample course with 2 lessons
- ✅ Full CRUD for lessons and progress
- ✅ htmx + AlpineJS + Tailwind integration
- ✅ Responsive design (mobile-friendly)

## Next Steps

See `README.md` for:
- Detailed architecture explanation
- How to add new courses
- API endpoint documentation
- Development workflow
- Scaling to production

---

**That's it!** You now have a working educational platform demonstrating modern web technologies.
