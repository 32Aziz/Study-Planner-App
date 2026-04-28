"""
manage_tasks.py
---------------
Manage Tasks page for the Study Planner app.

This page:
- Displays tasks in a table.
- Provides search, filter, and sorting.
- Allows task status updates.
- Allows deleting tasks with confirmation.
"""

import streamlit as st

from src import database as db
from src import utils


def show_manage_tasks() -> None:
    """Render the Manage Tasks page."""
    st.title("📋 Manage Tasks")
    st.markdown("*Search, filter, update, and delete your study tasks*")

    # -----------------------------------------------------------------------
    # Search and filter controls
    # -----------------------------------------------------------------------

    with st.expander("🔍 Search & Filter", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            search_query = st.text_input(
                "🔍 Search",
                placeholder="Title or subject",
            )

        with col2:
            subjects = ["All"] + db.get_distinct_subjects()
            filter_subject = st.selectbox("Subject", subjects)

        with col3:
            filter_status = st.selectbox(
                "Status",
                ["All"] + utils.STATUS_OPTIONS,
            )

        with col4:
            filter_priority = st.selectbox(
                "Priority",
                ["All"] + utils.PRIORITY_LEVELS,
            )

        with col5:
            sort_by = st.selectbox(
                "Sort By",
                ["due_date", "priority"],
                format_func=lambda value: "Due Date" if value == "due_date" else "Priority",
            )

    # -----------------------------------------------------------------------
    # Fetch tasks
    # -----------------------------------------------------------------------

    if search_query.strip():
        tasks = db.search_tasks(search_query.strip())
    else:
        tasks = db.filter_tasks(
            status=filter_status,
            priority=filter_priority,
            subject=filter_subject,
            sort_by=sort_by,
        )

    st.markdown(f"**{len(tasks)} task(s) found**")

    if not tasks:
        st.info("No tasks match your criteria.")
        return

    # -----------------------------------------------------------------------
    # Display task table
    # -----------------------------------------------------------------------

    display_df = utils.tasks_to_display_df(tasks)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Update / Delete Task")

    task_ids = [task["id"] for task in tasks]

    task_labels = {
        task["id"]: f"[{task['id']}] {task['title']} — {task['subject']}"
        for task in tasks
    }

    col_update, col_delete = st.columns(2)

    # -----------------------------------------------------------------------
    # Update status form
    # -----------------------------------------------------------------------

    with col_update:
        with st.form("update_status_form"):
            st.markdown("**Update Status**")

            selected_id_update = st.selectbox(
                "Select Task",
                task_ids,
                format_func=lambda task_id: task_labels[task_id],
                key="update_select",
            )

            new_status = st.selectbox(
                "New Status",
                utils.STATUS_OPTIONS,
            )

            update_submitted = st.form_submit_button(
                "🔄 Update",
                use_container_width=True,
                type="primary",
            )

        if update_submitted:
            updated = db.update_task_status(selected_id_update, new_status)

            if updated:
                st.success(f"✅ Task {selected_id_update} updated to {new_status}.")
                st.rerun()
            else:
                st.error("❌ Task not found.")

    # -----------------------------------------------------------------------
    # Delete task form
    # -----------------------------------------------------------------------

    with col_delete:
        with st.form("delete_task_form"):
            st.markdown("**Delete Task**")

            selected_id_delete = st.selectbox(
                "Select Task",
                task_ids,
                format_func=lambda task_id: task_labels[task_id],
                key="delete_select",
            )

            confirm_delete = st.checkbox(
                "I confirm I want to permanently delete this task."
            )

            delete_submitted = st.form_submit_button(
                "🗑️ Delete",
                use_container_width=True,
            )

        if delete_submitted:
            if not confirm_delete:
                st.warning("Please tick the confirmation checkbox first.")
                return

            deleted = db.delete_task(selected_id_delete)

            if deleted:
                st.success(f"🗑️ Task {selected_id_delete} deleted.")
                st.rerun()
            else:
                st.error("❌ Task not found.")