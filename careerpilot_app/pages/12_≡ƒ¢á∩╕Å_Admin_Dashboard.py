import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, init_theme_state
from utils.auth import init_db, require_admin
from utils.db import get_history, all_users_df

st.set_page_config(page_title="Admin Dashboard · CareerPilot AI", page_icon="🛠️", layout="wide")
init_db(); init_theme_state(); inject_css()
require_admin()

hero("🛠️ College Analytics Dashboard", "Admin-only view: placement stats, department comparisons, and student rankings across the whole platform.")

history = get_history()
users = all_users_df()

if history.empty:
    st.info("No prediction data yet across the platform.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total Students", len(users))
with c2: kpi_card("Placed Students", int((history["placement_status"] == "Placed").sum()))
with c3: kpi_card("Placement %", f"{(history['placement_status']=='Placed').mean()*100:.1f}%")
with c4: kpi_card("Avg CGPA", f"{history['cgpa'].mean():.2f}")

c5, c6 = st.columns(2)
with c5: kpi_card("Average Salary", f"₹{history['predicted_salary'].mean():.1f} LPA")
with c6: kpi_card("Highest Salary", f"₹{history['predicted_salary'].max():.1f} LPA")

st.markdown("### 🏛️ Department Statistics")
dept_stats = history.groupby("department").agg(
    students=("student_name", "count"),
    placement_rate=("placement_status", lambda x: (x == "Placed").mean() * 100),
    avg_salary=("predicted_salary", "mean"),
    avg_cgpa=("cgpa", "mean"),
).reset_index()
st.dataframe(dept_stats.round(2), use_container_width=True, hide_index=True)

c7, c8 = st.columns(2)
with c7:
    fig = px.bar(dept_stats, x="department", y="placement_rate", title="Placement % by Department", color_discrete_sequence=["#2563EB"])
    st.plotly_chart(fig, use_container_width=True)
with c8:
    fig = px.bar(dept_stats, x="department", y="avg_salary", title="Average Salary by Department (LPA)", color_discrete_sequence=["#22C55E"])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Year-wise / Time Trends")
history["created_at"] = pd.to_datetime(history["created_at"])
history["month"] = history["created_at"].dt.to_period("M").astype(str)
trend = history.groupby("month").agg(predictions=("id", "count"), placement_rate=("placement_status", lambda x: (x == "Placed").mean() * 100)).reset_index()
fig = px.line(trend, x="month", y="placement_rate", title="Placement Rate Trend Over Time", markers=True, color_discrete_sequence=["#2563EB"])
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🏆 Student Rankings (by Placement Probability)")
ranking = history.sort_values("probability", ascending=False)[["student_name", "department", "cgpa", "probability", "predicted_salary", "placement_status"]].drop_duplicates("student_name").head(20)
ranking.insert(0, "rank", range(1, len(ranking) + 1))
st.dataframe(ranking, use_container_width=True, hide_index=True)

st.markdown("### 👥 Registered Users")
st.dataframe(users, use_container_width=True, hide_index=True)
