import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, init_theme_state
from utils.auth import init_db, require_login
from utils.predictor import predict_salary

st.set_page_config(page_title="Salary Predictor · CareerPilot AI", page_icon="💰", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("💰 Salary Prediction", "Your expected salary band, powered by a RandomForest regression model trained on placement outcomes.")

if "last_student" not in st.session_state:
    st.warning("Run a prediction first on the **Prediction** page to see your salary band here.")
    st.stop()

student = st.session_state["last_student"]
salary = predict_salary(student)

c1, c2, c3 = st.columns(3)
with c1: kpi_card("Minimum", f"₹{salary['min']} LPA")
with c2: kpi_card("Expected", f"₹{salary['expected']} LPA", "Most likely offer")
with c3: kpi_card("Maximum", f"₹{salary['max']} LPA")

fig = go.Figure()
fig.add_trace(go.Bar(x=["Minimum", "Expected", "Maximum"], y=[salary["min"], salary["expected"], salary["max"]],
                      marker_color=["#F59E0B", "#2563EB", "#22C55E"], text=[f"₹{v}L" for v in [salary['min'], salary['expected'], salary['max']]],
                      textposition="outside"))
fig.update_layout(title="Salary Range (LPA)", height=380, yaxis_title="LPA")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📊 How you compare to your department")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "data", "students.csv"))
dep_df = df[(df.department == student["department"]) & (df.placed == 1)]

import plotly.express as px
fig = px.histogram(dep_df, x="salary_lpa", nbins=30, title=f"Salary Distribution — {student['department']}", color_discrete_sequence=["#94A3B8"])
fig.add_vline(x=salary["expected"], line_color="#2563EB", line_width=3, annotation_text="You", annotation_position="top")
st.plotly_chart(fig, use_container_width=True)

percentile = (dep_df["salary_lpa"] < salary["expected"]).mean() * 100 if len(dep_df) else 50
st.info(f"Your expected salary is higher than **{percentile:.0f}%** of placed students in {student['department']} in our dataset.")
