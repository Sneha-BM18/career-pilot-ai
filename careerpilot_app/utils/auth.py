"""
Authentication module for CareerPilot AI.
Handles Student / Admin login, signup, password hashing (SHA-256 + salt),
"remember me" via session state, and a Google-login-ready UI stub.
"""
import sqlite3
import hashlib
import secrets
import os
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "careerpilot.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            department TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            student_name TEXT,
            department TEXT,
            cgpa REAL,
            placement_status TEXT,
            probability REAL,
            predicted_salary REAL,
            risk_score REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            raw_json TEXT
        )
    """)
    conn.commit()

    # seed a default admin + demo student if empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        _create_user(conn, "Admin", "admin@careerpilot.ai", "admin123", role="admin")
        _create_user(conn, "Demo Student", "student@careerpilot.ai", "student123", role="student")
    conn.close()


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _create_user(conn, name, email, password, role="student", department=None):
    salt = secrets.token_hex(8)
    pw_hash = _hash_password(password, salt)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, salt, role, department) VALUES (?,?,?,?,?,?)",
            (name, email.lower().strip(), pw_hash, salt, role, department)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def register_user(name, email, password, role="student", department=None):
    conn = get_conn()
    ok = _create_user(conn, name, email, password, role, department)
    conn.close()
    return ok


def authenticate(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, password_hash, salt, role FROM users WHERE email=?", (email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    user_id, name, db_email, pw_hash, salt, role = row
    if _hash_password(password, salt) == pw_hash:
        return {"id": user_id, "name": name, "email": db_email, "role": role}
    return None


def is_logged_in():
    return st.session_state.get("auth_user") is not None


def current_user():
    return st.session_state.get("auth_user")


def login(user_dict, remember=False):
    st.session_state.auth_user = user_dict
    st.session_state.remember_me = remember


def logout():
    st.session_state.auth_user = None
    st.session_state.remember_me = False


def require_login():
    """Call at the top of protected pages."""
    if not is_logged_in():
        st.warning("🔒 Please log in from the Home page to access this feature.")
        st.stop()


def require_admin():
    require_login()
    if current_user().get("role") != "admin":
        st.error("⛔ This page is restricted to Admin accounts only.")
        st.stop()
