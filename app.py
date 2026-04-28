"""
app.py
------
Main entry point for the Study Planner Streamlit app.

This file:
- Configures the Streamlit page.
- Initializes the database.
- Builds the sidebar navigation.
- Calls each page function from pages_app/.
"""

import streamlit as st

from src import database as db
from pages_app.dashboard import show_dashboard
from pages_app.add_task import show_add_task
from pages_app.manage_tasks import show_manage_tasks
from pages_app.analytics_page import show_analytics
from pages_app.ai_page import show_ai_page


# ---------------------------------------------------------------------------
# Page configuration
# Must be the first Streamlit command.
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Custom CSS
# Keeps the UI clean and professional.
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

[data-testid="stSidebar"] * {
    color: #e8e8f0 !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e1e3f 0%, #2d2b55 100%);
    border: 1px solid #3a3870;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

[data-testid="stMetricValue"] {
    font-weight: 700;
    font-size: 2rem;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    border: none;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

[data-testid="stForm"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d2b55;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

h1 {
    color: #a78bfa !important;
}

h2 {
    color: #818cf8 !important;
}

h3 {
    color: #c4b5fd !important;
}

.stAlert {
    border-radius: 10px;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

hr {
    border-color: #2d2b55;
    margin: 1.5rem 0;
}

.sidebar-brand {
    text-align: center;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid #3a3870;
    margin-bottom: 1rem;
}

.sidebar-brand h2 {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
}

.sidebar-brand p {
    font-size: 0.8rem;
    opacity: 0.7;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Initialize database
# ---------------------------------------------------------------------------

db.init_db()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:2.5rem;">📚</div>
        <h2>Study Planner</h2>
        <p>Your academic command centre</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Task",
            "📋 Manage Tasks",
            "📊 Analytics",
            "🤖 AI Suggestions",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    stats = db.get_dashboard_stats()

    st.markdown(f"""
    <div style='font-size:0.85rem; opacity:0.8; line-height:1.8;'>
        📦 Total: <b>{stats['total']}</b><br>
        ✅ Done: <b>{stats['completed']}</b><br>
        🟡 Pending: <b>{stats['pending']}</b><br>
        🚨 Overdue: <b>{stats['overdue']}</b>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page router
# ---------------------------------------------------------------------------

if page == "🏠 Dashboard":
    show_dashboard()

elif page == "➕ Add Task":
    show_add_task()

elif page == "📋 Manage Tasks":
    show_manage_tasks()

elif page == "📊 Analytics":
    show_analytics()

elif page == "🤖 AI Suggestions":
    show_ai_page()