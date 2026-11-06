import os
import asyncio
import arxiv
import streamlit as st
from typing import AsyncGenerator

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 1. Retrieve the OpenRouter API Key
api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

# 2. Configure OpenRouter client for AutoGen
model_client = OpenAIChatCompletionClient(
    model="dots-studio/dots-3-note-preview:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "unknown",
    },
    extra_create_args={
        "extra_body": {
            "reasoning": {"enabled": True}
        }
    }
)

# 3. ArXiv fetch tool
def search_arxiv_papers(query: str, max_results: int = 5) -> str:
    """Searches arXiv for papers matching the topic query and returns titles and abstracts."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for paper in client.results(search):
        results.append(
            f"Title: {paper.title}\n"
            f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            f"URL: {paper.entry_id}\n"
            f"Abstract: {paper.summary}\n"
            f"{'-'*40}"
        )
    return "\n".join(results) if results else "No papers found."


# 4. Agent Definitions
search_agent = AssistantAgent(
    name="Search_Agent",
    description="Agent responsible for searching arXiv and presenting findings.",
    model_client=model_client,
    tools=[search_arxiv_papers],
    system_message=(
        "You are an academic research discovery agent. Given a research query, "
        "retrieve relevant arXiv papers and present a clear overview of the findings."
    )
)

summarizer_agent = AssistantAgent(
    name="Summarizer",
    description="Agent that synthesizes papers into a comprehensive structured literature review.",
    model_client=model_client,
    system_message=(
        "You are an expert academic synthesizer. Analyze the papers found by Search_Agent and "
        "produce a structured, comprehensive literature review with key themes, methodologies, "
        "and critical gaps in Markdown format."
    )
)

# 5. Pipeline Generator
async def run_litrev(topic: str, num_papers: int = 5) -> AsyncGenerator[str, None]:
    team = RoundRobinGroupChat(
        participants=[search_agent, summarizer_agent],
        termination_condition=MaxMessageTermination(max_messages=2)
    )

    task_prompt = f"Conduct a literature review on: '{topic}'. Fetch up to {num_papers} papers."

    async for message in team.run_stream(task=task_prompt):
        if hasattr(message, "content") and message.content:
            yield f"{message.source}: {message.content}"
