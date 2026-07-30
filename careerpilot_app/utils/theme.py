"""
Theme & styling module for CareerPilot AI.
Implements the required color palette, glassmorphism cards, gradient hero,
rounded corners, soft shadows, and a persistent dark/light mode toggle.
"""
import streamlit as st

PRIMARY = "#2563EB"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"
BG_LIGHT = "#F8FAFC"
CARD_LIGHT = "#FFFFFF"
BG_DARK = "#0B1120"
CARD_DARK = "#151C2C"


def init_theme_state():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


def inject_css():
    """Injects global CSS respecting the current theme."""
    init_theme_state()
    dark = st.session_state.theme == "dark"

    bg = BG_DARK if dark else BG_LIGHT
    card = CARD_DARK if dark else CARD_LIGHT
    text = "#E5E9F2" if dark else "#0F172A"
    subtext = "#8B94A8" if dark else "#64748B"
    border = "rgba(255,255,255,0.08)" if dark else "rgba(15,23,42,0.06)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {bg};
        color: {text};
    }}

    section[data-testid="stSidebar"] {{
        background: {card};
        border-right: 1px solid {border};
    }}

    h1, h2, h3, h4 {{
        font-family: 'Poppins', sans-serif;
        color: {text};
    }}

    p, span, label, div {{
        color: {text};
    }}

    .cp-subtext {{ color: {subtext} !important; }}

    /* ---- Hero ---- */
    .cp-hero {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #1E40AF 45%, #0EA5E9 100%);
        border-radius: 24px;
        padding: 64px 48px;
        color: white;
        box-shadow: 0 30px 60px -20px rgba(37,99,235,0.45);
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }}
    .cp-hero::after {{
        content: "";
        position: absolute; top: -60px; right: -60px;
        width: 260px; height: 260px; border-radius: 50%;
        background: rgba(255,255,255,0.12);
    }}
    .cp-hero h1 {{ color: white !important; font-size: 2.6rem; font-weight: 800; margin-bottom: 12px; }}
    .cp-hero p {{ color: rgba(255,255,255,0.9) !important; font-size: 1.05rem; max-width: 620px; }}
    .cp-badge {{
        display:inline-block; background: rgba(255,255,255,0.18); color:white;
        padding: 6px 14px; border-radius: 999px; font-size: 0.8rem; font-weight:600;
        margin-bottom: 18px; backdrop-filter: blur(6px);
    }}

    /* ---- Cards ---- */
    .cp-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 22px 22px;
        box-shadow: 0 8px 24px -12px rgba(15,23,42,0.12);
        transition: transform .2s ease, box-shadow .2s ease;
        height: 100%;
    }}
    .cp-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -16px rgba(37,99,235,0.25);
        border-color: rgba(37,99,235,0.35);
    }}
    .cp-card .cp-icon {{ font-size: 1.8rem; margin-bottom: 10px; display:block; }}
    .cp-card h4 {{ margin: 0 0 6px 0; font-size: 1.05rem; }}
    .cp-card p {{ font-size: 0.86rem; color: {subtext} !important; margin: 0; line-height:1.5; }}

    /* ---- Glass card ---- */
    .cp-glass {{
        background: rgba(255,255,255,{'0.06' if dark else '0.55'});
        backdrop-filter: blur(14px);
        border: 1px solid {border};
        border-radius: 18px;
        padding: 20px;
    }}

    /* ---- KPI ---- */
    .cp-kpi {{
        background: {card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 6px 18px -12px rgba(15,23,42,0.15);
    }}
    .cp-kpi .val {{ font-family:'Poppins',sans-serif; font-size: 1.6rem; font-weight:800; color: {PRIMARY}; }}
    .cp-kpi .lbl {{ font-size: 0.78rem; color: {subtext}; text-transform: uppercase; letter-spacing: .04em; font-weight:600;}}
    .cp-kpi .delta-up {{ color: {SUCCESS}; font-size: 0.78rem; font-weight:600; }}
    .cp-kpi .delta-warn {{ color: {WARNING}; font-size: 0.78rem; font-weight:600; }}

    /* ---- Badges / pills ---- */
    .cp-pill {{
        display:inline-block; padding: 4px 12px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 700; margin: 2px 4px 2px 0;
    }}
    .cp-pill-green {{ background: rgba(34,197,94,0.15); color: {SUCCESS}; }}
    .cp-pill-amber {{ background: rgba(245,158,11,0.15); color: {WARNING}; }}
    .cp-pill-red {{ background: rgba(239,68,68,0.15); color: {DANGER}; }}
    .cp-pill-blue {{ background: rgba(37,99,235,0.15); color: {PRIMARY}; }}

    /* Buttons */
    .stButton>button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid {border} !important;
        transition: all .15s ease;
    }}
    .stButton>button[kind="primary"] {{
        background: {PRIMARY} !important;
        box-shadow: 0 10px 24px -10px rgba(37,99,235,0.5);
    }}
    .stButton>button:hover {{ transform: translateY(-1px); }}

    /* Section title */
    .cp-section-eyebrow {{
        color: {PRIMARY}; font-weight: 700; font-size: 0.78rem;
        letter-spacing: .08em; text-transform: uppercase; margin-bottom: 6px;
    }}

    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def hero(title, subtitle, badge="✨ AI-Powered Career Platform"):
    st.markdown(f"""
    <div class="cp-hero">
        <span class="cp-badge">{badge}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon, title, desc):
    st.markdown(f"""
    <div class="cp-card">
        <span class="cp-icon">{icon}</span>
        <h4>{title}</h4>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, delta=None, delta_type="up"):
    delta_html = ""
    if delta:
        cls = "delta-up" if delta_type == "up" else "delta-warn"
        delta_html = f'<div class="{cls}">{delta}</div>'
    st.markdown(f"""
    <div class="cp-kpi">
        <div class="lbl">{label}</div>
        <div class="val">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def pill(text, kind="blue"):
    return f'<span class="cp-pill cp-pill-{kind}">{text}</span>'
