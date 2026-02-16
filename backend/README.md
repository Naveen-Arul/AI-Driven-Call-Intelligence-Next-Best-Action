# AI Call Intelligence Platform - Backend

FastAPI backend for transcription and call intelligence.

## 🚀 Platform Overview

Production-grade AI Call Intelligence Platform with 4-layer architecture:

- **Step 1**: Transcription Service (OpenAI Whisper STT)
- **Step 2**: NLP Analysis Layer (Sentiment + Intent + Entities)
- **Step 3**: LLM Intelligence (Groq Llama 3.1 contextual reasoning)
- **Step 4**: Business Rules Engine (Governance + validation layer)

## 📁 Structure

```
backend/
├── app.py                          # FastAPI application (v4.0.0)
├── services/
│   ├── transcription_service.py    # Layer 1: Whisper STT
│   ├── nlp_service.py             # Layer 2: NLP Analysis
│   ├── llm_service.py             # Layer 3: LLM Intelligence
│   ├── action_engine.py           # Layer 4: Business Rules
│   └── __init__.py                # Service exports
├── uploads/                        # Audio file storage
├── requirements.txt                # Python dependencies
├── .env                           # API keys (not in git)
├── test_*.py                      # Test suites
└── README.md
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

`.env` file contains:
- `ELEVENLABS_API_KEY`
- `GROQ_API_KEY`

### 3. Run Server

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload
```

Server runs on: `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```1️⃣ Transcribe Audio
```
POST /transcribe
Content-Type: multipart/form-data
Body: file: <audio_file.wav>
```

### 2️⃣ Analyze Transcript
```
POST /analyze
Content-Type: application/json
Body: { "transcript": "..." }
```

### 3️⃣ LLM Intelligence
```
POST /intelligence
Content-Type: application/json
Body: { "transcript": "...", "nlp_insights": {...} }
```

### 4️⃣ Final Decision (Business Rules)
```
POST /decision
Content-Type: application/json
Body: { "nlp_insights": {...}, "llm_output": {...}       "text": "Individual segment text"
    }
  ],
  "processing_time": 4.12,
  "filename": "call_recording.wav"
}
```

## 🧪 Testing

### Using cURL

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@your_audio.wav"
```

### Using Python

```python
import requests

url = "http://localhost:8000/transcribe"
files = {"file": open("audio.wav", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using Postman

1. POST → `http://localhost:8000/transcribe`
2. Body → form-data
3. Key: `file` (type: File)
4. Select audio file
5. Send
### Layer 1: Transcription
- ✅ OpenAI Whisper (base model)
- ✅ Timestamped segments
- ✅ Multi-format support (WAV, MP3, M4A, FLAC, OGG)

### Layer 2: NLP Analysis
- ✅ VADER sentiment analysis
- ✅ 10 keyword categories (demo, pricing, complaint, churn, etc.)
- ✅ Entity extraction (Money, Dates)
- ✅ Intent classification (9 intent types)

### Layer 3: LLM Intelligence
- ✅ Groq Llama 3.1-8b-instant
- ✅ Structured JSON output
- ✅ Priority scoring (0-100)
- ✅ Risk/opportunity detection
- ✅ Action recommendations

### Layer 4: Business Rules
- ✅ 6 production governance rules
- ✅ Confidence scoring (sentiment + keywords + entities)
- ✅ Escalation logic
- ✅ Revenue opportunity detection
- ✅ Churn risk mitigation
- ✅ Error handling
- ✅ CORS enabled
- ✅ Environment variable management

## 📊 Supported Audio Formats

- WAV
- MP3
- M4A
- FLACPlatform Status

- ✅ Step 1: Transcription Service (Whisper STT)
- ✅ Step 2: NLP Analysis Layer (VADER + keyword detection + entity extraction)
- ✅ Step 3: LLM Intelligence (Groq Llama 3.1-8b-instant)
- ✅ Step 4: Business Rules Engine (6 production rules + confidence scoring)
- ⬜ Step 5: CRM Integration Layer
- ⬜ Step 6: Analytics & KPI Dashboardence (Groq + structured outputs)
- [ ] Step 4: Next-Best-Action Engine
- [ ] Step 5: CRM Integration
- [ ] Step 6: Dashboard UI

## 🏗️ Architecture Principles

1. **Separation of Concerns** - Business logic in services/
2. **Single Responsibility** - Each service does one thing well
3. **Clean Code** - Production-ready, documented, typed
4. **Scalability** - Async by default with FastAPI
