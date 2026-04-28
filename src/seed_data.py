"""
seed_data.py
------------
Adds demo study tasks to the database.

Use this file for testing and demo purposes.

Run from the project root with:
    python -m src.seed_data
"""

from datetime import date, timedelta

from src import database as db


# ---------------------------------------------------------------------------
# Demo tasks
# ---------------------------------------------------------------------------

TASKS = [
    {
        "title": "Review Linear Algebra Chapter 4",
        "subject": "Mathematics",
        "description": "Focus on eigenvalues, eigenvectors, and diagonalisation.",
        "due_date": (date.today() + timedelta(days=2)).isoformat(),
        "priority": "High",
        "estimated_hours": 3.0,
        "status": "In Progress",
    },
    {
        "title": "Write Essay on Industrial Revolution",
        "subject": "History",
        "description": "2000-word essay using academic sources.",
        "due_date": (date.today() + timedelta(days=5)).isoformat(),
        "priority": "High",
        "estimated_hours": 5.0,
        "status": "Pending",
    },
    {
        "title": "Physics Lab Report Wave Optics",
        "subject": "Physics",
        "description": "Write the double-slit experiment results.",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
        "priority": "High",
        "estimated_hours": 2.5,
        "status": "Pending",
    },
    {
        "title": "Practice Python OOP Exercises",
        "subject": "Computer Science",
        "description": "Complete exercises 7 to 12 from the course workbook.",
        "due_date": (date.today() + timedelta(days=3)).isoformat(),
        "priority": "Medium",
        "estimated_hours": 2.0,
        "status": "Pending",
    },
    {
        "title": "Read Macroeconomics Chapter 9",
        "subject": "Economics",
        "description": "GDP, inflation, and monetary policy summary.",
        "due_date": (date.today() + timedelta(days=4)).isoformat(),
        "priority": "Medium",
        "estimated_hours": 1.5,
        "status": "Pending",
    },
    {
        "title": "Spanish Vocabulary Flashcards",
        "subject": "Languages",
        "description": "Learn 50 new words from Unit 6.",
        "due_date": (date.today() + timedelta(days=7)).isoformat(),
        "priority": "Low",
        "estimated_hours": 1.0,
        "status": "Pending",
    },
    {
        "title": "Statistics Hypothesis Testing Problems",
        "subject": "Mathematics",
        "description": "Practice t-tests and chi-squared tests.",
        "due_date": (date.today() + timedelta(days=6)).isoformat(),
        "priority": "Medium",
        "estimated_hours": 2.5,
        "status": "Pending",
    },
    {
        "title": "CS Algorithm Design Assignment",
        "subject": "Computer Science",
        "description": "Implement Dijkstra algorithm and analyze complexity.",
        "due_date": (date.today() + timedelta(days=10)).isoformat(),
        "priority": "High",
        "estimated_hours": 4.0,
        "status": "Pending",
    },
    {
        "title": "Review Calculus Exam Notes",
        "subject": "Mathematics",
        "description": "Limits, derivatives, and integrals revision.",
        "due_date": (date.today() - timedelta(days=1)).isoformat(),
        "priority": "High",
        "estimated_hours": 3.0,
        "status": "Pending",
    },
    {
        "title": "Biology Cell Division Quiz Prep",
        "subject": "Biology",
        "description": "Mitosis vs meiosis key stages and diagrams.",
        "due_date": (date.today() + timedelta(days=3)).isoformat(),
        "priority": "Medium",
        "estimated_hours": 1.5,
        "status": "Completed",
    },
]


# ---------------------------------------------------------------------------
# Seeder function
# ---------------------------------------------------------------------------

def seed() -> None:
    """Initialize database and insert demo tasks."""
    db.init_db()

    print("Seeding database with demo tasks...")

    for task in TASKS:
        task_id = db.add_task(
            title=task["title"],
            subject=task["subject"],
            description=task["description"],
            due_date=task["due_date"],
            priority=task["priority"],
            estimated_hours=task["estimated_hours"],
        )

        if task["status"] != "Pending":
            db.update_task_status(task_id, task["status"])

    print(f"Done. {len(TASKS)} demo tasks inserted.")


if __name__ == "__main__":
    seed()