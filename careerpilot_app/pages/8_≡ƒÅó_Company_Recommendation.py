import streamlit as st
import plotly.express as px
import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, pill, init_theme_state
from utils.auth import init_db, require_login
from utils.recommendations import recommend_companies

st.set_page_config(page_title="Company Recommendation · CareerPilot AI", page_icon="🏢", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("🏢 Company Recommendation", "Ranked companies matched to your CGPA, skills, department, and experience.")

if "last_student" not in st.session_state:
    st.warning("Run a prediction first on the **Prediction** page to see personalized company matches.")
    st.stop()

student = st.session_state["last_student"]
avg_skill = (student["programming_skills"] + student["technical_score"]) / 2
companies = recommend_companies(student["department"], student["cgpa"], avg_skill)

df = pd.DataFrame(companies)
fig = px.bar(df.sort_values("fit_score"), x="fit_score", y="name", orientation="h", color="eligible",
             color_discrete_map={True: "#22C55E", False: "#CBD5E1"}, title="Company Fit Score")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🎯 Ranked Matches")
for c in companies:
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
        with c1:
            st.markdown(f"**{c['name']}**")
            st.caption(c["tier"])
        with c2:
            st.progress(c["fit_score"] / 100, text=f"Fit {c['fit_score']}%")
        with c3:
            st.caption(f"Min CGPA: {c['min_cgpa']} · Min Skill: {c['min_skill']}%")
        with c4:
            st.markdown(pill("Eligible ✅", "green") if c["eligible"] else pill("Not Yet", "amber"), unsafe_allow_html=True)
    st.divider()
