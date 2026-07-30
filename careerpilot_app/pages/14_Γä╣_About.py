import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, feature_card, init_theme_state
from utils.auth import init_db
from utils.predictor import get_metrics

st.set_page_config(page_title="About · CareerPilot AI", page_icon="ℹ️", layout="wide")
init_db(); init_theme_state(); inject_css()

hero("ℹ️ About CareerPilot AI", "AI-Powered Placement Prediction & Career Guidance Platform.")

st.markdown("""
### Project Overview
CareerPilot AI predicts a student's placement probability and expected salary from their academic
and skill profile, then turns that prediction into a concrete, prioritized action plan — skill gaps
to close, companies to target, and a career roadmap to follow.
""")

c1, c2, c3 = st.columns(3)
with c1:
    feature_card("🧠", "Machine Learning", "RandomForest classifier + regressor trained with Scikit-learn on a realistic synthetic dataset.")
with c2:
    feature_card("📊", "Analytics", "Interactive Plotly dashboards covering distributions, correlations, and model performance.")
with c3:
    feature_card("📁", "Reports", "Professional PDF/CSV/Excel/JSON exports with QR codes, ready to share.")

st.markdown("### 🧰 Technology Stack")
stack = ["Python", "Streamlit", "Pandas", "NumPy", "Scikit-learn", "Plotly", "Matplotlib",
         "Joblib", "SQLite", "OpenPyXL", "ReportLab", "qrcode"]
cols = st.columns(4)
for i, tech in enumerate(stack):
    with cols[i % 4]:
        st.markdown(f"""<div class="cp-card" style="text-align:center; padding:14px;"><b>{tech}</b></div>""", unsafe_allow_html=True)
        st.write("")

st.markdown("### 🧪 Machine Learning Model")
try:
    metrics = get_metrics()
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Accuracy", f"{metrics['accuracy']*100:.1f}%")
    with m2: st.metric("F1 Score", f"{metrics['f1']*100:.1f}%")
    with m3: st.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
    with m4: st.metric("Salary R²", f"{metrics['salary_r2']:.3f}")
except Exception:
    st.caption("Model metrics will appear here once trained.")

st.markdown("""
### 👨‍💻 Developers
Built as a full-stack AI product demo — Senior Full Stack Engineering, UI/UX Design,
Data Science, and Product Design all rolled into one codebase.

### 📄 Version & License
**Version:** 1.0.0
**License:** MIT — free to use, modify, and extend for academic or portfolio purposes.

### ✉️ Contact
For questions or feature requests, open an issue in your project repository or reach out to your team.

---
*CareerPilot AI is an educational/demo project. Predictions are AI-generated estimates for guidance
and do not guarantee real-world placement outcomes.*
""")
