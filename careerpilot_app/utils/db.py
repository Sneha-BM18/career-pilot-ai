"""
Prediction history storage (SQLite) — supports create, list, filter, update, delete.
"""
import json
import pandas as pd
from utils.auth import get_conn


def save_prediction(user_email, student, prediction, salary):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO predictions (user_email, student_name, department, cgpa, placement_status,
                                  probability, predicted_salary, risk_score, raw_json)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        user_email, student["name"], student["department"], student["cgpa"],
        prediction["status"], prediction["probability"], salary["expected"],
        prediction["risk_score"], json.dumps({"student": student, "prediction": prediction, "salary": salary})
    ))
    conn.commit()
    pred_id = cur.lastrowid
    conn.close()
    return pred_id


def get_history(user_email=None):
    conn = get_conn()
    if user_email:
        df = pd.read_sql_query("SELECT * FROM predictions WHERE user_email=? ORDER BY created_at DESC", conn, params=(user_email,))
    else:
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY created_at DESC", conn)
    conn.close()
    return df


def delete_prediction(pred_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id=?", (pred_id,))
    conn.commit()
    conn.close()


def get_prediction(pred_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions WHERE id=?", (pred_id,))
    row = cur.fetchone()
    cols = [d[0] for d in cur.description]
    conn.close()
    return dict(zip(cols, row)) if row else None


def all_users_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT id, name, email, role, department, created_at FROM users ORDER BY created_at DESC", conn)
    conn.close()
    return df
