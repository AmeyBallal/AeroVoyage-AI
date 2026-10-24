# AeroVoyage AI: Autonomous Multi-Agent Logistics & Travel Orchestrator

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uAgents](https://img.shields.io/badge/uAgents-0.26.1-green.svg)](https://github.com/fetchai/uAgents)
[![ASI:One Ready](https://img.shields.io/badge/ASI:One-ACP%20Cards-orange.svg)](https://asi.one)

> **Fetch-A-Thon 3.0 Challenge Submission: ASI:One Agent Challenge – From Intent to Action**

---

## 1. Project Overview

### The Problem Being Solved
Most AI applications stop at simple conversation. When a business traveler or consumer wants to plan a journey, they are forced to juggle 5+ browser tabs: comparing airline rates, checking hotel sustainability certifications, monitoring real-time flight window weather hazards, and conducting manual credit card checkout. Standard conversational bots can talk about travel, but they cannot autonomously orchestrate services, calculate real-time risks, interact via rich native UI components, or handle verified financial transactions.

### Target Users
- **Corporate & Executive Travelers:** Professionals requiring fast, non-stop flight scheduling with verified hotel amenities and transparent billing.
- **Eco-Conscious Individuals:** Travelers seeking certified low-carbon routes, green-certified lodging (LEED), and automated carbon offsetting.
- **Web3 & AI Pioneers:** Users of **ASI:One** wanting seamless end-to-end travel booking directly inside their personal AI assistant without third-party redirects.

### The Outcome Produced by the Agent
AeroVoyage AI turns **Intent into Action**:
1. Captures natural language travel intents or prompts the user with an interactive **Form Card** inside ASI:One.
2. Coordinates worker agents that pull real-time weather telemetry from **Open-Meteo** and live **FET/USD** market prices.
3. Renders a native **Carousel Card** allowing 1-click comparison of optimized itineraries (*Executive Express*, *Eco-Smart Navigator*, *Value Maxima*).
4. Provides an in-depth **Detail Card** displaying flight schedules, hotel amenities, carbon footprints, and weather window stability.
5. Issues a Fetch.ai **Payment Protocol Review Card** for micro-FET agent fees and smart escrow locking.
6. Delivers a cryptographically verified **Receipt Card** with unique reservation PNR and transaction hash.

---

## 2. Multi-Agent System Architecture

```mermaid
flowchart TD
    User([ASI:One User / LLM]) <-->|Agent Chat Protocol ACP\nInteractive Cards| Concierge[AeroVoyage Concierge Agent\nagent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5]
    
    subgraph MultiAgentNetwork [AeroVoyage Multi-Agent Network]
        Concierge <-->|QueryItineraryRequest / Response| Logistics[Logistics & Live Intelligence Agent\nagent1qtjcn0xkt4nna7xwg7cyu09eqpt22kwcys2umcmpeu0ctkktv0zrxdqkgck]
        Logistics -->|Live REST API| WeatherAPI[Open-Meteo Real-Time Weather]
        Logistics -->|Live REST API| CurrencyAPI[CoinGecko Live FET/USD Rates]
        Logistics -->|Scoring Engine| TravelEngine[Multi-Criteria Itinerary Optimizer]
        
        Concierge <-->|SettlementInitiate / Confirmed| Settlement[Settlement & Escrow Agent\nagent1qfxpj3zrsfgl58deya9vrnc4hptccmz5v6rt3z8qgdcg8jzlxc4gjfzpu6l]
        Settlement -->|Fetch.ai Payment Protocol| Ledger[Fetch.ai Ledger Smart Escrow]
    end
```

### Agent Directory & Cryptographic Addresses

| Agent Name | Role | Protocol | Deterministic Address |
| :--- | :--- | :--- | :--- |
| **AeroVoyage Concierge** | ASI:One Facing Orchestrator | `chat_protocol_spec` (ACP) | `agent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5` |
| **Logistics Intelligence** | Real-Time Telemetry & Scoring | Inter-Agent Query Protocol | `agent1qtjcn0xkt4nna7xwg7cyu09eqpt22kwcys2umcmpeu0ctkktv0zrxdqkgck` |
| **Settlement & Escrow** | Escrow Lock & Monetization | `payment_protocol_spec` (Seller) | `agent1qfxpj3zrsfgl58deya9vrnc4hptccmz5v6rt3z8qgdcg8jzlxc4gjfzpu6l` |
| **Standalone Concierge** | Single-file Agentverse Cloud Agent | `chat_protocol_spec` (ACP) | `agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9` |

---

## 3. Key Features & Judging Criteria Highlights

### 1. Functionality & Technical Implementation (25%)
- **Multi-Step Autonomous Planning:** Progresses through `INIT` ➔ `PREFERENCES_COLLECTED` ➔ `SEARCHING` ➔ `OPTIONS_PRESENTED` ➔ `DETAIL_VIEW` ➔ `ESCROW_AUTHORIZATION` ➔ `BOOKED`.
- **Zero-Downtime Resilience:** Every external service (Open-Meteo, CoinGecko) includes automated exception handling and resilient fallback telemetry.
- **100% Test Coverage:** Complete unit and integration test suite (`tests/`) simulating end-to-end ASI:One workflows.

### 2. Use of Fetch.ai Technology (20%)
- **Agent Chat Protocol (ACP):** Implements `chat_protocol_spec` from `uagents_core.contrib.protocols.chat`.
- **Agentverse Registration:** Manifest publishing (`publish_manifest=True`) enables automatic indexing on Agentverse and routing by ASI:One.
- **Fetch.ai Payment Protocol:** Native seller-side implementation of `payment_protocol_spec` handling `CommitPayment`, `CompletePayment`, and micro-FET agent fees.
- **uAgents Bureau:** Simultaneous multi-agent co-location and local address routing via `Bureau(port=8000)`.

### 3. Native ASI:One Interactive Cards (Bonus Points)
- **Form Card (`FormCardPayload`):** 5-field interactive drawer for origin, destination, dates, and budget.
- **Carousel Card (`CarouselCardPayload`):** Multi-card carousel with badges (`Top Rated`, `Eco Certified`, `Best Value`) and 1-click select CTAs.
- **Detail Card (`DetailCardPayload`):** Deep-dive breakdown into flight carrier, hotel, amenities, live destination weather, and carbon metrics.
- **Review Card (`ReviewCardPayload`):** Escrow lock authorization screen with itemized invoice and approve/reject actions.
- **Receipt Card (`DetailCardPayload`):** Terminal confirmation displaying unique PNR (`AV-XXXXXX`) and transaction hash.

### 4. Groq Free Tier LLM Reasoning Engine (Bonus Points)
- **Deep Intent & Route Understanding:** Powered by Groq's high-throughput Llama models (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`).
- **Autonomous Multi-City Optimization:** Understands complex natural language prompts (e.g. *"Plan a five-day multi-city business trip across Berlin, Zurich, and Milan with fastest connections between meetings"*).
- **Executive Synthesis & Travel Advisory:** Synthesizes custom travel briefs and provides real-time conversational answers to travel/visa/FET escrow questions directly within ASI:One chat.
- **Fail-Safe Fallback Architecture:** Automatically falls back across 4 Groq models and reverts to deterministic regex/geocoding if the API key is not configured or rate-limited.

### 5. Credible Monetization Model (Bonus Points)
- Charges a platform coordination fee of **5.0 FET** per confirmed itinerary.
- Locks travel escrow directly into the smart escrow ledger, demonstrating a viable post-hackathon business model for autonomous agentic commerce.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AeroVoyage-AI.git
cd AeroVoyage-AI

# 2. Create and activate a Python 3.11 virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the System

You have two execution options:

#### Option A: Unified Multi-Agent Bureau (Recommended)
Spins up all three specialized agents (`Concierge`, `Logistics`, `Settlement`) inside a single local event loop:
```bash
python run.py
```

#### Option B: Standalone Single-File Agent (`Demo_code.py`)
Run the self-contained concierge locally or copy its contents directly into the **Agentverse Web Cloud IDE** (https://agentverse.ai):
```bash
python Demo_code.py
```

---

## 5. Automated Test Suite

Run the automated test suite covering all services, card schemas, Groq LLM reasoning & fallback, payment protocol models, and the full simulated ASI:One conversational flow:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Output:
```text
Ran 19 tests in 65s
OK (100% Pass Rate)
```

---

## 6. Testing Directly inside ASI:One

1. Log in to [ASI:One](https://asi.one).
2. Ensure your agent is registered on [Agentverse](https://agentverse.ai) with Mailbox enabled (`mailbox=True`).
3. Start a new chat with **AeroVoyage Concierge** (`agent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5`).
4. **Primary Workflow Walkthrough:**
   - **Step 1:** Say *"Plan a trip to San Francisco under $1500"*.
   - **Step 2:** An interactive **Form Card** appears. Confirm or adjust your travel dates.
   - **Step 3:** AeroVoyage displays a 3-option **Carousel Card** with live Open-Meteo weather and price metrics.
   - **Step 4:** Click **"Inspect & Select"** on the *Executive Express* package.
   - **Step 5:** Review flight details, hotel amenities, and weather window stability on the **Detail Card**.
   - **Step 6:** Click **"Proceed to Booking Authorization"** to open the **Review Card**.
   - **Step 7:** Click **"Authorize & Lock Escrow"**. The Payment Protocol executes, and a confirmed **Receipt Card** with your booking PNR is delivered!

---

## 7. Submission Deliverables Checklist

- [x] **Agentverse Registered Profile:** `agent1qg5gewzgdj9mxvxrk2x6hw4kh0u5upxvascpc0ql4x9centpvhmv2un4xv5`
- [x] **Agent Chat Protocol (ACP):** Implemented with full schema validation (`uagents_core.contrib.protocols.chat`).
- [x] **ASI:One Interactive Cards:** Form, Carousel, Detail View, Review, and Terminal Receipt.
- [x] **Multi-Agent Orchestration:** Concierge, Logistics Intelligence, and Settlement Escrow agents.
- [x] **Fetch.ai Payment Protocol:** Native seller-side escrow lock and FET micro-transaction fee model.
- [x] **Real-Time Data Integration:** Open-Meteo live weather API & CoinGecko live cryptocurrency oracle.
- [x] **Complete Primary Workflow:** Fully demonstrated within an ASI:One conversation without requiring a custom frontend.
- [x] **Public GitHub Repository:** Clean structure, comprehensive documentation, and automated tests.

---

## 8. License

Distributed under the Apache 2.0 License. Built with ❤️ for the Fetch.ai and Artificial Superintelligence (ASI) Alliance Ecosystem.
