"""Groq Free Tier LLM Service for AeroVoyage AI.

Integrates ultra-fast Llama-3 models (llama-3.3-70b-versatile, llama-3.1-8b-instant)
via Groq API for:
1. Advanced natural language intent understanding & entity extraction
2. Dynamic multi-city route & meeting connection optimization
3. Real-time itinerary personalization with weather & FET rate awareness
4. Conversational travel advisory inside ASI:One chat
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("AeroVoyage.LLM")

# Supported Free Tier Models on Groq
FREE_TIER_MODELS = [
    os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "llama-3.2-1b-preview",
]
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def get_groq_api_key() -> Optional[str]:
    """Retrieve Groq API key from environment."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    return key if key and key != "your_groq_api_key_here" else None


def is_groq_available() -> bool:
    """Check if Groq API key is configured."""
    return get_groq_api_key() is not None


def _call_groq(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    timeout: float = 8.0,
) -> Optional[str]:
    """Internal helper to call Groq OpenAI-compatible API with automatic model fallback."""
    api_key = get_groq_api_key()
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    candidates = [model] if model else FREE_TIER_MODELS

    for cand in candidates:
        payload: Dict[str, Any] = {
            "model": cand,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            elif resp.status_code in (404, 429):
                logger.info(f"Groq model '{cand}' returned {resp.status_code}, trying next model in chain...")
                continue
            else:
                logger.warning(f"Groq API error ({resp.status_code}): {resp.text[:200]}")
                break
        except Exception as exc:
            logger.warning(f"Groq call failed for {cand}: {exc}")

    return None


def parse_intent_with_llm(user_text: str) -> Optional[Dict[str, Any]]:
    """Extract destination cities, duration, budget, and business focus using Groq."""
    if not is_groq_available():
        return None

    system_prompt = (
        "You are an expert travel intent parser for AeroVoyage AI on Fetch.ai / ASI:One. "
        "Extract the trip details from the user prompt into valid JSON format.\n\n"
        "Output JSON structure:\n"
        "{\n"
        '  "cities": ["City1", "City2", ...],\n'
        '  "origin": "Origin City/Airport or null",\n'
        '  "days": <integer duration, default 3>,\n'
        '  "budget": <numeric USD budget, default 1500.0>,\n'
        '  "is_business": <boolean>,\n'
        '  "is_multi_city": <boolean>,\n'
        '  "meeting_focus": <brief string describing connection or meeting request, e.g. "Fastest connections between meetings">,\n'
        '  "special_requests": <string or null>\n'
        "}\n"
        "Always ensure cities contains all destination cities mentioned in order of itinerary."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]

    raw = _call_groq(messages, json_mode=True, temperature=0.1, timeout=6.0)
    if not raw:
        return None

    try:
        data = json.loads(raw)
        if data.get("cities") and isinstance(data["cities"], list) and len(data["cities"]) > 0:
            return {
                "cities": [c.strip().title() for c in data["cities"] if isinstance(c, str)],
                "origin": data.get("origin") or "",
                "days": int(data.get("days", 3)),
                "budget": float(data.get("budget", 1500.0)),
                "is_business": bool(data.get("is_business", True)),
                "is_multi_city": len(data.get("cities", [])) > 1 or bool(data.get("is_multi_city", False)),
                "meeting_focus": data.get("meeting_focus", "Optimized business transit"),
                "special_requests": data.get("special_requests"),
                "llm_parsed": True,
            }
    except Exception as exc:
        logger.warning(f"Error parsing LLM intent JSON: {exc}")

    return None


def synthesize_travel_brief_with_llm(
    route_label: str,
    days: int,
    weather_summary: str,
    packages: List[Dict[str, Any]],
    user_query: str,
) -> Optional[str]:
    """Generate a personalized, executive-level summary of the travel packages."""
    if not is_groq_available():
        return None

    system_prompt = (
        "You are AeroVoyage AI, the autonomous Travel & Logistics Concierge on ASI:One. "
        "Write a concise, polished 2-3 paragraph executive summary of the curated travel options. "
        "Highlight the fastest connections between meetings, zero-delay weather outlook, "
        "and how Fetch.ai smart escrow locks protect their reservations. "
        "Keep it professional, action-oriented, and formatted with bullet points."
    )

    pkg_briefs = []
    for p in packages[:3]:
        pkg_briefs.append(
            f"- {p['title']}: ${p['price_usd']:,.2f} USD (~{p['price_fet']:,.1f} FET). "
            f"Carrier: {p['carrier']}. Lodging: {p['hotel']}."
        )

    user_msg = (
        f"User Prompt: '{user_query}'\n"
        f"Route: {route_label} ({days} days)\n"
        f"Weather Telemetry: {weather_summary}\n"
        f"Generated Packages:\n" + "\n".join(pkg_briefs)
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]

    return _call_groq(messages, temperature=0.3, max_tokens=350, timeout=7.0)


def answer_travel_qa_with_llm(user_question: str, context: Optional[str] = None) -> Optional[str]:
    """Answer general travel, transit, visa, or crypto escrow questions in-character."""
    if not is_groq_available():
        return None

    system_prompt = (
        "You are AeroVoyage AI, an autonomous travel concierge agent operating on ASI:One and Agentverse. "
        "Answer the user's travel, logistics, or payment question directly, clearly, and concisely (1-2 short paragraphs). "
        "If asking about payments, explain that reservations are secured via Fetch.ai Payment Protocol in FET tokens. "
        "Always remain helpful, courteous, and authoritative."
    )

    user_content = user_question
    if context:
        user_content = f"Trip Context: {context}\n\nUser Question: {user_question}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    return _call_groq(messages, temperature=0.4, max_tokens=300, timeout=7.0)
