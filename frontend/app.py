"""
BizGenie AI — Streamlit Frontend
Plain Text → Full Business Plan Agent
"""
import streamlit as st
import requests
import json
import time
import io
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Read backend URL from Streamlit secrets (cloud) or environment variable (local)
try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
except Exception:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BizGenie AI — Business Plan Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — Dark Premium Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

/* ── Root ── */
:root {
  --bg-primary:   #0f1117;
  --bg-secondary: #161b27;
  --bg-card:      #1a2035;
  --bg-card2:     #1e2640;
  --accent-purple:#7c3aed;
  --accent-blue:  #3b82f6;
  --accent-green: #10b981;
  --accent-orange:#f59e0b;
  --accent-pink:  #ec4899;
  --accent-cyan:  #06b6d4;
  --text-primary: #f1f5f9;
  --text-muted:   #94a3b8;
  --border:       #2d3748;
  --success:      #10b981;
  --warning:      #f59e0b;
  --danger:       #ef4444;
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Remove Streamlit default padding ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* ── Header ── */
.biz-header {
    background: linear-gradient(135deg, #1a1040 0%, #0f1840 50%, #0a1628 100%);
    border: 1px solid #2d3748;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 14px;
    margin-bottom: 1.2rem;
    gap: 1rem;
}
.biz-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: white;
    white-space: nowrap;
    flex-shrink: 0;
}
.biz-logo span { color: #a78bfa; }
.biz-title {
    text-align: center;
    flex: 1;
}
.biz-title h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    padding: 0;
    line-height: 1.2;
}
.biz-title p {
    color: var(--text-muted);
    font-size: 0.82rem;
    margin: 4px 0 0 0;
}
.header-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-shrink: 0;
}
.header-btn {
    background: #1e2a45;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.76rem;
    color: #94a3b8;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
}
.header-btn:hover { background: #253350; color: white; }
.header-btn-primary {
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.76rem;
    color: white;
    cursor: pointer;
    font-weight: 600;
    white-space: nowrap;
}

/* ── Metric Cards ── */
.metric-grid { display: flex; gap: 10px; flex-wrap: wrap; margin: 0.8rem 0; }
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    flex: 1;
    min-width: 110px;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.metric-icon { font-size: 1.3rem; margin-bottom: 5px; }
.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: white;
    margin: 2px 0;
}
.metric-label { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

/* ── Section Cards ── */
.section-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
    transition: transform 0.2s;
    height: 100%;
    box-sizing: border-box;
}
.section-card:hover { transform: translateY(-1px); }
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: center;
    gap: 7px;
}
.section-body { font-size: 0.81rem; color: var(--text-muted); line-height: 1.6; }
.section-body ul { padding-left: 1.1rem; margin: 0; }
.section-body li { margin-bottom: 3px; }

/* ── Progress Tracker ── */
.progress-step {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    border-radius: 8px;
    margin-bottom: 5px;
    background: var(--bg-card2);
    border: 1px solid var(--border);
    font-size: 0.82rem;
    transition: all 0.3s;
}
.step-icon { font-size: 0.95rem; min-width: 22px; text-align: center; }
.step-name { flex: 1; font-weight: 500; }
.step-status { font-size: 0.72rem; font-weight: 600; }
.step-completed .step-status { color: var(--success); }
.step-running .step-status { color: var(--warning); }
.step-pending .step-status { color: var(--text-muted); }

/* ── Competitor Table ── */
.comp-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.comp-table th {
    background: #1e2a45;
    color: var(--text-muted);
    text-transform: uppercase;
    font-size: 0.67rem;
    letter-spacing: 0.5px;
    padding: 7px 10px;
    text-align: left;
}
.comp-table td { padding: 7px 10px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
.comp-table tr:last-child td { border-bottom: none; }
.comp-table tr:hover td { background: rgba(255,255,255,0.03); }

/* ── SWOT Grid ── */
.swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.swot-box { border-radius: 9px; padding: 10px; }
.swot-s { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); }
.swot-w { background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.25); }
.swot-o { background: rgba(59,130,246,0.10); border: 1px solid rgba(59,130,246,0.25); }
.swot-t { background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.25); }
.swot-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
.swot-s .swot-label { color: #10b981; }
.swot-w .swot-label { color: #ef4444; }
.swot-o .swot-label { color: #3b82f6; }
.swot-t .swot-label { color: #f59e0b; }
.swot-item { font-size: 0.76rem; color: var(--text-muted); margin-bottom: 3px; }

/* ── Milestone ── */
.milestone-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.8rem;
}
.milestone-q {
    background: rgba(124,58,237,0.2);
    color: #a78bfa;
    border-radius: 6px;
    padding: 2px 7px;
    font-weight: 600;
    font-size: 0.72rem;
    white-space: nowrap;
    min-width: 76px;
    text-align: center;
}
.milestone-text { color: var(--text-primary); }

/* ── Generate Button ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.5) !important;
}
.stButton > button:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
}

/* Download button special style */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.35) !important;
    margin-top: 8px !important;
}
[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(16,185,129,0.5) !important;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}
.stTextArea textarea:focus { border-color: var(--accent-purple) !important; }

/* ── Sidebar ── */
[data-testid="stSidebarNav"] { display: none; }
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 4px;
    cursor: pointer;
    font-size: 0.87rem;
    color: var(--text-muted);
    transition: all 0.2s;
}
.sidebar-nav-item.active {
    background: rgba(124,58,237,0.2);
    color: #a78bfa;
    font-weight: 600;
}
.sidebar-nav-item:hover { background: rgba(255,255,255,0.05); color: white; }

