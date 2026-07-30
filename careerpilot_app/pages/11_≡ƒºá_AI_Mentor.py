import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_css, hero, init_theme_state
from utils.auth import init_db, require_login

st.set_page_config(page_title="AI Mentor · CareerPilot AI", page_icon="🧠", layout="wide")
init_db(); init_theme_state(); inject_css()
require_login()

hero("🧠 AI Career Mentor", "Ask about interview prep, resumes, projects, certifications, or coding practice. Runs fully offline with a rule-based response engine — swap in an LLM API key any time.")

KB = [
    (["tcs", "infosys", "wipro", "cognizant", "capgemini", "accenture"], lambda q: (
        "For mass-recruiter interviews (TCS/Infosys/Wipro/Cognizant/Capgemini/Accenture), focus on:\n"
        "1) **Aptitude & reasoning** — practice daily on IndiaBix / PrepInsta.\n"
        "2) **Communication round** — prepare a crisp 60-second self-intro and 2-3 project stories using the STAR method.\n"
        "3) **Technical basics** — OOPs, DBMS, OS, and one language in depth (Java/Python).\n"
        "4) Review your resume for consistent formatting and be ready to explain every line."
    )),
    (["amazon", "microsoft", "google", "product", "faang"], lambda q: (
        "For product-company interviews (Amazon/Microsoft/Google):\n"
        "1) **DSA is non-negotiable** — grind LeetCode Medium/Hard, focus on patterns not just problems.\n"
        "2) **System design basics** even for freshers — read 'Grokking the System Design Interview'.\n"
        "3) Prepare **behavioral stories** mapped to leadership principles (especially for Amazon).\n"
        "4) Have 1-2 projects you can discuss at a deep technical level, including trade-offs you made."
    )),
    (["resume", "cv"], lambda q: (
        "Quick resume wins:\n"
        "- Keep it to **1 page**, use a clean ATS-friendly template (no tables/graphics).\n"
        "- Lead bullets with **action verbs** and quantify impact (%, time saved, users reached).\n"
        "- Put your **skills section** near the top, matched to the job description keywords.\n"
        "- Check the Resume Analyzer page for your personalized ATS score and checklist."
    )),
    (["project", "projects"], lambda q: (
        "Good fresher project ideas:\n"
        "- A **full-stack app** solving a real campus/local problem (shows end-to-end ownership).\n"
        "- An **open-source contribution** — even 2-3 merged PRs stand out.\n"
        "- A small **ML/data project** with a clear dataset, EDA, and a deployed demo.\n"
        "Pick 2-3 you can talk about in depth rather than 6 shallow ones."
    )),
    (["certification", "certificate", "course"], lambda q: (
        "Certifications that actually help freshers:\n"
        "- **NPTEL** certification in a core subject relevant to your branch.\n"
        "- A **cloud fundamentals** badge (AWS Cloud Practitioner / Azure Fundamentals).\n"
        "- A **HackerRank Skill Certification** in your primary language.\n"
        "Pick 1-2 and finish them — don't collect certificates without applying the skill."
    )),
    (["coding", "dsa", "leetcode", "improve"], lambda q: (
        "To improve coding skills systematically:\n"
        "1) Pick **one language** and get comfortable with its syntax and standard library.\n"
        "2) Do **pattern-based DSA practice** (arrays → two pointers → sliding window → trees → graphs → DP).\n"
        "3) Solve 3-5 problems/week consistently rather than binging — consistency beats volume.\n"
        "4) Re-solve problems you struggled with after a week to reinforce the pattern."
    )),
    (["interview", "prepare", "preparation"], lambda q: (
        "General interview prep checklist:\n"
        "- Research the company's products and recent news.\n"
        "- Prepare 3-4 STAR-format stories (Situation, Task, Action, Result).\n"
        "- Practice explaining your resume projects out loud, not just reading them.\n"
        "- Prepare 2-3 thoughtful questions to ask the interviewer.\n"
        "- Do at least one mock interview before the real one."
    )),
    (["salary", "negotiat"], lambda q: (
        "On salary: check the **Salary Predictor** page for your expected band based on your profile. "
        "In negotiations, always let the company state a number first if possible, and negotiate based on "
        "market data and the value of your skills — not just personal need."
    )),
    (["skill gap", "skills", "weak"], lambda q: (
        "Head to the **Skills gap** page — it shows your current vs. required levels per skill, "
        "ranked by priority, each mapped to a specific course. Start with the 'High priority' ones first."
    )),
]

DEFAULT_REPLY = (
    "I don't have a scripted answer for that yet, but here's what generally helps: check the **Skills gap** "
    "page for a personalized roadmap, the **Career** page for suggested paths, and the **Resume Analyzer** "
    "for concrete resume fixes. You can also try asking about a specific company, resume, projects, "
    "certifications, coding practice, interviews, or salary."
)

SAMPLE_QUESTIONS = [
    "How do I prepare for TCS?",
    "How can I improve my resume?",
    "What projects should I build?",
    "What certifications should I complete?",
    "How do I prepare for interviews?",
    "How can I improve my coding skills?",
]


def get_reply(query):
    q = query.lower()
    for keywords, responder in KB:
        if any(k in q for k in keywords):
            return responder(q)
    return DEFAULT_REPLY


if "mentor_chat" not in st.session_state:
    st.session_state.mentor_chat = [
        {"role": "assistant", "content": "Hi! I'm your AI Career Mentor. Ask me about interview prep, resumes, projects, certifications, or coding practice."}
    ]

st.markdown("#### 💡 Try asking:")
cols = st.columns(3)
for i, q in enumerate(SAMPLE_QUESTIONS):
    with cols[i % 3]:
        if st.button(q, use_container_width=True, key=f"sample_{i}"):
            st.session_state.mentor_chat.append({"role": "user", "content": q})
            st.session_state.mentor_chat.append({"role": "assistant", "content": get_reply(q)})

st.divider()

for msg in st.session_state.mentor_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_q = st.chat_input("Ask your career mentor anything...")
if user_q:
    st.session_state.mentor_chat.append({"role": "user", "content": user_q})
    reply = get_reply(user_q)
    st.session_state.mentor_chat.append({"role": "assistant", "content": reply})
    st.rerun()
