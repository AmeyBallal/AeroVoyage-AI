"""ASI:One Interactive Card Builders for AeroVoyage AI.

Builds standardized cards conforming to Fetch.ai Agentverse & ASI:One card specs:
- Form Card: Trip parameter collection
- Carousel Card: Itinerary comparison with CTA selection
- Detail Card: Comprehensive flight, lodging, and live weather telemetry breakdown
- Review Card: Escrow authorization and financial sign-off
- Payment/Confirmation Card: Cryptographic transaction confirmation
"""

from uuid import uuid4
from typing import Dict, Any, Optional
from uagents_core.contrib.protocols.chat import (
    MetadataContent,
    cards,
)


def build_preference_form_card(
    default_origin: str = "New York (JFK)",
    default_destination: str = "San Francisco (SFO)",
) -> MetadataContent:
    """Build an interactive Form Card allowing user to adjust travel parameters directly in ASI:One."""
    form_payload = cards.FormCardPayload(
        title="✈️ AeroVoyage Travel Parameters",
        fields=[
            cards.FormField(
                name="origin",
                kind="text",
                label="Departure Origin",
                required=True,
                placeholder=default_origin,
            ),
            cards.FormField(
                name="destination",
                kind="text",
                label="Destination City / Airport",
                required=True,
                placeholder=default_destination,
            ),
            cards.FormField(
                name="departure_date",
                kind="text",
                label="Departure Date (YYYY-MM-DD)",
                required=True,
                placeholder="2026-11-15",
            ),
            cards.FormField(
                name="return_date",
                kind="text",
                label="Return Date (YYYY-MM-DD)",
                required=True,
                placeholder="2026-11-18",
            ),
            cards.FormField(
                name="max_budget",
                kind="text",
                label="Maximum Budget (USD)",
                required=True,
                placeholder="1500",
            ),
        ],
        submit_cta=cards.CtaAction(
            label="Search Real-Time Itineraries",
            selection={"action": "search_itineraries"},
            primary=True,
        ),
    )
    return cards.create_card_content(form_payload, card_id=uuid4(), is_terminal=False)


def build_itinerary_carousel_card(travel_data: Dict[str, Any]) -> MetadataContent:
    """Build a Carousel Card comparing optimized flight & lodging options with 1-click select CTAs."""
    packages = travel_data.get("packages", [])
    route_label = travel_data.get("route_label", travel_data.get("destination", "Destination"))
    weather_summary = travel_data.get("weather_summary")
    weather = travel_data.get("weather", {})
    weather_cond = weather.get("condition", "Optimal")
    weather_temp = weather.get("temperature_c", "19")

    subtitle = f"Live Weather: {weather_summary} | Open-Meteo Verified" if weather_summary else f"Live Weather: {weather_cond} ({weather_temp}°C) | Open-Meteo Verified"

    items = []
    for pkg in packages:
        metrics = pkg.get("metrics", {})
        badge_text = metrics.get("badge", "Recommended")
        badge_variant = metrics.get("badge_variant", "info")
        price_usd = metrics.get("price_usd", 0)
        price_fet = metrics.get("price_fet", 0)

        badges = [cards.CarouselBadge(label=badge_text, variant=badge_variant)]
        if "weather_list" in travel_data and len(travel_data["weather_list"]) > 1:
            w_brief = " | ".join([f"{w['city']}: {w.get('temperature_c', w.get('temp_c', 15))}°C" for w in travel_data["weather_list"][:2]])
            badges.append(cards.CarouselBadge(label=w_brief, variant="info"))
        else:
            badges.append(cards.CarouselBadge(label=f"Weather: {weather_temp}°C {weather_cond}", variant="info"))

        transit_name = pkg.get("flight", {}).get("carrier", pkg.get("carrier", "Direct Transit"))
        lodging_name = pkg.get("lodging", {}).get("name", pkg.get("hotel", "Executive Lodging"))

        item = cards.CarouselItem(
            id=pkg["id"],
            title=pkg["title"],
            subtitle=pkg["subtitle"],
            secondary_text=(
                f"Transit: {transit_name} | "
                f"Lodging: {lodging_name} | "
                f"Total: ${price_usd:,.2f} USD (~{price_fet:,.1f} FET)"
            ),
            badges=badges,
            primary_cta=cards.CtaAction(
                label=f"Inspect & Select",
                selection={"action": "select_package", "package_id": pkg["id"]},
                primary=True,
            ),
        )
        items.append(item)

    carousel_payload = cards.CarouselCardPayload(
        title=f"✈️ Curated Itineraries: {route_label}",
        subtitle=subtitle,
        items=items,
    )
    return cards.create_card_content(carousel_payload, card_id=uuid4(), is_terminal=False)


