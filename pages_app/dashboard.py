"""
dashboard.py
------------
Dashboard page for the Study Planner app.

This page shows:
- Total tasks
- Completed tasks
- Pending tasks
- Overdue tasks
- Upcoming deadlines
- Completion progress gauge
"""

import streamlit as st
import plotly.graph_objects as go

from src import database as db
from src import utils


def show_dashboard() -> None:
    """Render the dashboard page."""
    stats = db.get_dashboard_stats()

    st.title("🏠 Dashboard")
    st.markdown("*Your study overview at a glance*")

    # -----------------------------------------------------------------------
    # Metric cards
    # -----------------------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    completion_percent = (
        round(stats["completed"] / stats["total"] * 100)
        if stats["total"]
        else 0
    )

    col1.metric("📦 Total Tasks", stats["total"])
    col2.metric("✅ Completed", stats["completed"], delta=f"{completion_percent}%")
    col3.metric("⏳ Pending", stats["pending"])
    col4.metric(
        "🚨 Overdue",
        stats["overdue"],
        delta=f"-{stats['overdue']}" if stats["overdue"] > 0 else None,
        delta_color="inverse" if stats["overdue"] > 0 else "normal",
    )

    st.markdown("---")

    col_a, col_b = st.columns([3, 2])

    # -----------------------------------------------------------------------
    # Upcoming deadlines
    # -----------------------------------------------------------------------

    with col_a:
        st.subheader("📅 Upcoming Deadlines")

        upcoming_tasks = stats["upcoming"]

        if not upcoming_tasks:
            st.info("No upcoming tasks. Great job staying on top of things!")
        else:
            for task in upcoming_tasks:
                priority_color = utils.PRIORITY_COLORS.get(task["priority"], "#aaa")
                urgency = utils.urgency_label(task["due_date"], task["status"])

                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg,#1e1e3f,#2d2b55);
                    border-left: 4px solid {priority_color};
                    border-radius: 10px;
                    padding: 0.8rem 1rem;
                    margin-bottom: 0.6rem;
                ">
                    <b>{task['title']}</b>
                    <span style="float:right; font-size:0.85rem; opacity:0.8;">
                        {urgency}
                    </span><br>
                    <span style="font-size:0.82rem; opacity:0.7;">
                        📘 {task['subject']} &nbsp;|&nbsp;
                        {utils.PRIORITY_EMOJI.get(task['priority'], '')} {task['priority']} &nbsp;|&nbsp;
                        ⏱ {task['estimated_hours']}h
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Completion progress chart
    # -----------------------------------------------------------------------

    with col_b:
        st.subheader("📈 Progress")

        if stats["total"] > 0:
            progress_value = round((stats["completed"] / stats["total"]) * 100, 1)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progress_value,
                number={"suffix": "%", "font": {"size": 28}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#7c3aed"},
                    "bgcolor": "#1e1e3f",
                    "bordercolor": "#2d2b55",
                    "steps": [
                        {"range": [0, 33], "color": "#3b0764"},
                        {"range": [33, 66], "color": "#4c1d95"},
                        {"range": [66, 100], "color": "#5b21b6"},
                    ],
                },
                title={"text": "Completion Rate", "font": {"size": 16}},
            ))

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e8e8f0",
                height=250,
                margin=dict(t=40, b=10, l=20, r=20),
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Add tasks to see your progress.")

    # -----------------------------------------------------------------------
    # Helpful dashboard message
    # -----------------------------------------------------------------------

    if stats["overdue"] > 0:
        st.warning(
            f"⚠️ You have {stats['overdue']} overdue task(s). "
            "Go to Manage Tasks to update them."
        )

    elif stats["total"] == 0:
        st.info("👋 Welcome! Go to Add Task to start your study plan.")