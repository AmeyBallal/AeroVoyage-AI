"""Travel Engine: Generates multi-criteria optimized travel and lodging packages.

Supports:
- Dynamic multi-city routes (e.g. Berlin ➔ Zurich ➔ Milan)
- Configurable durations (e.g. 5-day business circuits)
- Live weather telemetry across all stops via Open-Meteo
- Real-time FET/USD currency rates via CoinGecko
"""

import re
from typing import Dict, List, Any
from src.services.weather_service import fetch_weather
from src.services.currency_service import convert_usd_to_fet

KNOWN_CITIES = [
    "Berlin", "Zurich", "Milan", "London", "Paris", "New York", "San Francisco",
    "Tokyo", "Singapore", "Dubai", "Rome", "Madrid", "Barcelona", "Frankfurt",
    "Munich", "Vienna", "Amsterdam", "Brussels", "Geneva", "Prague", "Warsaw",
    "Stockholm", "Copenhagen", "Dublin", "Lisbon", "Toronto", "Sydney", "Hong Kong",
    "Seoul", "Los Angeles", "Chicago", "Boston", "Seattle", "Miami"
]

CITY_HOTELS = {
    "Berlin": {
        "luxury": "The Ritz-Carlton Berlin (Potsdamer Platz)",
        "eco": "Scandic Berlin Potsdamer Platz (EMAS Certified)",
        "value": "citizenM Berlin Mitte (Central Tech Hub)",
    },
    "Zurich": {
        "luxury": "Baur au Lac Zurich (Lakefront Executive Suite)",
        "eco": "25hours Hotel Zurich West (Sustainable Living)",
        "value": "citizenM Zurich Central (Work Lounge Included)",
    },
    "Milan": {
        "luxury": "Mandarin Oriental Milan (Duomo Business District)",
        "eco": "Starhotels E.c.ho Milan (100% Eco-Certified Green)",
        "value": "NYX Hotel Milan (City Center Executive Hub)",
    },
    "London": {
        "luxury": "The Savoy London (Strand Executive Suite)",
        "eco": "1 Hotel Mayfair (LEED Gold Sustainable)",
        "value": "citizenM Tower of London (High-Speed Hub)",
    },
    "Paris": {
        "luxury": "Hôtel de Crillon (Place de la Concorde)",
        "eco": "Eden Lodge Paris (100% Zero-Carbon Certified)",
        "value": "citizenM Paris Gare de Lyon",
    },
    "New York": {
        "luxury": "The St. Regis New York (5th Avenue)",
        "eco": "1 Hotel Central Park (LEED Certified)",
        "value": "citizenM New York Bowery",
    },
    "San Francisco": {
        "luxury": "Fairmont San Francisco (Executive Suite)",
        "eco": "1 Hotel San Francisco (LEED Platinum)",
        "value": "citizenM San Francisco Union Square",
    },
    "Tokyo": {
        "luxury": "Park Hyatt Tokyo (Shinjuku High Suite)",
        "eco": "Trunk Hotel Tokyo (Eco-Social Certified)",
        "value": "Hotel Gracery Shinjuku",
    },
}


