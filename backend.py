'''
Core module for a multi-agent literature-review assistant built on the AutoGen AgentChat stack (v0.4+). It exposes a single coroutine, run_litrev(), that orchestrates a two-agent workflow:

search_agent — formulates an arXiv query and retrieves papers via arxiv_search.

summarizer — turns the selected papers into a concise Markdown literature review.

The module is self-contained and ready to drop into CLI apps or frameworks like Streamlit, FastAPI, and Gradio.
'''


from __future__ import annotations
import os
import asyncio
from typing import AsyncGenerator, Dict, List

import arxiv  
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import (
    TextMessage
)
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
load_dotenv()

def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """Return a compact list of arXiv papers matching *query*.

    Each element contains: ``title``, ``authors``, ``published``, ``summary`` and
    ``pdf_url``.  The helper is wrapped as an AutoGen *FunctionTool* below so it
    can be invoked by agents through the normal tool‑use mechanism.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers: List[Dict] = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary,
            "pdf_url": result.pdf_url
        })
    return papers
arxiv_tool = FunctionTool(
    arxiv_search,
    description=(
        "searches arXiv and returns up to *max_results* papers, each containing a title, authors, published date, summary, and PDF URL."
        ),
)

#agent and  team factory
def build_team() -> RoundRobinGroupChat:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing API key. Set OPENAI_API_KEY or OPENROUTER_API_KEY (your OpenRouter key starts with sk-or-...)."
        )

    # Tell Autogen what this non-OpenAI model can do
    DEEPSEEK_MODEL = "deepseek/deepseek-chat-v3.1:free"
    DEEPSEEK_MODEL_INFO = {
        "provider": "openrouter",
        "family": "deepseek",
        "endpoint_type": "chat-completion",
        "context_length": 8192,
        "function_calling": True,
        "reasoning": True,
        "vision": False,
        "input_audio": False,
        "output_audio": False,
        "structured_output": True,
        "json_output": True,
    }

    llm_client = OpenAIChatCompletionClient(
        model=DEEPSEEK_MODEL,
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        model_info=DEEPSEEK_MODEL_INFO,   # <-- important
    )

    search_agent = AssistantAgent(
        name="search_agent",
        description="Crafts arXiv queries and retrieves candidate papers.",
        system_message=(
            "Given a user topic, think of the best arXiv query and call the provided tool. "
            "Always fetch five-times the papers requested so you can down-select the most relevant ones. "
            "Return exactly the requested number as concise JSON to the summarizer."
        ),
        tools=[arxiv_tool],
        model_client=llm_client,
        reflect_on_tool_use=True,
    )

    summarizer = AssistantAgent(
        name="summarizer",
        description="Produces a short Markdown review from provided papers.",
        system_message=(
            "You are an expert researcher. When you receive the JSON list of papers, write a literature-review style report in Markdown:\n"
            "1) 2–3 sentence intro.\n"
            "2) One bullet per paper with: [title](link), authors, problem, key contribution.\n"
            "3) One-sentence takeaway."
        ),
        model_client=llm_client,
    )

    return RoundRobinGroupChat(
        participants=[search_agent, summarizer], max_turns=2
        )



#orchestrator is like a function

async def run_litrev(
    topic: str,
    num_papers: int = 5,
    model: str = "deepseek/deepseek-chat-v3.1:free",
) -> AsyncGenerator[str, None]:
    """Yield strings representing the conversation in real‑time."""

    team = build_team()
    task_prompt = (
        f"Conduct a literature review on **{topic}** and return exactly {num_papers} papers."
    )

    async for msg in team.run_stream(task=task_prompt):
        if isinstance(msg, TextMessage):
            yield f"{msg.source}: {msg.content}"

#cli testing
if __name__ == "__main__":
    async def _demo() -> None:
        async for line in run_litrev("Artificial Intelligence", num_papers=5):
            print(line)

    asyncio.run(_demo()) 