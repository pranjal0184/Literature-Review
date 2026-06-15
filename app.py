import asyncio
import streamlit as st
from backend import run_litrev

# ---------- Page & Theme ----------
st.set_page_config(
    page_title="LitScope",
    page_icon="◎",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

/* ── Reset & Base ─────────────────────────────── */
:root {
  --bg:        #08090d;
  --surface:   #0f1117;
  --surface-2: #161920;
  --border:    #1e2130;
  --border-2:  #252a3a;
  --text:      #f0ede6;
  --muted:     #8a8fa8;
  --subtle:    #3d4260;
  --gold:      #c8a96e;
  --gold-dim:  #7a6540;
  --green:     #4caf7d;
}

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

*, *::before, *::after {
  font-family: "DM Sans", system-ui, sans-serif !important;
  box-sizing: border-box;
}

/* ── Hide Streamlit chrome ────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1120px;
}

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.sidebar-wordmark {
  font-family: "DM Serif Display", serif !important;
  font-size: 1.4rem;
  color: var(--text) !important;
  letter-spacing: -0.02em;
  margin-bottom: 0.1rem;
}
.sidebar-tagline {
  font-size: 0.72rem;
  color: var(--muted) !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 1.4rem;
}
.sidebar-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1rem 0;
}
.sidebar-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted) !important;
  margin-bottom: 0.5rem;
}
.sidebar-tip {
  font-size: 0.8rem;
  color: var(--subtle) !important;
  line-height: 1.6;
}
.sidebar-tip span {
  color: var(--muted) !important;
}
.sidebar-credit {
  font-size: 0.75rem;
  color: var(--subtle) !important;
  margin-top: 0.3rem;
}
.sidebar-credit strong {
  color: var(--muted) !important;
  font-weight: 600;
}

/* ── Page header ──────────────────────────────── */
.page-eyebrow {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold) !important;
  margin-bottom: 0.45rem;
}
.page-title {
  font-family: "DM Serif Display", serif !important;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 400;
  color: var(--text) !important;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin: 0 0 0.5rem 0;
}


/* ── Input zone ───────────────────────────────── */
.stTextInput label,
.stSlider label {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.09em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  margin-bottom: 0.3rem !important;
}

.stTextInput > div > div > input {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 8px !important;
  padding: 0.75rem 1rem !important;
  font-size: 0.95rem !important;
  font-weight: 400 !important;
  transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--gold-dim) !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(200, 169, 110, 0.08) !important;
}
.stTextInput > div > div > input::placeholder {
  color: var(--subtle) !important;
}

/* ── Slider ───────────────────────────────────── */
.stSlider > div > div { color: var(--text) !important; }
.stSlider [role="slider"] {
  background: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(200, 169, 110, 0.15) !important;
}
.stSlider [data-baseweb="slider"] > div > div > div {
  background: var(--gold) !important;
}

/* ── Button ───────────────────────────────────── */
.stButton > button {
  background: var(--gold) !important;
  color: #08090d !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 0.72rem 1.2rem !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em !important;
  transition: opacity 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover {
  opacity: 0.88 !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
  opacity: 1 !important;
}

/* ── Download button — outlined ───────────────── */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--muted) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 8px !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.03em !important;
  transition: border-color 0.15s ease, color 0.15s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
  border-color: var(--gold-dim) !important;
  color: var(--gold) !important;
  background: transparent !important;
  transform: none !important;
}

/* ── Tabs ─────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
  margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--subtle) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  padding: 0.6rem 1.2rem !important;
  border-bottom: 2px solid transparent !important;
  transition: color 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
  color: var(--text) !important;
  border-bottom: 2px solid var(--gold) !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── Chat / messages ──────────────────────────── */
.stChatMessage {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 0.9rem 1rem !important;
  margin-bottom: 0.75rem !important;
}
.stChatMessage p { color: var(--text) !important; font-size: 0.92rem !important; }

.agent-pill {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  margin-bottom: 0.5rem;
}
.pill-search {
  background: rgba(76, 175, 125, 0.1);
  color: #4caf7d !important;
  border: 1px solid rgba(76, 175, 125, 0.25);
}
.pill-summarizer {
  background: rgba(200, 169, 110, 0.1);
  color: var(--gold) !important;
  border: 1px solid rgba(200, 169, 110, 0.25);
}

