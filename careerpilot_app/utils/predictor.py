"""
Loads the trained models and exposes simple predict_* functions used by pages.
Falls back to training on first run if artifacts are missing.
"""
import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


def _ensure_models():
    needed = ["placement_model.pkl", "salary_model.pkl", "scaler.pkl", "encoders.pkl", "metrics.pkl", "feature_columns.pkl"]
    if not all(os.path.exists(os.path.join(MODEL_DIR, f)) for f in needed):
        from utils.train_model import train_and_save
        train_and_save()


def load_artifacts():
    _ensure_models()
    clf = joblib.load(os.path.join(MODEL_DIR, "placement_model.pkl"))
    reg = joblib.load(os.path.join(MODEL_DIR, "salary_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
    metrics = joblib.load(os.path.join(MODEL_DIR, "metrics.pkl"))
    feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))
    return clf, reg, scaler, encoders, metrics, feature_columns


def _build_feature_row(student, encoders, feature_columns):
    row = {
        "age": student["age"],
        "cgpa": student["cgpa"],
        "internships": student["internships"],
        "projects": student["projects"],
        "programming_skills": student["programming_skills"],
        "communication_skills": student["communication_skills"],
        "aptitude_score": student["aptitude_score"],
        "technical_score": student["technical_score"],
        "work_experience": student["work_experience"],
        "certifications": student["certifications"],
        "soft_skills": student["soft_skills"],
        "leadership": int(student["leadership"]),
        "hackathons": student["hackathons"],
    }
    for col, src_key in [("gender_code", "gender"), ("department_code", "department"), ("degree_code", "degree")]:
        le = encoders[col]
        val = student[src_key]
        if val not in le.classes_:
            val = le.classes_[0]
        row[col] = le.transform([val])[0]

    df = pd.DataFrame([row])
    return df[feature_columns]


def predict_placement(student: dict):
    clf, reg, scaler, encoders, metrics, feature_columns = load_artifacts()
    X = _build_feature_row(student, encoders, feature_columns)
    X_scaled = scaler.transform(X)
    proba = clf.predict_proba(X_scaled)[0][1]
    status = "Placed" if proba >= 0.5 else "Not Placed"
    risk_score = round((1 - proba) * 100, 1)
    return {
        "status": status,
        "probability": round(proba * 100, 1),
        "risk_score": risk_score,
        "confidence": "High" if abs(proba - 0.5) > 0.3 else ("Medium" if abs(proba - 0.5) > 0.12 else "Low"),
    }


def predict_salary(student: dict):
    clf, reg, scaler, encoders, metrics, feature_columns = load_artifacts()
    X = _build_feature_row(student, encoders, feature_columns)
    X_scaled = scaler.transform(X)
    pred = reg.predict(X_scaled)[0]
    pred = float(np.clip(pred, 3.0, 45.0))
    return {
        "expected": round(pred, 2),
        "min": round(max(3.0, pred * 0.82), 2),
        "max": round(pred * 1.28, 2),
    }


def get_metrics():
    _ensure_models()
    return joblib.load(os.path.join(MODEL_DIR, "metrics.pkl"))


def get_feature_importance_df():
    metrics = get_metrics()
    fi = metrics["feature_importance"]
    df = pd.DataFrame({"feature": list(fi.keys()), "importance": list(fi.values())})
    return df.sort_values("importance", ascending=False)
