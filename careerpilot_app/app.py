import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from utils.theme import inject_css, hero, feature_card, kpi_card, toggle_theme, init_theme_state
from utils.auth import init_db, authenticate, register_user, login, logout, is_logged_in, current_user
from utils.db import get_history, all_users_df
from utils.predictor import get_metrics

st.set_page_config(page_title="CareerPilot AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

init_db()
init_theme_state()
inject_css()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### 🚀 CareerPilot AI")
    st.caption("AI-Powered Placement Prediction & Career Guidance")
    st.divider()

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption("🌙 Dark mode" if st.session_state.theme == "light" else "☀️ Light mode")
    with col_b:
        if st.button("Toggle", key="theme_toggle_btn", use_container_width=True):
            toggle_theme()
            st.rerun()

    st.divider()

    if is_logged_in():
        user = current_user()
        st.success(f"Signed in as **{user['name']}**  \n`{user['role']}`")
        if st.button("Log out", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.info("👋 Log in below to unlock Prediction, Analytics, History, Reports and more.")

    st.divider()
    st.caption("🏠 Home · 🤖 Prediction · 📊 Analytics · 🎯 Skills · 💼 Career\n📜 History · 📁 Reports · ⚙ Settings · 🌙 Theme · ℹ About")

# ---------------- Hero ----------------
hero(
    "Plot the route to your placement.",
    "CareerPilot AI predicts your placement probability, closes your skill gaps, and recommends the companies and salary range you're actually positioned for — powered by a trained Scikit-learn model, not guesswork."
)

# ---------------- Auth panel (if not logged in) ----------------
if not is_logged_in():
    tab_login, tab_signup = st.tabs(["🔐 Log in", "✨ Create account"])

    with tab_login:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Welcome back")
            email = st.text_input("Email", placeholder="student@careerpilot.ai", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")
            c1, c2 = st.columns(2)
            with c1:
                remember = st.checkbox("Remember me")
            with c2:
                st.markdown("<div style='text-align:right; padding-top:8px;'><a href='#'>Forgot password?</a></div>", unsafe_allow_html=True)

            if st.button("Log in →", type="primary", use_container_width=True):
                user = authenticate(email, password)
                if user:
                    login(user, remember)
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

            st.button("🔵 Continue with Google (UI demo)", use_container_width=True, disabled=True,
                       help="Google OAuth UI is ready — connect your OAuth client ID to activate.")

            with st.expander("Demo credentials"):
                st.code("Admin  → admin@careerpilot.ai / admin123\nStudent → student@careerpilot.ai / student123")

        with col2:
            st.markdown("#### Why students use CareerPilot")
            feature_card("🎯", "Know your odds", "See your real placement probability, not a guess — backed by a trained ML model.")
            st.write("")
            feature_card("🧭", "Close the gap", "Get a prioritized, personalized skill roadmap before your next application cycle.")

    with tab_signup:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Create your account")
            name = st.text_input("Full name", key="su_name")
            su_email = st.text_input("Email", key="su_email")
            department = st.selectbox("Department", ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical"])
            su_pw = st.text_input("Password", type="password", key="su_pw")
            role = st.radio("Account type", ["student", "admin"], horizontal=True)

            if st.button("Create account →", type="primary", use_container_width=True):
                if not name or not su_email or len(su_pw) < 6:
                    st.error("Fill in your name, a valid email, and a password of at least 6 characters.")
                else:
                    ok = register_user(name, su_email, su_pw, role=role, department=department)
                    if ok:
                        st.success("Account created! Head to the Log in tab.")
                    else:
                        st.error("An account with that email already exists.")
        with col2:
            st.markdown("#### What you'll get")
            feature_card("📄", "Instant reports", "Download a polished PDF placement report with QR code, ready to share.")
            st.write("")
            feature_card("🤖", "AI career mentor", "Ask questions about interview prep, resumes, and skills anytime.")

# ---------------- Signed-in home content ----------------
else:
    metrics = get_metrics()
    history = get_history()

    st.markdown("### 📊 Live Platform Stats")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Students", f"{len(all_users_df())}", "+ growing")
    with c2: kpi_card("Total Predictions", f"{len(history)}", "Live")
    with c3:
        placement_rate = (history["placement_status"].eq("Placed").mean() * 100) if len(history) else 0
        kpi_card("Placement Rate", f"{placement_rate:.0f}%", "of predictions")
    with c4: kpi_card("Model Accuracy", f"{metrics['accuracy']*100:.1f}%", "RandomForest")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        avg_cgpa = history["cgpa"].mean() if len(history) else 0
        kpi_card("Average CGPA", f"{avg_cgpa:.2f}")
    with c6:
        avg_sal = history["predicted_salary"].mean() if len(history) else 0
        kpi_card("Average Salary", f"₹{avg_sal:.1f} LPA")
    with c7: kpi_card("Active Users", f"{len(all_users_df())}")
    with c8: kpi_card("Companies Covered", "11")

    st.markdown("### 🧩 Everything on your flight plan")
    r1 = st.columns(4)
    feats = [
        ("🤖", "AI Placement Prediction", "Get your placement probability from a trained ML model."),
        ("🎯", "Skill Gap Analysis", "See exactly which skills to close, and in what order."),
        ("🧭", "Career Roadmap", "Personalized paths, internships, and certifications."),
        ("📄", "Resume Analyzer", "ATS score plus concrete resume, LinkedIn & GitHub tips."),
        ("🎤", "Interview Preparation", "Company-specific prep guidance from the AI mentor."),
        ("💰", "Salary Prediction", "Min / expected / max salary band for your profile."),
        ("🏢", "Company Recommendation", "Ranked companies you're actually eligible for."),
        ("📊", "Analytics Dashboard", "Explore placement trends with interactive Plotly charts."),
    ]
    for i, (icon, title, desc) in enumerate(feats):
        with r1[i % 4]:
            feature_card(icon, title, desc)
            st.write("")

    cta1, cta2 = st.columns(2)
    with cta1:
        if st.button("🤖 Start Prediction →", type="primary", use_container_width=True):
            st.switch_page("pages/2_Prediction.py")

    with cta2:
        if st.button("📊 Explore Dashboard →", use_container_width=True):
            st.switch_page("pages/3_Analytics.py")

    st.markdown("### 🕓 Recent Predictions")
    if len(history):
        st.dataframe(
            history[["student_name", "department", "cgpa", "placement_status", "probability", "predicted_salary", "created_at"]].head(6),
            use_container_width=True, hide_index=True
        )
    else:
        st.caption("No predictions yet — run your first one from the Prediction page.")

    st.markdown("### 💬 What students say")
    t1, t2, t3 = st.columns(3)
    testimonials = [
        ("Ananya R.", "Computer Science", "The skill-gap roadmap told me exactly what to fix. Went from 52% to 81% match in 3 weeks."),
        ("Rahul K.", "Mechanical", "Didn't expect an ML tool to actually recommend companies I'd realistically get into."),
        ("Priya S.", "Information Technology", "The PDF report looked more professional than anything my placement cell gave me."),
    ]
    for col, (n, d, q) in zip([t1, t2, t3], testimonials):
        with col:
            st.markdown(f"""<div class="cp-card"><p style="font-style:italic;">"{q}"</p>
            <p style="margin-top:10px;"><b>{n}</b><br/><span class="cp-subtext">{d}</span></p></div>""", unsafe_allow_html=True)

    st.markdown("### ❓ Frequently asked questions")
    with st.expander("How accurate is the placement prediction?"):
        st.write(f"Our RandomForest model is trained on a synthetic-but-realistic dataset and currently reports **{metrics['accuracy']*100:.1f}% accuracy** and **{metrics['roc_auc']:.2f} ROC-AUC** on held-out test data. See the Analytics page for full metrics.")
    with st.expander("Is my data stored anywhere?"):
        st.write("Predictions are stored locally in a SQLite database (`database/careerpilot.db`) so you can revisit your History — nothing is sent to an external server.")
    with st.expander("Can I bulk-predict for a whole class?"):
        st.write("Yes — head to the Prediction page and use the CSV Bulk Prediction section to upload a CSV of students.")

st.divider()
st.markdown("""
<div style="text-align:center; padding: 10px 0;">
<span class="cp-subtext">© 2026 CareerPilot AI · Built with Streamlit, Scikit-learn &amp; Plotly · Not affiliated with any placement cell</span>
</div>
""", unsafe_allow_html=True)
