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
            # Removed st.form to make Subject Mode and other fields fully reactive
            st.markdown("---")
            e_col1, e_col2 = st.columns(2)

            # Helper to clear confirmation when any field changes
            def on_field_change():
                st.session_state[f"confirm_update_{selected_id_edit}"] = False

            with e_col1:
                new_title = st.text_input("Title", value=current_task["title"], on_change=on_field_change)
                
                st.write("**Subject Management**")
                existing_subjects = db.get_distinct_subjects()
                try:
                    subj_idx = existing_subjects.index(current_task["subject"])
                    subject_mode = st.radio("Subject Mode", ["Existing", "Rename/New"], horizontal=True, key=f"edit_mode_{selected_id_edit}", on_change=on_field_change)
                    if subject_mode == "Existing":
                        new_subject = st.selectbox("Select Subject", existing_subjects, index=subj_idx, on_change=on_field_change)
                    else:
                        new_subject = st.text_input("New/Modified Subject Name", value=current_task["subject"], on_change=on_field_change)
                except:
                    new_subject = st.text_input("Subject", value=current_task["subject"], on_change=on_field_change)

                new_priority = st.selectbox(
                    "Priority",
                    utils.PRIORITY_LEVELS,
                    index=utils.PRIORITY_LEVELS.index(current_task["priority"]),
                    on_change=on_field_change
                )

            with e_col2:
                try:
                    curr_due_date = datetime.fromisoformat(current_task["due_date"]).date()
                except:
                    curr_due_date = date.today()

                new_due_date = st.date_input("Due Date", value=curr_due_date, on_change=on_field_change)
                new_hours = st.number_input(
                    "Est. Hours",
                    min_value=0.5,
                    value=float(current_task["estimated_hours"]),
                    step=0.5,
                    on_change=on_field_change
                )
                new_status = st.selectbox(
                    "Status",
                    utils.STATUS_OPTIONS,
                    index=utils.STATUS_OPTIONS.index(current_task["status"]),
                    on_change=on_field_change
                )

            new_description = st.text_area("Description", value=current_task["description"], on_change=on_field_change)

            st.write("---")
            # Step 1: Initial Action Button
            if not st.session_state.get(f"confirm_update_{selected_id_edit}", False):
                update_triggered = st.button(
                    "💾 Save Changes to Task",
                    use_container_width=True,
                    type="primary",
                )
                if update_triggered:
                    st.session_state[f"confirm_update_{selected_id_edit}"] = True
                    st.rerun()
            
            # Step 2: Confirmation Dialog
            if st.session_state.get(f"confirm_update_{selected_id_edit}", False):
                st.warning("🔍 **Review your changes:**")
                st.markdown(f"""
                - **Title:** {new_title}
                - **Subject:** {new_subject}
                - **Priority:** {new_priority}
                - **Due Date:** {new_due_date}
                - **Hours:** {new_hours}
                - **Status:** {new_status}
                - **Description:** {new_description[:50]}{'...' if len(new_description) > 50 else ''}
                """)
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state[f"confirm_update_{selected_id_edit}"] = False
                        st.rerun()
                with col_c2:
                    confirm_final = st.button("✅ Yes, Update Now", use_container_width=True, type="primary")
                
                if confirm_final:
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
                        st.session_state[f"confirm_update_{selected_id_edit}"] = False
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

                        if updated:
                            st.toast(f"✅ Task '{new_title}' updated!", icon="💾")
                            st.success(f"✨ Task updated successfully. Refreshing in 3s...")
                            st.balloons()
                            st.session_state[f"confirm_update_{selected_id_edit}"] = False
                            import time
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update task.")
                            st.session_state[f"confirm_update_{selected_id_edit}"] = False

    # -----------------------------------------------------------------------
    # Delete Task Tab
    # -----------------------------------------------------------------------

    with tab_delete:
        st.markdown("### 🗑️ Remove Task")
        
        st.warning("⚠️ **Caution:** Deleting a task is permanent and cannot be undone.")
        
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

        if not st.session_state.get(f"confirm_delete_{selected_id_delete}", False):
            delete_triggered = st.button(
                "🗑️ Delete Permanently",
                use_container_width=True,
                type="secondary",
            )
            if delete_triggered:
                if not confirm_delete:
                    st.error("Please check the confirmation box first.")
                else:
                    st.session_state[f"confirm_delete_{selected_id_delete}"] = True
                    st.rerun()
        
        if st.session_state.get(f"confirm_delete_{selected_id_delete}", False):
            st.error(f"❗ **Are you absolutely sure?** This will delete: **{current_task['title'] if current_task else selected_id_delete}**")
            
            col_dc1, col_dc2 = st.columns(2)
            with col_dc1:
                if st.button("🔙 No, Keep It", use_container_width=True):
                    st.session_state[f"confirm_delete_{selected_id_delete}"] = False
                    st.rerun()
            with col_dc2:
                final_delete = st.button("🔥 Yes, Delete Now", use_container_width=True, type="primary")
            
            if final_delete:
                deleted = db.delete_task(selected_id_delete)

                if deleted:
                    st.toast(f"🗑️ Task deleted successfully", icon="🗑️")
                    st.success(f"✅ Task has been removed. Refreshing in 3s...")
                    st.session_state[f"confirm_delete_{selected_id_delete}"] = False
                    import time
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error("❌ Task not found.")
                    st.session_state[f"confirm_delete_{selected_id_delete}"] = False