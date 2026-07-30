import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, feature_card, init_theme_state
from utils.auth import init_db, require_login
from utils.recommendations import career_suggestions
from utils.predictor import predict_placement

st.set_page_config(page_title="Career Guide · CareerPilot AI", page_icon="💼", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("💼 Career Roadmap", "Your personalized path — suggested roles, internships, certifications, and project ideas based on your latest prediction.")

if "last_student" not in st.session_state:
    st.info("Run a prediction on the **Prediction** page first for a fully personalized roadmap. Showing a general Computer Science roadmap below.")
    department = "Computer Science"
    prediction = {"probability": 60}
else:
    student = st.session_state["last_student"]
    department = student["department"]
    prediction = st.session_state.get("last_prediction", {"probability": 60})

career = career_suggestions(department, prediction)

st.markdown(f"""<div class="cp-glass"><b>🧭 Focus for you:</b> {career['focus']}</div>""", unsafe_allow_html=True)
st.write("")

st.markdown("### 🎯 Suggested Career Paths")
cols = st.columns(len(career["paths"]))
for col, path in zip(cols, career["paths"]):
    with col:
        feature_card("💼", path, f"A strong fit for {department} graduates with your current profile.")

st.markdown("### 🎓 Recommended Internships")
for i in career["internships"]:
    st.markdown(f"- {i}")

st.markdown("### 📜 Recommended Certifications")
for c in career["certifications"]:
    st.markdown(f"- {c}")

st.markdown("### 💻 Coding Platforms to Practice On")
cols = st.columns(len(career["coding_platforms"]))
for col, p in zip(cols, career["coding_platforms"]):
    with col:
        st.markdown(f"""<div class="cp-card" style="text-align:center;"><h4>{p}</h4></div>""", unsafe_allow_html=True)

st.markdown("### 💡 Project Ideas to Strengthen Your Portfolio")
for p in career["project_ideas"]:
    st.markdown(f"- {p}")

st.markdown("### 🗺️ Learning Roadmap")
roadmap = [
    ("Month 1", "Close top-priority skill gaps (see Skills page) + revise fundamentals"),
    ("Month 2", "Build 1-2 portfolio projects + start applying to internships"),
    ("Month 3", "Mock interviews, resume polish, and apply to shortlisted companies"),
]
for month, desc in roadmap:
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f"**{month}**")
    with c2:
        st.markdown(desc)
    st.divider()
