"""
ai_page.py
----------
AI Suggestions page for the Study Planner app.

This page is the AI bonus feature.

It:
- Reads tasks from the database.
- Uses Gemini if GEMINI_API_KEY exists.
- Falls back to rule-based suggestions if no key exists.
"""

import os

import streamlit as st

from src import database as db
from src import ai_suggestions as ai
from src import utils


def show_ai_page() -> None:
    """Render the AI Suggestions page."""
    st.title("🤖 AI Study Suggestions")
    st.markdown("*Personalized advice based on your current tasks*")

    all_tasks = db.get_all_tasks()

    if not all_tasks:
        st.info("📭 No tasks found. Add some tasks first to get suggestions.")
        return

    incomplete_count = sum(
        1 for task in all_tasks
        if task["status"] != "Completed"
    )

    col_info, col_button = st.columns([3, 1])

    with col_info:
        st.markdown(
            f"Analyzing **{len(all_tasks)} total** tasks "
            f"({incomplete_count} incomplete) to generate your study plan."
        )

    with col_button:
        generate = st.button(
            "✨ Generate Suggestions",
            type="primary",
            use_container_width=True,
        )

    # -----------------------------------------------------------------------
    # API key status message
    # -----------------------------------------------------------------------

    has_api_key = bool(os.getenv("GEMINI_API_KEY", "").strip())

    if has_api_key:
        st.success("🔑 Gemini API key detected. AI-powered suggestions enabled.")
    else:
        st.info(
            "💡 No Gemini API key found. The app will use smart rule-based suggestions. "
            "Add GEMINI_API_KEY to a .env file to enable Gemini."
        )

    # -----------------------------------------------------------------------
    # Generate or show cached suggestions
    # -----------------------------------------------------------------------

    if generate or "ai_suggestions_cache" in st.session_state:
        if generate:
            with st.spinner("🧠 Generating personalized study suggestions..."):
                suggestions, source = ai.get_study_suggestions(all_tasks)

            st.session_state["ai_suggestions_cache"] = (suggestions, source)
        else:
            suggestions, source = st.session_state["ai_suggestions_cache"]

        st.markdown("---")

        if source == "gemini":
            st.success("✨ Powered by Gemini AI")
        else:
            st.info("🔧 Generated using rule-based fallback")

        st.markdown("### 📖 Your Personalized Study Plan")
        st.markdown(suggestions)

        # -------------------------------------------------------------------
        # Pending task summary
        # -------------------------------------------------------------------

        st.markdown("---")
        st.subheader("📋 Pending Tasks Summary")

        pending_tasks = [
            task for task in all_tasks
            if task["status"] != "Completed"
        ]

        if not pending_tasks:
            st.success("🎉 All done!")
            return

        sorted_pending = sorted(
            pending_tasks,
            key=lambda task: (
                utils.days_until(task["due_date"])
                if utils.days_until(task["due_date"]) is not None
                else 9999,
                utils.priority_sort_key(task["priority"]),
            ),
        )

        for task in sorted_pending:
            urgency = utils.urgency_label(task["due_date"], task["status"])
            priority_color = utils.PRIORITY_COLORS.get(task["priority"], "#aaa")

            st.markdown(f"""
            <div style="
                background:linear-gradient(135deg,#1e1e3f,#2d2b55);
                border-left:4px solid {priority_color};
                border-radius:10px;
                padding:0.7rem 1rem;
                margin-bottom:0.5rem;
            ">
                {utils.PRIORITY_EMOJI.get(task['priority'], '')}
                <b>{task['title']}</b>
                <span style='float:right;font-size:0.82rem;opacity:0.8;'>
                    {urgency}
                </span><br>
                <span style='font-size:0.8rem;opacity:0.7;'>
                    📘 {task['subject']} &nbsp;|&nbsp;
                    {utils.STATUS_EMOJI.get(task['status'], '')} {task['status']} &nbsp;|&nbsp;
                    ⏱ {task['estimated_hours']}h
                </span>
            </div>
            """, unsafe_allow_html=True)