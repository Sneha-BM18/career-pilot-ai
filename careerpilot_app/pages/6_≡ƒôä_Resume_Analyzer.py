import streamlit as st
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, init_theme_state
from utils.auth import init_db, require_login
from utils.recommendations import resume_tips

st.set_page_config(page_title="Resume Analyzer · CareerPilot AI", page_icon="📄", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("📄 Resume Analyzer", "An ATS-style score plus concrete resume, LinkedIn, and GitHub tips based on your profile.")

if "last_student" not in st.session_state:
    st.warning("Run a prediction first on the **Prediction** page so we can analyze your actual profile.")
    st.stop()

student = st.session_state["last_student"]
resume = resume_tips(student)

c1, c2 = st.columns([1, 2])
with c1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=resume["score"],
        title={"text": "ATS Resume Score"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#2563EB"},
               "steps": [{"range": [0, 50], "color": "#FEE2E2"}, {"range": [50, 75], "color": "#FEF3C7"}, {"range": [75, 100], "color": "#DCFCE7"}]}
    ))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("#### 🛠️ Suggested Improvements")
    for t in resume["tips"]:
        st.markdown(f"- {t}")

st.markdown("### ✅ Resume Checklist")
cols = st.columns(2)
for i, item in enumerate(resume["checklist"]):
    with cols[i % 2]:
        st.checkbox(item, key=f"check_{i}")

c3, c4 = st.columns(2)
with c3:
    st.markdown("### 💼 LinkedIn Optimization")
    for t in resume["linkedin_tips"]:
        st.markdown(f"- {t}")
with c4:
    st.markdown("### 🐙 GitHub Tips")
    for t in resume["github_tips"]:
        st.markdown(f"- {t}")

st.markdown("### 📤 Optional: Upload your resume (PDF/DOCX) for a keyword scan")
uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
if uploaded:
    st.success(f"Received `{uploaded.name}`. Keyword-matching against job descriptions is a great next feature to wire up with a resume-parsing library like `pyresparser` or `pdfplumber`.")
