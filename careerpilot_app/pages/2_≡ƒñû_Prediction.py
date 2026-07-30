import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, pill, init_theme_state
from utils.auth import init_db, require_login, current_user
from utils.predictor import predict_placement, predict_salary
from utils.recommendations import skill_gap_analysis, career_suggestions
from utils.db import save_prediction

st.set_page_config(page_title="Prediction · CareerPilot AI", page_icon="🤖", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("🤖 AI Placement Prediction", "Fill in your profile — our RandomForest model predicts your placement probability, risk score, and expected salary in real time.")

tab_single, tab_bulk = st.tabs(["🧍 Single Prediction", "📁 CSV Bulk Prediction"])

DEPARTMENTS = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical"]
DEGREES = ["B.Tech", "B.E", "M.Tech", "BCA", "MCA"]
GENDERS = ["Male", "Female", "Other"]

with tab_single:
    with st.form("prediction_form"):
        st.markdown("#### Student Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Name", value=current_user()["name"])
            age = st.number_input("Age", 18, 30, 21)
            gender = st.selectbox("Gender", GENDERS)
        with c2:
            department = st.selectbox("Department", DEPARTMENTS)
            degree = st.selectbox("Degree", DEGREES)
            cgpa = st.slider("CGPA", 5.0, 10.0, 7.5, 0.05)
        with c3:
            internships = st.slider("Internships", 0, 5, 1)
            projects = st.slider("Projects", 0, 10, 3)
            work_experience = st.slider("Work Experience (months)", 0, 36, 0)

        st.markdown("#### Skills & Scores")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            programming_skills = st.slider("Programming Skills", 0, 100, 70)
            aptitude_score = st.slider("Aptitude Score", 0, 100, 65)
        with d2:
            communication_skills = st.slider("Communication Skills", 0, 100, 65)
            technical_score = st.slider("Technical Score", 0, 100, 70)
        with d3:
            soft_skills = st.slider("Soft Skills", 0, 100, 60)
            certifications = st.slider("Certifications", 0, 10, 1)
        with d4:
            hackathons = st.slider("Hackathons", 0, 10, 1)
            leadership = st.checkbox("Leadership experience (club/team lead, etc.)")

        submitted = st.form_submit_button("🚀 Predict Placement", type="primary", use_container_width=True)

    if submitted:
        student = dict(name=name, age=age, gender=gender, department=department, degree=degree,
                        cgpa=cgpa, internships=internships, projects=projects,
                        programming_skills=programming_skills, communication_skills=communication_skills,
                        aptitude_score=aptitude_score, technical_score=technical_score,
                        work_experience=work_experience, certifications=certifications,
                        soft_skills=soft_skills, leadership=leadership, hackathons=hackathons)

        prediction = predict_placement(student)
        salary = predict_salary(student)
        save_prediction(current_user()["email"], student, prediction, salary)
        st.session_state["last_student"] = student
        st.session_state["last_prediction"] = prediction
        st.session_state["last_salary"] = salary

        st.success("Prediction complete and saved to your History.")

        r1, r2 = st.columns([1, 1.4])
        with r1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prediction["probability"],
                number={"suffix": "%"},
                title={"text": "Placement Probability"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2563EB"},
                    "steps": [
                        {"range": [0, 40], "color": "#FEE2E2"},
                        {"range": [40, 70], "color": "#FEF3C7"},
                        {"range": [70, 100], "color": "#DCFCE7"},
                    ],
                    "threshold": {"line": {"color": "#EF4444", "width": 3}, "value": 50},
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            status_kind = "green" if prediction["status"] == "Placed" else "amber"
            st.markdown(f"### {pill(prediction['status'], status_kind)}", unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            with k1: kpi_card("Confidence", prediction["confidence"])
            with k2: kpi_card("Risk Score", f"{prediction['risk_score']}%")
            with k3: kpi_card("Expected Salary", f"₹{salary['expected']} LPA")
            st.progress(min(1.0, prediction["probability"] / 100))
            st.caption(f"Salary range: ₹{salary['min']} – ₹{salary['max']} LPA")

        st.markdown("#### 🎯 Quick skill-gap preview")
        skills = skill_gap_analysis(department, student)[:4]
        cols = st.columns(4)
        for col, s in zip(cols, skills):
            with col:
                st.markdown(f"**{s['skill']}**")
                st.progress(s["current"] / 100)
                st.caption(f"{s['current']}% → target {s['required']}% · {pill(s['priority'], 'red' if s['priority']=='High' else ('amber' if s['priority']=='Medium' else 'green'))}", unsafe_allow_html=True)
        st.info("See the full breakdown on the **Skills gap** page, and your personalized roadmap on **Career**.")

with tab_bulk:
    st.markdown("#### Upload a CSV of students for bulk prediction")
    st.caption("Required columns: name, age, gender, department, degree, cgpa, internships, projects, programming_skills, communication_skills, aptitude_score, technical_score, work_experience, certifications, soft_skills, leadership, hackathons")

    sample = pd.DataFrame([{
        "name": "Sample Student", "age": 22, "gender": "Male", "department": "Computer Science",
        "degree": "B.Tech", "cgpa": 7.8, "internships": 1, "projects": 3, "programming_skills": 75,
        "communication_skills": 65, "aptitude_score": 70, "technical_score": 72, "work_experience": 0,
        "certifications": 1, "soft_skills": 60, "leadership": 0, "hackathons": 1
    }])
    st.download_button("⬇️ Download sample CSV template", sample.to_csv(index=False), "sample_students.csv", "text/csv")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            results = []
            for _, row in df.iterrows():
                student = row.to_dict()
                student["leadership"] = bool(student.get("leadership", 0))
                pred = predict_placement(student)
                sal = predict_salary(student)
                results.append({**student, "placement_status": pred["status"], "probability": pred["probability"],
                                 "predicted_salary": sal["expected"], "risk_score": pred["risk_score"]})
                save_prediction(current_user()["email"], student, pred, sal)

            res_df = pd.DataFrame(results)
            st.success(f"Predicted {len(res_df)} students.")

            c1, c2, c3 = st.columns(3)
            with c1: kpi_card("Total Students", len(res_df))
            with c2: kpi_card("Predicted Placed", int((res_df['placement_status'] == 'Placed').sum()))
            with c3: kpi_card("Avg. Predicted Salary", f"₹{res_df['predicted_salary'].mean():.1f} LPA")

            import plotly.express as px
            fig = px.histogram(res_df, x="probability", nbins=20, title="Distribution of Placement Probability", color_discrete_sequence=["#2563EB"])
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(res_df, use_container_width=True, hide_index=True)

            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Download results as CSV", res_df.to_csv(index=False), "bulk_predictions.csv", "text/csv", use_container_width=True)
            with c2:
                import io
                xbuf = io.BytesIO()
                with pd.ExcelWriter(xbuf, engine="openpyxl") as writer:
                    res_df.to_excel(writer, index=False, sheet_name="Predictions")
                st.download_button("⬇️ Download results as Excel", xbuf.getvalue(), "bulk_predictions.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        except Exception as e:
            st.error(f"Couldn't process that file: {e}")
