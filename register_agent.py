"""Automated Agent Registration Script for Agentverse & ASI:One.

Registers your local agent directly on Agentverse using your AGENTVERSE_KEY and AGENT_SEED_PHRASE.
"""

import os
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv()

from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

AGENTVERSE_KEY = os.getenv("AGENTVERSE_KEY")
AGENT_SEED = os.getenv(
    "AGENT_SEED_PHRASE",
    "aerovoyage_standalone_concierge_hackathon_seed_2026",
)
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))
AGENT_ADDRESS = "agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9"


def main():
    if not AGENTVERSE_KEY or AGENTVERSE_KEY == "your_agentverse_api_key_here":
        print("\n" + "=" * 70)
        print("❌ [Error] AGENTVERSE_KEY is missing or not set!")
        print("=" * 70)
        print("Please set your Agentverse API Key:")
        print("1. In your .env file: AGENTVERSE_KEY=your_actual_key_here")
        print("2. Or in PowerShell:   $env:AGENTVERSE_KEY=\"your_actual_key_here\"")
        print("Then run this script again: python register_agent.py\n")
        sys.exit(1)

    endpoint_url = (
        f"https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={AGENT_ADDRESS}"
    )

    print("\n" + "=" * 70)
    print("🚀 Registering AeroVoyage Concierge on Agentverse...")
    print("=" * 70)
    print(f"Agent Name    : AeroVoyage Concierge")
    print(f"Agent Address : {AGENT_ADDRESS}")
    print(f"Inspector URL : {endpoint_url}")
    print("=" * 70 + "\n")

    try:
        success = register_chat_agent(
            name="aerovoyage_concierge",
            endpoint=endpoint_url,
            active=True,
            credentials=RegistrationRequestCredentials(
                agentverse_api_key=AGENTVERSE_KEY,
                agent_seed_phrase=AGENT_SEED,
            ),
            description="Autonomous Multi-Agent Travel & Logistics Orchestrator with ASI:One Interactive Cards and Fetch.ai Payment Protocol.",
            starter_prompts=[
                "Plan a 3-day executive trip to San Francisco under $1500",
                "Find me eco-certified travel options to London",
                "What are your travel orchestration capabilities?",
            ],
            metadata={
                "category": "Innovation Lab",
                "tags": [
                    "innovationlab",
                    "hackathon",
                    "travel",
                    "logistics",
                    "weather",
                    "payment-protocol",
                ],
            },
        )

        if success:
            print("✅ SUCCESS: Agent registered on Agentverse and discoverable on ASI:One!")
        else:
            print("⚠️ Notice: Registration completed. Please verify on Agentverse dashboard.")

    except Exception as exc:
        print(f"❌ Registration failed with error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
