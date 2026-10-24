"""End-to-End Simulation Test: Simulates an entire ASI:One conversational interaction.

Validates the complete intent-to-action multi-agent pipeline:
1. User initiates chat (StartSession) -> Concierge responds with Form Card.
2. User submits Form Card preferences -> Concierge sends QueryItineraryRequest to Logistics Agent.
3. Logistics Agent computes real-time packages -> replies with QueryItineraryResponse.
4. Concierge receives response -> delivers Carousel Card to user with live weather & options.
5. User selects an option -> Concierge delivers Detail Card.
6. User clicks proceed -> Concierge delivers Review Card with Escrow Authorization.
7. User approves escrow lock -> Concierge dispatches SettlementInitiateRequest to Settlement Agent.
8. Settlement Agent locks escrow -> returns SettlementConfirmedResponse.
9. Concierge delivers terminal Receipt Card to user with confirmed PNR and Tx ID.
"""

import json
import unittest
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    StartSessionContent,
    TextContent,
    cards,
)

from src.config import LOGISTICS_ADDRESS, SETTLEMENT_ADDRESS
from src.protocols.internal_protocols import (
    QueryItineraryRequest,
    QueryItineraryResponse,
    SettlementInitiateRequest,
    SettlementConfirmedResponse,
)
from src.services.travel_engine import generate_itinerary_packages
from src.agents.concierge_agent import (
    concierge_agent,
    handle_chat_message,
    handle_logistics_response,
    handle_settlement_confirmed,
)


