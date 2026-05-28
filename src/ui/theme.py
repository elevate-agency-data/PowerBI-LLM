"""Visual theme for the PowerBI Assistant — single CSS injection point.

Keeps every styling concern in one module so tabs and components stay free of
hard-coded styles (Single Responsibility). New themes can be added without
modifying existing components (Open/Closed).
"""

from __future__ import annotations

import streamlit as st

# ── Modern professional palette ──────────────────────────────────────────────
PRIMARY = "#4f46e5"        # indigo-600
PRIMARY_HOVER = "#4338ca"  # indigo-700
ACCENT = "#8b5cf6"         # violet-500
TEXT = "#0f172a"           # slate-900
MUTED = "#64748b"          # slate-500
BORDER = "#e2e8f0"         # slate-200
SURFACE = "#ffffff"
BG = "#f8fafc"             # slate-50
SUCCESS = "#10b981"        # emerald-500
WARNING = "#f59e0b"        # amber-500


def apply_theme() -> None:
    """Inject the global CSS and set page configuration."""
    st.set_page_config(
        page_title="Power BI Assistant",
        page_icon="💡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #0f172a;
}
.stApp { background: #f8fafc; }
[data-testid="stHeader"] { background: transparent; }

/* Main content area */
.block-container {
    padding-top: 1.75rem;
    padding-bottom: 4rem;
    max-width: 1180px;
}

/* ─── Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] [data-testid="stHeading"] h1,
[data-testid="stSidebar"] h1 {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    letter-spacing: 0.02em;
}

/* Sidebar brand block */
.pbi-brand {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.25rem 0 0.9rem 0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 1.1rem;
}
.pbi-brand-dot {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 4px 10px rgba(79,70,229,0.25);
}
.pbi-brand-name {
    font-weight: 700;
    color: #0f172a;
    font-size: 1.02rem;
    line-height: 1.1;
}
.pbi-brand-tag {
    color: #64748b;
    font-size: 0.78rem;
    margin-top: 2px;
}

/* Sidebar section heading */
.pbi-sidebar-section {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.7rem;
    color: #94a3b8;
    font-weight: 700;
    margin: 1.1rem 0 0.5rem 0;
    padding-top: 0.6rem;
    border-top: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ─── Tabs ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    border-bottom: 1px solid #e2e8f0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    height: 46px;
    padding: 0 1.1rem;
    background: transparent !important;
    color: #64748b !important;
    font-weight: 600;
    font-size: 0.95rem;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.15s ease, border-color 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #0f172a !important; }
.stTabs [aria-selected="true"] {
    color: #4f46e5 !important;
    border-bottom-color: #4f46e5 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem; }

/* ─── Buttons ────────────────────────────────────────────────────────── */
.stButton button {
    background: #4f46e5;
    color: white !important;
    border: 1px solid #4f46e5;
    border-radius: 10px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    font-size: 0.93rem;
    box-shadow: 0 1px 2px rgba(15,23,42,0.06);
    transition: all 0.15s ease;
}
.stButton button:hover {
    background: #4338ca !important;
    border-color: #4338ca !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(79,70,229,0.28);
}
.stButton button:focus { box-shadow: 0 0 0 3px rgba(79,70,229,0.25) !important; }
.stDownloadButton button { background: #0f172a; border-color: #0f172a; }
.stDownloadButton button:hover { background: #1e293b !important; border-color: #1e293b !important; }

/* ─── File uploader ──────────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    background: #ffffff;
    border: 1.5px dashed #cbd5e1;
    border-radius: 12px;
    padding: 0.85rem;
    transition: border-color 0.15s ease, background 0.15s ease;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #4f46e5;
    background: #eef2ff;
}
[data-testid="stFileUploaderDropzone"] button {
    background: white !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #64748b !important;
}

/* ─── Inputs ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.15) !important;
}
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

/* ─── Alerts ─────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: white;
}

/* ─── Expanders ──────────────────────────────────────────────────────── */
[data-testid="stExpander"] details {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    background: white !important;
}
[data-testid="stExpander"] summary { font-weight: 600; color: #0f172a; }

/* ─── Hero ───────────────────────────────────────────────────────────── */
.pbi-hero {
    background: linear-gradient(135deg, #eef2ff 0%, #ffffff 55%, #f5f3ff 100%);
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 1.6rem 1.9rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.pbi-hero::after {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(closest-side, rgba(139,92,246,0.18), transparent);
    pointer-events: none;
}
.pbi-hero-eyebrow {
    color: #4f46e5;
    font-weight: 700;
    font-size: 0.74rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}
.pbi-hero-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 0.6rem 0;
    line-height: 1.18;
    letter-spacing: -0.01em;
}
.pbi-hero-subtitle {
    font-size: 1.02rem;
    color: #475569;
    margin: 0;
    line-height: 1.55;
    max-width: 720px;
}

/* ─── Feature cards ──────────────────────────────────────────────────── */
.pbi-feature-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}
.pbi-feature {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    transition: all 0.18s ease;
}
.pbi-feature:hover {
    box-shadow: 0 8px 24px rgba(15,23,42,0.07);
    border-color: #c7d2fe;
    transform: translateY(-1px);
}
.pbi-feature-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: #eef2ff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    margin-bottom: 0.65rem;
}
.pbi-feature-title {
    font-weight: 700;
    color: #0f172a;
    font-size: 1rem;
    margin: 0 0 0.3rem 0;
}
.pbi-feature-body {
    color: #64748b;
    font-size: 0.875rem;
    margin: 0;
    line-height: 1.55;
}

/* ─── Prereq pills strip ─────────────────────────────────────────────── */
.pbi-prereq-wrap {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.25rem;
    padding: 0.6rem 0.9rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    flex-wrap: wrap;
}
.pbi-prereq-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
    margin-right: 0.4rem;
    letter-spacing: 0.02em;
}
.pbi-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid;
}
.pbi-pill.ok { background: #ecfdf5; color: #047857; border-color: #a7f3d0; }
.pbi-pill.miss { background: #fffbeb; color: #b45309; border-color: #fde68a; }
.pbi-pill-dot {
    width: 6px; height: 6px;
    border-radius: 999px;
    background: currentColor;
    display: inline-block;
}

/* ─── Section headers (inside tabs) ──────────────────────────────────── */
.pbi-section-eyebrow {
    color: #4f46e5;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.pbi-section-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.005em;
}
.pbi-section-sub {
    color: #64748b;
    font-size: 0.95rem;
    margin: 0 0 1.25rem 0;
    line-height: 1.55;
    max-width: 720px;
}

/* ─── Chat ───────────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 0.55rem 0.95rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
}
[data-testid="stChatInput"] {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
}

/* ─── Empty-state card for Chat ──────────────────────────────────────── */
.pbi-empty {
    background: white;
    border: 1px dashed #cbd5e1;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    color: #64748b;
    margin: 0.5rem 0 1rem 0;
}
.pbi-empty-title { font-weight: 700; color: #0f172a; margin-bottom: 0.3rem; }

/* Streamlit footer hide */
footer { visibility: hidden; }

/* Compact spacing tweaks */
[data-testid="stVerticalBlock"] > div:has(> div.pbi-hero) { margin-bottom: 0 !important; }
</style>
"""
