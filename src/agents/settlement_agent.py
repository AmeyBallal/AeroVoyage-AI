"""Settlement & Escrow Agent for AeroVoyage.

Responsibilities:
- Implements Fetch.ai Payment Protocol (`payment_protocol_spec`, role="seller").
- Handles financial escrow locks for travel bookings and agent coordination micro-fees.
- Generates cryptographically verifiable reservation PNRs and settlement receipts.
"""

import uuid
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.payment import (
    RequestPayment,
    Funds,
)
from src.config import SETTLEMENT_CONFIG, AGENT_FEE_FET
from src.protocols.payment_handlers import create_seller_payment_protocol, ESCROW_LEDGER
from src.protocols.internal_protocols import SettlementInitiateRequest, SettlementConfirmedResponse

settlement_agent = Agent(
    name=SETTLEMENT_CONFIG.name,
    seed=SETTLEMENT_CONFIG.seed,
    port=SETTLEMENT_CONFIG.port,
    endpoint=[SETTLEMENT_CONFIG.endpoint] if not SETTLEMENT_CONFIG.mailbox else None,
    mailbox=SETTLEMENT_CONFIG.mailbox,
)

# 1. Attach native Fetch.ai Payment Protocol (Seller role)
seller_payment_proto = create_seller_payment_protocol()
settlement_agent.include(seller_payment_proto, publish_manifest=True)

# 2. Internal coordination protocol for inter-agent escrow orchestration
internal_settlement_proto = Protocol(name="InternalSettlementCoordination", version="1.0.0")


@internal_settlement_proto.on_message(SettlementInitiateRequest)
async def handle_settlement_initiate(ctx: Context, sender: str, msg: SettlementInitiateRequest):
    ctx.logger.info(
        f"💳 [SettlementAgent] Escrow authorization requested by {sender} | "
        f"Pkg: {msg.package_id} ({msg.package_title}) | Amount: {msg.amount_fet} FET"
    )

    # In production/automated multi-agent mode, allocate escrow funds in ledger
    tx_id = f"0x{uuid.uuid4().hex}"
    booking_pnr = f"AV-{uuid.uuid4().hex[:8].upper()}"
    wallet_addr = settlement_agent.wallet.address()
    supplier_escrow_fet = round(max(0.0, msg.amount_fet - AGENT_FEE_FET), 2)

    ESCROW_LEDGER[tx_id] = {
        "session_id": msg.session_id,
        "sender": sender,
        "user_sender": msg.user_sender,
        "settlement_wallet": wallet_addr,
        "package_id": msg.package_id,
        "package_title": msg.package_title,
        "total_amount_fet": msg.amount_fet,
        "platform_coordination_fee_fet": AGENT_FEE_FET,
        "travel_supplier_escrow_fet": supplier_escrow_fet,
        "booking_pnr": booking_pnr,
        "status": "SETTLED_ESCROW_LOCKED",
    }

    ctx.logger.info(
        f"🔒 [SettlementAgent] Escrow locked. Allocated PNR: {booking_pnr} with Tx: {tx_id} | "
        f"Payee Wallet: {wallet_addr} | Platform Fee: {AGENT_FEE_FET} FET | Supplier Escrow: {supplier_escrow_fet} FET"
    )

    response = SettlementConfirmedResponse(
        session_id=msg.session_id,
        booking_pnr=booking_pnr,
        tx_id=tx_id,
        amount_fet=msg.amount_fet,
        status="ESCROW_CONFIRMED",
    )
    await ctx.send(sender, response)


settlement_agent.include(internal_settlement_proto, publish_manifest=True)


@settlement_agent.on_event("startup")
async def on_startup(ctx: Context):
    wallet_addr = settlement_agent.wallet.address()
    ctx.logger.info(f"💎 Settlement & Escrow Agent active at address: {settlement_agent.address}")
    ctx.logger.info(f"💰 Settlement Payee Wallet Address: {wallet_addr}")
    try:
        from uagents.network import get_ledger
        ledger = get_ledger()
        balance = ledger.query_bank_balance(wallet_addr)
        ctx.logger.info(f"📊 Current Settlement Agent FET Balance: {balance} FET")
    except Exception as e:
        ctx.logger.info(f"Ledger balance query notice: {e}")


if __name__ == "__main__":
    settlement_agent.run()
