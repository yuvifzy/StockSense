# StockSense 🛒📈

[![Status](https://img.shields.io/badge/Status-MVP-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Smart stock suggestions and demand forecasting for Indian Kirana stores—powered by AI, delivered via WhatsApp.**

---

## 📖 Overview

India has over 12 million *kirana* (neighborhood grocery) stores. Most are run by single owner-operators managing purchasing, sales, and inventory entirely from memory or handwritten ledgers. 

**StockSense** is designed to solve the two biggest silent revenue killers for these businesses:
1. **Stockouts:** Fast-moving items running out, leading to lost sales.
2. **Deadstock:** Capital locked up in slow-moving or seasonal products.

By leveraging **WhatsApp** as the primary interface, StockSense removes the friction of complex ERP software and requires zero onboarding time. Owners simply send a text, voice note, or photo of their daily sales, and StockSense handles the rest.

---

## ✨ Core Features (MVP)

* 📱 **WhatsApp-Native Onboarding:** Zero app downloads. A simple guided conversation registers the store, location, and preferred language.
* 🗣️ **Natural Language Parsing:** Uses Gemini AI to understand free-text sales inputs in Hindi, Tamil, and Hinglish (e.g., *"Atta 5kg - 3, Maggi - 12"*).
* 📊 **Weekly Demand Forecasting:** Time-series forecasting (via Facebook Prophet) predicts next week's sales per SKU.
* 📦 **Smart Reorder Recommendations:** Suggests exact quantities to reorder, factoring in a safety buffer to prevent stockouts.
* 🌐 **Multi-Language Support:** First-class support for Hindi, Tamil, and English.
* 📸 **Ledger OCR (Upcoming):** Simply snap a picture of a handwritten daily ledger to digitize sales.

---

## 🛠️ Tech Stack

StockSense is built for simplicity, scale, and extremely low latency for WhatsApp messaging:

* **Interface:** Meta WhatsApp Cloud API
* **Backend:** FastAPI (Python) or Express (Node.js) 
* **Database:** PostgreSQL (Supabase)
* **NLP / AI:** Google Gemini 1.5 Flash (via Google AI Studio)
* **Forecasting Engine:** Facebook Prophet
* **Task Queue:** Celery + Redis (Upstash)
* **Deployment:** Railway / Render

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+ or Node.js 18+
* PostgreSQL database (e.g., Supabase free tier)
* Meta Developer Account (for WhatsApp Business API)
* Google AI Studio API Key (for Gemini)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/StockSense.git
   cd StockSense
   ```

2. **Set up virtual environment (if using Python):**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file based on `.env.example`:
   ```env
   WHATSAPP_TOKEN=your_meta_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_id
   GEMINI_API_KEY=your_gemini_key
   DATABASE_URL=your_supabase_postgres_url
   REDIS_URL=your_upstash_redis_url
   ```

4. **Run the Application:**
   ```bash
   uvicorn main:app --reload
   # or
   npm run dev
   ```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Empowering local businesses, one message at a time.*
