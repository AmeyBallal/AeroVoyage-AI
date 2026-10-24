"""Unified Entrypoint for AeroVoyage Multi-Agent System.

Usage:
  python run.py                   # Runs all 3 agents simultaneously via uAgents Bureau
  python run.py --agent concierge # Runs only the ASI:One-facing Concierge Agent
  python run.py --agent logistics # Runs only the Logistics & Live Intelligence Agent
  python run.py --agent settlement# Runs only the Settlement & Escrow Agent
"""

import sys
import argparse

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from uagents import Bureau

from src.agents.concierge_agent import concierge_agent
from src.agents.logistics_agent import logistics_agent
from src.agents.settlement_agent import settlement_agent
from src.config import (
    CONCIERGE_ADDRESS,
    LOGISTICS_ADDRESS,
    SETTLEMENT_ADDRESS,
)


def main():
    parser = argparse.ArgumentParser(description="AeroVoyage Multi-Agent Runner")
    parser.add_argument(
        "--agent",
        choices=["all", "concierge", "logistics", "settlement"],
        default="all",
        help="Specify which agent to start (default: all via Bureau)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print(">>> AEROVOYAGE AI: MULTI-AGENT LOGISTICS & TRAVEL ORCHESTRATOR")
    print("=" * 70)
    print(f"Concierge Agent Address : {CONCIERGE_ADDRESS}")
    print(f"Logistics Agent Address : {LOGISTICS_ADDRESS}")
    print(f"Settlement Agent Address: {SETTLEMENT_ADDRESS}")
    print("=" * 70 + "\n")

    if args.agent == "concierge":
        print("Starting Concierge Agent (ASI:One & Agentverse)...")
        concierge_agent.run()
    elif args.agent == "logistics":
        print("Starting Logistics & Live Intelligence Agent...")
        logistics_agent.run()
    elif args.agent == "settlement":
        print("Starting Settlement & Escrow Agent (Payment Protocol)...")
        settlement_agent.run()
    else:
        print("Launching all 3 agents inside unified uAgents Bureau...")
        bureau = Bureau(port=8000)
        bureau.add(concierge_agent)
        bureau.add(logistics_agent)
        bureau.add(settlement_agent)
        bureau.run()


if __name__ == "__main__":
    main()
