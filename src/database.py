"""
database.py
-----------
Database access layer for the Study Planner app.

This file:
- Creates the SQLite database automatically.
- Stores the database inside data/study_planner.db.
- Provides CRUD functions.
- Provides search, filter, sort, and dashboard statistics helpers.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "study_planner.db"


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create the tasks table if it does not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT DEFAULT '',
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'Pending',
                estimated_hours REAL NOT NULL DEFAULT 1.0,
                created_at TEXT NOT NULL
            )
        """)


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def add_task(
    title: str,
    subject: str,
    description: str,
    due_date: str,
    priority: str,
    estimated_hours: float,
) -> int:
    """Insert a new task and return the new task ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO tasks (
                title, subject, description, due_date,
                priority, status, estimated_hours, created_at
            )
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?)
        """, (
            title,
            subject,
            description,
            due_date,
            priority,
            estimated_hours,
            datetime.now().isoformat(),
        ))

        return cursor.lastrowid


def get_all_tasks() -> list[dict]:
    """Return all tasks ordered by due date."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM tasks
            ORDER BY due_date ASC
        """).fetchall()

        return [dict(row) for row in rows]


def get_task_by_id(task_id: int) -> dict | None:
    """Return one task by ID, or None if not found."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM tasks
            WHERE id = ?
        """, (task_id,)).fetchone()

        return dict(row) if row else None


def update_task_status(task_id: int, new_status: str) -> bool:
    """Update task status. Returns True if a task was updated."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        """, (new_status, task_id))

        return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Returns True if a task was deleted."""
    with get_connection() as conn:
        cursor = conn.execute("""
            DELETE FROM tasks
            WHERE id = ?
        """, (task_id,))

        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Search, filter, and sort
# ---------------------------------------------------------------------------

def search_tasks(query: str) -> list[dict]:
    """Search tasks by title or subject."""
    with get_connection() as conn:
        like_query = f"%{query}%"

        rows = conn.execute("""
            SELECT * FROM tasks
            WHERE title LIKE ? OR subject LIKE ?
            ORDER BY due_date ASC
        """, (like_query, like_query)).fetchall()

        return [dict(row) for row in rows]


def filter_tasks(
    status: str = "",
    priority: str = "",
    subject: str = "",
    sort_by: str = "due_date",
) -> list[dict]:
    """Filter tasks and sort them by due date or priority."""
    priority_order = """
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
        END
    """

    if sort_by == "priority":
        sort_clause = f"{priority_order} ASC, due_date ASC"
    else:
        sort_clause = "due_date ASC"

    conditions = []
    params = []

    if status and status != "All":
        conditions.append("status = ?")
        params.append(status)

    if priority and priority != "All":
        conditions.append("priority = ?")
        params.append(priority)

    if subject and subject != "All":
        conditions.append("subject = ?")
        params.append(subject)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql = f"""
        SELECT * FROM tasks
        {where_clause}
        ORDER BY {sort_clause}
    """

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------------------------

def get_dashboard_stats() -> dict:
    """Return totals used by the dashboard page and sidebar."""
    today = datetime.now().date().isoformat()

    with get_connection() as conn:
        total = conn.execute("""
            SELECT COUNT(*) FROM tasks
        """).fetchone()[0]

        completed = conn.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE status = 'Completed'
        """).fetchone()[0]

        pending = conn.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE status != 'Completed'
        """).fetchone()[0]

        overdue = conn.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE due_date < ? AND status != 'Completed'
        """, (today,)).fetchone()[0]

        upcoming_rows = conn.execute("""
            SELECT * FROM tasks
            WHERE due_date >= ? AND status != 'Completed'
            ORDER BY due_date ASC
            LIMIT 5
        """, (today,)).fetchall()

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "upcoming": [dict(row) for row in upcoming_rows],
    }


def get_distinct_subjects() -> list[str]:
    """Return all unique subjects in alphabetical order."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT subject
            FROM tasks
            ORDER BY subject ASC
        """).fetchall()

        return [row[0] for row in rows]