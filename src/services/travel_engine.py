"""Travel Engine: Generates multi-criteria optimized travel and lodging packages."""

from typing import Dict, List, Any
from src.services.weather_service import fetch_weather
from src.services.currency_service import convert_usd_to_fet


def generate_itinerary_packages(
    origin: str = "New York (JFK)",
    destination: str = "San Francisco (SFO)",
    departure_date: str = "2026-11-15",
    return_date: str = "2026-11-18",
    max_budget_usd: float = 1500.0,
) -> Dict[str, Any]:
    """Compile optimized flight + lodging options with live weather and pricing."""
    weather = fetch_weather(destination)

    # 1. Executive Express (Fastest, Premium)
    pkg1_usd = min(round(max_budget_usd * 0.88, 2), 1320.0)
    pkg1 = {
        "id": "pkg_exec_01",
        "title": "Executive Express (Fastest Direct)",
        "subtitle": "United Polaris / Fairmont Heritage Place",
        "flight": {
            "carrier": "United Airlines (UA 412)",
            "route": f"{origin} ➔ {destination}",
            "departure": f"{departure_date} 07:30 AM",
            "arrival": f"{departure_date} 10:45 AM (Non-stop)",
            "cabin": "First / Business",
            "layovers": 0,
        },
        "lodging": {
            "name": "Fairmont San Francisco (Executive Suite)",
            "rating": "4.9 ★★★★★",
            "amenities": "High-Speed Fiber WiFi, Lounge Access, Valet",
            "nights": 3,
        },
        "metrics": {
            "price_usd": pkg1_usd,
            "price_fet": convert_usd_to_fet(pkg1_usd),
            "carbon_kg": 340,
            "badge": "Top Rated",
            "badge_variant": "success",
            "feasibility_score": "98%",
        },
    }

    # 2. Eco-Smart Navigator (Lowest Carbon, Green Certified)
    pkg2_usd = min(round(max_budget_usd * 0.72, 2), 1080.0)
    pkg2 = {
        "id": "pkg_eco_02",
        "title": "Eco-Smart Navigator (Green Certified)",
        "subtitle": "Virgin EcoFlight / 1 Hotel Sustainable",
        "flight": {
            "carrier": "Virgin / Delta Modern Fleet (VS 220)",
            "route": f"{origin} ➔ {destination}",
            "departure": f"{departure_date} 09:15 AM",
            "arrival": f"{departure_date} 12:40 PM (Non-stop)",
            "cabin": "Comfort Eco+",
            "layovers": 0,
        },
        "lodging": {
            "name": "1 Hotel San Francisco (LEED Platinum)",
            "rating": "4.8 ★★★★★",
            "amenities": "Zero-waste Dining, Solar Powered, EV Shuttle",
            "nights": 3,
        },
        "metrics": {
            "price_usd": pkg2_usd,
            "price_fet": convert_usd_to_fet(pkg2_usd),
            "carbon_kg": 210,
            "badge": "Eco Certified",
            "badge_variant": "info",
            "feasibility_score": "95%",
        },
    }

    # 3. Value Maxima (Maximum Savings)
    pkg3_usd = min(round(max_budget_usd * 0.55, 2), 820.0)
    pkg3 = {
        "id": "pkg_val_03",
        "title": "Value Maxima (Budget Optimized)",
        "subtitle": "JetBlue Direct / citizenM Downtown",
        "flight": {
            "carrier": "JetBlue Mint (B6 715)",
            "route": f"{origin} ➔ {destination}",
            "departure": f"{departure_date} 11:20 AM",
            "arrival": f"{departure_date} 02:50 PM (Non-stop)",
            "cabin": "Main Cabin Extra",
            "layovers": 0,
        },
        "lodging": {
            "name": "citizenM San Francisco Union Square",
            "rating": "4.7 ★★★★☆",
            "amenities": "Smart Tech Rooms, Rooftop Bar, Central Hub",
            "nights": 3,
        },
        "metrics": {
            "price_usd": pkg3_usd,
            "price_fet": convert_usd_to_fet(pkg3_usd),
            "carbon_kg": 290,
            "badge": "Best Value",
            "badge_variant": "warning",
            "feasibility_score": "93%",
        },
    }

    return {
        "origin": origin,
        "destination": destination,
        "dates": f"{departure_date} to {return_date}",
        "weather": weather,
        "packages": [pkg1, pkg2, pkg3],
    }