class MockContext:
    def __init__(self):
        self.sent_messages = []
        self.agent = concierge_agent

        class MockLogger:
            def info(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass
            def debug(self, msg): pass

        self.logger = MockLogger()

    async def send(self, destination: str, message: Any):
        self.sent_messages.append((destination, message))


class TestEndToEndSimulation(unittest.IsolatedAsyncioTestCase):

    async def test_complete_asi_one_workflow(self):
        ctx = MockContext()
        user_address = "agent1_mock_asi_one_user_sim_001"

        # ---------------------------------------------------------
        # Step 1: User opens conversation in ASI:One (StartSession)
        # ---------------------------------------------------------
        start_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[StartSessionContent(type="start-session")],
        )
        await handle_chat_message(ctx, user_address, start_msg)

        # Verify welcome message and FormCard
        self.assertGreaterEqual(len(ctx.sent_messages), 2)
        _, welcome_chat = ctx.sent_messages[-1]
        self.assertIsInstance(welcome_chat, ChatMessage)
        self.assertIn("Welcome to AeroVoyage AI", welcome_chat.content[0].text)

        form_meta = welcome_chat.content[1]
        form_card = cards.extract_card(form_meta)
        self.assertIsInstance(form_card.payload, cards.FormCardPayload)

        # ---------------------------------------------------------
        # Step 2: User submits travel preferences via Form Card
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        form_submit_meta = cards.create_card_response_content(
            card_id=uuid4(),
            selection={
                "action": "search_itineraries",
                "origin": "New York (JFK)",
                "destination": "San Francisco (SFO)",
                "departure_date": "2026-11-20",
                "return_date": "2026-11-24",
                "max_budget": "1600",
            },
        )
        submit_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[form_submit_meta],
        )
        await handle_chat_message(ctx, user_address, submit_msg)

        # Multi-agent dispatch: Concierge dispatches query to Logistics Agent
        dest, query_req = ctx.sent_messages[-1]
        self.assertEqual(dest, LOGISTICS_ADDRESS)
        self.assertIsInstance(query_req, QueryItineraryRequest)
        self.assertEqual(query_req.destination, "San Francisco (SFO)")

        # ---------------------------------------------------------
        # Step 3: Logistics Agent responds with real-time package data
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        itinerary_data = generate_itinerary_packages(
            origin=query_req.origin,
            destination=query_req.destination,
            departure_date=query_req.departure_date,
            return_date=query_req.return_date,
            max_budget_usd=query_req.max_budget,
        )
        logistics_resp = QueryItineraryResponse(
            session_id=user_address,
            success=True,
            data_json=json.dumps(itinerary_data),
        )
        await handle_logistics_response(ctx, LOGISTICS_ADDRESS, logistics_resp)

        # Concierge presents Carousel Card to user
        dest, carousel_chat = ctx.sent_messages[-1]
        self.assertEqual(dest, user_address)
        self.assertIsInstance(carousel_chat, ChatMessage)
        carousel_meta = carousel_chat.content[1]
        carousel_card = cards.extract_card(carousel_meta)
        self.assertIsInstance(carousel_card.payload, cards.CarouselCardPayload)
        self.assertEqual(len(carousel_card.payload.items), 3)

        selected_pkg_id = carousel_card.payload.items[0].id

        # ---------------------------------------------------------
        # Step 4: User clicks "Inspect & Select" on Option 1
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        select_meta = cards.create_card_response_content(
            card_id=uuid4(),
            selection={
                "action": "select_package",
                "package_id": selected_pkg_id,
            },
        )
        select_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[select_meta],
        )
        await handle_chat_message(ctx, user_address, select_msg)

        dest, detail_chat = ctx.sent_messages[-1]
        self.assertEqual(dest, user_address)
        detail_meta = detail_chat.content[1]
        detail_card = cards.extract_card(detail_meta)
        self.assertIsInstance(detail_card.payload, cards.DetailCardPayload)

        # ---------------------------------------------------------
        # Step 5: User clicks "Proceed to Booking Authorization"
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        review_request_meta = cards.create_card_response_content(
            card_id=uuid4(),
            selection={
                "action": "proceed_to_review",
                "package_id": selected_pkg_id,
            },
        )
        review_req_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[review_request_meta],
        )
        await handle_chat_message(ctx, user_address, review_req_msg)

        dest, review_chat = ctx.sent_messages[-1]
        self.assertEqual(dest, user_address)
        review_meta = review_chat.content[1]
        review_card = cards.extract_card(review_meta)
        self.assertIsInstance(review_card.payload, cards.ReviewCardPayload)

        # ---------------------------------------------------------
        # Step 6: User clicks "Authorize & Lock Escrow" (Payment Protocol)
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        authorize_meta = cards.create_card_response_content(
            card_id=uuid4(),
            selection={
                "action": "confirm_escrow_payment",
                "package_id": selected_pkg_id,
                "amount_fet": 7590.16,
            },
        )
        authorize_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[authorize_meta],
        )
        await handle_chat_message(ctx, user_address, authorize_msg)

        # Concierge dispatches payment settlement request to Settlement Agent
        dest, settle_req = ctx.sent_messages[-1]
        self.assertEqual(dest, SETTLEMENT_ADDRESS)
        self.assertIsInstance(settle_req, SettlementInitiateRequest)

        # ---------------------------------------------------------
        # Step 7: Settlement Agent locks escrow and confirms
        # ---------------------------------------------------------
        ctx.sent_messages.clear()
        settle_conf = SettlementConfirmedResponse(
            session_id=user_address,
            booking_pnr="AV-CONFIRM-9901",
            tx_id="0xdeadbeef778899",
            amount_fet=7590.16,
            status="ESCROW_CONFIRMED",
        )
        await handle_settlement_confirmed(ctx, SETTLEMENT_ADDRESS, settle_conf)

        # Concierge delivers final confirmation and Receipt Card to user
        dest, receipt_chat = ctx.sent_messages[-1]
        self.assertEqual(dest, user_address)
        self.assertIsInstance(receipt_chat, ChatMessage)
        receipt_meta = receipt_chat.content[1]
        receipt_card = cards.extract_card(receipt_meta)
        self.assertIsInstance(receipt_card.payload, cards.DetailCardPayload)
        self.assertTrue(receipt_card.is_terminal)
        self.assertIn("AV-CONFIRM-9901", receipt_chat.content[0].text)

    async def test_asi_one_json_text_card_action(self):
        """Tests that when ASI:One sends a card action as JSON text inside TextContent,
        the agent parses it as a card selection instead of treating it as an NLP query.
        """
        ctx = MockContext()
        user_address = "agent1_mock_asi_one_json_text_user"

        # 1. First user asks for San Francisco trip
        search_msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text="Plan a 3-day executive trip to San Francisco under $1500")],
        )
        await handle_chat_message(ctx, user_address, search_msg)

        # 2. Simulate Logistics response with San Francisco packages
        itinerary_data = generate_itinerary_packages(
            origin="New York",
            destination="San Francisco",
            departure_date="2026-11-20",
            return_date="2026-11-23",
            max_budget_usd=1500.0,
        )
        logistics_resp = QueryItineraryResponse(
            session_id=user_address,
            success=True,
            data_json=json.dumps(itinerary_data),
        )
        await handle_logistics_response(ctx, LOGISTICS_ADDRESS, logistics_resp)

        # Verify carousel was presented
        dest, carousel_chat = ctx.sent_messages[-1]
        self.assertIn("San Francisco", carousel_chat.content[0].text)

        # 3. User clicks card action in ASI:One, which sends JSON text:
        ctx.sent_messages.clear()
        json_card_click = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text='{"action":"select_package","pkg_id":"pkg_val_03","approved":true}')],
        )
        await handle_chat_message(ctx, user_address, json_card_click)

        # Should present DetailCard for San Francisco pkg_val_03, NOT Berlin-Zurich-Milan!
        self.assertGreaterEqual(len(ctx.sent_messages), 2)
        dest, detail_chat = ctx.sent_messages[-1]
        self.assertEqual(dest, user_address)
        self.assertIn("Detailed Breakdown", detail_chat.content[0].text)
        detail_meta = detail_chat.content[1]
        detail_card = cards.extract_card(detail_meta)
        self.assertIsInstance(detail_card.payload, cards.DetailCardPayload)
        # Check summary rows contain San Francisco
        found_sf = any("San Francisco" in r.value for r in detail_card.payload.summary_rows)
        self.assertTrue(found_sf)


if __name__ == "__main__":
    unittest.main()
