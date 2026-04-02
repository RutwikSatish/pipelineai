import streamlit as st
from groq import Groq
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="PipelineAI · ExecuSource Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #0F1624;
        border: 1px solid #1C2A3E;
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }
    [data-testid="metric-container"] label {
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #7B90AC !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #1C2A3E;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.7rem 1.2rem;
        font-size: 13px;
        font-weight: 600;
        color: #7B90AC;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #F0F4FF !important;
        border-bottom: 2px solid #3B82F6 !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* Buttons */
    .stButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 13px;
        border-radius: 8px;
        padding: 0.5rem 1.4rem;
        border: none;
        transition: opacity 0.15s;
    }
    .stButton > button:hover { opacity: 0.88; }

    /* Text areas & inputs */
    .stTextArea textarea, .stTextInput input {
        background: #080D1A !important;
        border: 1px solid #1C2A3E !important;
        border-radius: 8px !important;
        color: #F0F4FF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3B82F6 !important;
        box-shadow: none !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #080D1A !important;
        border: 1px solid #1C2A3E !important;
        border-radius: 8px !important;
    }

    /* Cards / info boxes */
    .pipeline-card {
        background: #0F1624;
        border: 1px solid #1C2A3E;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.6rem;
    }
    .match-card-top {
        border-left: 3px solid #3B82F6;
    }
    .match-card {
        border-left: 3px solid #1C2A3E;
    }

    /* Skill chips */
    .chip {
        display: inline-block;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        color: #93C5FD;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 500;
        margin: 2px;
    }

    /* Status badges */
    .badge-warm   { background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3);  color:#F59E0B; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }
    .badge-cold   { background:rgba(107,114,128,0.12);border:1px solid rgba(107,114,128,0.3); color:#9CA3AF; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }
    .badge-active { background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3);  color:#10B981; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; }

    /* Score display */
    .score-green { color: #10B981; font-size: 2rem; font-weight: 900; line-height: 1; }
    .score-amber { color: #F59E0B; font-size: 2rem; font-weight: 900; line-height: 1; }
    .score-gray  { color: #6B7280; font-size: 2rem; font-weight: 900; line-height: 1; }

    /* Divider */
    hr { border-color: #1C2A3E !important; margin: 0.8rem 0 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0A101F;
        border-right: 1px solid #1C2A3E;
    }
    [data-testid="stSidebar"] .stMarkdown p { color: #7B90AC; font-size: 13px; }

    /* Output box */
    .output-box {
        background: #0F1624;
        border: 1px solid #1C2A3E;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        font-size: 14px;
        line-height: 1.8;
        color: #F0F4FF;
        white-space: pre-wrap;
    }
    .section-label {
        font-size: 11px;
        color: #7B90AC;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.7rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────
CANDIDATES = [
    {"id": 1,  "name": "Sarah Chen",    "title": "Sr. Cloud Engineer",   "skills": ["AWS","Azure","Terraform","Python","K8s"],          "exp": 7, "loc": "Atlanta, GA",    "status": "warm",   "placed": "Nov 2024", "rate": "$95/hr",  "notes": "Strong AWS Solutions Architect. Prefers contract-to-hire."},
    {"id": 2,  "name": "Marcus Webb",   "title": "Cybersecurity Analyst","skills": ["CISSP","SIEM","Pen Testing","Zero Trust","SOC"],    "exp": 5, "loc": "Denver, CO",     "status": "cold",   "placed": "Mar 2024", "rate": "$85/hr",  "notes": "CISSP certified. Last role ended on good terms. Needs re-engagement."},
    {"id": 3,  "name": "Priya Nair",    "title": "Data Engineer",        "skills": ["Python","Spark","Databricks","Snowflake","dbt"],   "exp": 6, "loc": "Atlanta, GA",    "status": "warm",   "placed": "Dec 2024", "rate": "$90/hr",  "notes": "Deep Databricks & Snowflake expertise. Very in-demand profile."},
    {"id": 4,  "name": "James Okafor", "title": "Full Stack Developer",  "skills": ["React","Node.js","TypeScript","PostgreSQL","Docker"],"exp": 4,"loc": "Dallas, TX",     "status": "active", "placed": "Feb 2025", "rate": "$80/hr",  "notes": "Currently on contract through Q3 2025. Strong performer."},
    {"id": 5,  "name": "Elena Vasquez","title": "DevOps Engineer",       "skills": ["Kubernetes","Terraform","AWS","GitOps","Helm"],    "exp": 8, "loc": "Remote",         "status": "cold",   "placed": "Jan 2024", "rate": "$105/hr", "notes": "Senior-level. Left last role voluntarily. Strong references."},
    {"id": 6,  "name": "Tyler Brooks", "title": "ML / AI Engineer",      "skills": ["PyTorch","LLMs","Python","MLflow","HuggingFace"],  "exp": 3, "loc": "Atlanta, GA",    "status": "warm",   "placed": "Oct 2024", "rate": "$100/hr", "notes": "Hot profile — LLM fine-tuning experience. Multiple client interests."},
    {"id": 7,  "name": "Neha Patel",   "title": "IT Program Manager",    "skills": ["PMP","Agile","SAFe","Cloud Migrations","JIRA"],    "exp": 9, "loc": "Miami, FL",      "status": "active", "placed": "Mar 2025", "rate": "$110/hr", "notes": "On 12-month engagement. Re-engage Q4 2025."},
    {"id": 8,  "name": "Derek Nguyen", "title": "Network Engineer",      "skills": ["Cisco","CCNA","SD-WAN","Firewall","BGP"],          "exp": 6, "loc": "Greenville, SC", "status": "warm",   "placed": "Sep 2024", "rate": "$75/hr",  "notes": "Solid infrastructure background. Strong references."},
]

STATUS_LABELS = {"warm": "Warm", "cold": "Cold", "active": "Placed"}

def chips_html(skills, max_show=4):
    shown = skills[:max_show]
    rest  = len(skills) - max_show
    html  = "".join(f'<span class="chip">{s}</span>' for s in shown)
    if rest > 0:
        html += f'<span style="font-size:11px;color:#7B90AC;margin-left:4px;">+{rest}</span>'
    return html

def badge_html(status):
    return f'<span class="badge-{status}">{STATUS_LABELS[status]}</span>'

def score_color_class(score):
    if score >= 80: return "score-green"
    if score >= 60: return "score-amber"
    return "score-gray"

# ─── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">⚡</div>
        <div>
            <div style="font-size:17px;font-weight:800;color:#F0F4FF;line-height:1;letter-spacing:-0.02em;">PipelineAI</div>
            <div style="font-size:10px;color:#7B90AC;letter-spacing:0.05em;text-transform:uppercase;">Powered by Groq + Llama</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);color:#93C5FD;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;letter-spacing:0.04em;">EXECUSOURCE DEMO v1.0</span>', unsafe_allow_html=True)
    st.markdown("---")

    _secret_key = st.secrets.get("GROQ_API_KEY", "")
    if _secret_key:
        api_key = _secret_key
        st.success("\u2713 API key loaded from secrets", icon="\U0001f511")
    else:
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Or set GROQ_API_KEY in .streamlit/secrets.toml",
        )

    st.markdown("---")
    st.markdown("**About this tool**")
    st.markdown("PipelineAI solves three core problems facing ExecuSource's IT division in 2026:")
    st.markdown("- 📊 **Dashboard** — Full pipeline visibility at a glance")
    st.markdown("- ⚡ **Smart Match** — AI ranks candidates for any job req")
    st.markdown("- ✉ **Outreach Gen** — Personalized re-engagement emails")
    st.markdown("---")
    st.markdown('<p style="font-size:11px;color:#3B4D63;">Built with Groq · llama-3.3-70b-versatile</p>', unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  📊  Dashboard  ", "  ⚡  Smart Match  ", "  ✉  Outreach Generator  "])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
with tab1:
    warm_c   = [c for c in CANDIDATES if c["status"] == "warm"]
    cold_c   = [c for c in CANDIDATES if c["status"] == "cold"]
    active_c = [c for c in CANDIDATES if c["status"] == "active"]

    # Metric row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total in Pool",    len(CANDIDATES), help="All IT candidates")
    m2.metric("🔥 Warm",          len(warm_c),     help="Placed 3–6 months ago — ready to re-engage")
    m3.metric("❄️ Cold",           len(cold_c),     help="Placed 6+ months ago — needs outreach")
    m4.metric("✅ Active (Placed)",len(active_c),   help="Currently on contract")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="section-label">Pipeline by Status</div>', unsafe_allow_html=True)
        pipe_df = pd.DataFrame([
            {"Status": "Placed", "Count": len(active_c), "color": "#10B981"},
            {"Status": "Warm",   "Count": len(warm_c),   "color": "#F59E0B"},
            {"Status": "Cold",   "Count": len(cold_c),   "color": "#4B5563"},
        ])
        fig1 = go.Figure(go.Bar(
            x=pipe_df["Status"], y=pipe_df["Count"],
            marker_color=pipe_df["color"].tolist(),
            text=pipe_df["Count"], textposition="outside",
        ))
        fig1.update_layout(
            plot_bgcolor="#0F1624", paper_bgcolor="#0F1624",
            font=dict(color="#7B90AC", family="Plus Jakarta Sans"),
            margin=dict(l=0, r=0, t=10, b=0), height=200,
            xaxis=dict(showgrid=False, showline=False, tickfont=dict(color="#7B90AC")),
            yaxis=dict(showgrid=False, showline=False, showticklabels=False),
        )
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        st.markdown('<div class="section-label">Top IT Skills in Pool</div>', unsafe_allow_html=True)
        skill_df = pd.DataFrame([
            {"Skill": "Cloud/DevOps", "n": 3},
            {"Skill": "Data Eng",     "n": 2},
            {"Skill": "ML / AI",      "n": 1},
            {"Skill": "Security",     "n": 1},
            {"Skill": "Full Stack",   "n": 1},
        ])
        fig2 = px.bar(skill_df, x="n", y="Skill", orientation="h",
                      color_discrete_sequence=["#3B82F6"])
        fig2.update_layout(
            plot_bgcolor="#0F1624", paper_bgcolor="#0F1624",
            font=dict(color="#7B90AC", family="Plus Jakarta Sans"),
            margin=dict(l=0, r=0, t=10, b=0), height=200,
            xaxis=dict(showgrid=False, showline=False, showticklabels=False, title=""),
            yaxis=dict(showgrid=False, showline=False, title="", tickfont=dict(color="#7B90AC")),
        )
        fig2.update_traces(marker_color="#3B82F6")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Candidate table
    st.markdown('<div class="section-label">Candidate Pool</div>', unsafe_allow_html=True)
    for c in CANDIDATES:
        with st.container():
            col_av, col_info, col_loc, col_skills, col_exp, col_rate, col_badge = st.columns([0.5, 2, 1.5, 3, 0.7, 0.8, 0.9])
            with col_av:
                initials = "".join(p[0] for p in c["name"].split())[:2].upper()
                colors   = ["#3B82F6","#8B5CF6","#EC4899","#10B981","#F59E0B","#EF4444","#06B6D4","#6366F1"]
                bg       = colors[ord(c["name"][0]) % len(colors)]
                st.markdown(f'<div style="width:34px;height:34px;border-radius:50%;background:{bg};display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fff;margin-top:4px;">{initials}</div>', unsafe_allow_html=True)
            with col_info:
                st.markdown(f'<div style="font-size:13px;font-weight:700;color:#F0F4FF;margin-top:4px;">{c["name"]}</div><div style="font-size:11px;color:#7B90AC;">{c["title"]}</div>', unsafe_allow_html=True)
            with col_loc:
                st.markdown(f'<div style="font-size:11px;color:#7B90AC;margin-top:8px;">📍 {c["loc"]}</div>', unsafe_allow_html=True)
            with col_skills:
                st.markdown(f'<div style="margin-top:6px;">{chips_html(c["skills"])}</div>', unsafe_allow_html=True)
            with col_exp:
                st.markdown(f'<div style="font-size:12px;color:#7B90AC;margin-top:8px;">{c["exp"]}yr exp</div>', unsafe_allow_html=True)
            with col_rate:
                st.markdown(f'<div style="font-size:12px;font-weight:700;color:#F59E0B;margin-top:8px;">{c["rate"]}</div>', unsafe_allow_html=True)
            with col_badge:
                st.markdown(f'<div style="margin-top:7px;">{badge_html(c["status"])}</div>', unsafe_allow_html=True)
            st.markdown('<hr>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — SMART MATCH
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### ⚡ Smart Match")
    st.markdown('<p style="color:#7B90AC;font-size:13px;margin-top:-8px;">Paste a job requirement — Groq will rank all available candidates by fit score, with reasoning and risk flags.</p>', unsafe_allow_html=True)
    st.markdown("")

    jd_input = st.text_area(
        "Job Requirement",
        height=160,
        placeholder="Example:\n\nSeeking a Senior Cloud Engineer with 5+ years of AWS experience, strong Terraform/IaC skills, and Kubernetes expertise. Financial services background preferred. Contract-to-hire, Atlanta or remote...",
        label_visibility="collapsed",
    )

    run_match = st.button("⚡ Run AI Match", type="primary", disabled=not jd_input.strip())

    if run_match:
        if not api_key:
            st.error("Please enter your Groq API Key in the sidebar to use this feature.")
        else:
            pool      = [c for c in CANDIDATES if c["status"] != "active"]
            summaries = "\n".join(
                f'ID:{c["id"]} | {c["name"]} | {c["title"]} | Skills: {", ".join(c["skills"])} | {c["exp"]}yr | {c["loc"]} | {c["status"]}'
                for c in pool
            )
            prompt = f"""You are an expert IT staffing specialist at ExecuSource. Rank these candidates for the job below.
Return ONLY a raw JSON array — no markdown, no prose, no explanation.

JOB:
{jd_input}

AVAILABLE CANDIDATES (not currently placed):
{summaries}

Return top 4 matches as JSON:
[{{"id": number, "score": 0-100, "label": "Strong Match" | "Good Match" | "Partial Match", "reason": "One concise sentence on fit.", "gap": "One sentence on any concern or gap."}}]"""

            with st.spinner("Analyzing candidates with Groq + Llama..."):
                try:
                    client   = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    raw     = response.choices[0].message.content.strip()
                    clean   = raw.replace("```json", "").replace("```", "").strip()
                    results = json.loads(clean)

                    st.markdown("")
                    st.markdown(f'<div class="section-label">AI Match Results — {len(results)} candidates ranked</div>', unsafe_allow_html=True)

                    for i, r in enumerate(results):
                        c = next((x for x in CANDIDATES if x["id"] == r["id"]), None)
                        if not c:
                            continue
                        card_class = "pipeline-card match-card-top" if i == 0 else "pipeline-card match-card"
                        col_rank, col_av, col_info, col_score = st.columns([0.3, 0.4, 5, 0.7])
                        with col_rank:
                            st.markdown(f'<div style="font-size:11px;color:#7B90AC;font-weight:800;margin-top:14px;text-align:center;">#{i+1}</div>', unsafe_allow_html=True)
                        with col_av:
                            initials = "".join(p[0] for p in c["name"].split())[:2].upper()
                            colors   = ["#3B82F6","#8B5CF6","#EC4899","#10B981","#F59E0B","#EF4444","#06B6D4","#6366F1"]
                            bg       = colors[ord(c["name"][0]) % len(colors)]
                            st.markdown(f'<div style="width:38px;height:38px;border-radius:50%;background:{bg};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#fff;margin-top:8px;">{initials}</div>', unsafe_allow_html=True)
                        with col_info:
                            label_color = "#6EE7B7" if "Strong" in r["label"] else "#FCD34D" if "Good" in r["label"] else "#9CA3AF"
                            st.markdown(f"""
                            <div style="background:#0F1624;border:1px solid #1C2A3E;border-left:3px solid {'#3B82F6' if i == 0 else '#1C2A3E'};border-radius:10px;padding:12px 16px;margin-bottom:4px;">
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
                                    <span style="font-size:14px;font-weight:800;color:#F0F4FF;">{c['name']}</span>
                                    <span style="font-size:12px;color:#7B90AC;">{c['title']}</span>
                                    {badge_html(c['status'])}
                                    <span style="background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.25);color:#C4B5FD;border-radius:4px;padding:2px 7px;font-size:11px;font-weight:600;">{r['label']}</span>
                                </div>
                                <div style="font-size:12px;color:#6EE7B7;margin-bottom:4px;line-height:1.5;">✓ {r['reason']}</div>
                                {'<div style="font-size:12px;color:#FCA5A5;line-height:1.5;">△ ' + r['gap'] + '</div>' if r.get('gap') else ''}
                                <div style="margin-top:8px;">{chips_html(c['skills'], max_show=5)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_score:
                            css_cls = score_color_class(r["score"])
                            st.markdown(f'<div style="text-align:center;margin-top:10px;"><div class="{css_cls}">{r["score"]}</div><div style="font-size:9px;color:#7B90AC;text-transform:uppercase;letter-spacing:0.05em;margin-top:2px;">score</div></div>', unsafe_allow_html=True)

                except json.JSONDecodeError:
                    st.error("Groq returned an unexpected format. Please try again.")
                except Exception as e:
                    if "auth" in str(e).lower() or "401" in str(e):
                        st.error("Invalid Groq API key. Please check your key in the sidebar.")
                    else:
                        st.error(f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# TAB 3 — OUTREACH GENERATOR
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ✉ Outreach Generator")
    st.markdown('<p style="color:#7B90AC;font-size:13px;margin-top:-8px;">Select a warm or cold candidate, describe the opportunity, and Groq will write a personalized re-engagement email in seconds.</p>', unsafe_allow_html=True)
    st.markdown("")

    reengageable = [c for c in CANDIDATES if c["status"] != "active"]
    candidate_options = {
        f"{c['name']}  ·  {c['title']}  [{STATUS_LABELS[c['status']]}]": c
        for c in reengageable
    }

    col_sel, col_job = st.columns([1, 1])
    with col_sel:
        st.markdown("**Select a Candidate**")
        choice = st.selectbox(
            "Candidate",
            options=list(candidate_options.keys()),
            index=0,
            label_visibility="collapsed",
        )
        selected_c = candidate_options[choice]

        # Show candidate card
        initials = "".join(p[0] for p in selected_c["name"].split())[:2].upper()
        colors   = ["#3B82F6","#8B5CF6","#EC4899","#10B981","#F59E0B","#EF4444","#06B6D4","#6366F1"]
        bg       = colors[ord(selected_c["name"][0]) % len(colors)]
        st.markdown(f"""
        <div style="background:#0F1624;border:1px solid #1C2A3E;border-radius:10px;padding:14px 16px;margin-top:10px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <div style="width:40px;height:40px;border-radius:50%;background:{bg};display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:#fff;flex-shrink:0;">{initials}</div>
                <div>
                    <div style="font-size:14px;font-weight:700;color:#F0F4FF;">{selected_c['name']}</div>
                    <div style="font-size:12px;color:#7B90AC;">{selected_c['title']} · {selected_c['loc']}</div>
                </div>
            </div>
            <div style="margin-bottom:8px;">{chips_html(selected_c['skills'])}</div>
            <div style="font-size:11px;color:#7B90AC;margin-top:6px;">📅 Last placed: <strong style="color:#F0F4FF;">{selected_c['placed']}</strong> &nbsp;|&nbsp; 💰 {selected_c['rate']} &nbsp;|&nbsp; {badge_html(selected_c['status'])}</div>
            <div style="font-size:12px;color:#94A3B8;margin-top:8px;line-height:1.5;font-style:italic;">"{selected_c['notes']}"</div>
        </div>
        """, unsafe_allow_html=True)

    with col_job:
        st.markdown("**Opportunity Details**")
        job_info = st.text_area(
            "Opportunity",
            height=180,
            placeholder="E.g., We have a great contract-to-hire Data Engineer role at a fintech in Atlanta. 6 months, potential full-time. Snowflake + Python stack. Very collaborative team, great culture...",
            label_visibility="collapsed",
        )

    st.markdown("")
    gen_btn = st.button("✉  Generate Outreach Email", type="primary", disabled=not job_info.strip())

    if gen_btn:
        if not api_key:
            st.error("Please enter your Groq API Key in the sidebar to use this feature.")
        else:
            prompt = f"""You are a recruiter at ExecuSource, a top Atlanta staffing firm known for genuine, relationship-first recruiting. Write a short, warm re-engagement email to this IT professional. Under 140 words. Human and direct, not salesy. Reference their specific background naturally.

CANDIDATE:
Name: {selected_c['name']}
Title: {selected_c['title']}
Skills: {', '.join(selected_c['skills'])}
Last placed: {selected_c['placed']}
Notes: {selected_c['notes']}

OPPORTUNITY:
{job_info}

Write ONLY the email body. No subject line. No markdown."""

            with st.spinner("Writing personalized email with Groq + Llama..."):
                try:
                    client   = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=600,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    email_text = response.choices[0].message.content.strip()

                    st.markdown("")
                    st.markdown('<div class="section-label">Generated Email</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="output-box">{email_text}</div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.code(email_text, language=None)  # easy copy-paste fallback

                except Exception as e:
                    if "auth" in str(e).lower() or "401" in str(e):
                        st.error("Invalid Groq API key. Please check your key in the sidebar.")
                    else:
                        st.error(f"Error: {str(e)}")
