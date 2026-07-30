import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, toggle_theme, init_theme_state
from utils.auth import init_db, require_login, current_user, get_conn

st.set_page_config(page_title="Settings · CareerPilot AI", page_icon="⚙️", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("⚙️ Settings", "Manage your profile, theme, language, and notification preferences.")

user = current_user()

tab_profile, tab_appearance, tab_notify, tab_account = st.tabs(["👤 Profile", "🎨 Appearance", "🔔 Notifications", "🔐 Account"])

with tab_profile:
    st.markdown("#### Profile Details")
    name = st.text_input("Full name", value=user["name"])
    email = st.text_input("Email", value=user["email"], disabled=True)
    department = st.selectbox("Department", ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical"])
    if st.button("Save profile", type="primary"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET name=?, department=? WHERE email=?", (name, department, user["email"]))
        conn.commit()
        conn.close()
        st.session_state.auth_user["name"] = name
        st.success("Profile updated.")
        st.rerun()

with tab_appearance:
    st.markdown("#### Theme")
    current = st.session_state.theme
    st.write(f"Current theme: **{current.capitalize()}**")
    if st.button("🌙 Switch to Dark" if current == "light" else "☀️ Switch to Light"):
        toggle_theme()
        st.rerun()

    st.markdown("#### Language")
    st.selectbox("Interface language", ["English", "Hindi (coming soon)", "Tamil (coming soon)", "Telugu (coming soon)"], disabled=False)
    st.caption("Multi-language support is UI-ready; hook up an i18n dictionary to activate translations.")

with tab_notify:
    st.markdown("#### Notification Preferences")
    st.toggle("Email me when a new prediction is saved", value=True)
    st.toggle("Weekly skill-gap reminder", value=True)
    st.toggle("Product updates & tips", value=False)
    st.caption("These are UI-ready preferences — wire up an email service (e.g. SMTP or SendGrid) to make them functional.")

with tab_account:
    st.markdown("#### Account")
    st.write(f"Role: **{user['role']}**")
    new_pw = st.text_input("New password", type="password")
    if st.button("Update password"):
        if len(new_pw) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            import hashlib, secrets
            salt = secrets.token_hex(8)
            pw_hash = hashlib.sha256((salt + new_pw).encode()).hexdigest()
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash=?, salt=? WHERE email=?", (pw_hash, salt, user["email"]))
            conn.commit()
            conn.close()
            st.success("Password updated.")

    st.divider()
    st.markdown("#### Danger zone")
    if st.button("🚪 Log out of all sessions"):
        from utils.auth import logout
        logout()
        st.rerun()
