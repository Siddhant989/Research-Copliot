"""
app/agents/llm.py — One shared Gemini LLM instance used by all agents.

Why centralise it here?
  • All agents use the same model and temperature — change it in one place.
  • Avoids re-creating the client on every agent call (saves latency).

Usage in any agent file:
    from app.agents.llm import llm
    response = llm.invoke([SystemMessage(...), HumanMessage(...)])
    text = response.content
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()  # make sure .env is loaded even when imported early

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    google_api_key=os.getenv("GEMINI_API_KEY", ""),
    temperature=0.3,       # lower = more focused/deterministic answers
    max_output_tokens=2048,
)
