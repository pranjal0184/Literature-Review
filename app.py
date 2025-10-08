import asyncio
import streamlit as st
from backend import run_litrev

# ---------- Page & Theme ----------
st.set_page_config(
    page_title="LitScope – Research Review",
    page_icon="🕮",
    layout="wide"
)

# Global CSS for dark theme, beige text, fonts, and bigger UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

:root{
  --bg: #0b0b0b;
  --panel: #121212;
  --text: #f5f5dc; /* Beige */
  --muted: #d8d8c0; /* Softer beige */
  --accent: #bfa76a; /* Gold-ish accent */
  --accent-2: #8c7853;
}

html, body, .stApp { background: var(--bg) !important; color: var(--text) !important; }
*, .stMarkdown, .stTextInput, .stSlider, .stSelectbox, .stButton { font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important; }
h1, h2, h3, h4, h5 { color: var(--text) !important; font-weight: 800; letter-spacing: .2px; }
p, span, div { color: var(--text) !important; }
code, pre { background: #1e1e1e !important; color: var(--muted) !important; }

.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

.sidebar .sidebar-content { background: var(--panel) !important; }
[data-testid="stSidebar"] { background: var(--panel) !important; border-right: 1px solid #1e1e1e; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: #1a1a1a !important;
  color: var(--text) !important;
  border: 1px solid #2a2a2a !important;
  border-radius: 10px !important;
  padding: .7rem .9rem !important;
  font-size: 1.05rem !important;
}

.stSlider > div > div { color: var(--text) !important; }
.stSlider [role="slider"] {
  box-shadow: 0 0 0 4px rgba(191, 167, 106, .25) !important;
  background: var(--accent) !important;
}
.stSlider [data-baseweb="slider"] > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
}

.stButton button {
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  color: #0b0b0b !important;
  border: none !important;
  border-radius: 12px !important;
  padding: .65rem 1rem !important;
  font-weight: 700 !important;
  letter-spacing: .3px;
  transition: transform .08s ease;
}
.stButton button:hover { transform: translateY(-1px); }
.stButton button:active { transform: translateY(0); }

.badge {
  display:inline-block; padding:.2rem .55rem; border-radius:999px;
  background:#1e1a12; border:1px solid #3a341f; color:var(--muted);
  font-size:.8rem; font-weight:600; letter-spacing:.2px;
}

.role-tag { font-weight:800; padding:.15rem .45rem; border-radius:.5rem; }
.role-search { background:#0f2a2a; border:1px solid #1f4d4d; color:#bfe3e3;}
.role-sum { background:#2a1f0f; border:1px solid #4d3f1f; color:#f0d9a6;}

.chat-bubble {
  background:#131313; border:1px solid #242424; border-radius:16px; padding:1rem;
}
.section-card {
  background:#121212; border:1px solid #222; border-radius:16px; padding:1rem 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🕮 LitScope")
    st.markdown(
        "An AI-assisted literature review tool that fetches papers from **arXiv** "
        "and drafts a crisp review."
    )
    st.markdown("---")
    st.markdown("**Tips**")
    st.caption("• Try: *“diffusion models safety”*, *“LLM factuality benchmarks”*, *“federated learning healthcare”*")
    st.markdown("---")
    st.markdown("**About**")
    st.caption("Built by **Pranjal Kumari** · Streamlit + AutoGen · arXiv search")

# ---------- Header ----------
st.markdown("<h1>LitScope</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='badge'>AI-assisted paper discovery & review</div>",
    unsafe_allow_html=True
)
st.write("")

# ---------- Inputs ----------
col1, col2, col3 = st.columns([4, 2, 2], vertical_alignment="center")
with col1:
    query = st.text_input(
        "Research topic",
        placeholder="e.g., Retrieval-Augmented Generation evaluation",
    )
with col2:
    n_papers = st.slider("Number of papers", min_value=1, max_value=10, value=5)
with col3:
    go = st.button("🔎 Generate Review", use_container_width=True)

# Tabs for UX
tab_conv, tab_final = st.tabs(["💬 Conversation", "📝 Final Review"])

# State to hold final review content
if "final_review_md" not in st.session_state:
    st.session_state.final_review_md = ""

def _render_message(role: str, content: str):
    cls = "role-search" if role.strip().lower().startswith("search") else "role-sum"
    with st.chat_message("assistant"):
        st.markdown(
            f"<span class='role-tag {cls}'>{role}</span>",
            unsafe_allow_html=True
        )
        st.markdown(f"<div class='chat-bubble'>{content}</div>", unsafe_allow_html=True)

async def _runner(topic: str, num: int):
    # Stream frames and show them live in Conversation tab
    with tab_conv:
        container = st.container()
        async for frame in run_litrev(topic, num_papers=num):
            role, *rest = frame.split(":", 1)
            content = rest[0].strip() if rest else ""
            with container:
                _render_message(role, content)
            # Capture the latest summarizer output into state
            if role.strip().lower().startswith("summarizer"):
                st.session_state.final_review_md = content

    # After streaming, show Final tab with nicely formatted review + download
    with tab_final:
        st.markdown("#### Generated Review")
        if st.session_state.final_review_md:
            st.markdown(
                f"<div class='section-card'>{st.session_state.final_review_md}</div>",
                unsafe_allow_html=True
            )
            st.download_button(
                "⬇️ Download Markdown",
                data=st.session_state.final_review_md.encode("utf-8"),
                file_name="literature_review.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info("No review yet — run one from the **Conversation** tab.")

# ---------- Run ----------
if go and query:
    with st.status("Fetching papers & synthesizing insights…", expanded=True) as status:
        st.write("🔗 Querying arXiv")
        st.write("🧠 Coordinating search & summary agents")
        try:
            # Primary attempt
            asyncio.run(_runner(query, n_papers))
            status.update(label="Done", state="complete")
            st.toast("Review complete 🎉", icon="✅")
        except RuntimeError:
            # Fallback for environments with a running loop (e.g., Streamlit Cloud)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_runner(query, n_papers))
            status.update(label="Done", state="complete")
            st.toast("Review complete 🎉", icon="✅")
elif go and not query:
    st.warning("Please enter a research topic to continue.")
