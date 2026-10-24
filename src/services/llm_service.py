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

# Supported Free Tier Models on Groq (prioritizing active models on user account)
FREE_TIER_MODELS = [
    os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
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


def route_and_reason_query(
    user_text: str,
    session_context: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Primary LLM Orchestrator:
    Autonomously reasons over user input to decide between:
    1. Conversational Q&A / Travel Advisory (visas, baggage, FET payments, weather questions, capabilities)
    2. Context Gathering / Clarification (when origin, destination, timing/dates, or budget is missing)
    3. Real-time Itinerary Search & Booking (when all required context items are known)
    """
    ctx = session_context or {}
    ctx_origin = ctx.get("origin") or None
    ctx_dest = ctx.get("destination") or None
    ctx_time = ctx.get("travel_time") or ctx.get("departure_date") or None
    ctx_budget = ctx.get("budget") or None

    if not is_groq_available():
        return evaluate_travel_context_fallback(user_text, ctx)

    router_prompt = (
        "You are AeroVoyage AI, the autonomous Travel & Logistics Concierge on ASI:One.\n"
        "Analyze the user message in light of current session knowledge:\n"
        f"Known context: {{\n"
        f'  "origin": {json.dumps(ctx_origin)},\n'
        f'  "destination": {json.dumps(ctx_dest)},\n'
        f'  "travel_time": {json.dumps(ctx_time)},\n'
        f'  "budget": {json.dumps(ctx_budget)}\n'
        "}}\n\n"
        "Required travel parameters to build an itinerary:\n"
        "1. origin: Where the user lives / departs from (e.g. New York, London, Mumbai, San Francisco)\n"
        "2. destination: Where the user wants to go (e.g. San Francisco, Tokyo, Berlin, Zurich, Milan, Paris)\n"
        "3. travel_time: What dates / timing or duration they want to plan (e.g. next Friday, 3 days, Nov 15-20)\n"
        "4. budget: Their target budget in USD or FET (e.g. $1500, 2000 USD, 5000 FET)\n\n"
        "Rules:\n"
        "1. If user asks general Q&A / travel advisory / capabilities / visas / baggage / how FET escrow works:\n"
        '   Output JSON: {"intent": "conversational_qa", "reply": "<your 1-2 paragraph authoritative answer as AeroVoyage Concierge>"}\n'
        "2. If user mentions travel intent, answers previous questions, or provides travel details:\n"
        "   - Extract any newly mentioned values for origin, cities (destination), travel_time, budget, days.\n"
        "   - Combine newly extracted values with Known context.\n"
        "   - If ANY of the 4 parameters (origin, destination, travel_time, budget) are still missing or unknown:\n"
        "     Output JSON: {\n"
        '       "intent": "ask_clarification",\n'
        '       "missing_fields": ["origin", ...],\n'
        '       "extracted": {"origin": "<origin or null>", "cities": ["<city>", ...], "travel_time": "<timing or null>", "budget": <float or null>, "days": <int or null>},\n'
        '       "reply": "<friendly, engaging response acknowledging what is known and asking specifically for the missing details: where they live, where they want to go, what time/dates, and what budget>"\n'
        "     }\n"
        "   - If ALL 4 parameters (origin, destination, travel_time, budget) are known:\n"
        "     Output JSON: {\n"
        '       "intent": "plan_itinerary",\n'
        '       "origin": "<origin>",\n'
        '       "cities": ["<city1>", ...],\n'
        '       "travel_time": "<travel_time>",\n'
        '       "days": <int, default 3>,\n'
        '       "budget": <float, default 1500.0>,\n'
        '       "is_business": <bool, default true>,\n'
        '       "meeting_focus": "<brief meeting or connection focus>"\n'
        "     }\n"
        "Always output valid JSON only."
    )

    messages = [
        {"role": "system", "content": router_prompt},
        {"role": "user", "content": user_text},
    ]

    raw = _call_groq(messages, json_mode=True, temperature=0.1, timeout=8.0)
    if not raw:
        return evaluate_travel_context_fallback(user_text, ctx)

    try:
        data = json.loads(raw)
        # Sanity check: if intent is ask_clarification but all 4 fields are now present, convert to plan_itinerary
        if data.get("intent") == "ask_clarification":
            ext = data.get("extracted", {})
            origin = ext.get("origin") or ctx_origin
            cities = ext.get("cities") or ([ctx_dest] if ctx_dest else [])
            time_val = ext.get("travel_time") or ctx_time
            budget_val = ext.get("budget") or ctx_budget
            if origin and cities and time_val and budget_val:
                return {
                    "intent": "plan_itinerary",
                    "origin": origin,
                    "cities": cities if isinstance(cities, list) else [cities],
                    "travel_time": time_val,
                    "days": int(ext.get("days") or 3),
                    "budget": float(budget_val),
                    "is_business": True,
                    "meeting_focus": "Fastest connections between meetings with guaranteed buffers",
                }
        return data
    except Exception as exc:
        logger.warning(f"Error parsing LLM router decision: {exc}")
        return evaluate_travel_context_fallback(user_text, ctx)


def evaluate_travel_context_fallback(
    user_text: str,
    session_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Deterministic NLP and Regex fallback when Groq LLM is unavailable."""
    ctx = dict(session_context or {})
    lower_text = user_text.lower()
    
    # Check general Q&A / greetings without travel intent
    qa_triggers = ("how does", "what is", "do i need", "visa", "baggage", "escrow", "who are you", "what can you do")
    if any(q in lower_text for q in qa_triggers) and not any(k in lower_text for k in ("plan", "book", "trip", "travel", "flight", "hotel", "destination")):
        return {
            "intent": "conversational_qa",
            "reply": (
                "AeroVoyage AI is your autonomous Travel & Logistics Concierge on ASI:One. "
                "I orchestrate multi-city business itineraries, monitor live weather telemetry via Open-Meteo, "
                "and settle coordination fees and vendor escrows via Fetch.ai FET ledger."
            ),
        }

    # Extract origin ("from <city>", "leaving <city>", "living in <city>", "live in <city>", "departing <city>")
    extracted_origin = ctx.get("origin")
    origin_match = re.search(
        r"\b(?:from|leaving|living\s+in|live\s+in|departing\s+(?:from)?)\s+([A-Za-z\s]+?)(?=[,.]|\s+(?:to|heading|visiting|on|in|next|under|plan|\$|for|$)|$)",
        user_text,
        re.IGNORECASE,
    )
    if origin_match:
        extracted_origin = origin_match.group(1).strip().title()

    # Extract destination ("to <city>", "visiting <city>", "trip to <city>")
    extracted_dest = ctx.get("destination")
    dest_cities = []
    dest_match = re.search(
        r"\b(?:to|visiting|trip\s+to|heading\s+to)\s+([A-Za-z\s,]+?)(?=[,.]|\s+(?:from|on|in|next|under|with|\$|for|$)|$)",
        user_text,
        re.IGNORECASE,
    )
    if dest_match:
        cand_str = dest_match.group(1).strip()
        parts = [p.strip().title() for p in re.split(r"[,&]|\band\b", cand_str) if p.strip()]
        if parts:
            dest_cities = parts
            extracted_dest = " ➔ ".join(dest_cities)
    elif not extracted_dest:
        # Check against common known cities
        common_cities = ["Berlin", "Zurich", "Milan", "London", "Paris", "New York", "San Francisco", "Tokyo", "Dubai", "Singapore"]
        for c in common_cities:
            if re.search(r"\b" + re.escape(c) + r"\b", user_text, re.IGNORECASE):
                dest_cities.append(c)
        if dest_cities:
            extracted_dest = " ➔ ".join(dest_cities)

    # Extract travel_time / duration
    extracted_time = ctx.get("travel_time")
    time_match = re.search(r"(\d+)[-\s]day|\b(?:next\s+(?:week|month|friday|monday|weekend)|tomorrow|this\s+weekend|\d{1,2}\s+(?:days|nights))\b", user_text, re.IGNORECASE)
    days = ctx.get("days", 3)
    if time_match:
        extracted_time = time_match.group(0).strip()
        day_digit = re.search(r"(\d+)", extracted_time)
        if day_digit:
            days = int(day_digit.group(1))

    # Extract budget
    extracted_budget = ctx.get("budget")
    budget_match = re.search(r"\b(?:under|budget\s*(?:of|is)?\s*|\$)\s*\$?(\d{2,6})\b|\$(\d{2,6})", user_text, re.IGNORECASE)
    if budget_match:
        val_str = budget_match.group(1) or budget_match.group(2)
        try:
            extracted_budget = float(val_str)
        except (ValueError, TypeError):
            pass

    # Check missing fields
    missing = []
    if not extracted_origin:
        missing.append("origin")
    if not extracted_dest and not dest_cities:
        missing.append("destination")
    if not extracted_time:
        missing.append("travel_time")
    if not extracted_budget:
        missing.append("budget")

    if missing:
        questions = []
        if "origin" in missing:
            questions.append("• 📍 **Where do you live / where are you departing from?**")
        if "destination" in missing:
            questions.append("• 🎯 **Where do you want to travel to?**")
        if "travel_time" in missing:
            questions.append("• 📅 **What time or dates are you planning for, and for how many days?**")
        if "budget" in missing:
            questions.append("• 💰 **What is your estimated budget (in USD or FET)?**")

        known_brief = []
        if extracted_origin:
            known_brief.append(f"Departing from **{extracted_origin}**")
        if extracted_dest:
            known_brief.append(f"Traveling to **{extracted_dest}**")
        if extracted_time:
            known_brief.append(f"Timing: **{extracted_time}**")
        if extracted_budget:
            known_brief.append(f"Budget: **${extracted_budget:,.0f}**")

        known_str = f"Noted: {', '.join(known_brief)}. " if known_brief else ""
        reply_msg = (
            f"👋 {known_str}To curate your optimal flight connections, hotel stays, and live Open-Meteo weather forecast, please share:\n\n"
            + "\n".join(questions)
            + "\n\nYou can reply directly in chat or use the travel parameters card below!"
        )

        return {
            "intent": "ask_clarification",
            "missing_fields": missing,
            "extracted": {
                "origin": extracted_origin,
                "cities": dest_cities if dest_cities else ([extracted_dest] if extracted_dest else []),
                "travel_time": extracted_time,
                "budget": extracted_budget,
                "days": days,
            },
            "reply": reply_msg,
        }

    # All 4 are present!
    cities = dest_cities if dest_cities else [extracted_dest]
    return {
        "intent": "plan_itinerary",
        "origin": extracted_origin,
        "cities": cities,
        "travel_time": extracted_time,
        "days": days,
        "budget": extracted_budget,
        "is_business": True,
        "meeting_focus": "Fastest connections between meetings with guaranteed buffers",
    }


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
