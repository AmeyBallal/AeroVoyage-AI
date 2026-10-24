"""Unit tests for Fetch.ai Payment Protocol and Internal Messaging."""

import unittest
from uagents_core.contrib.protocols.payment import (
    CommitPayment,
    CompletePayment,
    RejectPayment,
    RequestPayment,
    Funds,
    payment_protocol_spec,
)
from src.protocols.internal_protocols import (
    QueryItineraryRequest,
    QueryItineraryResponse,
    SettlementInitiateRequest,
    SettlementConfirmedResponse,
)
from src.protocols.payment_handlers import create_seller_payment_protocol, ESCROW_LEDGER


class TestProtocols(unittest.TestCase):

    def test_payment_models(self):
        funds = Funds(amount=25.0, currency="FET", payment_method="fetch_ledger")
        self.assertEqual(float(funds.amount), 25.0)
        self.assertEqual(funds.currency, "FET")

        commit = CommitPayment(
            funds=funds,
            recipient="agent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5",
            transaction_id="0xdeadbeef123",
            reference="AV-REF-001",
            description="AeroVoyage Escrow Authorization",
            metadata={"pkg_id": "pkg_exec_01"},
        )
        self.assertEqual(commit.transaction_id, "0xdeadbeef123")
        self.assertEqual(commit.reference, "AV-REF-001")

    def test_internal_protocols(self):
        query_req = QueryItineraryRequest(
            session_id="session_user_01",
            origin="JFK",
            destination="SFO",
            departure_date="2026-11-15",
            return_date="2026-11-18",
            max_budget=1500.0,
        )
        self.assertEqual(query_req.session_id, "session_user_01")
        self.assertEqual(query_req.max_budget, 1500.0)

        settle_req = SettlementInitiateRequest(
            session_id="session_user_01",
            package_id="pkg_exec_01",
            package_title="Executive Express",
            amount_fet=7585.16,
            user_sender="agent1user",
        )
        self.assertEqual(settle_req.amount_fet, 7585.16)

    def test_seller_protocol_creation(self):
        proto = create_seller_payment_protocol()
        self.assertEqual(proto.name, "AgentPaymentProtocol")
        self.assertEqual(proto._role, "seller")


if __name__ == "__main__":
    unittest.main()
