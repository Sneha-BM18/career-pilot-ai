import streamlit as st
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, pill, init_theme_state
from utils.auth import init_db, require_login
from utils.recommendations import skill_gap_analysis

st.set_page_config(page_title="Skill Gap · CareerPilot AI", page_icon="🎯", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("🎯 Skill Gap Analysis", "See exactly which skills separate you from your target roles, prioritized and mapped to a learning roadmap.")

if "last_student" not in st.session_state:
    st.warning("Run a prediction first on the **Prediction** page to generate your personalized skill-gap analysis.")
    department = st.selectbox("Or preview for a department", ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical"])
    student = {"programming_skills": 60, "technical_score": 60, "aptitude_score": 60, "soft_skills": 60}
else:
    student = st.session_state["last_student"]
    department = student["department"]
    st.success(f"Showing skill-gap analysis for **{student['name']}** ({department})")

skills = skill_gap_analysis(department, student)

# Radar chart: current vs required
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=[s["current"] for s in skills], theta=[s["skill"] for s in skills], fill="toself", name="Current", line_color="#2563EB"))
fig.add_trace(go.Scatterpolar(r=[s["required"] for s in skills], theta=[s["skill"] for s in skills], fill="toself", name="Required", line_color="#F59E0B", opacity=0.5))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Current vs Required Skill Levels", height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 Prioritized Roadmap")
for s in skills:
    kind = "red" if s["priority"] == "High" else ("amber" if s["priority"] == "Medium" else "green")
    with st.container():
        c1, c2, c3 = st.columns([2, 3, 2])
        with c1:
            st.markdown(f"**{s['skill']}** {pill(s['priority'], kind)}", unsafe_allow_html=True)
        with c2:
            st.progress(s["current"] / 100, text=f"{s['current']}% → target {s['required']}%")
        with c3:
            st.caption(f"📚 {s['course']}")
    st.divider()

st.markdown("### 🗓️ Weekly Learning Timeline")
high_priority = [s for s in skills if s["priority"] == "High"]
timeline_skills = (high_priority + skills)[:4]
cols = st.columns(4)
for i, (col, s) in enumerate(zip(cols, timeline_skills)):
    with col:
        st.markdown(f"**Week {i*2+1}-{i*2+2}**")
        st.markdown(f"🎯 {s['skill']}")
        st.caption(s["course"])

st.markdown("### 📈 Skill Progress Tracker")
st.caption("Track your progress as you complete each course (session-only demo tracker).")
for s in skills:
    key = f"progress_{s['skill']}"
    if key not in st.session_state:
        st.session_state[key] = s["current"]
    st.session_state[key] = st.slider(f"{s['skill']} progress", 0, 100, st.session_state[key], key=f"slider_{s['skill']}")
