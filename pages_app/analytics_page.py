"""
analytics_page.py
-----------------
Analytics page for the Study Planner app.

This page is the data science bonus feature.

It shows:
- Tasks by subject.
- Tasks by status.
- Estimated study hours by subject.
- Workload by due date.
- Subject summary table.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from src import database as db


def show_analytics() -> None:
    """Render the Analytics page."""
    st.title("📊 Analytics")
    st.markdown("*Visualize your study workload and progress*")

    all_tasks = db.get_all_tasks()

    if not all_tasks:
        st.info("📭 No tasks yet. Add some tasks to see analytics.")
        return

    df = pd.DataFrame(all_tasks)

    row1_col1, row1_col2 = st.columns(2)

    # -----------------------------------------------------------------------
    # Chart 1: Tasks by subject
    # -----------------------------------------------------------------------

    with row1_col1:
        st.subheader("📘 Tasks by Subject")

        subject_counts = df.groupby("subject").size().reset_index(name="Count")

        fig1 = px.pie(
            subject_counts,
            names="subject",
            values="Count",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Purples_r,
        )

        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e8f0",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=20, b=20),
        )

        st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------------------------------------------------
    # Chart 2: Tasks by status
    # -----------------------------------------------------------------------

    with row1_col2:
        st.subheader("📊 Tasks by Status")

        status_counts = df.groupby("status").size().reset_index(name="Count")

        color_map = {
            "Pending": "#FFA500",
            "In Progress": "#3498DB",
            "Completed": "#2ECC71",
        }

        fig2 = px.bar(
            status_counts,
            x="status",
            y="Count",
            color="status",
            color_discrete_map=color_map,
            text="Count",
        )

        fig2.update_traces(textposition="outside")

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e8f0",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2d2b55"),
            margin=dict(t=20, b=20),
        )

        st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------------------------------------------------
    # Chart 3: Priority Distribution
    # -----------------------------------------------------------------------
    
    st.markdown("---")
    row_p1, row_p2 = st.columns([1, 2])
    
    with row_p1:
        st.subheader("🚩 Priority Mix")
        priority_counts = df.groupby("priority").size().reset_index(name="Count")
        
        from src import utils
        fig_p = px.pie(
            priority_counts,
            names="priority",
            values="Count",
            color="priority",
            color_discrete_map=utils.PRIORITY_COLORS,
            hole=0.4
        )
        fig_p.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e8f0",
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=20, b=50, l=0, r=0)
        )
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
    
    with row_p2:
        st.subheader("💡 Analysis Insight")
        total_h = df["estimated_hours"].sum()
        avg_h = df["estimated_hours"].mean()
        high_p = len(df[df["priority"] == "High"])
        
        st.markdown(f"""
        <div style="background: rgba(124, 58, 237, 0.1); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(124, 58, 237, 0.3);">
            <ul style="margin: 0; padding-left: 1.2rem;">
                <li>Total estimated effort: <b>{total_h:.1f} hours</b></li>
                <li>Average effort per task: <b>{avg_h:.1f} hours</b></li>
                <li>High priority tasks: <b>{high_p}</b> (<i>{ (high_p/len(df)*100):.1f}% of total</i>)</li>
            </ul>
            <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                Tip: High priority tasks should ideally be less than 20% of your total workload to avoid burnout.
            </p>
        </div>
        """, unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns(2)

    # -----------------------------------------------------------------------
    # Chart 3: Study hours by subject
    # -----------------------------------------------------------------------

    with row2_col1:
        st.subheader("⏱️ Study Hours by Subject")

        hours_df = df.groupby("subject")["estimated_hours"].sum().reset_index()
        hours_df.columns = ["Subject", "Hours"]

        fig3 = px.bar(
            hours_df,
            y="Subject",
            x="Hours",
            orientation="h",
            color="Hours",
            color_continuous_scale="Purples",
            text="Hours",
        )

        fig3.update_traces(
            texttemplate="%{text:.1f}h",
            textposition="outside",
        )

        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e8f0",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor="#2d2b55"),
            yaxis=dict(showgrid=False),
            margin=dict(t=20, b=20),
        )

        st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------------------------------------------------
    # Chart 4: Workload by due date
    # -----------------------------------------------------------------------

    with row2_col2:
        st.subheader("📅 Workload by Due Date")

        upcoming_df = df[df["status"] != "Completed"].copy()

        if upcoming_df.empty:
            st.success("🎉 All tasks completed. No upcoming workload.")
        else:
            upcoming_df["due_date"] = pd.to_datetime(upcoming_df["due_date"])

            workload = (
                upcoming_df.groupby("due_date")["estimated_hours"]
                .sum()
                .reset_index()
            )

            workload.columns = ["Due Date", "Hours"]

            fig4 = px.area(
                workload,
                x="Due Date",
                y="Hours",
                color_discrete_sequence=["#7c3aed"],
            )

            fig4.update_traces(
                fill="tozeroy",
                fillcolor="rgba(124,58,237,0.25)",
            )

            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8e8f0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2d2b55"),
                margin=dict(t=20, b=20),
            )

            st.plotly_chart(fig4, use_container_width=True)

    # -----------------------------------------------------------------------
    # Subject summary table
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.subheader("📋 Subject Summary")

    summary = (
        df.groupby("subject")
        .agg(
            Tasks=("id", "count"),
            Completed=("status", lambda status: (status == "Completed").sum()),
            Total_Hours=("estimated_hours", "sum"),
        )
        .reset_index()
    )

    summary.columns = [
        "Subject",
        "Total Tasks",
        "Completed",
        "Total Hours",
    ]

    summary["Completion %"] = (
        summary["Completed"] / summary["Total Tasks"] * 100
    ).round(1).astype(str) + "%"

    st.dataframe(summary, use_container_width=True, hide_index=True)