"""Unit tests for AeroVoyage External Services (Weather, Currency, Travel Engine)."""

import unittest
from src.services.weather_service import fetch_weather, get_city_coords
from src.services.currency_service import get_fet_price_usd, convert_usd_to_fet, convert_fet_to_usd
from src.services.travel_engine import generate_itinerary_packages


class TestServices(unittest.TestCase):

    def test_city_coords(self):
        coords = get_city_coords("London")
        self.assertAlmostEqual(coords["lat"], 51.5074, places=2)
        self.assertAlmostEqual(coords["lon"], -0.1278, places=2)

    def test_weather_service_structure(self):
        weather = fetch_weather("San Francisco")
        self.assertIn("city", weather)
        self.assertIn("temperature_c", weather)
        self.assertIn("condition", weather)
        self.assertIn("stability", weather)
        self.assertIn("source", weather)
        self.assertIsInstance(weather["temperature_c"], (int, float))

    def test_currency_conversions(self):
        fet_rate = get_fet_price_usd()
        self.assertGreater(fet_rate, 0.0)

        usd_val = 135.0
        fet_val = convert_usd_to_fet(usd_val)
        self.assertGreater(fet_val, 0.0)

        converted_back = convert_fet_to_usd(fet_val)
        self.assertAlmostEqual(usd_val, converted_back, delta=1.0)

    def test_travel_engine_packages(self):
        itinerary = generate_itinerary_packages(
            origin="New York (JFK)",
            destination="London (LHR)",
            max_budget_usd=2000.0,
        )
        self.assertEqual(itinerary["origin"], "New York (JFK)")
        self.assertEqual(itinerary["destination"], "London (LHR)")
        self.assertEqual(len(itinerary["packages"]), 3)

        for pkg in itinerary["packages"]:
            self.assertIn("id", pkg)
            self.assertIn("title", pkg)
            self.assertIn("flight", pkg)
            self.assertIn("lodging", pkg)
            self.assertIn("metrics", pkg)
            self.assertLessEqual(pkg["metrics"]["price_usd"], 2000.0)

    def test_multi_city_intent_and_routing(self):
        from src.services.travel_engine import parse_intent_from_text
        prompt = "Plan a five-day multi-city business trip across Berlin, Zurich, and Milan with the fastest connections between meetings, and show me a summary card of the full itinerary."
        intent = parse_intent_from_text(prompt)
        self.assertEqual(intent["cities"], ["Berlin", "Zurich", "Milan"])
        self.assertEqual(intent["days"], 5)
        self.assertTrue(intent["is_multi_city"])

        itinerary = generate_itinerary_packages(
            cities=intent["cities"],
            days=intent["days"],
            max_budget_usd=intent["budget"],
        )
        self.assertEqual(len(itinerary["packages"]), 3)
        self.assertIn("Berlin ➔ Zurich ➔ Milan", itinerary["route_label"])
        self.assertIn("Fastest", itinerary["packages"][0]["title"])
        self.assertIn("Lufthansa", itinerary["packages"][0]["flight"]["carrier"])


if __name__ == "__main__":
    unittest.main()
