"""Internal message models for inter-agent communication within AeroVoyage."""

from typing import Optional
from uagents import Model


class QueryItineraryRequest(Model):
    """Sent by Concierge Agent to Logistics Agent."""
    session_id: str
    origin: str
    destination: str
    departure_date: str
    return_date: str
    max_budget: float


class QueryItineraryResponse(Model):
    """Returned by Logistics Agent to Concierge Agent."""
    session_id: str
    success: bool
    data_json: str
    error_msg: Optional[str] = None


class SettlementInitiateRequest(Model):
    """Sent by Concierge Agent to Settlement Agent to trigger Payment Protocol flow."""
    session_id: str
    package_id: str
    package_title: str
    amount_fet: float
    user_sender: str


class SettlementConfirmedResponse(Model):
    """Returned by Settlement Agent upon verified escrow commitment."""
    session_id: str
    booking_pnr: str
    tx_id: str
    amount_fet: float
    status: str
