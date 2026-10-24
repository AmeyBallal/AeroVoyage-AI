"""Unit tests for ASI:One Interactive Card Builders and Parsers."""

import unittest
from uuid import uuid4
from uagents_core.contrib.protocols.chat import (
    MetadataContent,
    cards,
)

from src.services.travel_engine import generate_itinerary_packages
from src.ui.cards import (
    build_preference_form_card,
    build_itinerary_carousel_card,
    build_package_detail_card,
    build_booking_review_card,
    build_payment_receipt_card,
    parse_card_response,
)


class TestCards(unittest.TestCase):

    def setUp(self):
        self.travel_data = generate_itinerary_packages()
        self.pkg = self.travel_data["packages"][0]
        self.weather = self.travel_data["weather"]

    def test_build_preference_form_card(self):
        meta = build_preference_form_card("JFK", "SFO")
        self.assertIsInstance(meta, MetadataContent)
        self.assertEqual(meta.type, "metadata")
        card = cards.extract_card(meta)
        self.assertIsNotNone(card)
        self.assertIsInstance(card.payload, cards.FormCardPayload)
        self.assertEqual(len(card.payload.fields), 5)

    def test_build_itinerary_carousel_card(self):
        meta = build_itinerary_carousel_card(self.travel_data)
        self.assertIsInstance(meta, MetadataContent)
        card = cards.extract_card(meta)
        self.assertIsNotNone(card)
        self.assertIsInstance(card.payload, cards.CarouselCardPayload)
        self.assertEqual(len(card.payload.items), 3)

    def test_build_package_detail_card(self):
        meta = build_package_detail_card(self.pkg, self.weather)
        self.assertIsInstance(meta, MetadataContent)
        card = cards.extract_card(meta)
        self.assertIsNotNone(card)
        self.assertIsInstance(card.payload, cards.DetailCardPayload)
        self.assertGreaterEqual(len(card.payload.summary_rows), 6)

    def test_build_booking_review_card(self):
        meta = build_booking_review_card(self.pkg, fee_fet=5.0)
        self.assertIsInstance(meta, MetadataContent)
        card = cards.extract_card(meta)
        self.assertIsNotNone(card)
        self.assertIsInstance(card.payload, cards.ReviewCardPayload)
        self.assertIsNotNone(card.payload.approve_cta)
        self.assertIsNotNone(card.payload.reject_cta)

    def test_build_payment_receipt_card(self):
        meta = build_payment_receipt_card(self.pkg, "0x123abc", "AV-9988", 7500.0)
        self.assertIsInstance(meta, MetadataContent)
        card = cards.extract_card(meta)
        self.assertIsNotNone(card)
        self.assertTrue(card.is_terminal)

    def test_card_response_parser(self):
        test_card_id = uuid4()
        response_content = cards.create_card_response_content(
            card_id=test_card_id,
            selection={"action": "select_package", "package_id": "pkg_exec_01"},
        )
        parsed = parse_card_response(response_content)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["card_id"], str(test_card_id))
        self.assertEqual(parsed["selection"]["action"], "select_package")
        self.assertEqual(parsed["selection"]["package_id"], "pkg_exec_01")


if __name__ == "__main__":
    unittest.main()
