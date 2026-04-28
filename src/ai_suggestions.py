"""
ai_suggestions.py
-----------------
AI and rule-based study suggestion engine.

This file:
- Uses Gemini API if GEMINI_API_KEY exists.
- Falls back to rule-based suggestions if no API key is available.
- Keeps the app usable even without external AI services.
"""

import os
from collections import Counter

from src.utils import days_until, priority_sort_key


# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Gemini helper
# ---------------------------------------------------------------------------

def _call_gemini(prompt: str) -> str | None:
    """Call Gemini and return the generated text, or None if unavailable."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(tasks: list[dict]) -> str:
    """Build a concise prompt for Gemini from incomplete tasks."""
    incomplete_tasks = [
        task for task in tasks
        if task["status"] != "Completed"
    ]

    if not incomplete_tasks:
        return ""

    task_lines = []

    for task in incomplete_tasks:
        delta = days_until(task["due_date"])
        days_text = f"{delta} days" if delta is not None else "unknown"

        task_lines.append(
            f"- [{task['priority']} priority] {task['title']} "
            f"(Subject: {task['subject']}, Due in {days_text}, "
            f"Estimated: {task['estimated_hours']} hours, "
            f"Status: {task['status']})"
        )

    tasks_block = "\n".join(task_lines)

    return f"""
You are a helpful academic study coach.

A student has these pending study tasks:

{tasks_block}

Give 5 concise and actionable study suggestions.

Focus on:
1. Which task to start first and why.
2. Which subject needs the most attention.
3. A simple study schedule for the next 2 or 3 days.
4. Time management based on estimated hours.
5. One motivational tip.

Use short bullet points.
"""


# ---------------------------------------------------------------------------
# Rule-based fallback
# ---------------------------------------------------------------------------

def _rule_based_suggestions(tasks: list[dict]) -> str:
    """Generate useful suggestions without AI."""
    incomplete_tasks = [
        task for task in tasks
        if task["status"] != "Completed"
    ]

    if not incomplete_tasks:
        return "🎉 Amazing! You have completed all your tasks. Take a well-deserved break!"

    def sort_key(task: dict):
        delta = days_until(task["due_date"])
        if delta is None:
            delta = 9999

        return (delta, priority_sort_key(task["priority"]))

    sorted_tasks = sorted(incomplete_tasks, key=sort_key)

    overdue_tasks = [
        task for task in incomplete_tasks
        if days_until(task["due_date"]) is not None
        and days_until(task["due_date"]) < 0
    ]

    urgent_tasks = [
        task for task in incomplete_tasks
        if days_until(task["due_date"]) is not None
        and 0 <= days_until(task["due_date"]) <= 2
    ]

    high_priority_tasks = [
        task for task in incomplete_tasks
        if task["priority"] == "High"
    ]

    subject_counts = Counter(task["subject"] for task in incomplete_tasks)
    busiest_subject = subject_counts.most_common(1)[0][0]

    total_hours = sum(
        float(task.get("estimated_hours", 0))
        for task in incomplete_tasks
    )

    suggestions = []

    first_task = sorted_tasks[0]
    delta = days_until(first_task["due_date"])

    if delta is not None and delta >= 0:
        due_text = f"in {delta} day(s)"
    else:
        due_text = "and it is already overdue"

    suggestions.append(
        f"📌 **Start with:** {first_task['title']} "
        f"({first_task['subject']}) because it is "
        f"{first_task['priority'].lower()} priority and due {due_text}."
    )

    if overdue_tasks:
        overdue_titles = ", ".join(
            task["title"] for task in overdue_tasks[:3]
        )
        suggestions.append(
            f"🚨 **Overdue:** Focus on these first: {overdue_titles}."
        )

    suggestions.append(
        f"📚 **Subject focus:** {busiest_subject} needs more attention "
        f"because it has {subject_counts[busiest_subject]} pending task(s)."
    )

    if urgent_tasks:
        urgent_plan = " → ".join(
            task["title"] for task in urgent_tasks[:3]
        )
        suggestions.append(
            f"🗓️ **Today's plan:** Work on {urgent_plan} because they are due soon."
        )
    else:
        suggestions.append(
            "🗓️ **Today's plan:** Use 25-minute study blocks for your highest-priority task."
        )

    if total_hours > 0:
        suggestions.append(
            f"⏱️ **Time management:** You have about {total_hours:.1f} hours of study remaining. "
            "Break this into smaller focused sessions."
        )

    if len(high_priority_tasks) > 1:
        suggestions.append(
            f"🔴 **High priority warning:** You have {len(high_priority_tasks)} high-priority tasks. "
            "Review them daily."
        )

    suggestions.append(
        "💪 **Motivation:** Small progress every day is better than waiting for a perfect study session."
    )

    return "\n\n".join(suggestions)


# ---------------------------------------------------------------------------
# Public function used by the app
# ---------------------------------------------------------------------------

def get_study_suggestions(tasks: list[dict]) -> tuple[str, str]:
    """Return suggestions and the source: gemini or rule-based."""
    if not tasks or all(task["status"] == "Completed" for task in tasks):
        return (
            "🎉 All tasks are completed! Add new tasks to get personalized suggestions.",
            "rule-based",
        )

    prompt = _build_prompt(tasks)

    if prompt:
        gemini_result = _call_gemini(prompt)

        if gemini_result:
            return gemini_result, "gemini"

    return _rule_based_suggestions(tasks), "rule-based"