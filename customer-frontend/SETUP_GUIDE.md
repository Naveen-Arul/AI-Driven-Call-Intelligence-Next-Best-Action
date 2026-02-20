# 🎯 Customer Voice Bot - Complete Setup Guide

This guide will get your web-based voice bot running in **5 minutes**.

## Overview

You now have **TWO separate frontends**:

1. **Customer Voice Bot** (`customer-frontend/`) - NEW ✨
   - Customer-facing voice chat interface
   - Browser-based (no phone needed)
   - Real-time voice conversations with AI

2. **Admin Portal** (`frontend/`) - EXISTING ✅
   - Admin dashboard
   - Call management and approval workflows
   - Analytics and insights

## Prerequisites

✅ Python 3.8+ installed
✅ Backend dependencies installed: `pip install -r backend/requirements.txt`
✅ Environment variables configured in `.env`

## Quick Start (3 Steps)

### Step 1: Verify Environment Variables

Make sure these are set in `e:\PROJECT\vocal-jan-29\.env`:

```env
# Required for Voice Bot
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional (for phone-based Twilio features)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### Step 2: Start Backend API

```powershell
cd e:\PROJECT\vocal-jan-29\backend
python app.py
```

Wait for: `✅ All services initialized successfully`

Backend runs at: `http://localhost:5000`

### Step 3: Start Customer Frontend

**Option A: Double-click the launcher (Easiest!)**

```
customer-frontend\start.bat
```

This will:
- Start backend API (if not running)
- Start frontend server on port 8080
- Automatically open your browser

**Option B: Manual start**

```powershell
cd e:\PROJECT\vocal-jan-29\customer-frontend
python -m http.server 8080
```

Then open: `http://localhost:8080`

## Testing the Voice Bot

1. **Open Browser**: Go to `http://localhost:8080`

2. **Allow Microphone**: Click "Allow" when browser asks for permission

3. **Select Language**: Choose your preferred language from dropdown

4. **Start Talking**: 
   - Click the "Start Talking" button
   - Speak your query (e.g., "What are your business hours?")
   - Click "Stop" when done

5. **Listen to AI**: 
   - Watch the status indicators (Transcribing → Thinking → Speaking)
   - AI will respond with natural voice
   - See transcript update in real-time

6. **Continue Conversation**: 
   - Click "Start Talking" again
   - AI remembers context from previous messages

## Test Scenarios

Try these example conversations:

### English Test
```
You: "Hello, I need help with my account"
AI: "I'd be happy to help you with your account. What specific issue are you experiencing?"
You: "I forgot my password"
AI: "I understand. Let me guide you through the password reset process..."
```

### Tamil Test
```
You: "வணக்கம், உங்கள் வணிக நேரங்கள் என்ன?"
AI: "வணக்கம்! எங்கள் வணிக நேரங்கள் காலை 9 மணி முதல் மாலை 6 மணி வரை..."
```

### Hindi Test
```
You: "नमस्ते, मुझे सहायता चाहिए"
AI: "नमस्ते! मैं आपकी सहायता करने के लिए यहाँ हूँ..."
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Complete System Flow                     │
└─────────────────────────────────────────────────────────────┘

CUSTOMER SIDE (New - Web Voice Bot):
┌──────────────────┐
│  Browser Client  │ ← User speaks into microphone
│  (Port 8080)     │
└────────┬─────────┘
         │ POST /api/voice/transcribe
         │ POST /api/voice/chat
         │ POST /api/voice/tts
         ↓
┌──────────────────┐
│   Backend API    │ ← Whisper + Groq + ElevenLabs
│  (Port 5000)     │
└────────┬─────────┘
         │ Real-time voice processing
         │ Conversation management
         ↓
    (Optional: Auto-save to database)


ADMIN SIDE (Existing - React Dashboard):
┌──────────────────┐
│  React Admin UI  │ ← Admins review calls
│  (Port 3000)     │
└────────┬─────────┘
         │ GET /calls
         │ POST /approve-action
         │ POST /reject-action
         ↓
┌──────────────────┐
│   Backend API    │ ← Same backend as customer side
│  (Port 5000)     │
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│   MongoDB        │ ← Persistent storage
│                  │
└──────────────────┘
```

## API Endpoints

### Voice Bot Endpoints (NEW)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/voice/transcribe` | POST | Speech to text (Whisper) |
| `/api/voice/chat` | POST | Get AI response (Groq) |
| `/api/voice/tts` | POST | Text to speech (ElevenLabs) |
| `/api/voice/end-session` | POST | End conversation session |
| `/api/voice/health` | GET | Check service health |

### Admin Endpoints (EXISTING)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process-call` | POST | Process recorded call |
| `/calls` | GET | List all calls |
| `/calls/{call_id}` | GET | Get call details |
| `/approve-action/{call_id}` | POST | Approve suggested action |
| `/reject-action/{call_id}` | POST | Reject suggested action |

## Troubleshooting

### 1. Backend won't start

**Error**: `ModuleNotFoundError: No module named 'elevenlabs'`

**Solution**:
```powershell
cd backend
pip install -r requirements.txt
```

### 2. Microphone not working

**Error**: Browser shows "Microphone access denied"

