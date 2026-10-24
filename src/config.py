"""Configuration and environment settings for AeroVoyage AI Multi-Agent System."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AgentConfig:
    name: str
    seed: str
    port: int
    mailbox: bool = False
    endpoint: str = None


# Concierge Agent (ASI:One facing)
CONCIERGE_CONFIG = AgentConfig(
    name=os.getenv("CONCIERGE_AGENT_NAME", "aerovoyage_concierge"),
    seed=os.getenv("CONCIERGE_AGENT_SEED", "aerovoyage_concierge_seed_phrase_hackathon_2026_01"),
    port=int(os.getenv("CONCIERGE_AGENT_PORT", "8000")),
    mailbox=os.getenv("CONCIERGE_MAILBOX", "false").lower() in ("true", "1", "yes"),
    endpoint=os.getenv("CONCIERGE_ENDPOINT", "http://127.0.0.1:8000/submit"),
)

# Logistics Agent (Worker)
LOGISTICS_CONFIG = AgentConfig(
    name=os.getenv("LOGISTICS_AGENT_NAME", "aerovoyage_logistics"),
    seed=os.getenv("LOGISTICS_AGENT_SEED", "aerovoyage_logistics_seed_phrase_hackathon_2026_02"),
    port=int(os.getenv("LOGISTICS_AGENT_PORT", "8001")),
    mailbox=os.getenv("LOGISTICS_MAILBOX", "false").lower() in ("true", "1", "yes"),
    endpoint=os.getenv("LOGISTICS_ENDPOINT", "http://127.0.0.1:8001/submit"),
)

# Settlement Agent (Payment Protocol)
SETTLEMENT_CONFIG = AgentConfig(
    name=os.getenv("SETTLEMENT_AGENT_NAME", "aerovoyage_settlement"),
    seed=os.getenv("SETTLEMENT_AGENT_SEED", "aerovoyage_settlement_seed_phrase_hackathon_2026_03"),
    port=int(os.getenv("SETTLEMENT_AGENT_PORT", "8002")),
    mailbox=os.getenv("SETTLEMENT_MAILBOX", "false").lower() in ("true", "1", "yes"),
    endpoint=os.getenv("SETTLEMENT_ENDPOINT", "http://127.0.0.1:8002/submit"),
)

# Deterministic addresses for inter-agent routing
CONCIERGE_ADDRESS = "agent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5"
LOGISTICS_ADDRESS = "agent1qtjcn0xkt4nna7xwg7cyu09eqpt22kwcys2umcmpeu0ctkktv0zrxdqkgck"
SETTLEMENT_ADDRESS = "agent1qfxpj3zrsfgl58deya9vrnc4hptccmz5v6rt3z8qgdcg8jzlxc4gjfzpu6l"

# Financial settings
AGENT_FEE_FET = float(os.getenv("AGENT_FEE_FET", "5.0"))
FET_ESTIMATED_USD_RATE = 1.35
