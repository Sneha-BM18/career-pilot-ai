"""
Generates a synthetic (but realistic-feeling) student placement dataset and
trains two Scikit-learn models:
  1. RandomForestClassifier  -> placement probability
  2. RandomForestRegressor   -> expected salary (LPA)

Run this once with `python utils/train_model.py` to (re)generate:
  data/students.csv
  models/placement_model.pkl
  models/salary_model.pkl
  models/metrics.pkl
  models/scaler.pkl
"""
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

DEPARTMENTS = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Electrical"]
DEGREES = ["B.Tech", "B.E", "M.Tech", "BCA", "MCA"]
GENDERS = ["Male", "Female", "Other"]

FEATURE_COLUMNS = [
    "age", "gender_code", "department_code", "degree_code", "cgpa",
    "internships", "projects", "programming_skills", "communication_skills",
    "aptitude_score", "technical_score", "work_experience", "certifications",
    "soft_skills", "leadership", "hackathons"
]


def generate_dataset(n=2500, seed=42):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "name": [f"Student_{i:04d}" for i in range(n)],
        "age": rng.integers(20, 24, n),
        "gender": rng.choice(GENDERS, n, p=[0.55, 0.42, 0.03]),
        "department": rng.choice(DEPARTMENTS, n),
        "degree": rng.choice(DEGREES, n, p=[0.45, 0.2, 0.1, 0.1, 0.15]),
        "cgpa": np.clip(rng.normal(7.4, 1.0, n), 5.0, 10.0).round(2),
        "internships": rng.integers(0, 4, n),
        "projects": rng.integers(0, 6, n),
        "programming_skills": rng.integers(30, 100, n),
        "communication_skills": rng.integers(30, 100, n),
        "aptitude_score": rng.integers(30, 100, n),
        "technical_score": rng.integers(30, 100, n),
        "work_experience": rng.integers(0, 24, n),
        "certifications": rng.integers(0, 6, n),
        "soft_skills": rng.integers(30, 100, n),
        "leadership": rng.integers(0, 2, n),
        "hackathons": rng.integers(0, 5, n),
    })

    # Encode categorical for a latent "placement score"
    dep_weight = {d: w for d, w in zip(DEPARTMENTS, [1.15, 1.1, 0.95, 0.9, 0.85, 0.95])}
    df["dep_w"] = df["department"].map(dep_weight)

    latent = (
        df["cgpa"] * 9
        + df["internships"] * 6
        + df["projects"] * 3
        + df["programming_skills"] * 0.35
        + df["communication_skills"] * 0.15
        + df["aptitude_score"] * 0.2
        + df["technical_score"] * 0.3
        + df["work_experience"] * 0.4
        + df["certifications"] * 3
        + df["soft_skills"] * 0.1
        + df["leadership"] * 5
        + df["hackathons"] * 3
        + df["dep_w"] * 10
        + rng.normal(0, 12, n)
    )
    threshold = np.percentile(latent, 38)  # ~62% placement rate, realistic
    df["placed"] = (latent > threshold).astype(int)

    # Salary depends on similar signals + placement
    base_salary = (
        3.0
        + df["cgpa"] * 0.55
        + df["programming_skills"] * 0.03
        + df["technical_score"] * 0.025
        + df["internships"] * 0.35
        + df["certifications"] * 0.15
        + df["hackathons"] * 0.2
        + df["dep_w"] * 1.5
        + rng.normal(0, 1.1, n)
    )
    df["salary_lpa"] = np.where(df["placed"] == 1, np.clip(base_salary, 3.0, 45.0).round(2), 0.0)

    df.drop(columns=["dep_w"], inplace=True)
    return df


def encode_features(df, encoders=None, fit=True):
    df = df.copy()
    if encoders is None:
        encoders = {}
    for col, src in [("gender_code", "gender"), ("department_code", "department"), ("degree_code", "degree")]:
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[src])
            encoders[col] = le
        else:
            le = encoders[col]
            df[col] = df[src].map(lambda v: v if v in le.classes_ else le.classes_[0])
            df[col] = le.transform(df[col])
    return df, encoders


def train_and_save():
    df = generate_dataset()
    df.to_csv(os.path.join(DATA_DIR, "students.csv"), index=False)

    df_enc, encoders = encode_features(df, fit=True)
    X = df_enc[FEATURE_COLUMNS]
    y_class = df_enc["placed"]
    y_reg = df_enc["salary_lpa"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_class, test_size=0.2, random_state=42, stratify=y_class)
    clf = RandomForestClassifier(n_estimators=250, max_depth=10, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_importance": dict(zip(FEATURE_COLUMNS, clf.feature_importances_.tolist())),
    }
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    metrics["roc_fpr"] = fpr.tolist()
    metrics["roc_tpr"] = tpr.tolist()

    # Regression model only on placed students
    placed_mask = df_enc["placed"] == 1
    X_reg = scaler.transform(df_enc.loc[placed_mask, FEATURE_COLUMNS])
    y_reg_placed = df_enc.loc[placed_mask, "salary_lpa"]
    Xr_train, Xr_test, yr_train, yr_test = train_test_split(X_reg, y_reg_placed, test_size=0.2, random_state=42)
    reg = RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)
    reg.fit(Xr_train, yr_train)
    metrics["salary_r2"] = reg.score(Xr_test, yr_test)

    joblib.dump(clf, os.path.join(MODEL_DIR, "placement_model.pkl"))
    joblib.dump(reg, os.path.join(MODEL_DIR, "salary_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    joblib.dump(encoders, os.path.join(MODEL_DIR, "encoders.pkl"))
    joblib.dump(metrics, os.path.join(MODEL_DIR, "metrics.pkl"))
    joblib.dump(FEATURE_COLUMNS, os.path.join(MODEL_DIR, "feature_columns.pkl"))

    print("Training complete.")
    print(f"Accuracy: {metrics['accuracy']:.3f} | F1: {metrics['f1']:.3f} | ROC-AUC: {metrics['roc_auc']:.3f}")
    print(f"Salary model R^2: {metrics['salary_r2']:.3f}")
    return metrics


if __name__ == "__main__":
    train_and_save()