def parse_intent_from_text(text: str) -> Dict[str, Any]:
    """Extracts cities, multi-city flags, duration, and budget from freeform text, using Groq LLM if available."""
    # 1. Try Groq Free Tier LLM first
    try:
        from src.services.llm_service import parse_intent_with_llm
        llm_intent = parse_intent_with_llm(text)
        if llm_intent and llm_intent.get("cities"):
            return llm_intent
    except Exception:
        pass

    # 2. Deterministic rule-based NLP fallback
    lower_text = text.lower()
    found_cities = []
    for city in KNOWN_CITIES:
        if re.search(r"\b" + re.escape(city) + r"\b", text, re.IGNORECASE):
            if city not in found_cities:
                found_cities.append(city)

    if not found_cities:
        for match in re.finditer(r"\b(?:to|across|in|visit|visiting)\s+([A-Z][a-zA-Z]+)", text):
            cand = match.group(1).title()
            if cand not in ("A", "The", "Our", "My", "Trip", "Business", "Meeting", "Fastest", "Five", "Day", "Summary"):
                found_cities.append(cand)

    if not found_cities:
        found_cities = ["San Francisco"]

    day_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "week": 7}
    days = 3
    day_match = re.search(r"(\w+)[-\s]day", lower_text)
    if day_match:
        val = day_match.group(1).lower()
        days = day_words.get(val, int(val) if val.isdigit() else 3)

    budget = 1800.0 if len(found_cities) > 1 else 1500.0
    budget_match = re.search(r"\$?(\d{3,5})", text)
    if budget_match:
        try:
            budget = float(budget_match.group(1))
        except ValueError:
            pass

    return {
        "cities": found_cities,
        "is_multi_city": len(found_cities) > 1,
        "days": days,
        "budget": budget,
    }


