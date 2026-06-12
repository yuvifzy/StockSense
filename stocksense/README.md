# 📦 StockSense

**WhatsApp-based AI inventory forecasting for Indian kirana stores**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.x-DC382D?style=flat-square&logo=redis&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

---

StockSense is a conversational AI assistant that helps kirana (grocery) store owners across India manage inventory through WhatsApp. Owners simply text their daily sales in natural language — Hindi, Hinglish, Tamil, or English — and the system generates weekly demand forecasts, reorder recommendations, and deadstock alerts. No app downloads, no training, no spreadsheets.

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER JOURNEY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣  Owner sends "Hi" on WhatsApp                               │
│     ↓                                                           │
│  2️⃣  Bot onboards in 4 messages: language → name → pincode      │
│     ↓                                                           │
│  3️⃣  Owner texts daily sales: "Atta 5kg – 3, Maggi – 12"       │
│     ↓                                                           │
│  4️⃣  Gemini AI parses items → stored in PostgreSQL              │
│     ↓                                                           │
│  5️⃣  Every Monday 8AM: NeuralProphet forecast + reorder list    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **WhatsApp-native onboarding** — store registered in under 5 messages
- **Natural language sales input** — `"Atta 5kg – 3 bika, Maggi – 12"` parsed by Gemini AI
- **Multilingual support** — Hindi, Tamil, and English, switchable mid-conversation
- **Weekly demand forecasts** — SKU-level predictions generated every Monday at 8 AM IST
- **Reorder recommendations** — suggested quantities with a 1.2× safety buffer
- **Deadstock alerts** — flags items with zero movement for 14+ days
- **Daily reminders** — 9 PM nudge if no sales data received that day

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI |
| **Database** | PostgreSQL (Supabase), SQLite (local dev) |
| **AI / NLP** | Google Gemini 2.0 Flash Lite |
| **Forecasting** | NeuralProphet (time-series) |
| **Conversation State** | Redis |
| **Task Queue** | Celery + Celery Beat |
| **WhatsApp** | Meta Cloud API (webhooks) |
| **Deployment** | Railway.app |

---

## 📁 Project Structure

```
stocksense/
├── app/
│   ├── main.py              # FastAPI entry point, DB init
│   ├── config.py            # Environment settings
│   ├── database.py          # SQLAlchemy engine and session
│   ├── celery_app.py        # Celery instance
│   ├── tasks.py             # Scheduled forecast + reminder tasks
│   ├── models/              # ORM models
│   │   ├── store.py         #   Store registration
│   │   ├── sku.py           #   SKU catalog (with ARRAY variants)
│   │   ├── sales_log.py     #   Daily sales records
│   │   ├── forecast.py      #   Weekly demand forecasts
│   │   └── message_log.py   #   WhatsApp message audit trail
│   ├── routes/              # API routes
│   │   └── whatsapp.py      #   Webhook endpoint + message router
│   └── services/            # Business logic
│       ├── nlp_parser.py    #   Gemini-powered sales text parser
│       ├── messenger.py     #   WhatsApp send/reply (multilingual)
│       ├── conversation.py  #   Redis-backed state machine
│       ├── forecaster.py    #   NeuralProphet forecast engine
│       └── sales_persistence.py  # Sales data write layer
├── test_local.py            # Local webhook simulation script
├── requirements.txt
├── Procfile
├── railway.json
├── .env.example
└── .gitignore
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.9+
- Redis

```bash
# macOS
brew install redis
brew services start redis
```

### Installation

```bash
cd stocksense

# Install dependencies
python3 -m pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys (see table below)

# Start the server
python3 -m uvicorn app.main:app --reload --port 8000
```

### Test locally

In a second terminal:

```bash
python3 test_local.py
```

This simulates a full WhatsApp onboarding flow with 5 messages:
`Hi` → `1` (English) → `Gupta Store` → `560001` → `Atta 5kg – 3, Maggi – 12`

---

## 🔐 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (Supabase) | `postgresql://user:pass@host:6543/postgres` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `GEMINI_API_KEY` | Google AI Studio API key | `AQ.xxxxxxxx` |
| `WHATSAPP_TOKEN` | Meta Cloud API bearer token | `EAAG...` |
| `WHATSAPP_PHONE_ID` | WhatsApp Business phone number ID | `10xxxxxxxxxx` |
| `VERIFY_TOKEN` | Webhook verification token (any string) | `stocksense_verify_2026` |

> **⚠️ Never commit `.env` to version control.** Use `.env.example` as a template.

For local development without Supabase, use SQLite:
```
DATABASE_URL=sqlite:///./stocksense_test.db
```

---

## ☁️ Deployment

StockSense is deployed on **Railway.app**.

1. Connect your GitHub repo to Railway
2. Set all environment variables in the Railway dashboard
3. Provision a **Redis** service in Railway and link it
4. Point `DATABASE_URL` to your **Supabase** PostgreSQL instance (port `6543` for connection pooler)
5. Railway auto-detects `Procfile` and `railway.json` — deploy triggers on push

---

## 📊 Project Status

| Milestone | Status |
|-----------|--------|
| Core backend (FastAPI + ORM) | ✅ Complete |
| WhatsApp conversation state machine | ✅ Complete |
| Gemini NLP sales parser | ✅ Complete |
| NeuralProphet forecasting engine | ✅ Complete |
| Celery scheduled tasks | ✅ Complete |
| Supabase PostgreSQL migration | ✅ Complete |
| Railway deployment config | ✅ Complete |
| WhatsApp Business API approval | ⏳ Pending |
| Production launch | 🔜 Upcoming |

---

## 📄 License

This project is developed as part of an academic portfolio. All rights reserved.
