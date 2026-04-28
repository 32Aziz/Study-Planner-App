"""
add_task.py
-----------
Add Task page for the Study Planner app.

This page:
- Shows a form for adding a study task.
- Validates user input.
- Saves valid tasks to the SQLite database.
"""

from datetime import date

import streamlit as st

from src import database as db
from src import utils


def show_add_task() -> None:
    """Render the Add Task page."""
    st.title("➕ Add New Study Task")
    st.markdown("*Fill in the form below to add a task to your study plan*")

    # -----------------------------------------------------------------------
    # Add task form
    # -----------------------------------------------------------------------

    with st.form("add_task_form", clear_on_submit=True):
        st.subheader("📝 Task Details")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Task Title *",
                placeholder="e.g. Chapter 5 Calculus Review",
            )

            subject = st.text_input(
                "Subject *",
                placeholder="e.g. Mathematics",
            )

            priority = st.selectbox(
                "Priority *",
                utils.PRIORITY_LEVELS,
            )

        with col2:
            due_date = st.date_input(
                "Due Date *",
                min_value=date.today(),
            )

            estimated_hours = st.number_input(
                "Estimated Hours *",
                min_value=0.5,
                max_value=200.0,
                value=2.0,
                step=0.5,
            )

            status_init = st.selectbox(
                "Initial Status",
                utils.STATUS_OPTIONS,
            )

        description = st.text_area(
            "Description / Notes",
            placeholder="Optional: add notes, resources, or instructions here.",
            height=100,
        )

        submitted = st.form_submit_button(
            "✅ Add Task",
            use_container_width=True,
            type="primary",
        )

    # -----------------------------------------------------------------------
    # Validate and save
    # -----------------------------------------------------------------------

    if submitted:
        errors = utils.validate_task_input(
            title,
            subject,
            due_date,
            estimated_hours,
        )

        if errors:
            for error in errors:
                st.error(f"❌ {error}")
            return

        try:
            task_id = db.add_task(
                title=title.strip(),
                subject=subject.strip(),
                description=description.strip(),
                due_date=due_date.isoformat(),
                priority=priority,
                estimated_hours=estimated_hours,
            )

            if status_init != "Pending":
                db.update_task_status(task_id, status_init)

            st.success(f"🎉 Task '{title.strip()}' added successfully! ID: {task_id}")
            st.balloons()

        except Exception as error:
            st.error(f"❌ Database error: {error}")

    # -----------------------------------------------------------------------
    # Planning tips
    # -----------------------------------------------------------------------

    with st.expander("💡 Tips for effective task planning"):
        st.markdown("""
        - Use clear task titles.
        - Break large tasks into smaller tasks.
        - Estimate hours honestly.
        - Use High priority only for urgent tasks.
        - Review your plan every day.
        """)