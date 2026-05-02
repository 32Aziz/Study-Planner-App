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
from datetime import datetime, date

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
    # Using st.dataframe with selection disabled to prevent the "cell moving" behavior
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("⚙️ Task Action Center")
    st.markdown("*Refine your study plan by editing or removing tasks*")

    task_ids = [task["id"] for task in tasks]
    task_labels = {
        task["id"]: f"[{task['id']}] {task['title']} — {task['subject']}"
        for task in tasks
    }

    # Use tabs for a cleaner, more focused design
    tab_edit, tab_delete = st.tabs(["✏️ Edit Task", "🗑️ Delete Task"])

    # -----------------------------------------------------------------------
    # Edit Task Tab
    # -----------------------------------------------------------------------

    with tab_edit:
        st.markdown("### 📝 Modify Task Details")
        col_select, _ = st.columns([2, 1])
        with col_select:
            selected_id_edit = st.selectbox(
                "Select a task to modify",
                task_ids,
                format_func=lambda task_id: task_labels[task_id],
                key="edit_select",
            )

        # Fetch current task details to pre-populate the form
        current_task = next((t for t in tasks if t["id"] == selected_id_edit), None)

        if current_task:
            with st.form("edit_task_form"):
                # Use columns inside the form for a better layout
                e_col1, e_col2 = st.columns(2)

                with e_col1:
                    new_title = st.text_input("Title", value=current_task["title"])
                    
                    # Moved outside the form to be reactive
                    st.write("---")
                    st.write("**Subject Management**")
                    existing_subjects = db.get_distinct_subjects()
                    try:
                        subj_idx = existing_subjects.index(current_task["subject"])
                        subject_mode = st.radio("Subject Mode", ["Existing", "Rename/New"], horizontal=True, key=f"edit_mode_{selected_id_edit}")
                        if subject_mode == "Existing":
                            new_subject = st.selectbox("Select Subject", existing_subjects, index=subj_idx)
                        else:
                            new_subject = st.text_input("New/Modified Subject Name", value=current_task["subject"])
                    except:
                        new_subject = st.text_input("Subject", value=current_task["subject"])
                    st.write("---")

                    new_priority = st.selectbox(
                        "Priority",
                        utils.PRIORITY_LEVELS,
                        index=utils.PRIORITY_LEVELS.index(current_task["priority"])
                    )

                with e_col2:
                    try:
                        curr_due_date = datetime.fromisoformat(current_task["due_date"]).date()
                    except:
                        curr_due_date = date.today()

                    new_due_date = st.date_input("Due Date", value=curr_due_date)
                    new_hours = st.number_input(
                        "Est. Hours",
                        min_value=0.5,
                        value=float(current_task["estimated_hours"]),
                        step=0.5
                    )
                    new_status = st.selectbox(
                        "Status",
                        utils.STATUS_OPTIONS,
                        index=utils.STATUS_OPTIONS.index(current_task["status"])
                    )

                new_description = st.text_area("Description", value=current_task["description"])

                update_submitted = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True,
                    type="primary",
                )

            if update_submitted:
                # Validate inputs
                errors = utils.validate_task_input(
                    new_title,
                    new_subject,
                    new_due_date,
                    new_hours,
                )

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    updated = db.update_task(
                        selected_id_edit,
                        new_title.strip(),
                        new_subject.strip(),
                        new_description.strip(),
                        new_due_date.isoformat(),
                        new_priority,
                        new_hours,
                        new_status
                    )

                    # Confirmation step
                    st.info("💡 Review your changes above. Clicking 'Save Changes' will update the database.")
                    
                    if updated:
                        st.toast(f"✅ Task '{new_title}' updated!", icon="💾")
                        st.success(f"✨ Task '{new_title}' updated successfully.")
                        st.balloons()
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ Failed to update task.")

    # -----------------------------------------------------------------------
    # Delete Task Tab
    # -----------------------------------------------------------------------

    with tab_delete:
        st.markdown("### 🗑️ Remove Task")
        
        # Warning box for deletion
        st.warning("⚠️ **Caution:** Deleting a task is permanent and cannot be undone.")
        
        with st.form("delete_task_form"):
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                selected_id_delete = st.selectbox(
                    "Select Task to Delete",
                    task_ids,
                    format_func=lambda task_id: task_labels[task_id],
                    key="delete_select",
                )

            with col_d2:
                st.write("") # Spacer
                st.write("") # Spacer
                confirm_delete = st.checkbox(
                    "Confirm deletion"
                )

            delete_submitted = st.form_submit_button(
                "🗑️ Delete Permanently",
                use_container_width=True,
                type="secondary",
            )

        if delete_submitted:
            if not confirm_delete:
                st.error("Please check the confirmation box to delete.")
                return

            deleted = db.delete_task(selected_id_delete)

            if deleted:
                st.toast(f"🗑️ Task deleted successfully", icon="🗑️")
                st.success(f"✅ Task {selected_id_delete} has been removed.")
                import time
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("❌ Task not found.")