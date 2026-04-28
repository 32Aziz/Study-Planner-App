"""
utils.py
--------
Utility/helper functions for the Study Planner app.

This file includes:
- Constants for statuses and priorities.
- Input validation.
- Date formatting.
- Urgency labels.
- DataFrame formatting for displaying tasks.
"""

from datetime import datetime, date
from typing import Any


# ---------------------------------------------------------------------------
# Constants used across the app
# ---------------------------------------------------------------------------

PRIORITY_LEVELS = ["High", "Medium", "Low"]
STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]

PRIORITY_COLORS = {
    "High": "#FF4B4B",
    "Medium": "#FFA500",
    "Low": "#2ECC71",
}

STATUS_COLORS = {
    "Pending": "#FFA500",
    "In Progress": "#3498DB",
    "Completed": "#2ECC71",
}

STATUS_EMOJI = {
    "Pending": "🟡",
    "In Progress": "🔵",
    "Completed": "✅",
}

PRIORITY_EMOJI = {
    "High": "🔴",
    "Medium": "🟠",
    "Low": "🟢",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_task_input(
    title: str,
    subject: str,
    due_date: Any,
    estimated_hours: float,
) -> list[str]:
    """Validate task form inputs and return a list of error messages."""
    errors: list[str] = []

    if not title or not title.strip():
        errors.append("Task title is required.")
    elif len(title.strip()) < 3:
        errors.append("Task title must be at least 3 characters.")
    elif len(title.strip()) > 100:
        errors.append("Task title must be at most 100 characters.")

    if not subject or not subject.strip():
        errors.append("Subject is required.")

    if due_date is None:
        errors.append("Due date is required.")
    elif isinstance(due_date, date) and due_date < date.today():
        errors.append("Due date cannot be in the past.")

    if estimated_hours is None or estimated_hours <= 0:
        errors.append("Estimated hours must be a positive number.")
    elif estimated_hours > 500:
        errors.append("Estimated hours seems unrealistically high.")

    return errors


# ---------------------------------------------------------------------------
# Date and display formatting helpers
# ---------------------------------------------------------------------------

def format_date(date_str: str) -> str:
    """Convert ISO date string into readable format."""
    if not date_str:
        return "—"

    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return date_str


def days_until(due_date_str: str) -> int | None:
    """Return number of days until due date. Negative means overdue."""
    if not due_date_str:
        return None

    try:
        due = date.fromisoformat(due_date_str)
        return (due - date.today()).days
    except ValueError:
        return None


def urgency_label(due_date_str: str, status: str) -> str:
    """Return a readable urgency message for a task."""
    if status == "Completed":
        return "✅ Done"

    delta = days_until(due_date_str)

    if delta is None:
        return ""

    if delta < 0:
        return f"🚨 {abs(delta)}d overdue"

    if delta == 0:
        return "⚠️ Due today"

    if delta == 1:
        return "⚠️ Due tomorrow"

    if delta <= 3:
        return f"⚠️ Due in {delta}d"

    return f"📅 {delta}d left"


def priority_sort_key(priority: str) -> int:
    """Return a numeric priority value for sorting."""
    return {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }.get(priority, 99)


# ---------------------------------------------------------------------------
# DataFrame helper
# ---------------------------------------------------------------------------

def tasks_to_display_df(tasks: list[dict]):
    """Convert task dictionaries into a clean display DataFrame."""
    import pandas as pd

    if not tasks:
        return pd.DataFrame()

    df = pd.DataFrame(tasks)

    df["Days Left"] = df["due_date"].apply(days_until)
    df["Urgency"] = df.apply(
        lambda row: urgency_label(row["due_date"], row["status"]),
        axis=1,
    )
    df["Due Date"] = df["due_date"].apply(format_date)

    rename_map = {
        "id": "ID",
        "title": "Title",
        "subject": "Subject",
        "description": "Description",
        "priority": "Priority",
        "status": "Status",
        "estimated_hours": "Est. Hours",
        "created_at": "Created",
    }

    df = df.rename(columns=rename_map)
    df = df.drop(columns=["due_date", "Created"], errors="ignore")

    columns = [
        "ID",
        "Title",
        "Subject",
        "Priority",
        "Status",
        "Due Date",
        "Days Left",
        "Urgency",
        "Est. Hours",
        "Description",
    ]

    columns = [col for col in columns if col in df.columns]

    return df[columns]