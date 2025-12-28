# 🛒 XStore Customer Support AI Agent

An intelligent, multilingual customer support chatbot built with **LangGraph** for e-commerce clothing stores.
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://xstore-customer-support.streamlit.app)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎬 Live Demo

👉 **[Try it now!](https://mevludesilakazan-xstore-customer-support.streamlit.app)**

## ✨ Features

- 🌍 **Bilingual Support** - Turkish & English with auto-detection
- 🧠 **Smart Categorization** - 7 specialized categories
- 💬 **Context-Aware Responses** - Store-specific information
- 📊 **Sentiment Analysis** - Auto-escalation for negative sentiment
- ⚡ **Fast & Free** - Powered by Groq (Llama 3.3 70B)

## 📂 Categories

| Category | Description |
|----------|-------------|
| 👕 Product & Size | Size guide, fabric, stock, fit recommendations |
| 📦 Order & Shipping | Order status, tracking, delivery times |
| 🔄 Return & Exchange | Return policy, exchange process, refunds |
| 💳 Payment & Invoice | Payment options, installments, invoices |
| 🔐 Account | Password reset, profile, membership |
| 🎁 Campaigns | Discounts, coupons, promotions |
| ℹ️ General | Business hours, contact info |

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/xstore-customer-support.git
cd xstore-customer-support

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
chmod +x start.sh
./start.sh
```

**Access:**
- 🛒 Chatbot: http://localhost:8501
- ⚙️ Admin: http://localhost:8502
- 🔍 Elasticsearch: http://localhost:9200

**Stop:**
```bash
docker-compose down
```

### Option 2: Manual Setup

```bash
git clone https://github.com/YOUR_USERNAME/xstore-customer-support.git
cd xstore-customer-support
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 4. Run the demo

```bash
# Jupyter Notebook
jupyter notebook notebooks/demo.ipynb

# Or Streamlit app
streamlit run web/streamlit_app.py
```

## 🔑 Get API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / Login
3. Create API Key
4. Add to `.env` file

## 📁 Project Structure

```
xstore-customer-support/
├── config/
│   └── store_config.py       # Store settings (customize here!)
├── src/
│   ├── agents/
│   │   └── support_agent.py  # Main LangGraph agent
│   ├── prompts/
│   │   ├── tr_prompts.py     # Turkish prompts
│   │   └── en_prompts.py     # English prompts
│   └── utils/
│       └── helpers.py        # Helper functions
├── api/
│   └── main.py               # FastAPI endpoint
├── web/
│   └── streamlit_app.py      # Streamlit UI
├── tests/
│   └── test_agent.py         # Unit tests
└── notebooks/
    └── demo.ipynb            # Demo notebook
```

## ⚙️ Configuration

Edit `config/store_config.py` to customize for your store:

```python
STORE = {
    "name": "YourStore",
    "return_days": 14,
    "free_shipping_limit": 1200,
    "shipping_days": "2-4 business days",
    # ... more settings
}
```

## 🧪 Example Usage

```python
from src.agents.support_agent import ask

# Turkish
ask("Siparişim ne zaman gelir?")

# English
ask("What is your return policy?")

# Force language
ask("Beden tablosu", language="tr")
```

## 📊 How It Works

```
User Query
    ↓
[Detect Language] → TR / EN
    ↓
[Categorize] → Product / Order / Return / ...
    ↓
[Analyze Sentiment] → Positive / Neutral / Negative
    ↓
    ├── Negative → [Escalate to Human]
    └── Other → [Generate Response]
    ↓
Response
```

## 🛠️ Tech Stack

- **LangGraph** - Workflow orchestration
- **LangChain** - LLM integration
- **Groq** - Fast LLM inference (Llama 3.3 70B)
- **Streamlit** - Web UI
- **FastAPI** - REST API

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@MevludeSilaKazan](https://github.com/MevludeSilaKazan)

---

⭐ If you found this project helpful, please give it a star!