/* ── Review card ──────────────────────────────── */
.review-card {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 1.6rem 1.8rem !important;
  line-height: 1.75 !important;
  margin-bottom: 1.2rem;
}
.review-card p, .review-card li, .review-card span {
  color: var(--text) !important;
  font-size: 0.93rem !important;
}
.review-card h1,.review-card h2,.review-card h3 {
  color: var(--text) !important;
  font-family: "DM Serif Display", serif !important;
  font-weight: 400 !important;
  margin-top: 1.4rem !important;
}

/* ── Section label ────────────────────────────── */
.section-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted) !important;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.section-label::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── Status / info ────────────────────────────── */
.stAlert {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--muted) !important;
}
.stStatus {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}

/* ── Misc ─────────────────────────────────────── */
code, pre {
  background: var(--surface-2) !important;
  color: var(--muted) !important;
  border-radius: 4px !important;
}
p, span, div, li { color: var(--text) !important; }
a { color: var(--gold) !important; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<div class='sidebar-wordmark'>◎ LitScope</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-tagline'>Research Review Engine</div>", unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-label'>Try asking about</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='sidebar-tip'>
      <span>→</span> Diffusion models safety<br>
      <span>→</span> LLM factuality benchmarks<br>
      <span>→</span> Federated learning in healthcare<br>
      <span>→</span> Retrieval-augmented generation
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-label'>Built by</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='sidebar-credit'>
      <strong>Pranjal Kumari</strong><br>
      Streamlit · AutoGen · arXiv
    </div>
    """, unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<div class='page-eyebrow'>AI-assisted literature discovery</div>", unsafe_allow_html=True)
st.markdown("<h1 class='page-title'>LitScope</h1>", unsafe_allow_html=True)

# ---------- Inputs ----------
col1, col2, col3 = st.columns([4, 2, 2], vertical_alignment="bottom")
with col1:
    query = st.text_input(
        "Research topic",
        placeholder="e.g., Retrieval-Augmented Generation evaluation",
        label_visibility="visible"
    )
with col2:
    n_papers = st.slider("Papers to fetch", min_value=1, max_value=10, value=5)
with col3:
    go = st.button("Run review →", use_container_width=True)

st.write("")

# ---------- Tabs ----------
tab_conv, tab_final = st.tabs(["Conversation", "Final Review"])

if "final_review_md" not in st.session_state:
    st.session_state.final_review_md = ""


def _render_message(role: str, content: str):
    role_lower = role.strip().lower()
    if role_lower.startswith("search"):
        pill_cls = "pill-search"
        label = "Search Agent"
    else:
        pill_cls = "pill-summarizer"
        label = "Summarizer"

    with st.chat_message("assistant"):
        st.markdown(
            f"<span class='agent-pill {pill_cls}'>{label}</span>",
            unsafe_allow_html=True
        )
        st.markdown(content)


async def _runner(topic: str, num: int):
    with tab_conv:
        st.markdown("<div class='section-label'>Live agent output</div>", unsafe_allow_html=True)
        container = st.container()
        async for frame in run_litrev(topic, num_papers=num):
            role, *rest = frame.split(":", 1)
            content = rest[0].strip() if rest else ""
            with container:
                _render_message(role, content)
            if role.strip().lower().startswith("summarizer"):
                st.session_state.final_review_md = content

    with tab_final:
        st.markdown("<div class='section-label'>Generated review</div>", unsafe_allow_html=True)
        if st.session_state.final_review_md:
            st.markdown(
                f"<div class='review-card'>{st.session_state.final_review_md}</div>",
                unsafe_allow_html=True
            )
            st.download_button(
                "Download as Markdown",
                data=st.session_state.final_review_md.encode("utf-8"),
                file_name="literature_review.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info("No review yet — run a search from the Conversation tab.")


# ---------- Run ----------
if go and query:
    with st.status("Scanning arXiv and synthesizing insights…", expanded=True) as status:
        st.write("Querying arXiv for relevant papers")
        st.write("Coordinating search and summarization agents")
        try:
            asyncio.run(_runner(query, n_papers))
            status.update(label="Review complete", state="complete")
            st.toast("Done", icon="✓")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_runner(query, n_papers))
            status.update(label="Review complete", state="complete")
            st.toast("Done", icon="✅")
elif go and not query:
    st.warning("Enter a research topic to get started.")
