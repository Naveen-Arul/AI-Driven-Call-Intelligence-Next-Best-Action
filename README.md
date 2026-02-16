# 🧠 AI-Driven Call Intelligence & Next-Best-Action Platform

**Transform passive call recordings into structured intelligence and automated next actions.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Overview

This platform converts sales and support call recordings into:
- **Structured transcripts** with timestamps
- **Sentiment analysis** and keyword detection
- **Intent classification** and entity extraction
- **AI-powered action recommendations** with priority scoring
- **Risk and opportunity assessment**

Built with production-grade architecture using **FastAPI**, **OpenAI Whisper**, **VADER Sentiment**, and **Groq LLM**.

---

## 🏗️ Architecture

### 3-Layer Intelligence Stack

```
┌─────────────────────────────────────────────────────────┐
│                   Audio Recording                        │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  Layer 1: STT       │
          │  Whisper Model      │
          │  (Speech-to-Text)   │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────────────┐
          │  Layer 2: NLP Analysis      │
          │  • Sentiment (VADER)        │
          │  • Keywords (10 categories) │
          │  • Entities (Regex)         │
          │  • Intent (9 types)         │
          └──────────┬──────────────────┘
                     │
          ┌──────────▼────────────────────┐
          │  Layer 3: LLM Intelligence    │
          │  Groq Llama 3.1               │
          │  • Contextual reasoning       │
          │  • Action recommendations     │
          │  • Priority scoring (0-100)   │
          │  • Risk/opportunity assessment│
          └──────────┬────────────────────┘
                     │
          ┌──────────▼──────────────┐
          │  Structured JSON Output  │
          └──────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip package manager
- API Keys:
  - Groq API Key ([Get it here](https://console.groq.com/))
  - ElevenLabs API Key (Optional, for future features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Naveen-Arul/AI-Driven-Call-Intelligence-Next-Best-Action.git
cd AI-Driven-Call-Intelligence-Next-Best-Action
```

2. **Set up environment variables**
```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at `http://localhost:8000`

---

## 📡 API Endpoints

### 1. Health Check
```http
GET /
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "transcription_service": "ready",
  "nlp_service": "ready",
  "llm_service": "ready"
}
```

---

### 2. Transcribe Audio
```http
POST /transcribe
Content-Type: multipart/form-data
```

**Request:**
- `file`: Audio file (wav, mp3, m4a, flac, ogg)

**Response:**
```json
{
  "transcript": "Full transcript text",
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 3.4,
      "text": "Individual segment"
    }
  ],
  "language": "en",
  "processing_time": 4.83
}
```

---

### 3. Analyze Transcript (NLP)
```http
POST /analyze
Content-Type: application/json
```

**Request:**
```json
{
  "transcript": "Your call transcript here..."
}
```

**Response:**
```json
{
  "sentiment": {
    "compound": 0.89,
    "positive": 0.35,
    "neutral": 0.60,
    "negative": 0.05,
    "sentiment_label": "positive"
  },
  "intent": "demo_request",
  "keywords": {
    "demo": ["demo"],
    "interest": ["interested"],
    "timeline": ["next week"]
  },
  "entities": [
    {"text": "next week", "label": "DATE"}
  ]
}
```

---

### 4. Generate Intelligence (LLM)
```http
POST /intelligence
Content-Type: application/json
```

**Request:**
```json
{
  "transcript": "Call transcript...",
  "nlp_analysis": {
    "sentiment": {...},
    "intent": "demo_request",
    "keywords": {...},
    "entities": [...]
  }
}
```

**Response:**
```json
{
  "call_summary_short": "Customer expressed interest in demo",
  "call_summary_detailed": "Detailed summary...",
  "risk_level": "low",
  "opportunity_level": "high",
  "recommended_action": "Schedule demo for next Tuesday",
  "priority_score": 95,
  "reasoning": "High opportunity due to positive sentiment and demo request"
}
```

---

## 🧪 Testing

### Test Transcription Service
```bash
cd backend
python test_api.py
```

### Test NLP Analysis
```bash
python test_nlp.py
```

### Test LLM Intelligence
```bash
python test_llm.py
```

---

## 📊 Features

### ✅ Completed (Steps 1-3)

- **Speech-to-Text**: OpenAI Whisper with multi-speaker detection
- **Sentiment Analysis**: VADER with compound scoring
- **Keyword Detection**: 10 business categories (demo, pricing, complaint, etc.)
- **Entity Extraction**: Regex-based (Money, Dates, Organizations)
- **Intent Classification**: 9 intent types with rule-based logic
- **LLM Intelligence**: Groq Llama 3.1 for contextual reasoning
- **Priority Scoring**: Automated 0-100 urgency calculation
- **Risk Assessment**: High/Medium/Low churn and complaint detection
- **Opportunity Detection**: Lead qualification and upsell signals

### 🔜 Coming Soon (Steps 4-6)

- **Business Rules Engine**: Action validation and override logic
- **CRM Integration**: Salesforce, HubSpot, Zoho connectors
- **Dashboard UI**: Real-time call monitoring and analytics
- **Email Automation**: Triggered follow-ups based on actions
- **Analytics & Reporting**: Conversion tracking, objection patterns
- **Multi-language Support**: Extended language models

---

## 📁 Project Structure

```
AI-Driven-Call-Intelligence-Next-Best-Action/
├── backend/
│   ├── services/
│   │   ├── transcription_service.py    # Whisper STT
│   │   ├── nlp_service.py              # Sentiment, keywords, entities
│   │   └── llm_service.py              # Groq LLM intelligence
│   ├── app.py                          # FastAPI application
│   ├── requirements.txt                # Python dependencies
│   ├── .env                            # API keys (not in git)
│   ├── test_api.py                     # Transcription tests
│   ├── test_nlp.py                     # NLP analysis tests
│   └── test_llm.py                     # LLM intelligence tests
├── 01_problem_statement.md             # Business problem analysis
├── 02_product_requirements_document.md # PRD specification
├── 03_solution_architecture.md         # Technical architecture
├── .gitignore
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here  # Optional
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ |
| **Speech-to-Text** | OpenAI Whisper (base model) |
| **Sentiment** | VADER Sentiment Analyzer |
| **LLM** | Groq (Llama 3.1-8b-instant) |
| **Server** | Uvicorn (ASGI) |
| **Python** | 3.12+ |

---

## 📈 Use Cases

### Sales Teams
- Automatic demo scheduling from positive calls
- Objection pattern detection
- Competitor mention tracking
- Qualified lead identification

### Support Teams
- Churn risk detection (cancel keywords + negative sentiment)
- Escalation triggers for frustrated customers
- Issue categorization
- First-call resolution tracking

### Operations
- Call quality monitoring
- Agent performance insights
- Compliance keyword detection
- SLA breach prevention

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Naveen Arul**

- GitHub: [@Naveen-Arul](https://github.com/Naveen-Arul)
- Repository: [AI-Driven-Call-Intelligence-Next-Best-Action](https://github.com/Naveen-Arul/AI-Driven-Call-Intelligence-Next-Best-Action)

---

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Groq for ultra-fast LLM inference
- FastAPI for modern Python web framework
- VADER for sentiment analysis

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for transforming call data into actionable intelligence**
