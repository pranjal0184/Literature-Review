# Streamlit app for literature review assistant defined in backend.py.
#users enter a topic, and the desired number of papers, then we can see the two agent conversation stream in real-time

import asyncio
import streamlit as st
from backend import run_litrev

st.set_page_config(page_title="Literature Review Assistant", page_icon="📚")
st.title("📚 Literature Review Assistant")

query = st.text_input("Research topic")
n_papers = st.slider("Number of papers", 1, 10, 5)

if st.button("Search") and query:

    async def _runner() -> None:
        chat_placeholder = st.container()
        async for frame in run_litrev(query, num_papers=n_papers):
            role, *rest = frame.split(":", 1)
            content = rest[0].strip() if rest else ""
            with chat_placeholder:
                with st.chat_message("assistant"):
                    st.markdown(f"**{role}**: {content}")

    with st.spinner("Working …"):
        try:
            asyncio.run(_runner())
        except RuntimeError:
            # Fallback when an event‑loop is already running (e.g. Streamlit Cloud)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_runner())

    st.success("Review complete 🎉")