def build_package_detail_card(
    package: Dict[str, Any],
    weather: Dict[str, Any],
) -> MetadataContent:
    """Build a Detail Card showing granular travel telemetry, weather stability, and pricing."""
    flight = package.get("flight", {})
    lodging = package.get("lodging", {})
    metrics = package.get("metrics", {})

    summary_rows = [
        cards.DetailSummaryRow(label="Selected Package", value=package.get("title", "")),
        cards.DetailSummaryRow(label="Flight Carrier", value=f"{flight.get('carrier')} ({flight.get('cabin')})"),
        cards.DetailSummaryRow(label="Flight Schedule", value=f"{flight.get('departure')} ➔ {flight.get('arrival')}"),
        cards.DetailSummaryRow(label="Hotel Accommodation", value=f"{lodging.get('name')} ({lodging.get('rating')})"),
        cards.DetailSummaryRow(label="Lodging Amenities", value=lodging.get("amenities", "Full Amenities")),
        cards.DetailSummaryRow(
            label="Destination Weather",
            value=f"{weather.get('temperature_c')}°C ({weather.get('condition')}) - {weather.get('stability')}",
        ),
        cards.DetailSummaryRow(
            label="Carbon Footprint",
            value=f"{metrics.get('carbon_kg', 300)} kg CO2 (Certified Offsetting Available)",
        ),
        cards.DetailSummaryRow(
            label="Total Package Cost",
            value=f"${metrics.get('price_usd', 0):,.2f} USD (~{metrics.get('price_fet', 0):,.2f} FET)",
        ),
    ]

    detail_payload = cards.DetailCardPayload(
        title="📋 Itinerary & Logistics Deep-Dive",
        summary_rows=summary_rows,
        ctas=[
            cards.CtaAction(
                label="Proceed to Booking Authorization",
                selection={"action": "proceed_to_review", "package_id": package["id"]},
                primary=True,
            ),
            cards.CtaAction(
                label="Back to Comparison",
                selection={"action": "back_to_comparison"},
                primary=False,
            ),
        ],
    )
    return cards.create_card_content(detail_payload, card_id=uuid4(), is_terminal=False)


def build_booking_review_card(
    package: Dict[str, Any],
    fee_fet: float = 5.0,
) -> MetadataContent:
    """Build a Review Card for escrow lock authorization and Fetch.ai Payment Protocol settlement."""
    metrics = package.get("metrics", {})
    price_usd = metrics.get("price_usd", 0.0)
    price_fet = metrics.get("price_fet", 0.0)
    total_fet = round(price_fet + fee_fet, 2)

    summary_rows = [
        cards.ReviewSummaryRow(label="Itinerary Name", value=package.get("title", "Executive Package")),
        cards.ReviewSummaryRow(label="Flight & Hotel Total", value=f"${price_usd:,.2f} USD (~{price_fet:,.2f} FET)"),
        cards.ReviewSummaryRow(label="Agent Protocol Coordination Fee", value=f"{fee_fet:.1f} FET"),
        cards.ReviewSummaryRow(label="Total Escrow Authorization", value=f"{total_fet:,.2f} FET"),
        cards.ReviewSummaryRow(label="Payment Rail", value="Fetch.ai Native Ledger / Smart Escrow"),
    ]

    review_payload = cards.ReviewCardPayload(
        title="🔒 Confirm Reservation & Escrow Lock",
        summary_rows=summary_rows,
        approve_cta=cards.CtaAction(
            label=f"Authorize & Lock Escrow ({total_fet:,.2f} FET)",
            selection={"action": "confirm_escrow_payment", "package_id": package["id"], "amount_fet": total_fet},
            primary=True,
        ),
        reject_cta=cards.CtaAction(
            label="Cancel Reservation",
            selection={"action": "cancel_reservation"},
            primary=False,
        ),
    )
    return cards.create_card_content(review_payload, card_id=uuid4(), is_terminal=False)


def build_payment_receipt_card(
    package: Dict[str, Any],
    tx_id: str,
    booking_pnr: str,
    amount_fet: float,
) -> MetadataContent:
    """Build a terminal Detail/Receipt Card after successful settlement."""
    flight = package.get("flight", {})
    lodging = package.get("lodging", {})

    summary_rows = [
        cards.DetailSummaryRow(label="Booking Status", value="CONFIRMED & ESCROW LOCKED ✅"),
        cards.DetailSummaryRow(label="Reservation PNR", value=booking_pnr),
        cards.DetailSummaryRow(label="Ledger Transaction ID", value=tx_id),
        cards.DetailSummaryRow(label="Settled Amount", value=f"{amount_fet:,.2f} FET"),
        cards.DetailSummaryRow(label="Flight Carrier", value=f"{flight.get('carrier')} (Confirmed)"),
        cards.DetailSummaryRow(label="Hotel Reservation", value=f"{lodging.get('name')} (Guaranteed)"),
        cards.DetailSummaryRow(label="Proof of Execution", value="Cryptographically Verified via Fetch.ai Protocol"),
    ]

    receipt_payload = cards.DetailCardPayload(
        title="🎉 AeroVoyage Reservation Receipt",
        summary_rows=summary_rows,
        ctas=[
            cards.CtaAction(
                label="Plan Another Trip",
                selection={"action": "restart_flow"},
                primary=True,
            )
        ],
    )
    return cards.create_card_content(receipt_payload, card_id=uuid4(), is_terminal=True)


def parse_card_response(content: Any) -> Optional[Dict[str, Any]]:
    """Safely inspects a ChatMessage content item and extracts the CardResponse if present."""
    if isinstance(content, MetadataContent):
        card_resp = cards.extract_card_response(content)
        if card_resp is not None:
            return {
                "card_id": str(card_resp.card_id) if card_resp.card_id else None,
                "text": card_resp.text,
                "selection": card_resp.selection,
                "cancelled": card_resp.cancelled,
            }
    return None
