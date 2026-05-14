# StockSense — Product Requirements Document
**Version:** 1.0 (MVP)
**Status:** Draft
**Author:** Product Team
**Last Updated:** May 2026

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [User Personas](#3-user-personas)
4. [User Stories](#4-user-stories)
5. [Core Features (MVP)](#5-core-features-mvp)
6. [Out of Scope for MVP](#6-out-of-scope-for-mvp)
7. [User Flow](#7-user-flow)
8. [Tech Stack Recommendation](#8-tech-stack-recommendation)
9. [Key Risks & Mitigations](#9-key-risks--mitigations)
10. [Open Questions](#10-open-questions)

---

## 1. Problem Statement

### The Core Pain

India has approximately 12 million kirana stores. The vast majority are run by a single owner-operator who manages purchasing, sales, and inventory entirely from memory or handwritten ledgers. There is no system — and the consequences are expensive.

### Specific Pains

**Stockouts kill revenue silently.** When a fast-moving SKU like Maggi noodles or Parle-G runs out on a Tuesday, the owner doesn't reorder until Friday when the distributor visits. The customer who couldn't find it went to the shop next door and may not come back. The owner doesn't track this lost sale — it simply doesn't exist in any record.

**Deadstock locks up capital.** Seasonal items (specific festival sweets, monsoon-demand products), slow-moving variants (a 5kg atta pack when the locality buys 2kg), and over-ordering from distributor pressure result in stock that sits for weeks. For a store operating on ₹2–5 lakh in monthly inventory turns, even ₹10,000–₹20,000 in deadstock per month is a 1–2% margin hit that the owner can't quantify.

**Purchasing is reactive, not predictive.** Most owners order when they "feel" stock is low or when a distributor salesperson visits and pushes products. There is no data-driven trigger. Orders are placed based on gut, not trend — so a spike in demand during a local festival, cricket match day, or school exam season is consistently under-served.

**No tools fit this user.** ERP software is too complex. Spreadsheets require laptop literacy. Existing inventory apps demand structured onboarding that owners abandon within a week. The owner IS the store — they don't have 20 minutes to learn a new tool. WhatsApp, however, they use every single day.

**The financial cost is real.** Conservative estimates suggest kirana stores lose 8–12% of potential revenue to stockouts and waste 3–6% of inventory value to deadstock annually. For a store doing ₹3 lakh/month in sales, that's ₹24,000–₹36,000 in avoidable losses every month.

---

## 2. Goals & Success Metrics

### v1 Definition of Success
MVP is successful if 100 active stores are using StockSense weekly at the end of Month 3, with measurable reduction in stockout frequency reported by users.

### User KPIs
| Metric | Target (Month 3) |
|---|---|
| Weekly Active Stores (WAS) | 100 |
| Avg. messages sent per store per week | ≥ 5 |
| % stores completing first full forecast cycle | ≥ 70% |
| User-reported stockout reduction | ≥ 30% self-reported |
| Reorder recommendation acceptance rate | ≥ 60% |

### Business KPIs
| Metric | Target (Month 3) |
|---|---|
| Total onboarded stores | 200 |
| 30-day retention rate | ≥ 55% |
| NPS score (sampled via WhatsApp) | ≥ 40 |
| Cost per active store (infra) | ≤ ₹50/month |

### Product KPIs
| Metric | Target |
|---|---|
| Time from first message to first forecast | ≤ 10 minutes |
| Forecast message delivery time | ≤ 30 seconds |
| SKU recognition accuracy (from natural language input) | ≥ 85% |
| System uptime | ≥ 99.5% |

---

## 3. User Personas

### Persona 1 — Ramesh Gupta

| Attribute | Detail |
|---|---|
| **Name** | Ramesh Gupta |
| **Age** | 52 |
| **Location** | Varanasi, Uttar Pradesh |
| **Store Type** | General kirana, 800 SKUs, ~₹2.5 lakh/month turnover |
| **Tech Comfort** | Uses WhatsApp to share photos, watches YouTube. Cannot type fast. Uses voice messages heavily. Has a basic Android phone (Redmi). |
| **Language** | Hindi only. Cannot read English labels on apps. |
| **Key Frustration** | "Teen baar ho chuka hai ki chawal khatam ho gaya aur main bhool gaya order karna." *(Three times this has happened — rice ran out and I forgot to reorder.)* He over-orders flour because his distributor gives a discount on bulk, and then it goes stale. He has no way to know how much is "right." |
| **Behaviour** | Opens WhatsApp 15–20 times a day. Manages accounts in a physical bahi-khata. Has a teenage son who occasionally helps with phone tasks. |

---

### Persona 2 — Meenakshi Pillai

| Attribute | Detail |
|---|---|
| **Name** | Meenakshi Pillai |
| **Age** | 39 |
| **Location** | Coimbatore, Tamil Nadu |
| **Store Type** | Semi-urban kirana with a small beverages section, ~₹4 lakh/month turnover |
| **Tech Comfort** | Comfortable with WhatsApp, uses Google Pay and PhonePe daily, has tried a basic billing app once but stopped using it after 2 weeks. Moderate English literacy. |
| **Language** | Prefers Tamil, comfortable with simple English |
| **Key Frustration** | Seasonal demand blindspots. During Pongal and local school exam periods, her beverage and snack sales spike 40%, but she always under-orders because she can't remember what exactly sold and by how much last year. Ends up turning away customers during peak days. |
| **Behaviour** | More digitally open than Ramesh. Would adopt a tool if it shows clear, immediate value. Skeptical of anything that requires more than 2 minutes of setup. |

---

## 4. User Stories

### Onboarding

- As **Ramesh**, I want to register my store by sending a simple WhatsApp message so that I don't have to download any app or fill a form.
- As **Meenakshi**, I want to set my preferred language (Tamil) at the start so that all messages and forecasts come to me in a language I understand.
- As **Ramesh**, I want StockSense to guide me step-by-step via WhatsApp so that I know exactly what information to send and when.

### Data Input

- As **Ramesh**, I want to send my daily sales as a voice message or a simple typed list (e.g., "Atta 5kg – 3 bika, Maggi – 12 biki") so that I don't have to learn a new format or interface.
- As **Meenakshi**, I want to send a photo of my handwritten sales ledger so that I don't have to retype numbers I've already written down.
- As **Ramesh**, I want StockSense to confirm what it understood from my message so that I can correct mistakes before they affect my forecast.

### Forecast Output

- As **Meenakshi**, I want to receive a weekly demand forecast per item in a clear, simple format so that I know how much of each product I'll likely sell next week.
- As **Ramesh**, I want the forecast delivered in Hindi with simple numbers — not charts or graphs — so that I can read and understand it on my phone without confusion.
- As **Meenakshi**, I want the forecast to flag items that are likely to spike (festival, season) so that I'm not caught off guard.

### Reorder Suggestion

- As **Ramesh**, I want StockSense to tell me exactly how much of each item to order this week so that I stop guessing and wasting money on over-ordering.
- As **Meenakshi**, I want to be able to reply "haan" or "nahi" to a reorder suggestion so that I can quickly confirm or skip a recommendation without typing a full response.
- As **Ramesh**, I want to know which items I currently have too much of (deadstock risk) so that I avoid ordering more of those until stock clears.

### Language Preference

- As **Ramesh**, I want to switch the bot language to Hindi at any time by typing "Hindi mein baat karo" so that I'm never stuck with English I can't read.
- As **Meenakshi**, I want to receive Tamil translations for all product categories and unit labels so that I never have to guess what an English term means.

---

## 5. Core Features (MVP)

### P0 — Must Have (Launch Blockers)

**P0.1 — WhatsApp Onboarding Flow**
One-line: A guided, conversational onboarding in under 5 messages that captures store name, location, and language preference.
Acceptance criteria: New user sends "Hi" → bot responds in detected language → collects store name, pin code, language preference → confirms registration. Completion rate ≥ 80% in testing.

**P0.2 — Natural Language Sales Input Parser**
One-line: Parse free-text or semi-structured sales input ("Atta 5kg – 4, Maggi – 10") into structured SKU + quantity records.
Acceptance criteria: Correctly identifies SKU name and quantity for ≥ 85% of inputs from a test set of 200 real kirana sales messages. Handles Hindi, Tamil, and Hinglish variants. Sends a confirmation message with parsed items for user approval.

**P0.3 — Weekly Demand Forecast**
One-line: Generate a 7-day SKU-level demand forecast every Monday morning based on the user's historical input.
Acceptance criteria: Forecast is delivered by 8:00 AM IST every Monday. Minimum 2 weeks of input data required before first forecast. Output is a plain-text WhatsApp message listing top 20 SKUs with predicted demand and confidence level (High / Medium / Low). Delivered in user's preferred language.

**P0.4 — Reorder Quantity Recommendation**
One-line: Alongside the forecast, recommend specific reorder quantities per SKU accounting for current stock (if provided) and a 1.2x safety buffer.
Acceptance criteria: Reorder message sent alongside forecast. User can reply with "confirm" or item-level overrides. Recommendations logged for accuracy tracking.

**P0.5 — Multi-language Support (Hindi + Tamil + English)**
One-line: All bot responses available in Hindi, Tamil, and English with language switchable by user command at any time.
Acceptance criteria: User can type "Hindi", "Tamil", or "English" at any point to switch language. All system messages, forecasts, and error responses have translations verified by a native speaker for each language.

---

### P1 — Should Have (Ship in Week 4–6)

**P1.1 — Daily Sales Reminder**
One-line: Send a daily nudge at 9:00 PM asking the user to share that day's sales if they haven't already.
Acceptance criteria: Reminder sent only if no sales message received that day. Max 1 reminder per day. User can type "band karo" / "stop" to pause reminders.

**P1.2 — Deadstock Alert**
One-line: Flag SKUs that have been in stock for 14+ days without sales movement.
Acceptance criteria: Weekly alert lists up to 5 items with no sales in the last 14 days. Alert includes suggested action ("Consider running an offer or returning to distributor").

**P1.3 — Image/Photo Input (OCR for Sales Ledger)**
One-line: Accept a photo of a handwritten sales ledger or printed bill and extract sales data via OCR.
Acceptance criteria: Works on clearly lit photos of standard bahi-khata entries. Extraction accuracy ≥ 70%. Extracted data shown to user for confirmation before saving.

**P1.4 — Current Stock Input**
One-line: Allow user to declare current stock levels per SKU, which improves reorder accuracy.
Acceptance criteria: User can send "Stock: Atta 5kg – 8 bags" and system stores this. Reorder calculation uses declared stock minus forecasted demand. Stock levels auto-decrement based on reported sales.

---

### P2 — Nice to Have (Post-MVP Backlog)

**P2.1 — Voice Message Input**
One-line: Accept WhatsApp voice notes and transcribe + parse them as sales input.
Acceptance criteria: Whisper-based transcription with ≥ 80% word accuracy on Hindi voice notes. Treated same as text input after transcription.

**P2.2 — Distributor Contact Sharing**
One-line: Let users save their distributor's WhatsApp number so reorder lists can be forwarded directly.
Acceptance criteria: User can register distributor number. Bot generates a pre-formatted order message the user can forward in one tap.

**P2.3 — Weekly Summary Report**
One-line: A plain-text weekly performance summary (top sellers, slow movers, estimated revenue).
Acceptance criteria: Sent every Sunday evening. Contains top 5 sellers, bottom 5 movers, and estimated weekly revenue based on reported sales.

---

## 6. Out of Scope for MVP

The following will NOT be built for v1. Any request to include these should be pushed to the v2 backlog.

- **Mobile app or web dashboard** — StockSense is WhatsApp-only for MVP. No React Native app, no browser dashboard.
- **Direct distributor integration** — No API connections to distributor ERP systems or FMCG wholesale platforms (Udaan, Metro Cash & Carry).
- **Automated ordering** — StockSense recommends; it does not place orders on the user's behalf.
- **Payments or credit tracking** — No udhaar (credit) ledger, no UPI integration, no accounts receivable features.
- **Barcode / QR scanning** — SKU input is text/voice only. Barcode scanning requires an app interface we're not building yet.
- **Multi-store management** — One WhatsApp number = one store. No owner-level aggregated dashboard.
- **Competitor price tracking** — No market price intelligence features.
- **Franchise / chain store features** — StockSense v1 is exclusively for independent single-owner stores.
- **Support for more than 3 languages** — Hindi, Tamil, and English only. Marathi, Telugu, Bengali are post-MVP.
- **Analytics dashboard for the team** — Internal admin tooling is minimal; raw database access is sufficient for v1.

---

## 7. User Flow

### Complete Flow: First Message → Reorder Recommendation

```
[DAY 0 — ONBOARDING]

Step 1: Discovery
  User sends "Hi" or "Namaste" to StockSense WhatsApp number
  (number shared via distributor network, poster, or referral)

Step 2: Language Detection & Selection
  Bot: "Namaste! StockSense aapki dukaan ke liye smart stock suggestions deta hai.
        Aap kaunsi bhasha mein baat karna chahenge?
        1. Hindi  2. Tamil  3. English"
  User replies: "1"

Step 3: Store Registration
  Bot asks: "Aapki dukaan ka naam kya hai?"
  User: "Gupta General Store"

  Bot asks: "Aapka pin code kya hai?"
  User: "221001"

  Bot: "Perfect! Gupta General Store, Varanasi register ho gaya. ✅
        Ab main aapko sikhaunga ki sales kaise share karein."

Step 4: First Sales Input Tutorial
  Bot: "Rozana raat ko apni sales aaise bhejein:
        [Item naam] – [bikne wali quantity]
        Example: Atta 5kg – 3, Maggi – 12, Parle-G – 20"

  User: "Atta 5kg – 3, Maggi – 12, Parle-G – 20, Tata Salt – 5"

Step 5: Confirmation
  Bot: "Maine yeh record kiya:
        ✅ Atta 5kg → 3 bags
        ✅ Maggi 70g → 12 packets
        ✅ Parle-G 75g → 20 packets
        ✅ Tata Salt 1kg → 5 packets
        Sahi hai? Haan / Nahi"

  User: "Haan"
  Bot: "Saved! Kal phir bhejein. Jitna zyada data, utna better forecast. 📊"

---

[DAYS 1–13 — DATA COLLECTION]

Daily reminder at 9 PM if no sales sent:
  Bot: "Aaj ki sales share karna bhool gaye? Abhi bhej dein! 🛒"

User sends sales daily (or skips some days — system handles gaps).

---

[DAY 14 — FIRST FORECAST (Monday 8:00 AM)]

Bot: "🔮 Is hafte ka forecast (15–21 May):

     TOP 10 SKUs jinhein ORDER KARNA CHAHIYE:

     1. Atta 5kg        → 18 bags expect  | Order: 20 bags  [High ✅]
     2. Maggi 70g       → 85 packets       | Order: 95 pkt   [High ✅]
     3. Parle-G 75g     → 140 packets      | Order: 150 pkt  [High ✅]
     4. Tata Salt 1kg   → 22 packets       | Order: 25 pkt   [Medium 🟡]
     5. Aashirvaad 1kg  → 10 bags          | Order: 12 bags  [Medium 🟡]
     ...

     ⚠️ DEADSTOCK ALERT:
     Sunfeast Dark Fantasy – 14 din se nahi bika. Order mat karna.

     Confirm karna ho toh reply karein: CONFIRM
     Changes ke liye: koi bhi item ka naam aur quantity bhejein."

User: "CONFIRM"

Bot: "Order list save ho gayi! ✅
     Apne distributor ko forward karne ke liye:
     [Pre-formatted order message generated]
     Copy karein aur distributor ko bhej dein. 📋"
```

---

## 8. Tech Stack Recommendation

### WhatsApp Layer
**WhatsApp Business API via Meta Cloud API (direct)**
Do not use a third-party BSP (Business Solution Provider) for MVP — they add cost and latency. Use Meta's Cloud API directly. Register a dedicated phone number. Use webhooks to receive messages and the Messages API to send responses.
Fallback: If Meta approval is delayed, use Twilio's WhatsApp Sandbox for development and early testing.

### Backend
**Runtime:** Node.js (Express) or Python (FastAPI) — choose FastAPI if the team is Python-first, which is likely given the AI components.
**Architecture:** Monolith for MVP. No microservices. A single service handles webhook ingestion, NLP parsing, forecast scheduling, and message dispatch.
**Hosting:** Railway.app or Render.com for simplicity and cost (≤ ₹2,000/month for MVP scale). Migrate to AWS/GCP only when hitting 1,000+ active stores.
**Task Queue:** Celery + Redis for async forecast generation and scheduled reminders. Celery Beat handles the Monday 8 AM and 9 PM reminder cron jobs.

### AI / Forecasting Layer
**NLP Parsing (Sales Input):** Gemini 1.5 Flash via Google AI Studio API. Prompt-engineer a structured extraction chain that handles Hindi, Hinglish, and Tamil input. Cost: ~$0.000375 per message at current pricing — negligible at MVP scale.
**Demand Forecasting:** Start with Facebook Prophet for time-series forecasting per SKU. It handles missing data, seasonality (weekly, annual), and holiday effects (Indian festivals via custom calendar). Requires minimum 14 days of data. Upgrade to a neural approach (TFT or N-BEATS) only if Prophet accuracy falls below 75% MAE at scale.
**OCR (P1 — ledger photo input):** Google Vision API or Tesseract (self-hosted). Google Vision is more accurate for handwritten Hindi text; use it.
**Language Translation:** Google Cloud Translation API for dynamic translation. Pre-translate all templated messages statically to reduce API calls.

### Database
**Primary DB:** PostgreSQL (hosted on Supabase — free tier covers MVP, simple interface, built-in auth).

**Schema (simplified):**
- `stores` — store_id, whatsapp_number, name, pin_code, language, created_at
- `sales_logs` — log_id, store_id, sku_id, quantity_sold, date, source (text/ocr/voice)
- `skus` — sku_id, store_id, canonical_name, variants[], unit
- `forecasts` — forecast_id, store_id, week_start, sku_id, predicted_qty, confidence, generated_at
- `reorder_suggestions` — suggestion_id, forecast_id, sku_id, suggested_qty, confirmed (bool)

**Cache:** Redis (via Upstash — serverless Redis, free tier) for session state management (multi-turn WhatsApp conversation context).

### Infrastructure Summary
| Component | Tool | Monthly Cost (MVP) |
|---|---|---|
| WhatsApp API | Meta Cloud API | Free (1,000 conversations/month free) |
| Backend hosting | Railway.app | ~₹1,500 |
| Database | Supabase | Free (up to 500MB) |
| Cache / Queue | Upstash Redis | Free |
| AI (NLP) | Gemini Flash | ~₹500 at 100 stores |
| Forecasting | Self-hosted Prophet | ₹0 |
| OCR | Google Vision | ~₹400 at P1 launch |
| **Total** | | **~₹2,400/month** |

---

## 9. Key Risks & Mitigations

### Risk 1 — Low Data Quality / Inconsistent Input
**Likelihood:** High. **Impact:** High.
Kirana owners will send messages in wildly different formats. "Atta bikii 3" vs "3 atta" vs a voice note in Bhojpuri. If the parser fails silently, forecast quality degrades without the user knowing.
**Mitigation:** Always send a confirmation message after every parse. Build a human-review queue for low-confidence parses (confidence < 70%) during the first 4 weeks — a team member reviews and corrects these to build a training dataset. Never let a bad parse silently corrupt the forecast. Log all raw inputs.

### Risk 2 — WhatsApp Business API Approval Delays / Policy Risk
**Likelihood:** Medium. **Impact:** Critical.
Meta can reject, delay, or revoke WhatsApp Business API access. Entire product distribution collapses if this happens.
**Mitigation:** Apply for API access on Day 1 of the project. Build on Twilio Sandbox in parallel so development is never blocked. Maintain a contingency plan for SMS-based input (Twilio SMS + similar NLP pipeline) as a fallback distribution channel. Do not tie go-to-market launch to API approval date.

### Risk 3 — User Abandonment After 1–2 Weeks
**Likelihood:** High. **Impact:** High.
The classic cold-start problem. Users need to input 14 days of data before getting a forecast. Most will drop off before seeing value.
**Mitigation:** Show micro-value earlier. After 3 days of input, send a "Top Seller This Week" message even without a full forecast. Frame it as a reward for consistency. Assign a human "onboarding buddy" (team member) who messages the first 50 stores manually to encourage them through the first 2 weeks. Design the reminder to feel helpful, not spammy.

### Risk 4 — Forecast Inaccuracy Destroying Trust
**Likelihood:** Medium. **Impact:** High.
If StockSense tells Ramesh to order 20 bags of Atta and only 8 sell, he will blame the tool and stop using it. Kirana owners have finely-tuned gut instincts — the product must earn trust, not demand it.
**Mitigation:** Always show confidence level (High/Medium/Low) alongside every forecast. Never recommend a reorder without flagging uncertainty. In the first month, bias recommendations conservatively (underestimate demand slightly to avoid over-ordering). Add a feedback mechanism: "Order liya? Kitna actual bika?" — use this to fine-tune Prophet parameters per store. Track forecast accuracy per store and proactively reach out to stores with MAE > 25%.

### Risk 5 — Regulatory / Data Privacy Risk
**Likelihood:** Low. **Impact:** Medium.
Storing sales data, store location, and owner identity creates obligations under India's Digital Personal Data Protection Act (DPDPA), 2023. Non-compliance can result in penalties.
**Mitigation:** Collect only what is necessary — no Aadhaar, PAN, or financial account data. Include a plain-Hindi privacy notice during onboarding: "Aapka data sirf aapke liye use hoga. Hum kisi ko nahi bechenge." Store all data on Indian servers (Supabase has an AWS ap-south-1 option). Draft a minimal privacy policy. Consult a tech lawyer before scaling past 500 stores.

---

## 10. Open Questions

The following must be resolved before sprint planning begins. Each has a suggested owner and decision deadline.

| # | Question | Why It Matters | Suggested Owner | Decide By |
|---|---|---|---|---|
| 1 | **What is the monetization model?** Free forever, freemium (X SKUs free), or ₹99/month subscription? This affects how aggressively we chase growth vs. retention from day 1. | Determines if we optimise for breadth (free) or depth (paid). | Founder | Before beta launch |
| 2 | **How do we source the first 200 stores?** Direct outreach? Distributor partnerships? FMCG brand pilots? The acquisition channel determines onboarding language, tone, and feature priority. | Cold-start without a channel plan is the #1 reason early B2SMB products die. | Founder + Marketing | Week 1 |
| 3 | **Do we pre-build a canonical SKU database or let users define their own SKUs?** A national SKU catalog (Maggi = canonical Maggi 70g pack) dramatically improves NLP accuracy but requires significant upfront work. | Directly impacts parser accuracy and cross-store analytics potential. | Tech Lead | Week 2 |
| 4 | **What is our minimum viable data threshold for a first forecast?** 7 days? 14 days? 21 days? Lower threshold gets users to value faster but reduces forecast quality. | Tradeoff between time-to-value and accuracy. Wrong choice either kills retention or kills trust. | Tech Lead + PM | Week 2 |
| 5 | **Should reorder recommendations include pricing / cost estimates?** If we know approximate MRP, we can show "estimated spend: ₹4,200 this order." This is high value but requires building or sourcing a price database. | High impact on perceived value, but scope risk if we try to do it in MVP. Decision: No for MVP, revisit at P1. | PM | Before MVP spec freeze |
| 6 | **How do we handle a store with no sales data for 3+ days?** Assume zero sales (understates demand) or skip those days in the model (biases forecast upward)? This is a core modeling decision. | Silent data gaps are the single biggest threat to forecast accuracy in this user segment. | Tech Lead (Data) | Week 3 |
| 7 | **Who handles WhatsApp message failures and user complaints at launch?** We need a defined support flow — even a simple one — before going live. A single frustrated owner posting "StockSense ne meri dukaan barbaad kar di" in a distributor group can kill a market. | Reputation risk is disproportionately high in tight-knit local merchant communities. | Ops Lead | Before go-live |

---

*This PRD covers StockSense v1 (MVP) scope only. A v2 document covering distributor integrations, multi-language expansion, and mobile app features will be drafted after 60 days of live usage data.*
