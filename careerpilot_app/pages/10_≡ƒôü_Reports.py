import streamlit as st
import pandas as pd
import json
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, init_theme_state
from utils.auth import init_db, require_login, current_user
from utils.predictor import predict_placement, predict_salary
from utils.recommendations import skill_gap_analysis, career_suggestions, resume_tips, recommend_companies
from utils.pdf_report import build_report
from utils.db import get_history

st.set_page_config(page_title="Reports · CareerPilot AI", page_icon="📁", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("📁 Prediction Reports", "Generate a polished PDF report with your prediction, salary band, skill gap, and recommendations — including a QR code and clean layout, ready to share.")

if "last_student" not in st.session_state:
    st.warning("Run a prediction on the **Prediction** page first, then come back here to generate your report.")
else:
    student = st.session_state["last_student"]
    prediction = st.session_state["last_prediction"]
    salary = st.session_state["last_salary"]

    skills = skill_gap_analysis(student["department"], student)
    career = career_suggestions(student["department"], prediction)
    resume = resume_tips(student)
    avg_skill = (student["programming_skills"] + student["technical_score"]) / 2
    companies = recommend_companies(student["department"], student["cgpa"], avg_skill)

    st.markdown(f"#### Report ready for **{student['name']}**")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Status", prediction["status"])
    with c2: st.metric("Probability", f"{prediction['probability']}%")
    with c3: st.metric("Expected Salary", f"₹{salary['expected']} LPA")
    with c4: st.metric("ATS Score", f"{resume['score']}/100")

    pdf_bytes = build_report(student, prediction, salary, career, skills, resume, companies)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.download_button("📄 Download PDF", pdf_bytes, f"CareerPilot_Report_{student['name'].replace(' ','_')}.pdf",
                            "application/pdf", type="primary", use_container_width=True)
    with d2:
        csv_data = pd.DataFrame([{**student, **{f"pred_{k}": v for k, v in prediction.items()}, **{f"salary_{k}": v for k, v in salary.items()}}]).to_csv(index=False)
        st.download_button("📊 Download CSV", csv_data, "career_report.csv", "text/csv", use_container_width=True)
    with d3:
        import io
        xbuf = io.BytesIO()
        with pd.ExcelWriter(xbuf, engine="openpyxl") as writer:
            pd.DataFrame([student]).to_excel(writer, index=False, sheet_name="Profile")
            pd.DataFrame([prediction]).to_excel(writer, index=False, sheet_name="Prediction")
            pd.DataFrame([salary]).to_excel(writer, index=False, sheet_name="Salary")
            pd.DataFrame(skills).to_excel(writer, index=False, sheet_name="Skill Gap")
        st.download_button("📗 Download Excel", xbuf.getvalue(), "career_report.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with d4:
        json_data = json.dumps({"student": student, "prediction": prediction, "salary": salary,
                                 "career": career, "skills": skills, "resume": resume}, indent=2, default=str)
        st.download_button("🧾 Download JSON", json_data, "career_report.json", "application/json", use_container_width=True)

st.divider()
st.markdown("### 📦 Export your full prediction history")
history = get_history(current_user()["email"])
if len(history):
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ All history (CSV)", history.to_csv(index=False), "full_history.csv", "text/csv", use_container_width=True)
    with c2:
        st.download_button("⬇️ All history (JSON)", history.to_json(orient="records", indent=2), "full_history.json", "application/json", use_container_width=True)
else:
    st.caption("No history yet.")
