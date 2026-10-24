"""Fetch.ai Payment Protocol Handlers for AeroVoyage Settlement & Escrow."""

import uuid
from typing import Dict, Any
from uagents import Protocol, Context
from uagents_core.contrib.protocols.payment import (
    CommitPayment,
    CompletePayment,
    RejectPayment,
    RequestPayment,
    Funds,
    payment_protocol_spec,
)

# Registry of active transactions and escrow states
ESCROW_LEDGER: Dict[str, Dict[str, Any]] = {}


def create_seller_payment_protocol() -> Protocol:
    """Creates the seller-side Payment Protocol instance adhering to Fetch.ai specs."""
    proto = Protocol(spec=payment_protocol_spec, role="seller")

    @proto.on_message(CommitPayment)
    async def handle_commit_payment(ctx: Context, sender: str, msg: CommitPayment):
        ctx.logger.info(
            f"💰 [PaymentProtocol] CommitPayment received from {sender} | "
            f"Amount: {msg.funds.amount} {msg.funds.currency} | "
            f"Reference: {msg.reference} | TxID: {msg.transaction_id}"
        )

        # Validate funds
        if msg.funds.amount <= 0 or msg.funds.currency.upper() != "FET":
            ctx.logger.warning(f"❌ [PaymentProtocol] Rejected invalid payment from {sender}")
            await ctx.send(
                sender,
                RejectPayment(
                    funds=msg.funds,
                    recipient=ctx.agent.address,
                    reference=msg.reference,
                    reason="Invalid currency or negative amount. Fetch.ai (FET) required.",
                ),
            )
            return

        # Record escrow state
        booking_pnr = f"AV-{uuid.uuid4().hex[:8].upper()}"
        ESCROW_LEDGER[msg.transaction_id] = {
            "sender": sender,
            "amount": msg.funds.amount,
            "currency": msg.funds.currency,
            "reference": msg.reference,
            "booking_pnr": booking_pnr,
            "status": "SETTLED_ESCROW_LOCKED",
        }

        ctx.logger.info(
            f"✅ [PaymentProtocol] Escrow locked. Issued PNR {booking_pnr} for Tx {msg.transaction_id}"
        )

        # Send completion receipt back to the buyer
        await ctx.send(sender, CompletePayment(transaction_id=msg.transaction_id))

    @proto.on_message(RejectPayment)
    async def handle_reject_payment(ctx: Context, sender: str, msg: RejectPayment):
        ctx.logger.warning(
            f"⚠️ [PaymentProtocol] Payment rejected by {sender}: Reference {msg.reference} - Reason: {msg.reason}"
        )

    return proto
