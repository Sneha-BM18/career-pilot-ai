import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, init_theme_state
from utils.auth import init_db, require_login
from utils.predictor import get_metrics, get_feature_importance_df, _ensure_models
from utils.db import get_history

st.set_page_config(page_title="Analytics · CareerPilot AI", page_icon="📊", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("📊 Analytics Dashboard", "Explore the training dataset and live prediction trends with interactive charts.")

_ensure_models()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "data", "students.csv"))
metrics = get_metrics()
history = get_history()

tab_overview, tab_charts, tab_model, tab_trends = st.tabs(["📈 Overview", "📊 Distributions", "🧠 Model Performance", "🕓 Prediction Trends"])

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Dataset Size", f"{len(df):,}")
    with c2: kpi_card("Placement Ratio", f"{df['placed'].mean()*100:.1f}%")
    with c3: kpi_card("Avg CGPA", f"{df['cgpa'].mean():.2f}")
    with c4: kpi_card("Avg Salary (placed)", f"₹{df.loc[df.placed==1,'salary_lpa'].mean():.1f} LPA")

    c5, c6 = st.columns(2)
    with c5:
        fig = px.pie(df, names=df["placed"].map({1: "Placed", 0: "Not Placed"}), title="Placement Ratio",
                     color_discrete_sequence=["#2563EB", "#F59E0B"], hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig = px.pie(df, names="gender", title="Gender Distribution", hole=0.5,
                     color_discrete_sequence=["#2563EB", "#22C55E", "#F59E0B"])
        st.plotly_chart(fig, use_container_width=True)

with tab_charts:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x="department", color=df["placed"].map({1: "Placed", 0: "Not Placed"}),
                            barmode="group", title="Department Distribution & Placement",
                            color_discrete_sequence=["#2563EB", "#F59E0B"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df, x="cgpa", nbins=30, title="CGPA Distribution", color_discrete_sequence=["#2563EB"])
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(df[df.placed == 1], x="salary_lpa", nbins=30, title="Salary Distribution (Placed Students)",
                            color_discrete_sequence=["#22C55E"])
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        skill_df = df.melt(value_vars=["programming_skills", "communication_skills", "aptitude_score", "technical_score", "soft_skills"],
                            var_name="skill", value_name="score")
        fig = px.box(skill_df, x="skill", y="score", title="Skill Score Distribution", color="skill")
        st.plotly_chart(fig, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        comp_df = df["department"].value_counts().reset_index()
        comp_df.columns = ["department", "count"]
        fig = px.bar(comp_df, x="department", y="count", title="Students per Department", color_discrete_sequence=["#2563EB"])
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig = px.scatter(df, x="internships", y="projects", color=df["placed"].map({1: "Placed", 0: "Not Placed"}),
                          title="Internship vs Project Analysis", color_discrete_sequence=["#2563EB", "#F59E0B"],
                          opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Correlation Heatmap")
    numeric_cols = ["cgpa", "internships", "projects", "programming_skills", "communication_skills",
                     "aptitude_score", "technical_score", "work_experience", "certifications",
                     "soft_skills", "leadership", "hackathons", "placed", "salary_lpa"]
    corr = df[numeric_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="Blues", title="Feature Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)

with tab_model:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Accuracy", f"{metrics['accuracy']*100:.1f}%")
    with c2: kpi_card("Precision", f"{metrics['precision']*100:.1f}%")
    with c3: kpi_card("Recall", f"{metrics['recall']*100:.1f}%")
    with c4: kpi_card("F1 Score", f"{metrics['f1']*100:.1f}%")
    with c5: kpi_card("ROC-AUC", f"{metrics['roc_auc']:.3f}")

    c6, c7 = st.columns(2)
    with c6:
        fi_df = get_feature_importance_df()
        fig = px.bar(fi_df, x="importance", y="feature", orientation="h", title="Feature Importance",
                     color_discrete_sequence=["#2563EB"])
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with c7:
        cm = np.array(metrics["confusion_matrix"])
        fig = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                         labels=dict(x="Predicted", y="Actual", color="Count"),
                         x=["Not Placed", "Placed"], y=["Not Placed", "Placed"],
                         title="Confusion Matrix")
        st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=metrics["roc_fpr"], y=metrics["roc_tpr"], mode="lines", name="ROC Curve", line=dict(color="#2563EB", width=3)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(color="#94A3B8", dash="dash")))
    fig.update_layout(title=f"ROC Curve (AUC = {metrics['roc_auc']:.3f})", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate", height=380)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Salary regression model R² score: {metrics['salary_r2']:.3f}")

with tab_trends:
    if len(history):
        history["created_at"] = pd.to_datetime(history["created_at"])
        history["date"] = history["created_at"].dt.date
        daily = history.groupby("date").size().reset_index(name="predictions")
        fig = px.line(daily, x="date", y="predictions", title="Prediction Trends Over Time", markers=True,
                      color_discrete_sequence=["#2563EB"])
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(history, x="department", color="placement_status", barmode="group",
                                title="Live Predictions by Department", color_discrete_sequence=["#2563EB", "#F59E0B"])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            monthly = history.copy()
            monthly["month"] = monthly["created_at"].dt.to_period("M").astype(str)
            monthly_avg = monthly.groupby("month")["probability"].mean().reset_index()
            fig = px.bar(monthly_avg, x="month", y="probability", title="Monthly Avg. Placement Probability",
                         color_discrete_sequence=["#22C55E"])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No live predictions yet. Run a prediction to populate this tab.")
