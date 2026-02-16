# AI Call Intelligence Platform - Backend

FastAPI backend for transcription and call intelligence.

## 🚀 Step 1: Transcription Service

Clean, modular Speech-to-Text using OpenAI Whisper.

## 📁 Structure

```
backend/
├── app.py                          # FastAPI application
├── services/
│   └── transcription_service.py    # Whisper STT service
├── uploads/                        # Audio file storage
├── requirements.txt                # Python dependencies
├── .env                           # API keys (not in git)
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
```
GET /
GET /health
```

### Transcribe Audio
```
POST /transcribe
Content-Type: multipart/form-data

Body:
  file: <audio_file.wav>
```

**Response:**
```json
{
  "transcript": "Full transcript text",
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 3.4,
      "text": "Individual segment text"
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

## 🎯 Features

- ✅ FastAPI (production-ready async framework)
- ✅ OpenAI Whisper transcription
- ✅ Timestamped segments
- ✅ Clean service architecture
- ✅ Error handling
- ✅ CORS enabled
- ✅ Environment variable management

## 📊 Supported Audio Formats

- WAV
- MP3
- M4A
- FLAC
- OGG

## 🔄 Next Steps

- [ ] Step 2: NLP Analysis Layer (sentiment, intent, entities)
- [ ] Step 3: LLM Intelligence (Groq + structured outputs)
- [ ] Step 4: Next-Best-Action Engine
- [ ] Step 5: CRM Integration
- [ ] Step 6: Dashboard UI

## 🏗️ Architecture Principles

1. **Separation of Concerns** - Business logic in services/
2. **Single Responsibility** - Each service does one thing well
3. **Clean Code** - Production-ready, documented, typed
4. **Scalability** - Async by default with FastAPI
