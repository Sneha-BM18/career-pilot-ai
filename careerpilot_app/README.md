# 🚀 CareerPilot AI

AI-Powered Placement Prediction & Career Guidance Platform — built with Python, Streamlit,
Scikit-learn, Pandas, NumPy, and Plotly.

## ✨ Features

- 🔐 Student / Admin login & signup (SQLite-backed, hashed passwords)
- 🏠 Home page with hero, live stats, feature cards, testimonials, FAQ
- 🤖 AI placement prediction (RandomForestClassifier) with gauge, confidence, risk score
- 📁 CSV bulk prediction with Excel/CSV export
- 🎯 Skill-gap analysis with radar chart, prioritized roadmap, progress tracker
- 💼 Personalized career roadmap: internships, certifications, coding platforms, project ideas
- 📄 Resume analyzer with ATS-style score and checklist
- 💰 Salary prediction (RandomForestRegressor) with min/expected/max band
- 🏢 Company recommendation engine (TCS, Infosys, Amazon, Google, and more)
- 📊 Analytics dashboard: distributions, correlation heatmap, ROC curve, confusion matrix, feature importance
- 📜 Prediction history: search, filter, sort, delete, export
- 📁 Reports: PDF (with QR code), CSV, Excel, JSON export
- 🧠 AI career mentor chatbot (rule-based, fully offline)
- 🛠️ Admin dashboard: college-wide stats, department comparison, rankings
- 🌙 Dark / light theme toggle
- ⚙️ Settings: profile, appearance, notifications, account

## 🧰 Tech Stack

Python · Streamlit · Pandas · NumPy · Scikit-learn · Plotly · Joblib · SQLite · OpenPyXL · ReportLab · qrcode

## 📁 Folder Structure

```
careerpilot_app/
├── app.py                          # Home page + login/signup
├── pages/
│   ├── 2_🤖_Prediction.py
│   ├── 3_📊_Analytics.py
│   ├── 4_🎯_Skill_Gap.py
│   ├── 5_💼_Career_Guide.py
│   ├── 6_📄_Resume_Analyzer.py
│   ├── 7_💰_Salary_Predictor.py
│   ├── 8_🏢_Company_Recommendation.py
│   ├── 9_📜_History.py
│   ├── 10_📁_Reports.py
│   ├── 11_🧠_AI_Mentor.py
│   ├── 12_🛠️_Admin_Dashboard.py
│   ├── 13_⚙_Settings.py
│   └── 14_ℹ_About.py
├── utils/
│   ├── theme.py                    # colors, CSS, hero/card components
│   ├── auth.py                     # login/signup, SQLite users table
│   ├── db.py                       # prediction history CRUD
│   ├── train_model.py              # dataset generation + model training
│   ├── predictor.py                # loads models, runs predictions
│   ├── recommendations.py          # career/skill/resume/company rules engine
│   └── pdf_report.py               # ReportLab PDF report builder
├── models/                         # trained .pkl artifacts (auto-generated)
├── data/                           # students.csv (auto-generated)
├── database/                       # careerpilot.db (auto-generated)
├── reports/
├── assets/
└── requirements.txt
```

## ▶️ Run locally (VS Code / terminal)

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) pre-train the models — the app will also do this automatically on first run
python utils/train_model.py

# 4. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**.

## 🔑 Demo credentials

```
Admin:   admin@careerpilot.ai   / admin123
Student: student@careerpilot.ai / student123
```

Or just sign up for a new account from the "Create account" tab.

## 📝 Notes

- All data is **local** — SQLite database and trained model files are created automatically on first run;
  nothing is sent to an external server.
- The ML model is trained on a **synthetic but realistic** dataset generated in `utils/train_model.py`.
  Swap in your own labeled dataset there to train on real data.
- The AI Mentor is a **rule-based** offline chatbot. To connect a real LLM, replace the `get_reply()`
  function in `pages/11_🧠_AI_Mentor.py` with a call to your preferred API (OpenAI, Anthropic, etc.).
- Google login is a **UI-ready stub** (button is present but disabled) — wire up OAuth to activate it.

## 📄 License

MIT — free to use, modify, and extend for academic, portfolio, or hackathon purposes.
