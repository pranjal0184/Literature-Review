"""
Core module for a multi-agent literature-review assistant built on AutoGen (v0.4+).
Exposes run_litrev() to orchestrate a two-agent arXiv search and summarization pipeline.
Compatible with Streamlit, FastAPI, and CLI execution.
"""

from __future__ import annotations
import os
import asyncio
from typing import AsyncGenerator, Dict, List

import arxiv
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


def _sync_arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """Internal synchronous worker for querying arXiv."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers: List[Dict] = []
    for result in client.results(search):
        papers.append({
            "title": result.title.strip().replace("\n", " "),
            "authors": [author.name for author in result.authors],
            "published": result.published.strftime("%Y-%m-%d") if result.published else "N/A",
            "summary": result.summary.strip().replace("\n", " "),
            "pdf_url": result.pdf_url,
        })
    return papers


async def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """Asynchronous tool wrapper to prevent blocking the async event loop."""
    return await asyncio.to_thread(_sync_arxiv_search, query, max_results)


arxiv_tool = FunctionTool(
    arxiv_search,
    description=(
        "Searches arXiv and returns up to *max_results* papers. Each result contains: "
        "title, authors, published date, summary, and pdf_url."
    ),
)


def _get_api_key() -> str:
    """Retrieve API key from Streamlit secrets (cloud) or environment variables (.env)."""
    try:
        import streamlit as st
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENROUTER_API_KEY", "")


def build_team(model: str = "dots-studio/dots-3-note-preview:free") -> RoundRobinGroupChat:
    """Builds and wires the search and summarizer agents into a RoundRobinGroupChat."""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "Missing OPENROUTER_API_KEY. Add it to Streamlit Secrets or your .env file."
        )

    # Generic OpenRouter configuration compatible with AutoGen v0.4+
    model_info = {
        "provider": "openrouter",
        "family": "unknown",
        "function_calling": True,
        "vision": False,
        "json_output": False,
    }

    llm_client = OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model_info=model_info,
        extra_create_args={
            "extra_body": {
                "reasoning": {"enabled": True}
            }
        },
    )

    search_agent = AssistantAgent(
        name="search_agent",
        description="Formulates arXiv search queries and fetches candidate papers.",
        system_message=(
            "You are an academic discovery agent. Formulate an effective arXiv query for the topic "
            "and call the arxiv_search tool. Fetch up to 3-5x the requested papers to filter for "
            "the most relevant ones, then provide the selected papers clearly to the summarizer."
        ),
        tools=[arxiv_tool],
        model_client=llm_client,
        reflect_on_tool_use=True,
    )

    summarizer = AssistantAgent(
        name="summarizer",
        description="Synthesizes paper abstracts into a structured Markdown literature review.",
        system_message=(
            "You are an expert academic reviewer. Using the papers provided by the search agent, "
            "write a structured literature review in Markdown with:\n"
            "1) A concise 2-3 sentence introduction.\n"
            "2) Structured bullet points per paper: **[Title](pdf_url)**, Authors, Problem, and Key Contribution.\n"
            "3) A synthesized takeaway and future outlook."
        ),
        model_client=llm_client,
    )

    return RoundRobinGroupChat(
        participants=[search_agent, summarizer],
        max_turns=2,
    )


async def run_litrev(
    topic: str,
    num_papers: int = 5,
    model: str = "dots-studio/dots-3-note-preview:free",
) -> AsyncGenerator[str, None]:
    """Orchestrates the multi-agent review run and yields conversational frames in real-time."""
    team = build_team(model=model)
    task_prompt = (
        f"Conduct a literature review on '{topic}'. Retrieve and review exactly {num_papers} papers."
    )

    async for msg in team.run_stream(task=task_prompt):
        if isinstance(msg, TextMessage):
            yield f"{msg.source}: {msg.content}"
        elif hasattr(msg, "content") and msg.content:
            text = msg.content if isinstance(msg.content, str) else str(msg.content)
            yield f"{getattr(msg, 'source', 'Agent')}: {text}"


if __name__ == "__main__":
    async def _demo() -> None:
        async for line in run_litrev("Retrieval Augmented Generation", num_papers=3):
            print(f"\n--- Output Frame ---\n{line}")

    asyncio.run(_demo())
