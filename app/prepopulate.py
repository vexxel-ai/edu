"""
Prepopulate the database with sample data for development/testing.
"""
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, select

from app.db import engine
from app.models import User, Course, Lesson, Progress


def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def prepopulate_db(session: Session) -> None:
    """Prepopulate the database with sample data."""

    # Check if data already exists
    existing_courses = session.exec(select(Course)).first()
    if existing_courses:
        print("Database already contains data. Skipping prepopulation.")
        return

    # Create sample users
    user1 = User(email="alice@example.com", supabase_id="demo-user-1")
    user2 = User(email="bob@example.com", supabase_id="demo-user-2")

    session.add(user1)
    session.add(user2)
    session.commit()
    print(f"Created 2 users: {user1.email}, {user2.email}")

    # Create sample courses
    dsa_course = Course(
        title="Data Structures & Algorithms",
        description="Master the fundamentals of DSA to ace technical interviews at top tech companies."
    )

    system_design_course = Course(
        title="System Design Fundamentals",
        description="Learn how to design scalable, distributed systems like a senior engineer."
    )

    session.add(dsa_course)
    session.add(system_design_course)
    session.commit()
    print(f"Created 2 courses: {dsa_course.title}, {system_design_course.title}")

    # Create lessons for DSA course
    dsa_lessons = [
        Lesson(
            course_id=dsa_course.uuid,
            slug="intro-to-arrays",
            title="Introduction to Arrays",
            content="# Arrays\n\nArrays are fundamental data structures that store elements in contiguous memory...",
            order=1
        ),
        Lesson(
            course_id=dsa_course.uuid,
            slug="linked-lists-basics",
            title="Linked Lists Basics",
            content="# Linked Lists\n\nLinked lists are dynamic data structures where elements are connected via pointers...",
            order=2
        ),
        Lesson(
            course_id=dsa_course.uuid,
            slug="stacks-and-queues",
            title="Stacks and Queues",
            content="# Stacks and Queues\n\nLearn about LIFO and FIFO data structures...",
            order=3
        ),
        Lesson(
            course_id=dsa_course.uuid,
            slug="binary-trees",
            title="Binary Trees",
            content="# Binary Trees\n\nTrees are hierarchical data structures with nodes and edges...",
            order=4
        ),
        Lesson(
            course_id=dsa_course.uuid,
            slug="graph-algorithms",
            title="Graph Algorithms",
            content="# Graphs\n\nGraphs represent relationships between entities using vertices and edges...",
            order=5
        ),
    ]

    # Create lessons for System Design course
    system_design_lessons = [
        Lesson(
            course_id=system_design_course.uuid,
            slug="scalability-basics",
            title="Scalability Fundamentals",
            content="# Scalability\n\nLearn the basics of horizontal and vertical scaling...",
            order=1
        ),
        Lesson(
            course_id=system_design_course.uuid,
            slug="load-balancing",
            title="Load Balancing",
            content="# Load Balancing\n\nDistribute traffic across multiple servers...",
            order=2
        ),
        Lesson(
            course_id=system_design_course.uuid,
            slug="caching-strategies",
            title="Caching Strategies",
            content="# Caching\n\nImprove performance with effective caching strategies...",
            order=3
        ),
        Lesson(
            course_id=system_design_course.uuid,
            slug="database-design",
            title="Database Design",
            content="# Database Design\n\nChoosing between SQL and NoSQL databases...",
            order=4
        ),
    ]

    for lesson in dsa_lessons + system_design_lessons:
        session.add(lesson)

    session.commit()
    print(f"Created {len(dsa_lessons)} lessons for DSA course")
    print(f"Created {len(system_design_lessons)} lessons for System Design course")

    # Create some progress records for user1
    progress_records = [
        Progress(
            user_id=user1.uuid,
            lesson_id=dsa_lessons[0].uuid,
            completed=True,
            completed_at=datetime.now(timezone.utc)
        ),
        Progress(
            user_id=user1.uuid,
            lesson_id=dsa_lessons[1].uuid,
            completed=True,
            completed_at=datetime.now(timezone.utc)
        ),
        Progress(
            user_id=user1.uuid,
            lesson_id=dsa_lessons[2].uuid,
            completed=False
        ),
    ]

    for progress in progress_records:
        session.add(progress)

    session.commit()
    print(f"Created {len(progress_records)} progress records for user1")
    print("\n✅ Database prepopulation completed successfully!")


def main():
    """Main function to run prepopulation."""
    print("Creating tables...")
    create_tables()

    print("\nPrepopulating database with sample data...")
    with Session(engine) as session:
        prepopulate_db(session)


if __name__ == "__main__":
    main()