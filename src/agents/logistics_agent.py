"""Logistics & Live Intelligence Agent for AeroVoyage.

Responsibilities:
- Autonomous real-time travel telemetry aggregation (Weather via Open-Meteo, Currency via CoinGecko).
- Multi-criteria flight and hotel package generation & scoring.
- Responds to inter-agent queries from the Concierge Agent.
"""

import json
from uagents import Agent, Context, Protocol
from src.config import LOGISTICS_CONFIG
from src.protocols.internal_protocols import QueryItineraryRequest, QueryItineraryResponse
from src.services.travel_engine import generate_itinerary_packages

# Initialize agent
logistics_agent = Agent(
    name=LOGISTICS_CONFIG.name,
    seed=LOGISTICS_CONFIG.seed,
    port=LOGISTICS_CONFIG.port,
    endpoint=[LOGISTICS_CONFIG.endpoint] if not LOGISTICS_CONFIG.mailbox else None,
    mailbox=LOGISTICS_CONFIG.mailbox,
)

logistics_proto = Protocol(name="LogisticsProtocol", version="1.0.0")


@logistics_proto.on_message(QueryItineraryRequest)
async def handle_query_itinerary(ctx: Context, sender: str, msg: QueryItineraryRequest):
    ctx.logger.info(
        f"🔎 [LogisticsAgent] Processing itinerary query from {sender} | "
        f"Route: {msg.origin} ➔ {msg.destination} | Budget: ${msg.max_budget}"
    )

    try:
        data = generate_itinerary_packages(
            origin=msg.origin,
            destination=msg.destination,
            departure_date=msg.departure_date,
            return_date=msg.return_date,
            max_budget_usd=msg.max_budget,
        )

        response = QueryItineraryResponse(
            session_id=msg.session_id,
            success=True,
            data_json=json.dumps(data),
            error_msg=None,
        )
        ctx.logger.info(
            f"✅ [LogisticsAgent] Compiled {len(data.get('packages', []))} packages. Responding to {sender}."
        )
    except Exception as exc:
        ctx.logger.error(f"❌ [LogisticsAgent] Itinerary computation failed: {exc}")
        response = QueryItineraryResponse(
            session_id=msg.session_id,
            success=False,
            data_json="{}",
            error_msg=str(exc),
        )

    await ctx.send(sender, response)


logistics_agent.include(logistics_proto, publish_manifest=True)


@logistics_agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"✈️ Logistics & Live Intelligence Agent active at address: {logistics_agent.address}")


if __name__ == "__main__":
    logistics_agent.run()
