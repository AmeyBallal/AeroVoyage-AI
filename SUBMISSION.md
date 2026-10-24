# Fetch-A-Thon 3.0: ASI:One Agent Challenge Submission

> **Project Name:** AeroVoyage AI – Autonomous Multi-Agent Logistics & Travel Orchestrator  
> **Challenge Track:** ASI:One Agent Challenge – From Intent to Action  
> **Category:** Innovation Lab  
> **Repository:** [https://github.com/AmeyBallal/AeroVoyage-AI](https://github.com/AmeyBallal/AeroVoyage-AI)  

---

## 📋 Required Deliverables Summary

| Deliverable Item | Submission Value / URL |
| :--- | :--- |
| **Project Title** | **AeroVoyage AI** |
| **Public GitHub Repository** | `https://github.com/AmeyBallal/AeroVoyage-AI.git` |
| **Agent Name** | `aerovoyage_concierge` |
| **Agentverse Address** | `agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9` |
| **Agentverse Inspector URL** | `https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000&address=agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9` |
| **Settlement Payee Wallet** | `fetch15a0xsau6vx8xks7k4k4mrquyz44t86vzs2g372` |
| **Dorado Testnet Explorer** | `https://explore-dorado.fetch.ai/accounts/fetch15a0xsau6vx8xks7k4k4mrquyz44t86vzs2g372` |
| **Verified Testnet Tx 1** | `https://explore-dorado.fetch.ai/transactions/DF98B144252FD820E7E7320D1A1657BF1D04AF8F2FBEA6072DBFC230C24799B6` |
| **Verified Testnet Tx 2** | `https://explore-dorado.fetch.ai/transactions/4F9521EC10589215ECB1FE505E7A0B035D4B27E1D1C77A5AEC01202197E71FA2` |
| **ASI:One Shared Chat URL** | *[Paste your shared chat link generated from ASI:One chat dashboard]* |
| **Demo Video Link** | *[Paste your YouTube / Loom video link – see DEMO_SCRIPT.md]* |

---

## 📝 Project Description (Copy-Paste Ready for Submission Agent)

### 1. The Problem Being Solved
Most AI applications stop at simple conversation. When travelers plan multi-city journeys, they are forced to juggle 5+ disconnected tools: comparing airlines, calculating meeting connection buffers, checking hotel sustainability certifications, monitoring real-time flight window weather hazards, and conducting manual credit card checkout with 3% fees. Traditional conversational bots merely talk about travel, but lack the autonomous agency to gather missing context, orchestrate specialized worker agents, verify live telemetry, or cryptographically settle financial commitments.

### 2. Target Users
- **Corporate & Executive Travelers:** Professionals requiring fast, non-stop flight scheduling with guaranteed meeting arrival buffers, VIP lounge access, and transparent ledger billing.
- **Eco-Conscious Individuals:** Travelers seeking verified low-carbon routes, green-certified lodging (LEED), and automated carbon offsetting.
- **Web3 & ASI:One Users:** Digital natives desiring an end-to-end travel concierge operating entirely within their personal AI assistant without third-party web redirects.

### 3. The Outcome Produced by the Agent
AeroVoyage AI turns **Intent into Action** through a complete 5-stage interactive workflow:
1. **Intelligent Context Clarification:** If a query is underspecified (e.g. *"Plan a trip to San Francisco"*), the agent dynamically inquires about missing parameters (origin, destination, timing, budget) and delivers an interactive **Travel Parameters Form Card**.
2. **Real-Time Telemetry & Multi-Agent Planning:** Gathers live destination weather from **Open-Meteo** and cryptocurrency rates from **CoinGecko**, while Groq LLM synthesizes an executive summary.
3. **Interactive Itinerary Comparison:** Delivers a native **Carousel Card** comparing *Executive Express*, *Eco-Smart Navigator*, and *Agile Corporate Value* options with 1-click select CTAs.
4. **Granular Telemetry Breakdown:** Presents an in-depth **Detail Card** displaying exact flight routes, hotel amenities, weather stability, and carbon footprints.
5. **On-Chain Settlement & Verified Escrow:** Issues an interactive **Review Card** under the Fetch.ai Payment Protocol. Upon user authorization, it broadcasts a live on-chain transaction over the Fetch.ai Dorado testnet ledger client, returning a terminal **Receipt Card** with a unique reservation PNR and verifiable block explorer link.

---

## 🏆 Bonus Criteria Alignment

1. **Effective Multi-Agent Collaboration:** Concierge Agent dispatches tasks to Logistics Agent and Settlement Agent using internal asynchronous schemas (`QueryItineraryRequest`, `SettlementInitiateRequest`).
2. **Payment Protocol & Credible Monetization Model:** Implements `payment_protocol_spec` with a sustainable 5.0 FET platform coordination fee model + smart escrow for supplier funds, broadcasting real transactions to payee wallet `fetch15a0xsau6vx8xks7k4k4mrquyz44t86vzs2g372` on the Dorado testnet.
3. **Effective Use of ASI:One Interactive Cards:** Complete interactive UI suite using `FormCardPayload`, `CarouselCardPayload`, `DetailCardPayload`, and `ReviewCardPayload`.
4. **Reliability & Tool Recovery:** Graceful fallback cascade: Open-Meteo caching, CoinGecko TTL in-memory rate-limit cache, Groq model fallback chain, deterministic regex/NLP parser, and testnet RPC fallback.
5. **Real-Time Data Integration:** Open-Meteo WMO weather API, CoinGecko crypto oracle, Groq LLM reasoning engine, and CosmPy Fetch.ai ledger client.
6. **Post-Hackathon Viability:** Realistic enterprise B2B SaaS business model where autonomous agents earn micro-FET revenue for logistics orchestration.

---

## 🚀 How to Submit on the Fetch-A-Thon 3.0 Dashboard

1. Open the [Fetch-A-Thon 3.0 Dashboard](https://asi.one).
2. Select the **Project Submission Agent** from the available agents.
3. Provide the project details from this document:
   - **Project Name:** AeroVoyage AI
   - **GitHub Repository:** `https://github.com/AmeyBallal/AeroVoyage-AI`
   - **Agentverse Profile / Inspector:** `https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000&address=agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9`
   - **ASI:One Shared Chat URL:** Click the **Share** button on your completed chat session in ASI:One and paste the link.
   - **Demo Video:** Your 2-3 minute YouTube or Loom link (recorded using `DEMO_SCRIPT.md`).
   - **Description:** Copy the *Problem*, *Target Users*, and *Outcome* sections above.
4. Verify all links are accessible to judges!
