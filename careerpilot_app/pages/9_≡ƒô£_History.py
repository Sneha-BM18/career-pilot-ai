import streamlit as st
import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, kpi_card, init_theme_state
from utils.auth import init_db, require_login, current_user
from utils.db import get_history, delete_prediction

st.set_page_config(page_title="History · CareerPilot AI", page_icon="📜", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("📜 Prediction History", "Every prediction you've run, searchable, filterable, and exportable.")

user = current_user()
scope = st.radio("Show", ["My predictions", "All predictions (if permitted)"], horizontal=True)
history = get_history(user["email"] if scope == "My predictions" or user["role"] != "admin" else None)

if history.empty:
    st.info("No predictions yet. Head to the Prediction page to run your first one.")
    st.stop()

c1, c2, c3 = st.columns(3)
with c1: kpi_card("Total Records", len(history))
with c2: kpi_card("Placed", int((history["placement_status"] == "Placed").sum()))
with c3: kpi_card("Avg. Probability", f"{history['probability'].mean():.1f}%")

st.markdown("### 🔎 Search & Filter")
f1, f2, f3, f4 = st.columns(4)
with f1:
    search = st.text_input("Search by student name")
with f2:
    dept_filter = st.multiselect("Department", sorted(history["department"].dropna().unique().tolist()))
with f3:
    status_filter = st.multiselect("Status", sorted(history["placement_status"].dropna().unique().tolist()))
with f4:
    sort_by = st.selectbox("Sort by", ["created_at", "probability", "cgpa", "predicted_salary"])

filtered = history.copy()
if search:
    filtered = filtered[filtered["student_name"].str.contains(search, case=False, na=False)]
if dept_filter:
    filtered = filtered[filtered["department"].isin(dept_filter)]
if status_filter:
    filtered = filtered[filtered["placement_status"].isin(status_filter)]
filtered = filtered.sort_values(sort_by, ascending=False)

st.markdown(f"### 📋 Results ({len(filtered)})")
st.dataframe(
    filtered[["id", "student_name", "department", "cgpa", "placement_status", "probability", "predicted_salary", "risk_score", "created_at"]],
    use_container_width=True, hide_index=True
)

c1, c2 = st.columns(2)
with c1:
    st.download_button("⬇️ Export filtered results (CSV)", filtered.to_csv(index=False), "prediction_history.csv", "text/csv", use_container_width=True)
with c2:
    del_id = st.number_input("Delete record by ID", min_value=0, step=1)
    if st.button("🗑️ Delete record", use_container_width=True):
        if del_id in filtered["id"].values:
            delete_prediction(int(del_id))
            st.success(f"Deleted record #{del_id}. Refresh to see the change.")
            st.rerun()
        else:
            st.error("ID not found in current results.")