/* ── Success Banner ── */
.success-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.1));
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 12px;
    padding: 0.85rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0.8rem 0;
}
.success-banner .icon { font-size: 1.4rem; }
.success-banner .text { font-weight: 600; color: #34d399; font-size: 0.9rem; }
.success-banner .sub { font-size: 0.77rem; color: var(--text-muted); }

/* ── Section Number Badge ── */
.section-badge {
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    color: white;
    border-radius: 5px;
    padding: 2px 7px;
    font-size: 0.7rem;
    font-weight: 700;
}
.section-badge-green { background: linear-gradient(135deg, #059669, #10b981); }
.section-badge-orange { background: linear-gradient(135deg, #d97706, #f59e0b); }
.section-badge-red { background: linear-gradient(135deg, #dc2626, #ef4444); }
.section-badge-cyan { background: linear-gradient(135deg, #0284c7, #06b6d4); }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 0.8rem 0 !important; }

/* ── Tab Bar ── */
.tab-bar {
    display: flex;
    gap: 5px;
    padding: 6px;
    background: var(--bg-secondary);
    border-radius: 10px;
    margin-top: 1rem;
    flex-wrap: wrap;
    border: 1px solid var(--border);
}
.tab-item {
    padding: 5px 12px;
    border-radius: 7px;
    font-size: 0.77rem;
    font-weight: 500;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s;
}
.tab-item.active { background: var(--accent-purple); color: white; }
.tab-item:hover:not(.active) { background: rgba(255,255,255,0.06); color: white; }

/* ── Streamlit Overrides ── */
[data-testid="stMarkdownContainer"] p { color: var(--text-muted); }
div[data-testid="stHorizontalBlock"] { gap: 0.8rem; }
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
.stDataFrame { background: var(--bg-card) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "new_plan"
if "plan_data" not in st.session_state:
    st.session_state.plan_data = None
if "agent_steps" not in st.session_state:
    st.session_state.agent_steps = {}
if "generating" not in st.session_state:
    st.session_state.generating = False
if "generated" not in st.session_state:
    st.session_state.generated = False
if "saved_plans" not in st.session_state:
    st.session_state.saved_plans = []
if "char_count" not in st.session_state:
    st.session_state.char_count = 0


# ─────────────────────────────────────────────
# Helper: Fetch saved plans
# ─────────────────────────────────────────────
def fetch_plans():
    try:
        r = requests.get(f"{BACKEND_URL}/api/plans", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def fetch_plan_by_id(plan_id: int):
    try:
        r = requests.get(f"{BACKEND_URL}/api/plans/{plan_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def delete_plan_api(plan_id: int):
    try:
        r = requests.delete(f"{BACKEND_URL}/api/plans/{plan_id}", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────
# Download Report Generator
# ─────────────────────────────────────────────
def generate_report_text(plan: dict) -> str:
    """Generate a well-formatted text report from the business plan."""
    lines = []
    es = plan.get("executive_summary", {})
    company = es.get("company_name", "Your Company")
    now = datetime.now().strftime("%B %d, %Y")

    lines.append("=" * 70)
    lines.append(f"  BIZGENIE AI — FULL BUSINESS PLAN REPORT")
    lines.append(f"  Generated: {now}")
    lines.append("=" * 70)
    lines.append("")

    # Executive Summary
    lines.append("━" * 70)
    lines.append("  EXECUTIVE SUMMARY")
    lines.append("━" * 70)
    lines.append(f"  Company:          {company}")
    lines.append(f"  Tagline:          {es.get('tagline', '')}")
    lines.append(f"  Industry:         {es.get('industry', '')}")
    lines.append(f"  Stage:            {es.get('stage', 'Seed')}")
    lines.append(f"  Market Size:      {es.get('market_size', '')}")
    lines.append(f"  Revenue (2028):   {es.get('revenue_projection', '')}")
    lines.append(f"  Users (2028):     {es.get('users_projection', '')}")
    lines.append(f"  Funding Needed:   {es.get('funding_required', '')}")
    lines.append("")
    lines.append(f"  Description:")
    lines.append(f"  {es.get('description', '')}")
    lines.append("")

    # Problem & Solution
    lines.append("━" * 70)
    lines.append("  1. PROBLEM STATEMENT")
    lines.append("━" * 70)
    lines.append(f"  {plan.get('problem_statement', '')}")
    lines.append("")

    lines.append("━" * 70)
    lines.append("  2. SOLUTION")
    lines.append("━" * 70)
    lines.append(f"  {plan.get('solution', '')}")
    lines.append("")

    # Market Opportunity
    lines.append("━" * 70)
    lines.append("  3. MARKET OPPORTUNITY")
    lines.append("━" * 70)
    for item in plan.get("market_opportunity", []):
        lines.append(f"  • {item}")
    lines.append("")

    # Target Audience
    lines.append("━" * 70)
    lines.append("  4. TARGET AUDIENCE")
    lines.append("━" * 70)
    for item in plan.get("target_audience", []):
        lines.append(f"  • {item}")
    lines.append("")

    # Business Model
    lines.append("━" * 70)
    lines.append("  5. BUSINESS MODEL")
    lines.append("━" * 70)
    bm = plan.get("business_model", {})
    streams = bm.get("revenue_streams", []) if isinstance(bm, dict) else []
    for s in streams:
        lines.append(f"  • {s}")
    lines.append(f"  Premium Revenue:  {bm.get('premium_percentage', 70)}%")
    lines.append(f"  Free Users:       {bm.get('free_percentage', 30)}%")
    lines.append("")

    # Competitor Analysis
    lines.append("━" * 70)
    lines.append("  6. COMPETITOR ANALYSIS")
    lines.append("━" * 70)
    lines.append(f"  {'Competitor':<28} {'Strengths':<22} {'Weaknesses'}")
    lines.append(f"  {'-'*28} {'-'*22} {'-'*20}")
    for c in plan.get("competitor_analysis", []):
        name = c.get("name", "")[:27]
        strength = c.get("strengths", "")[:21]
        weakness = c.get("weaknesses", "")[:30]
        lines.append(f"  {name:<28} {strength:<22} {weakness}")
    lines.append("")
    lines.append(f"  Competitive Advantage: {plan.get('competitive_advantage', '')}")
    lines.append("")

    # Marketing Strategy
    lines.append("━" * 70)
    lines.append("  7. MARKETING STRATEGY")
    lines.append("━" * 70)
    for s in plan.get("marketing_strategy", []):
        lines.append(f"  • {s}")
    lines.append(f"\n  Channels: {', '.join(plan.get('channels', []))}")
    lines.append("")

    # SWOT
    lines.append("━" * 70)
    lines.append("  8. SWOT ANALYSIS")
    lines.append("━" * 70)
    swot = plan.get("swot", {})
    for label, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses"),
                        ("Opportunities", "opportunities"), ("Threats", "threats")]:
        lines.append(f"  {label}:")
        for item in swot.get(key, []):
            lines.append(f"    – {item}")
    lines.append("")

    # Financial Projections
    lines.append("━" * 70)
    lines.append("  9. FINANCIAL PROJECTIONS")
    lines.append("━" * 70)
    financials = plan.get("financials", {})
    projections = financials.get("projections", [])
    lines.append(f"  {'Year':<8} {'Revenue':<12} {'Expenses':<12} {'Profit'}")
    lines.append(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*12}")
    for p in projections:
        lines.append(f"  {p.get('year',''):<8} {p.get('revenue',''):<12} {p.get('expenses',''):<12} {p.get('profit','')}")
    lines.append("")

    # Funding
    lines.append("━" * 70)
    lines.append("  10. FUNDING REQUIREMENTS")
    lines.append("━" * 70)
    fd = financials.get("funding_details", {})
    lines.append(f"  Amount:           {fd.get('amount', '')}")
    lines.append(f"  Type:             {fd.get('type', 'Seed Funding')}")
    lines.append(f"  Runway:           {financials.get('runway_months', 18)} months")
    lines.append(f"  Break-even:       {financials.get('break_even', '')}")
    alloc = fd.get("allocation", {})
    if alloc:
        lines.append("\n  Allocation:")
        for item, pct in alloc.items():
            lines.append(f"    • {item}: {pct}%")
    lines.append("")

    # Milestones
    lines.append("━" * 70)
    lines.append("  11. MILESTONE ROADMAP")
    lines.append("━" * 70)
    for m in plan.get("milestones", []):
        lines.append(f"  [{m.get('quarter','')}]  {m.get('milestone','')}")
    lines.append("")

    # Conclusion
    lines.append("━" * 70)
    lines.append("  12. CONCLUSION")
    lines.append("━" * 70)
    lines.append(f"  {plan.get('conclusion', '')}")
    lines.append("")
    lines.append("=" * 70)
    lines.append("  Generated by BizGenie AI  |  Powered by xAI Grok")
    lines.append("=" * 70)

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0 1.2rem;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#7c3aed,#3b82f6);
                    border-radius:9px;display:flex;align-items:center;justify-content:center;
                    font-size:1.1rem;">✨</div>
        <div>
            <div style="font-family:Outfit,sans-serif;font-weight:700;font-size:1.05rem;color:white;">BizGenie AI</div>
            <div style="font-size:0.68rem;color:#64748b;">Business Plan Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("📊", "Dashboard", "dashboard"),
        ("✨", "New Plan", "new_plan"),
        ("📁", "My Plans", "my_plans"),
        ("📋", "Templates", "templates"),
        ("🔍", "Market Research", "market_research"),
        ("💰", "Financial Tools", "financial_tools"),
        ("🎯", "Pitch Deck", "pitch_deck"),
        ("📈", "Reports", "reports"),
        ("🤖", "AI Chat Assistant", "ai_chat"),
    ]

    for icon, label, page_key in nav_items:
        active_class = "active" if st.session_state.page == page_key else ""
        if st.button(f"{icon}  {label}", key=f"nav_{page_key}",
                     use_container_width=True):
            st.session_state.page = page_key
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Recent Plans
    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:7px;'>Recent Plans</div>", unsafe_allow_html=True)
    plans = fetch_plans()
    if plans:
        for p in plans[:5]:
            col1, col2 = st.columns([4, 1])
            with col1:
                title_display = p['title'][:20] + "..." if len(p['title']) > 20 else p['title']
                if st.button(
                    f"📄 {title_display}",
                    key=f"plan_{p['id']}",
                    use_container_width=True
                ):
                    full = fetch_plan_by_id(p["id"])
                    if full and full.get("plan_data"):
                        st.session_state.plan_data = full["plan_data"]
                        st.session_state.generated = True
                        st.session_state.page = "new_plan"
                        st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{p['id']}"):
                    delete_plan_api(p["id"])
                    st.rerun()
    else:
        st.markdown("<div style='font-size:0.78rem;color:#475569;'>No plans yet.</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(59,130,246,0.15));
                border:1px solid rgba(124,58,237,0.4);border-radius:11px;padding:11px 13px;margin-top:6px;">
        <div style="font-size:0.78rem;font-weight:700;color:#a78bfa;margin-bottom:4px;">⚡ Upgrade to Pro</div>
        <div style="font-size:0.7rem;color:#64748b;margin-bottom:9px;">Unlock advanced features, custom templates, and more.</div>
        <div style="background:linear-gradient(135deg,#7c3aed,#3b82f6);border-radius:7px;padding:6px;
                    text-align:center;font-size:0.76rem;font-weight:600;color:white;cursor:pointer;">
            Upgrade Now
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:9px;padding:6px 0;">
        <div style="width:30px;height:30px;background:linear-gradient(135deg,#7c3aed,#ec4899);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:0.85rem;">👤</div>
        <div>
            <div style="font-size:0.82rem;font-weight:600;color:white;">Alex Johnson</div>
            <div style="font-size:0.68rem;color:#64748b;">alex@example.com</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Chart Helpers
# ─────────────────────────────────────────────
def make_financial_chart(projections: list) -> go.Figure:
    years = [p["year"] for p in projections]
    def parse_val(v):
        try:
            return float(v.replace("$","").replace("M","").replace("B","").replace("-","").strip() or 0) * (-1 if "-" in str(v) else 1)
        except:
            return 0
    revenues = [abs(parse_val(p["revenue"])) for p in projections]
    expenses = [abs(parse_val(p["expenses"])) for p in projections]
    profits  = [parse_val(p["profit"]) for p in projections]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Revenue", x=years, y=revenues,
                         marker_color="#3b82f6", marker_line_width=0))
    fig.add_trace(go.Bar(name="Expenses", x=years, y=expenses,
                         marker_color="#ef4444", marker_line_width=0))
    fig.add_trace(go.Scatter(name="Profit", x=years, y=profits,
                             mode="lines+markers", line=dict(color="#10b981", width=2.5),
                             marker=dict(size=7, color="#10b981")))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=0, r=0, t=28, b=0), barmode="group", height=200,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", ticksuffix="M", tickfont=dict(size=10)),
    )
    return fig


def make_funding_pie(allocation: dict) -> go.Figure:
    labels = list(allocation.keys())
    values = list(allocation.values())
    colors = ["#7c3aed", "#3b82f6", "#10b981", "#f59e0b"]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#1a2035", width=2)),
        textinfo="percent", textfont=dict(size=11, color="white"),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        showlegend=True,
        legend=dict(font=dict(size=10, color="#94a3b8"), orientation="v"),
        margin=dict(l=0, r=0, t=0, b=0), height=185,
    )
    return fig


# ─────────────────────────────────────────────
# GENERATE PLAN FUNCTION
# ─────────────────────────────────────────────
def generate_plan(idea: str, step_placeholder, status_placeholder):
    """Call backend API and update steps in real time."""
    AGENT_STEPS_LIST = [
        "Analyzing Idea", "Market Research", "Competitor Analysis",
        "Business Model", "Financial Projections", "Marketing Strategy",
        "Finalizing Business Plan",
    ]
    steps = {s: "pending" for s in AGENT_STEPS_LIST}

    def render_steps(steps_dict):
        icons = {"pending": "⬜", "running": "🔄", "completed": "✅", "failed": "❌"}
        html = ""
        for step, status in steps_dict.items():
            icon = icons.get(status, "⬜")
            css_class = f"step-{status}"
            color = {"pending": "#475569", "running": "#f59e0b",
                     "completed": "#10b981", "failed": "#ef4444"}.get(status, "#475569")
            html += f"""
            <div class="progress-step {css_class}">
                <span class="step-icon">{icon}</span>
                <span class="step-name">{step}</span>
                <span class="step-status" style="color:{color};">{status.upper()}</span>
            </div>"""
        step_placeholder.markdown(html, unsafe_allow_html=True)

    render_steps(steps)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/generate-plan-sync",
            json={"idea": idea}, timeout=300,
        )
        if resp.status_code == 200:
            data = resp.json()
            for step_info in data.get("steps", []):
                sname = step_info["step"]
                if sname in steps:
                    steps[sname] = "completed"
                    render_steps(steps)
                    time.sleep(0.08)
            for s in steps:
                steps[s] = "completed"
            render_steps(steps)
            return data.get("plan")
        else:
            status_placeholder.error(f"Backend error: {resp.text}")
            return None
    except requests.exceptions.ConnectionError:
        status_placeholder.error("⚠️ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
        return None
    except Exception as e:
        status_placeholder.error(f"Error: {str(e)}")
        return None


# ─────────────────────────────────────────────
# RENDER BUSINESS PLAN
# ─────────────────────────────────────────────
def render_business_plan(plan: dict):
    es = plan.get("executive_summary", {})
    company_name = es.get("company_name", "Your Company")
    tagline      = es.get("tagline", "")
    description  = es.get("description", "")

    # ── Executive Summary Header ──
    col_info, col_card = st.columns([2, 1])
    with col_info:
        st.markdown(f"""
        <div style="margin-bottom:0.8rem;">
            <div style="font-family:Outfit,sans-serif;font-size:1.45rem;font-weight:800;
                        background:linear-gradient(135deg,#a78bfa,#60a5fa);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        line-height:1.3;">
                📋 Executive Summary
            </div>
            <div style="color:#94a3b8;font-size:0.84rem;margin-top:5px;line-height:1.5;">{description}</div>
        </div>
        """, unsafe_allow_html=True)

        # Metric cards
        metrics = [
            ("🌐", es.get("market_size", "$14.7B"), f"Market Size ({es.get('year','2028')})"),
            ("💰", es.get("revenue_projection", "$18.3M"), f"Revenue ({es.get('year','2028')})"),
            ("👥", es.get("users_projection", "1.2M+"), f"Users ({es.get('year','2028')})"),
            ("🎯", es.get("funding_required", "$2.5M"), "Funding Required"),
        ]
        cols = st.columns(4)
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ec4899"]
        for i, (icon, val, label) in enumerate(metrics):
            cols[i].markdown(f"""
            <div class="metric-card" style="border-top:3px solid {colors[i]};">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value" style="color:{colors[i]};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_card:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e1050,#0f2040);
                    border:1px solid #3730a3;border-radius:14px;padding:1.2rem;
                    text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:7px;">🚀</div>
            <div style="font-family:Outfit,sans-serif;font-weight:800;font-size:1.2rem;
                        color:white;margin-bottom:4px;">{company_name}</div>
            <div style="font-size:0.75rem;color:#94a3b8;font-style:italic;margin-bottom:10px;">{tagline}</div>
            <div style="background:rgba(124,58,237,0.3);border-radius:8px;padding:7px;">
                <div style="font-size:0.68rem;color:#a78bfa;font-weight:600;">✨ AI-POWERED SOLUTION</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sections Grid (1-4) ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">
                <span class="section-badge">⚡ 1.</span> Problem Statement
            </div>
            <div class="section-body">{plan.get('problem_statement','')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="section-card" style="border-top:2px solid #10b981;">
            <div class="section-title">
                <span class="section-badge section-badge-green">✅ 2.</span> Solution
            </div>
            <div class="section-body">{plan.get('solution','')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        market_items = "".join([f"<li>{m}</li>" for m in plan.get("market_opportunity", [])])
        st.markdown(f"""
        <div class="section-card" style="border-top:2px solid #f59e0b;">
            <div class="section-title">
                <span class="section-badge section-badge-orange">📈 3.</span> Market Opportunity
            </div>
            <div class="section-body"><ul>{market_items}</ul></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        audience_items = "".join([f"<li>{a}</li>" for a in plan.get("target_audience", [])])
        st.markdown(f"""
        <div class="section-card" style="border-top:2px solid #ec4899;">
            <div class="section-title">
                <span class="section-badge section-badge-red">🎯 4.</span> Target Audience
            </div>
            <div class="section-body"><ul>{audience_items}</ul></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sections 5-8 ──
    col5, col6, col7, col8 = st.columns(4)
    biz_model = plan.get("business_model", {})

    with col5:
        streams = biz_model.get("revenue_streams", []) if isinstance(biz_model, dict) else []
        items_html = "".join([f"<li>{s}</li>" for s in streams])
        premium_pct = biz_model.get("premium_percentage", 70) if isinstance(biz_model, dict) else 70
        free_pct    = biz_model.get("free_percentage", 30) if isinstance(biz_model, dict) else 30
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title"><span class="section-badge">⚙️ 5.</span> Business Model</div>
            <div class="section-body"><ul>{items_html}</ul></div>
            <div style="display:flex;gap:6px;margin-top:10px;">
                <div style="flex:{premium_pct};background:linear-gradient(135deg,#7c3aed,#3b82f6);
                            border-radius:6px;padding:5px 8px;text-align:center;">
                    <div style="font-size:0.88rem;font-weight:700;color:white;">{premium_pct}%</div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.7);">Premium</div>
                </div>
                <div style="flex:{free_pct};background:#1e2a45;border-radius:6px;padding:5px 8px;text-align:center;">
                    <div style="font-size:0.88rem;font-weight:700;color:white;">{free_pct}%</div>
                    <div style="font-size:0.62rem;color:#64748b;">Free Users</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        competitors = plan.get("competitor_analysis", [])
        rows = ""
        for c in competitors:
            rows += f"""<tr>
                <td style="font-weight:600;color:white;">{c.get('name','')}</td>
                <td style="color:#10b981;">{c.get('strengths','')}</td>
                <td style="color:#ef4444;">{c.get('weaknesses','')}</td>
            </tr>"""
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title"><span class="section-badge section-badge-cyan">🔍 6.</span> Competitor Analysis</div>
            <table class="comp-table">
                <thead><tr><th>Competitor</th><th>Strengths</th><th>Weaknesses</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        strategies = plan.get("marketing_strategy", [])
        channels   = plan.get("channels", [])
        strat_html = "".join([f"<li>{s}</li>" for s in strategies])
        channel_badges = "".join([
            f'<span style="background:#1e2a45;border-radius:5px;padding:3px 7px;font-size:0.68rem;color:#94a3b8;margin:2px;display:inline-block;">{ch}</span>'
            for ch in channels
        ])
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title"><span class="section-badge section-badge-orange">📣 7.</span> Marketing Strategy</div>
            <div class="section-body"><ul>{strat_html}</ul></div>
            <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:3px;">{channel_badges}</div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        swot = plan.get("swot", {})
        def swot_items(items):
            return "".join([f'<div class="swot-item">• {i}</div>' for i in items[:3]])
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title"><span class="section-badge section-badge-green">⚡ 8.</span> SWOT Analysis</div>
            <div class="swot-grid">
                <div class="swot-box swot-s">
                    <div class="swot-label">Strengths</div>
                    {swot_items(swot.get('strengths', []))}
                </div>
                <div class="swot-box swot-w">
                    <div class="swot-label">Weaknesses</div>
                    {swot_items(swot.get('weaknesses', []))}
                </div>
                <div class="swot-box swot-o">
                    <div class="swot-label">Opportunities</div>
                    {swot_items(swot.get('opportunities', []))}
                </div>
                <div class="swot-box swot-t">
                    <div class="swot-label">Threats</div>
                    {swot_items(swot.get('threats', []))}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sections 9-12 ──
    col9, col10, col11, col12 = st.columns(4)
    financials  = plan.get("financials", {})
    projections = financials.get("projections", [])
    funding     = financials.get("funding_details", {})
    milestones  = plan.get("milestones", [])

    with col9:
        st.markdown("""
        <div class="section-title"><span class="section-badge">📊 9.</span> Financial Projections</div>
        """, unsafe_allow_html=True)
        if projections:
            st.plotly_chart(make_financial_chart(projections), width='stretch',
                            config={"displayModeBar": False})
            df = pd.DataFrame(projections)
            st.dataframe(df, hide_index=True, width='stretch',
                         column_config={"year":"Year","revenue":"Revenue",
                                        "expenses":"Expenses","profit":"Profit"})

    with col10:
        allocation = funding.get("allocation", {})
        st.markdown(f"""
        <div class="section-title"><span class="section-badge section-badge-orange">💰 10.</span> Funding Requirements</div>
        <div style="text-align:center;margin:6px 0 4px;">
            <div style="font-family:Outfit,sans-serif;font-size:1.5rem;font-weight:800;
                        background:linear-gradient(135deg,#f59e0b,#ec4899);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                {funding.get('amount', '$2.5M')}
            </div>
            <div style="font-size:0.75rem;color:#94a3b8;">{funding.get('type','Seed Funding')}</div>
        </div>
        """, unsafe_allow_html=True)
        if allocation:
            st.plotly_chart(make_funding_pie(allocation), width='stretch',
                            config={"displayModeBar": False})
            for item, pct in allocation.items():
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;font-size:0.76rem;
                            color:#94a3b8;padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span>{item}</span><span style="color:white;font-weight:600;">{pct}%</span>
                </div>
                """, unsafe_allow_html=True)

    with col11:
        st.markdown("""
        <div class="section-title"><span class="section-badge section-badge-cyan">🗺️ 11.</span> Milestone Roadmap</div>
        """, unsafe_allow_html=True)
        for m in milestones:
            st.markdown(f"""
            <div class="milestone-item">
                <span class="milestone-q">{m.get('quarter','')}</span>
                <span class="milestone-text">{m.get('milestone','')}</span>
            </div>
            """, unsafe_allow_html=True)

    with col12:
        conclusion = plan.get("conclusion", "")
        st.markdown(f"""
        <div class="section-card" style="border-top:2px solid #10b981;">
            <div class="section-title"><span class="section-badge section-badge-red">🏁 12.</span> Conclusion</div>
            <div class="section-body" style="color:#cbd5e1;line-height:1.65;">{conclusion}</div>
            <div style="margin-top:1rem;display:flex;gap:5px;flex-wrap:wrap;">
                <div style="background:rgba(16,185,129,0.15);border-radius:7px;padding:4px 9px;
                            font-size:0.7rem;color:#10b981;">✅ AI-Powered</div>
                <div style="background:rgba(59,130,246,0.15);border-radius:7px;padding:4px 9px;
                            font-size:0.7rem;color:#60a5fa;">📈 Scalable</div>
                <div style="background:rgba(236,72,153,0.15);border-radius:7px;padding:4px 9px;
                            font-size:0.7rem;color:#f472b6;">🚀 Innovative</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab Bar ──
    st.markdown("""
    <div class="tab-bar">
        <div class="tab-item active">Executive Summary</div>
        <div class="tab-item">Market Research</div>
        <div class="tab-item">Business Model</div>
        <div class="tab-item">Marketing Strategy</div>
        <div class="tab-item">Financial Plan</div>
        <div class="tab-item">Appendix</div>
        <div class="tab-item">Pitch Deck</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: New Plan
# ─────────────────────────────────────────────
if st.session_state.page == "new_plan":

    # ── Header ──
    es_data = (st.session_state.plan_data or {}).get("executive_summary", {})
    company_for_dl = es_data.get("company_name", "BusinessPlan")

    st.markdown("""
    <div class="biz-header">
        <div class="biz-logo">✨ <span>BizGenie</span> AI</div>
        <div class="biz-title">
            <h1>✨ Plain Text → Full Business Plan Agent</h1>
            <p>Turn your idea into a complete business plan in seconds! 🚀</p>
        </div>
        <div class="header-actions">
            <div class="header-btn">📤 Export Plan</div>
            <div class="header-btn">🔗 Share Plan</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 3])

    # ── LEFT: Input + Progress ──
    with left_col:
        st.markdown("""
        <div style="font-size:0.82rem;font-weight:700;color:#94a3b8;
                    text-transform:uppercase;letter-spacing:0.5px;margin-bottom:7px;">
            1. Enter Your Business Idea
        </div>
        """, unsafe_allow_html=True)

        idea_text = st.text_area(
            label="Business Idea",
            placeholder="An AI-powered fitness app that creates personalized workout plans, tracks progress, and provides nutrition guidance using machine learning.",
            height=145,
            max_chars=1000,
            key="idea_input",
            label_visibility="collapsed",
        )
        char_count = len(idea_text) if idea_text else 0
        st.markdown(f"""
        <div style="text-align:right;font-size:0.7rem;color:#475569;margin-top:-8px;margin-bottom:8px;">
            {char_count}/1000 characters
        </div>
        """, unsafe_allow_html=True)

        gen_button = st.button(
            "✨ Generate Full Business Plan",
            key="generate_btn",
            disabled=st.session_state.generating,
        )

        # ── Download Report Button ──
        if st.session_state.generated and st.session_state.plan_data:
            report_text = generate_report_text(st.session_state.plan_data)
            fname = f"{company_for_dl.replace(' ', '_')}_BizGenie_Report.txt"
            st.download_button(
                label="📥 Download Report",
                data=report_text.encode("utf-8"),
                file_name=fname,
                mime="text/plain",
                key="download_report_btn",
            )

        st.markdown("""
        <div style="font-size:0.82rem;font-weight:700;color:#94a3b8;
                    text-transform:uppercase;letter-spacing:0.5px;margin:1rem 0 7px;">
            2. AI Agent Progress
        </div>
        """, unsafe_allow_html=True)

        steps_placeholder = st.empty()
        status_msg = st.empty()

        AGENT_STEPS_LIST = [
            "Analyzing Idea", "Market Research", "Competitor Analysis",
            "Business Model", "Financial Projections", "Marketing Strategy",
            "Finalizing Business Plan",
        ]

        def render_initial_steps(completed_set=None):
            if completed_set is None:
                completed_set = set()
            html = ""
            for step in AGENT_STEPS_LIST:
                if step in completed_set:
                    icon, status_text, color, css = "✅", "Completed", "#10b981", "step-completed"
                else:
                    icon, status_text, color, css = "⬜", "Pending", "#475569", "step-pending"
                html += f"""
                <div class="progress-step {css}">
                    <span class="step-icon">{icon}</span>
                    <span class="step-name">{step}</span>
                    <span class="step-status" style="color:{color};">{status_text}</span>
                </div>"""
            steps_placeholder.markdown(html, unsafe_allow_html=True)

        if st.session_state.generated:
            render_initial_steps(set(AGENT_STEPS_LIST))
            st.markdown("""
            <div class="success-banner">
                <span class="icon">🎉</span>
                <div>
                    <div class="text">Business Plan Generated!</div>
                    <div class="sub">Your complete plan is ready. Download the report below ↑</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            render_initial_steps()

        # Handle generate button click
        if gen_button and idea_text and idea_text.strip():
            st.session_state.generating = True
            st.session_state.generated = False
            st.session_state.plan_data = None
            with st.spinner(""):
                plan = generate_plan(idea_text.strip(), steps_placeholder, status_msg)
            if plan:
                st.session_state.plan_data = plan
                st.session_state.generated = True
                st.session_state.generating = False
                st.rerun()
            else:
                st.session_state.generating = False
        elif gen_button and not (idea_text and idea_text.strip()):
            st.warning("Please enter your business idea first!")

    # ── RIGHT: Business Plan Output ──
    with right_col:
        if st.session_state.generated and st.session_state.plan_data:
            render_business_plan(st.session_state.plan_data)
        else:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:480px;text-align:center;opacity:0.55;">
                <div style="font-size:4.5rem;margin-bottom:1rem;">📋</div>
                <div style="font-family:Outfit,sans-serif;font-size:1.25rem;font-weight:700;color:white;margin-bottom:8px;">
                    Your Business Plan Will Appear Here
                </div>
                <div style="font-size:0.85rem;color:#64748b;max-width:380px;line-height:1.6;">
                    Enter your business idea on the left and click "Generate Full Business Plan" to get started.
                    Our AI agent will analyze your idea and create a comprehensive plan in seconds.
                </div>
                <div style="display:flex;gap:10px;margin-top:1.5rem;flex-wrap:wrap;justify-content:center;">
                    <div style="background:#1e2a45;border-radius:9px;padding:9px 14px;font-size:0.78rem;color:#94a3b8;">
                        📊 12 Comprehensive Sections
                    </div>
                    <div style="background:#1e2a45;border-radius:9px;padding:9px 14px;font-size:0.78rem;color:#94a3b8;">
                        📈 Financial Projections
                    </div>
                    <div style="background:#1e2a45;border-radius:9px;padding:9px 14px;font-size:0.78rem;color:#94a3b8;">
                        🤖 AI-Powered by Grok
                    </div>
                    <div style="background:#1e2a45;border-radius:9px;padding:9px 14px;font-size:0.78rem;color:#94a3b8;">
                        ⚡ 7-Step Agent Pipeline
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: Dashboard
# ─────────────────────────────────────────────
elif st.session_state.page == "dashboard":
    st.markdown("""
    <div style="font-family:Outfit,sans-serif;font-size:1.75rem;font-weight:800;
                background:linear-gradient(135deg,#a78bfa,#60a5fa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem;">
        📊 Dashboard
    </div>
    """, unsafe_allow_html=True)

    plans = fetch_plans()
    total = len(plans)
    completed = len([p for p in plans if p["status"] == "completed"])

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label, color in [
        (c1, "📄", total, "Total Plans", "#3b82f6"),
        (c2, "✅", completed, "Completed", "#10b981"),
        (c3, "🔄", total - completed, "In Progress", "#f59e0b"),
        (c4, "🤖", "Grok", "AI Model", "#7c3aed"),
    ]:
        col.markdown(f"""
        <div class="metric-card" style="border-top:3px solid {color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📁 Recent Plans")
    if plans:
        for p in plans:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{p['title']}** — _{p['idea']}_")
            col2.markdown(f"`{p['status']}`")
            if col3.button("Open", key=f"open_{p['id']}"):
                full = fetch_plan_by_id(p["id"])
                if full and full.get("plan_data"):
                    st.session_state.plan_data = full["plan_data"]
                    st.session_state.generated = True
                    st.session_state.page = "new_plan"
                    st.rerun()
    else:
        st.info("No plans yet. Create your first business plan!")
    if st.button("➕ Create New Plan"):
        st.session_state.page = "new_plan"
        st.rerun()


# ─────────────────────────────────────────────
# PAGE: My Plans
# ─────────────────────────────────────────────
elif st.session_state.page == "my_plans":
    st.markdown("""
    <div style="font-family:Outfit,sans-serif;font-size:1.75rem;font-weight:800;
                background:linear-gradient(135deg,#a78bfa,#60a5fa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem;">
        📁 My Plans
    </div>
    """, unsafe_allow_html=True)
    plans = fetch_plans()
    if not plans:
        st.info("No saved plans yet. Generate your first business plan!")
        if st.button("➕ Create New Plan"):
            st.session_state.page = "new_plan"
            st.rerun()
    else:
        for p in plans:
            with st.expander(f"📄 {p['title']} — {p['status'].upper()}", expanded=False):
                st.markdown(f"**Idea:** {p['idea']}")
                st.markdown(f"**Created:** {p.get('created_at','')}")
                col1, col2 = st.columns(2)
                if col1.button("📂 Open Plan", key=f"myplan_open_{p['id']}"):
                    full = fetch_plan_by_id(p["id"])
                    if full and full.get("plan_data"):
                        st.session_state.plan_data = full["plan_data"]
                        st.session_state.generated = True
                        st.session_state.page = "new_plan"
                        st.rerun()
                if col2.button("🗑️ Delete", key=f"myplan_del_{p['id']}"):
                    delete_plan_api(p["id"])
                    st.rerun()


# ─────────────────────────────────────────────
# Other Pages (Placeholder)
# ─────────────────────────────────────────────
else:
    page_map = {
        "templates":       ("📋", "Templates",        "Browse industry-specific business plan templates."),
        "market_research": ("🔍", "Market Research",   "Deep-dive market analysis powered by Grok AI."),
        "financial_tools": ("💰", "Financial Tools",   "Advanced financial modeling and projection tools."),
        "pitch_deck":      ("🎯", "Pitch Deck",        "Auto-generate investor-ready pitch decks from your plan."),
        "reports":         ("📈", "Reports",           "View analytics and insights across all your plans."),
        "ai_chat":         ("🤖", "AI Chat Assistant", "Chat with BizGenie AI for business advice and strategy."),
    }
    icon, title, desc = page_map.get(st.session_state.page, ("📄", "Page", "Coming soon."))
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:60vh;text-align:center;">
        <div style="font-size:3.8rem;margin-bottom:1rem;">{icon}</div>
        <div style="font-family:Outfit,sans-serif;font-size:1.75rem;font-weight:800;
                    background:linear-gradient(135deg,#a78bfa,#60a5fa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;">
            {title}
        </div>
        <div style="font-size:0.92rem;color:#64748b;max-width:400px;">{desc}</div>
        <div style="margin-top:1.5rem;background:#1e2640;border:1px solid #2d3748;border-radius:11px;
                    padding:10px 22px;font-size:0.83rem;color:#7c3aed;">🚀 Coming Soon in Pro Version</div>
    </div>
    """, unsafe_allow_html=True)
