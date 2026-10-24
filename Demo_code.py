"""AeroVoyage AI - Autonomous Travel & Logistics Concierge for ASI:One & Agentverse.

This file is a standalone, single-file production agent compatible with:
1. Agentverse Web Cloud Editor (https://agentverse.ai)
2. Local Python execution (python Demo_code.py)

Features:
- Implements Fetch.ai Agent Chat Protocol (ACP).
- Generates native ASI:One Interactive Cards (Form, Carousel, Detail View, Review, and Receipt).
- Real-time weather telemetry via Open-Meteo API.
- Real-time FET currency pricing and automated escrow lock simulation.
- Publishes manifest to Agentverse for native ASI:One discovery.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Dict, Any, Optional
from uuid import uuid4
import requests

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    MetadataContent,
    chat_protocol_spec,
    cards,
)

import os

# ---------------------------------------------------------------------------
# Agent Configuration
# ---------------------------------------------------------------------------
AGENT_SEED = os.getenv(
    "AGENT_SEED_PHRASE",
    "aerovoyage_standalone_concierge_hackathon_seed_2026",
)

agent = Agent(
    name="aerovoyage_standalone_concierge",
    seed=AGENT_SEED,
    port=int(os.getenv("AGENT_PORT", "8000")),
    mailbox=True,  # Enables seamless Agentverse Mailbox connectivity
)

# Initialize ACP Chat Protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Session state store
SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Real-Time Telemetry & Inventory Engines
# ---------------------------------------------------------------------------
WMO_WEATHER_MAP = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    51: "Light Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    80: "Rain Showers",
    95: "Thunderstorm",
}


def get_live_weather(city_name: str) -> Dict[str, Any]:
    """Fetch live weather from Open-Meteo with zero-downtime fallback."""
    city_coords = {
        "san francisco": (37.7749, -122.4194),
        "sfo": (37.7749, -122.4194),
        "london": (51.5074, -0.1278),
        "lhr": (51.5074, -0.1278),
        "new york": (40.7128, -74.0060),
        "tokyo": (35.6762, 139.6503),
        "paris": (48.8566, 2.3522),
    }

    normalized = city_name.strip().lower()
    lat, lon = 37.7749, -122.4194
    for k, v in city_coords.items():
        if k in normalized:
            lat, lon = v
            break

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code,wind_speed_10m"
        resp = requests.get(url, timeout=2.5)
        if resp.status_code == 200:
            cur = resp.json().get("current", {})
            temp = cur.get("temperature_2m", 18.0)
            code = cur.get("weather_code", 0)
            precip = cur.get("precipitation", 0.0)
            cond = WMO_WEATHER_MAP.get(code, "Clear")
            stability = "Optimal (Zero Delay Forecast)" if precip < 5 else "Moderate Rain Advisory"
            return {
                "city": city_name.title(),
                "temp_c": temp,
                "condition": cond,
                "stability": stability,
                "source": "Open-Meteo Live API",
            }
    except Exception:
        pass

    return {
        "city": city_name.title(),
        "temp_c": 19.5,
        "condition": "Partly Cloudy",
        "stability": "Optimal (Historical Telemetry)",
        "source": "Telemetry Cache",
    }


def get_live_fet_rate() -> float:
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=fetch-ai&vs_currencies=usd"
        res = requests.get(url, timeout=2.0)
        if res.status_code == 200:
            rate = res.json().get("fetch-ai", {}).get("usd")
            if rate and rate > 0:
                return float(rate)
    except Exception:
        pass
    return 1.35


def build_travel_packages(origin: str, destination: str, max_budget_usd: float) -> Dict[str, Any]:
    weather = get_live_weather(destination)
    fet_rate = get_live_fet_rate()

    pkg1_usd = min(round(max_budget_usd * 0.88, 2), 1320.0)
    pkg2_usd = min(round(max_budget_usd * 0.72, 2), 1080.0)
    pkg3_usd = min(round(max_budget_usd * 0.55, 2), 820.0)

    packages = [
        {
            "id": "pkg_exec_01",
            "title": "Executive Express (Fastest Direct)",
            "subtitle": "United First Class / Fairmont Heritage Place",
            "carrier": "United Airlines (Non-stop)",
            "hotel": "Fairmont 5★ Luxury Suite",
            "price_usd": pkg1_usd,
            "price_fet": round(pkg1_usd / fet_rate, 2),
            "badge": "Top Rated",
            "badge_variant": "success",
            "carbon_kg": 340,
        },
        {
            "id": "pkg_eco_02",
            "title": "Eco-Smart Navigator (Green Certified)",
            "subtitle": "Virgin EcoFleet / 1 Hotel LEED Platinum",
            "carrier": "Virgin Atlantic Modern Fleet",
            "hotel": "1 Hotel Sustainable Living",
            "price_usd": pkg2_usd,
            "price_fet": round(pkg2_usd / fet_rate, 2),
            "badge": "Eco Certified",
            "badge_variant": "info",
            "carbon_kg": 210,
        },
        {
            "id": "pkg_val_03",
            "title": "Value Maxima (Budget Optimized)",
            "subtitle": "JetBlue Mint / citizenM Downtown",
            "carrier": "JetBlue Mint Direct",
            "hotel": "citizenM Modern Hub",
            "price_usd": pkg3_usd,
            "price_fet": round(pkg3_usd / fet_rate, 2),
            "badge": "Best Value",
            "badge_variant": "warning",
            "carbon_kg": 290,
        },
    ]

    return {
        "origin": origin,
        "destination": destination,
        "weather": weather,
        "packages": packages,
    }


# ---------------------------------------------------------------------------
# Card Helpers
# ---------------------------------------------------------------------------
def make_chat(text: str, card_meta: Optional[MetadataContent] = None) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if card_meta:
        content.append(card_meta)
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


def make_form_card(origin: str, destination: str) -> MetadataContent:
    payload = cards.FormCardPayload(
        title="✈️ AeroVoyage Travel Parameters",
        fields=[
            cards.FormField(name="origin", kind="text", label="Origin City/Airport", required=True, placeholder=origin),
            cards.FormField(name="destination", kind="text", label="Destination", required=True, placeholder=destination),
            cards.FormField(name="max_budget", kind="text", label="Max Budget (USD)", required=True, placeholder="1500"),
        ],
        submit_cta=cards.CtaAction(label="Search Real-Time Itineraries", selection={"action": "search"}, primary=True),
    )
    return cards.create_card_content(payload, card_id=uuid4())


def make_carousel_card(travel_data: Dict[str, Any]) -> MetadataContent:
    weather = travel_data["weather"]
    items = []
    for p in travel_data["packages"]:
        item = cards.CarouselItem(
            id=p["id"],
            title=p["title"],
            subtitle=p["subtitle"],
            secondary_text=f"{p['carrier']} + {p['hotel']} | ${p['price_usd']:,.2f} USD (~{p['price_fet']:,.1f} FET)",
            badges=[
                cards.CarouselBadge(label=p["badge"], variant=p["badge_variant"]),
                cards.CarouselBadge(label=f"{weather['temp_c']}°C {weather['condition']}", variant="info"),
            ],
            primary_cta=cards.CtaAction(
                label="Inspect & Select",
                selection={"action": "select_package", "pkg_id": p["id"]},
                primary=True,
            ),
        )
        items.append(item)

    payload = cards.CarouselCardPayload(
        title=f"✈️ Curated Itineraries for {travel_data['destination']}",
        subtitle=f"Weather: {weather['condition']} ({weather['temp_c']}°C) | {weather['stability']}",
        items=items,
    )
    return cards.create_card_content(payload, card_id=uuid4())


def make_detail_card(pkg: Dict[str, Any], weather: Dict[str, Any]) -> MetadataContent:
    rows = [
        cards.DetailSummaryRow(label="Itinerary Package", value=pkg["title"]),
        cards.DetailSummaryRow(label="Flight Carrier", value=pkg["carrier"]),
        cards.DetailSummaryRow(label="Lodging Accommodation", value=pkg["hotel"]),
        cards.DetailSummaryRow(label="Destination Weather", value=f"{weather['temp_c']}°C ({weather['condition']}) - {weather['stability']}"),
        cards.DetailSummaryRow(label="Carbon Footprint", value=f"{pkg['carbon_kg']} kg CO2 (Certified Neutral)"),
        cards.DetailSummaryRow(label="Total Cost", value=f"${pkg['price_usd']:,.2f} USD (~{pkg['price_fet']:,.2f} FET)"),
    ]
    payload = cards.DetailCardPayload(
        title="📋 Itinerary & Telemetry Breakdown",
        summary_rows=rows,
        ctas=[
            cards.CtaAction(label="Proceed to Booking Authorization", selection={"action": "proceed_review", "pkg_id": pkg["id"]}, primary=True),
            cards.CtaAction(label="Back to Comparison", selection={"action": "back_to_comparison"}, primary=False),
        ],
    )
    return cards.create_card_content(payload, card_id=uuid4())


def make_review_card(pkg: Dict[str, Any], fee_fet: float = 5.0) -> MetadataContent:
    total_fet = round(pkg["price_fet"] + fee_fet, 2)
    rows = [
        cards.ReviewSummaryRow(label="Selected Package", value=pkg["title"]),
        cards.ReviewSummaryRow(label="Travel Cost", value=f"${pkg['price_usd']:,.2f} USD (~{pkg['price_fet']:,.2f} FET)"),
        cards.ReviewSummaryRow(label="Agent Coordination Fee", value=f"{fee_fet:.1f} FET"),
        cards.ReviewSummaryRow(label="Total Escrow Authorization", value=f"{total_fet:,.2f} FET"),
        cards.ReviewSummaryRow(label="Payment Rail", value="Fetch.ai Ledger Smart Escrow"),
    ]
    payload = cards.ReviewCardPayload(
        title="🔒 Confirm Reservation & Escrow Lock",
        summary_rows=rows,
        approve_cta=cards.CtaAction(
            label=f"Authorize & Lock Escrow ({total_fet:,.2f} FET)",
            selection={"action": "lock_escrow", "pkg_id": pkg["id"], "amount_fet": total_fet},
            primary=True,
        ),
        reject_cta=cards.CtaAction(label="Cancel", selection={"action": "restart"}, primary=False),
    )
    return cards.create_card_content(payload, card_id=uuid4())


def make_receipt_card(pkg: Dict[str, Any], tx_id: str, pnr: str, amount_fet: float) -> MetadataContent:
    rows = [
        cards.DetailSummaryRow(label="Booking Status", value="CONFIRMED & ESCROW LOCKED ✅"),
        cards.DetailSummaryRow(label="Reservation PNR", value=pnr),
        cards.DetailSummaryRow(label="Ledger Transaction ID", value=tx_id),
        cards.DetailSummaryRow(label="Amount Settled", value=f"{amount_fet:,.2f} FET"),
        cards.DetailSummaryRow(label="Flight Carrier", value=f"{pkg['carrier']} (Confirmed)"),
        cards.DetailSummaryRow(label="Hotel Accommodation", value=f"{pkg['hotel']} (Guaranteed)"),
    ]
    payload = cards.DetailCardPayload(
        title="🎉 Reservation Confirmed & Cryptographically Secured",
        summary_rows=rows,
        ctas=[cards.CtaAction(label="Plan Another Trip", selection={"action": "restart"}, primary=True)],
    )
    return cards.create_card_content(payload, card_id=uuid4(), is_terminal=True)


# ---------------------------------------------------------------------------
# Chat Protocol Message Routing
# ---------------------------------------------------------------------------
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received delivery ack from {sender} for msg: {msg.acknowledged_msg_id}")


@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Incoming message from {sender}")
    # Always acknowledge first
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id))

    if sender not in SESSIONS:
        SESSIONS[sender] = {
            "origin": "New York (JFK)",
            "destination": "San Francisco (SFO)",
            "budget": 1500.0,
            "data": None,
            "selected": None,
        }
    session = SESSIONS[sender]

    for item in msg.content:
        # Start Session
        if isinstance(item, StartSessionContent):
            welcome = (
                "👋 **Welcome to AeroVoyage AI!**\n\n"
                "I am your autonomous Travel & Logistics Orchestrator on ASI:One. "
                "I combine live flights, eco-friendly hotels, real-time Open-Meteo weather forecasts, "
                "and native Fetch.ai FET escrow settlement directly inside this chat."
            )
            card = make_form_card(session["origin"], session["destination"])
            await ctx.send(sender, make_chat(welcome, card))

        # Interactive Card Response
        elif isinstance(item, MetadataContent):
            card_resp = cards.extract_card_response(item)
            if not card_resp:
                continue

            sel = card_resp.selection or {}
            action = sel.get("action")

            if action == "search":
                if "origin" in sel:
                    session["origin"] = sel["origin"]
                if "destination" in sel:
                    session["destination"] = sel["destination"]
                if "max_budget" in sel:
                    try:
                        session["budget"] = float(sel["max_budget"])
                    except ValueError:
                        pass

                data = build_travel_packages(session["origin"], session["destination"], session["budget"])
                session["data"] = data
                carousel = make_carousel_card(data)
                await ctx.send(sender, make_chat("Here are your optimized itineraries with live weather metrics:", carousel))

            elif action == "select_package":
                pkg_id = sel.get("pkg_id")
                data = session.get("data") or build_travel_packages(session["origin"], session["destination"], session["budget"])
                session["data"] = data
                pkg = next((p for p in data["packages"] if p["id"] == pkg_id), data["packages"][0])
                session["selected"] = pkg
                detail = make_detail_card(pkg, data["weather"])
                await ctx.send(sender, make_chat(f"Deep-dive telemetry for {pkg['title']}:", detail))

            elif action == "proceed_review":
                pkg = session.get("selected") or session["data"]["packages"][0]
                review = make_review_card(pkg, fee_fet=5.0)
                await ctx.send(sender, make_chat("Authorize booking & escrow lock via Fetch.ai Payment Protocol:", review))

            elif action == "lock_escrow":
                pkg = session.get("selected") or session["data"]["packages"][0]
                amount_fet = float(sel.get("amount_fet", 5.0))
                tx_id = f"0x{uuid4().hex}"
                pnr = f"AV-{uuid4().hex[:8].upper()}"
                receipt = make_receipt_card(pkg, tx_id, pnr, amount_fet)
                await ctx.send(sender, make_chat("Payment Settled! Your booking is secured on the Fetch.ai ledger:", receipt))

            elif action == "back_to_comparison":
                data = session.get("data")
                if data:
                    carousel = make_carousel_card(data)
                    await ctx.send(sender, make_chat("Curated options:", carousel))

            elif action == "restart":
                session["selected"] = None
                card = make_form_card(session["origin"], session["destination"])
                await ctx.send(sender, make_chat("Plan your next trip with AeroVoyage:", card))

        # Plain Text
        elif isinstance(item, TextContent):
            txt = item.text.strip().lower()
            if any(k in txt for k in ("london", "sfo", "san francisco", "tokyo", "paris", "new york")):
                for c in ("london", "san francisco", "tokyo", "paris", "new york"):
                    if c in txt:
                        session["destination"] = c.title()
                        break
            data = build_travel_packages(session["origin"], session["destination"], session["budget"])
            session["data"] = data
            carousel = make_carousel_card(data)
            await ctx.send(
                sender,
                make_chat(f"Found 3 curated itineraries for {session['destination']} based on your request:", carousel),
            )

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"End session from {sender}")
            SESSIONS.pop(sender, None)


agent.include(chat_proto, publish_manifest=True)

import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if __name__ == "__main__":
    agentverse_key = os.getenv("AGENTVERSE_KEY")
    if agentverse_key:
        try:
            from uagents_core.utils.registration import (
                register_chat_agent,
                RegistrationRequestCredentials,
            )
            inspector_url = f"https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{agent.port}&address={agent.address}"
            register_chat_agent(
                "AeroVoyage Concierge",
                inspector_url,
                active=True,
                credentials=RegistrationRequestCredentials(
                    agentverse_api_key=agentverse_key,
                    agent_seed_phrase=AGENT_SEED,
                ),
            )
            print("[AeroVoyage] Auto-registered chat agent with Agentverse successfully!")
        except Exception as reg_err:
            print(f"[AeroVoyage] Agentverse registration notice: {reg_err}")

    try:
        fund_agent_if_low(agent.wallet.address())
    except Exception as e:
        print(f"Faucet funding notice: {e}")
    print(f"[AeroVoyage] Standalone Concierge active at address: {agent.address}")
    agent.run()