**Solution**:
- Click the 🔒 icon in address bar
- Allow microphone permission
- Refresh the page
- Try again

### 3. API connection error

**Error**: "Could not connect to API"

**Solution**:
- Make sure backend is running: `http://localhost:5000`
- Check backend terminal for errors
- Verify CORS is enabled (already configured)
- Open browser console (F12) to see detailed error

### 4. No AI response

**Error**: "AI response failed"

**Solution**:
- Check `.env` file has `GROQ_API_KEY`
- Verify Groq API key is valid
- Check backend logs for LLM errors
- Try speaking again

### 5. No audio playing

**Error**: Transcript shows AI response but no sound

**Solution**:
- Check `.env` file has `ELEVENLABS_API_KEY`
- Verify ElevenLabs API key is valid
- Check speaker volume
- Make sure browser allows audio playback
- Try refreshing the page

### 6. Poor transcription quality

**Issue**: Whisper transcribes incorrectly

**Solution**:
- Speak clearly and at normal pace
- Reduce background noise
- Select correct language before speaking
- Use a good quality microphone
- Speak louder or move closer to mic

## Testing Checklist

Before demo/hackathon:

- [ ] Backend starts without errors
- [ ] Frontend loads at `http://localhost:8080`
- [ ] Microphone permission granted
- [ ] Can record audio (click Start → Stop)
- [ ] Transcription works (text appears in transcript)
- [ ] AI response generates (shows in transcript)
- [ ] Audio plays (hear AI speaking)
- [ ] Multiple conversations work (click Start again)
- [ ] Language switching works (change dropdown)
- [ ] Admin portal still works at `http://localhost:3000`

## Performance Tips

### Speed Optimization

1. **Use base Whisper model** for real-time (already configured in voice_api.py)
2. **Keep conversations short** for faster responses
3. **Use Groq LLM** (already configured - 500ms response time)
4. **Stream TTS audio** (already implemented)

### Quality Optimization

1. **Good microphone** - USB mic recommended
2. **Quiet environment** - Reduce background noise
3. **Clear speech** - Speak naturally, not too fast
4. **Correct language selection** - Select before speaking

## Hackathon Demo Script

Perfect 3-minute demo:

**Minute 1: Introduction**
- "This is our AI-powered call intelligence system"
- "It has TWO interfaces: customer-facing voice bot + admin portal"
- Open customer voice bot: `http://localhost:8080`

**Minute 2: Voice Bot Demo**
- Click "Start Talking"
- Ask: "What are your business hours?"
- Show live transcription
- AI responds with natural voice
- Show conversation history

**Minute 3: Multilingual Demo**
- Switch to Tamil in dropdown
- Ask in Tamil: "உங்கள் சேவைகள் என்ன?"
- AI responds in Tamil
- Open admin portal: Show call appears in dashboard
- Highlight: Real-time, multilingual, AI-powered

**Key Points to Emphasize:**
✨ No phone needed - works in browser
✨ Supports 99+ languages
✨ Real-time AI conversation
✨ Natural voice synthesis
✨ Auto-integrates with admin system
✨ Cost-effective (~$0.02 per conversation)

## Next Steps

After basic testing works:

1. **Install Dependencies**:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Get Groq API key: https://console.groq.com
   - Get ElevenLabs API key: https://elevenlabs.io
   - Add to `.env` file

3. **Test Voice Bot**:
   - Run `customer-frontend\start.bat`
   - Test English conversation
   - Test Tamil/Hindi/Malayalam

4. **Test Admin Portal**:
   - Start React frontend: `cd frontend && npm start`
   - Verify call history shows
   - Test approval workflow

5. **Prepare Demo**:
   - Practice demo script
   - Prepare 2-3 test scenarios
   - Test on presentation laptop

## Support

**Need Help?**

1. Check logs:
   - Backend terminal: Shows API errors
   - Browser console (F12): Shows JavaScript errors

2. Verify services:
   - Backend health: `http://localhost:5000`
   - Voice API health: `http://localhost:5000/api/voice/health`

3. Test individual components:
   - Upload audio file to `/api/voice/transcribe`
   - Send text to `/api/voice/chat`
   - Generate speech with `/api/voice/tts`

## Success! 🎉

If you see:
- ✅ Browser loads voice chat UI
- ✅ Microphone records your voice
- ✅ Transcript shows your message
- ✅ AI responds with text
- ✅ You hear AI speaking

**You're ready for the hackathon!** 🚀

---

## File Overview

```
customer-frontend/
├── index.html          # Voice chat UI
├── style.css           # Styling
├── voice-chat.js       # Frontend logic
├── start.bat           # Quick launcher
├── README.md           # User guide
└── SETUP_GUIDE.md      # This file

backend/
├── app.py              # Main API (updated with voice routes)
├── voice_api.py        # Voice bot endpoints (NEW)
├── services/
│   ├── tts_service.py           # ElevenLabs TTS (NEW)
│   ├── conversation_service.py  # AI conversations (NEW)
│   └── ... (existing services)
└── requirements.txt    # Updated with twilio, elevenlabs

frontend/              # Admin portal (existing)
├── src/
└── package.json
```

---

**Questions? Issues? Check the troubleshooting section above!**

Good luck with your hackathon! 🏆
