"""
Grok API Client for BizGenie AI
Uses xAI's Grok API with OpenAI-compatible SDK
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Generator, Optional

load_dotenv()

GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-3-mini")


def get_grok_client(api_key: Optional[str] = None) -> OpenAI:
    """Return an OpenAI-compatible client pointed at xAI's endpoint."""
    key = api_key or os.getenv("GROK_API_KEY", "")
    if not key or key.startswith("your_"):
        raise ValueError(
            "No valid Grok API key found. "
            "Please enter your API key in the sidebar or set GROK_API_KEY in .env. "
            "Get a key at https://console.x.ai"
        )
    return OpenAI(api_key=key, base_url=GROK_BASE_URL)


def call_grok(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
) -> str:
    """Call Grok API and return full response text."""
    client = get_grok_client(api_key)
    response = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""


def call_grok_stream(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
) -> Generator:
    """Call Grok API with streaming."""
    client = get_grok_client(api_key)
    stream = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=2048,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
