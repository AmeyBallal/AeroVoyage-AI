# AeroVoyage AI – 3-Minute Demo Video Script & Walkthrough

> **Challenge:** ASI:One Agent Challenge – From Intent to Action (Fetch-A-Thon 3.0)  
> **Agent Name:** AeroVoyage Concierge (`aerovoyage_concierge`)  
> **Agent Address:** `agent1qdaxwrdn82n4ut3dag2ftltrqhne9ux2mvf9hgxwahw93zcm04na7wmdgh9`  
> **GitHub:** [https://github.com/AmeyBallal/AeroVoyage-AI](https://github.com/AmeyBallal/AeroVoyage-AI)  
> **Video Duration:** ~2:45 to 3:00 minutes

---

## 🎬 Video Production Setup
- **Screen 1 (Primary):** ASI:One chat dashboard ([asi.one](https://asi.one)) with AeroVoyage Concierge open.
- **Screen 2 (Side/Tab):** Fetch.ai Dorado Testnet Block Explorer showing Settlement Agent wallet ([explore-dorado.fetch.ai](https://explore-dorado.fetch.ai/accounts/fetch15a0xsau6vx8xks7k4k4mrquyz44t86vzs2g372)).
- **Screen 3 (Terminal):** Agent process running (`python Demo_code.py`) showing live ledger broadcasts.

---

## ⏱️ Scene-by-Scene Script

### Scene 1: The Problem & Value Proposition (0:00 - 0:35)
**Screen:** Show ASI:One chat interface and title slide: *AeroVoyage AI: From Intent to Action*.

**Voiceover:**
> *"Hello judges! Welcome to AeroVoyage AI. Most AI travel bots stop at conversation—they give you text recommendations, but force you to open five different browser tabs to check flight delays, verify hotel eco-credentials, monitor real-time weather hazards, and pull out a credit card to manually check out.
> 
> AeroVoyage AI turns **Intent into Action**. Built natively on the Fetch.ai uAgents framework for ASI:One, AeroVoyage is an autonomous multi-agent logistics orchestrator. It combines live Open-Meteo weather telemetry, Groq LLM reasoning, interactive native ASI:One Cards, and the Fetch.ai Payment Protocol to plan, optimize, and settle executive travel directly inside this chat."*

---

### Scene 2: Conversational Context Clarification (0:35 - 1:15)
**Screen:** In ASI:One chat, type: `"Plan a trip to San Francisco"`.

**Voiceover:**
> *"Let's test it live on ASI:One. If a user provides an underspecified prompt like 'Plan a trip to San Francisco', AeroVoyage doesn't hallucinate or make up arbitrary departure cities. 
> 
> Instead, our autonomous context reasoner identifies what is missing: where the user lives, their travel dates, and their budget. It prompts the user with clarifying questions and delivers a native **Travel Parameters Form Card**."*

**Action:**
- Show the agent asking for:
  1. Departure Origin
  2. Destination
  3. Travel Timing
  4. Budget
- Type: `"I live in New York, departing next week for 3 days with a $1500 budget"`.

**Voiceover:**
> *"Now that all four parameters are provided, our multi-agent network springs into action in real-time."*

---

### Scene 3: Real-Time Telemetry & Native Carousel Cards (1:15 - 1:55)
**Screen:** Show the agent delivering the **Executive Synthesis** and the interactive **Carousel Card**.

**Voiceover:**
> *"The Logistics Agent queries live weather from Open-Meteo—detecting live temperature and clear skies in San Francisco—while fetching live FET cryptocurrency prices from CoinGecko.
> 
> Groq's high-speed LLM synthesizes an executive meeting brief, and presents a native **ASI:One Carousel Card** with three tailored choices:
> 1. **Executive Express:** Priority meeting buffers and five-star luxury lodging.
> 2. **Eco-Smart Navigator:** High-speed green transit with certified carbon offsets.
> 3. **Agile Corporate Value:** Optimized point-to-point transit.
> 
> Let's click **'Inspect & Select'** on the Eco-Smart Navigator package."*

**Action:** Click **"Inspect & Select"** on `pkg_eco_02`.
- Show the **Detail Card** displaying flight schedules, hotel amenities, and carbon footprint.
- Click **"Proceed to Booking Authorization"**.

---

### Scene 4: Smart Escrow & Live On-Chain Settlement (1:55 - 2:35)
**Screen:** Show the **Review Card** with itemized Fetch.ai Payment Protocol breakdown.

**Voiceover:**
> *"Here is the **Review Card**. AeroVoyage implements a credible B2B monetization model: a flat 5.0 FET platform coordination fee, with the supplier balance secured in smart escrow.
> 
> When we click **'Authorize & Lock Escrow'**, watch what happens: the agent doesn't mock a transaction. It uses CosmPy and the Fetch.ai Dorado testnet ledger client to sign and broadcast a live on-chain token transfer from the Concierge wallet to the Settlement Agent payee wallet!"*

**Action:**
- Click **"Authorize & Lock Escrow"** (or type `{"action":"lock_escrow","pkg_id":"pkg_eco_02"}`).
- The confirmed **Receipt Card** appears with:
  - Reservation PNR: `AV-XXXXXX`
  - Real 64-character Dorado testnet Transaction Hash
  - Clickable block explorer URL!

**Voiceover:**
> *"Boom! The terminal **Receipt Card** is delivered right in chat. We have our unique reservation PNR and our live transaction hash."*

---

### Scene 5: Verifying on Fetch.ai Block Explorer & Wrap-Up (2:35 - 3:00)
**Screen:** Switch to browser tab showing [explore-dorado.fetch.ai](https://explore-dorado.fetch.ai/accounts/fetch15a0xsau6vx8xks7k4k4mrquyz44t86vzs2g372). Refresh to show the updated balance and transaction history.

**Voiceover:**
> *"Switching over to the Fetch.ai Dorado Block Explorer for our Settlement Agent wallet `fetch15a0...`, we can see our incoming escrow transfers, verified block height, and PNR memo cryptographically locked on-chain.
> 
> AeroVoyage AI proves that agents on ASI:One can move far beyond simple chatbots—delivering autonomous, real-time, monetized workflows from intent to on-chain execution.
> 
> Thank you for watching!"*

---

## 📌 Video Checklist for Submission
- [ ] Record in 1080p full HD with clear audio.
- [ ] Show the ASI:One chat interface clearly.
- [ ] Show the clickable block explorer link on [explore-dorado.fetch.ai](https://explore-dorado.fetch.ai).
- [ ] Upload to YouTube (Unlisted or Public) or Loom.
- [ ] Copy the video link into the project submission form on the Fetch-A-Thon 3.0 Dashboard.
