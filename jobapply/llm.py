from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from jobapply.config import OPENAI_API_KEY, OPENAI_MODEL


def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def chat_json(system: str, user: str, temperature: float = 0.2) -> dict[str, Any]:
    """Ask the model for a single JSON object."""
    client = get_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    return json.loads(text)


def chat_text(system: str, user: str, temperature: float = 0.3) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()
