"""
agents/llm.py — LLM factory for agent nodes.

All agents should use utils.llm_manager.invoke_with_fallback() for multi-key
fallback.  This module exposes make_llm() as a simple factory and keeps a
legacy `llm` singleton for any code that hasn't been migrated yet.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def make_llm(model: str, api_key: str) -> ChatGoogleGenerativeAI:
    """Create a fresh ChatGoogleGenerativeAI instance for the given key/model."""
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.3,
        max_output_tokens=4096,
        google_api_key=api_key,
    )


# ── Legacy singleton (fallback when no numbered keys exist) ───────────────────
_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    temperature=0.3,
    max_output_tokens=4096,
    google_api_key=_api_key,
)