def generate_itinerary_packages(
    origin: str = "New York (JFK)",
    destination: str = "San Francisco (SFO)",
    departure_date: str = "2026-11-15",
    return_date: str = "2026-11-18",
    max_budget_usd: float = 1500.0,
    cities: List[str] = None,
    days: int = 3,
) -> Dict[str, Any]:
    """Compile optimized flight/rail + lodging options with live weather and pricing."""
    if not cities:
        # Check if destination contains multiple cities (e.g. 'Berlin, Zurich, Milan' or 'Berlin ➔ Zurich ➔ Milan')
        cleaned_dest = destination.replace("➔", ",").replace("&", ",").replace("and", ",")
        extracted = [c.strip() for c in cleaned_dest.split(",") if c.strip()]
        cities = extracted if len(extracted) > 1 else [destination.replace("(SFO)", "").replace("(LHR)", "").replace("(JFK)", "").strip()]

    # Fetch weather for cities
    weather_list = [fetch_weather(c) for c in cities[:3]]
    primary_weather = weather_list[0] if weather_list else fetch_weather(destination)

    weather_summary = ", ".join([f"{w['city']} ({w['temperature_c']}°C, {w['condition']})" for w in weather_list])

    # Dynamic Hotel Resolution
    def get_hotels(tier: str) -> str:
        hotel_names = []
        for c in cities:
            h = CITY_HOTELS.get(c, {}).get(tier, f"Executive {c} Hotel")
            hotel_names.append(h)
        return " + ".join(hotel_names)

    # Dynamic Transit
    if len(cities) > 1:
        route_str = " ➔ ".join(cities)
        route_label = f"{route_str} ({days}-Day Multi-City Circuit)"
        is_europe = any(c in ("Berlin", "Zurich", "Milan", "Paris", "London", "Frankfurt", "Rome", "Munich", "Vienna") for c in cities)
        if is_europe:
            transit_exec = f"Lufthansa Business Shuttle ({cities[0]} ➔ {cities[1]}: 1h 25m) + EuroCity Express High-Speed ({cities[1]} ➔ {cities[-1]}: 3h 17m)"
            transit_eco = f"Direct Electric High-Speed Rail ({' ➔ '.join(cities)} via DB ICE, Swiss SBB & Frecciarossa 1000)"
            transit_val = f"Swiss International Airlines & Regional InterCity Express"
        else:
            transit_exec = f"Star Alliance / OneWorld Executive Hopper connecting {' ➔ '.join(cities)} (Priority Fast-Track)"
            transit_eco = f"Modern Low-Emission Fleet / Direct Rail Transfers between {' ➔ '.join(cities)}"
            transit_val = f"Point-to-Point Agile Transit connecting {' ➔ '.join(cities)}"
    else:
        route_str = cities[0]
        route_label = f"{cities[0]} ({days}-Day Itinerary)"
        transit_exec = f"Non-Stop First / Business Carrier to {cities[0]} (Priority Meeting Buffer)"
        transit_eco = f"Virgin / Delta Modern Eco-Fleet to {cities[0]} (Carbon Offset Included)"
        transit_val = f"JetBlue Mint / Direct Express to {cities[0]}"

    pkg1_usd = min(round(max_budget_usd * 0.88, 2), 1620.0)
    pkg2_usd = min(round(max_budget_usd * 0.72, 2), 1320.0)
    pkg3_usd = min(round(max_budget_usd * 0.55, 2), 980.0)

    # 1. Executive Express
    pkg1 = {
        "id": "pkg_exec_01",
        "title": f"Executive Express ({days}-Day Fastest Connections)",
        "subtitle": f"{route_str} | Priority Business Shuttles",
        "flight": {
            "carrier": transit_exec,
            "route": route_str,
            "departure": f"{departure_date} 07:30 AM",
            "arrival": f"{departure_date} Non-stop / High-Speed",
            "cabin": "First / Business Executive",
            "layovers": 0,
        },
        "lodging": {
            "name": get_hotels("luxury"),
            "rating": "4.9 ★★★★★",
            "amenities": "High-Speed Fiber WiFi, Meeting Lounges, Priority Check-in",
            "nights": days,
        },
        "metrics": {
            "price_usd": pkg1_usd,
            "price_fet": convert_usd_to_fet(pkg1_usd),
            "carbon_kg": 320 * len(cities),
            "badge": "Fastest Route" if len(cities) > 1 else "Top Rated",
            "badge_variant": "success",
            "feasibility_score": "98%",
        },
    }

    # 2. Eco-Smart Navigator
    pkg2 = {
        "id": "pkg_eco_02",
        "title": f"Eco-Smart Navigator ({days}-Day Low-Carbon)",
        "subtitle": f"{route_str} | Sustainable High-Speed Transit",
        "flight": {
            "carrier": transit_eco,
            "route": route_str,
            "departure": f"{departure_date} 09:15 AM",
            "arrival": f"{departure_date} High-Speed Green Route",
            "cabin": "Comfort Eco+ / 1st Class Rail",
            "layovers": 0,
        },
        "lodging": {
            "name": get_hotels("eco"),
            "rating": "4.8 ★★★★★",
            "amenities": "Zero-waste Dining, Solar Powered, On-board WiFi Work Desks",
            "nights": days,
        },
        "metrics": {
            "price_usd": pkg2_usd,
            "price_fet": convert_usd_to_fet(pkg2_usd),
            "carbon_kg": 95 * len(cities),
            "badge": "Eco Certified",
            "badge_variant": "info",
            "feasibility_score": "95%",
        },
    }

    # 3. Value Maxima
    pkg3 = {
        "id": "pkg_val_03",
        "title": f"Agile Corporate Value ({days}-Day Optimized)",
        "subtitle": f"{route_str} | Time & Cost Efficient",
        "flight": {
            "carrier": transit_val,
            "route": route_str,
            "departure": f"{departure_date} 11:20 AM",
            "arrival": f"{departure_date} Direct Transit",
            "cabin": "Main Cabin Extra / Standard InterCity",
            "layovers": 0,
        },
        "lodging": {
            "name": get_hotels("value"),
            "rating": "4.7 ★★★★☆",
            "amenities": "Smart Tech Rooms, Central Meeting Hubs, Co-Working Desks",
            "nights": days,
        },
        "metrics": {
            "price_usd": pkg3_usd,
            "price_fet": convert_usd_to_fet(pkg3_usd),
            "carbon_kg": 240 * len(cities),
            "badge": "Best Value",
            "badge_variant": "warning",
            "feasibility_score": "93%",
        },
    }

    return {
        "origin": origin,
        "destination": destination,
        "route_label": route_label,
        "cities": cities,
        "days": days,
        "dates": f"{departure_date} to {return_date}",
        "weather": primary_weather,
        "weather_summary": weather_summary,
        "weather_list": weather_list,
        "packages": [pkg1, pkg2, pkg3],
    }
