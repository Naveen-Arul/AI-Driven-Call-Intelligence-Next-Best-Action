# Customer Voice Bot - Web Interface

This is the **customer-facing** voice bot interface that allows users to speak with an AI assistant directly in their browser.

## Features

- 🎤 **Browser-Based Voice Chat** - No phone calls needed, uses your microphone and speakers
- 🌐 **Multilingual Support** - Speak in English, Tamil, Hindi, Malayalam, Telugu, and more
- 🤖 **AI-Powered Conversations** - Natural language understanding with contextual responses
- 🔊 **Natural Voice Responses** - High-quality text-to-speech powered by ElevenLabs
- 📝 **Live Transcript** - See the conversation history in real-time
- ⚡ **Real-time Processing** - Fast transcription, AI responses, and voice synthesis

## Technology Stack

- **Frontend**: Pure HTML, CSS, JavaScript (no framework dependencies)
- **Backend**: FastAPI with voice API endpoints
- **Speech-to-Text**: OpenAI Whisper
- **AI Conversation**: Groq Llama 3.1-8b-instant
- **Text-to-Speech**: ElevenLabs multilingual voices

## Quick Start

### 1. Start the Backend API

Make sure the backend server is running:

```powershell
# Navigate to backend folder
cd e:\PROJECT\vocal-jan-29\backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the API server
python app.py
```

The API should be running at `http://localhost:5000`

### 2. Start the Frontend Server

You can use any simple HTTP server to serve the frontend files. Here are a few options:

**Option A: Python HTTP Server (Simplest)**

```powershell
# Navigate to customer-frontend folder
cd e:\PROJECT\vocal-jan-29\customer-frontend

# Start HTTP server on port 8080
python -m http.server 8080
```

Then open: `http://localhost:8080`

**Option B: Node.js HTTP Server**

```powershell
# Install http-server globally (one-time)
npm install -g http-server

# Navigate to customer-frontend folder
cd e:\PROJECT\vocal-jan-29\customer-frontend

# Start server
http-server -p 8080
```

Then open: `http://localhost:8080`

**Option C: VS Code Live Server Extension**

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### 3. Use the Voice Bot

1. **Allow Microphone Access** - Your browser will ask for permission
2. **Select Language** - Choose the language you'll be speaking
3. **Click "Start Talking"** - Begin speaking your query
4. **Click "Stop"** - When you're done speaking
5. **Listen to AI Response** - The AI will respond with natural voice
6. **Repeat** - Continue the conversation

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     Customer Voice Bot Flow                     │
└─────────────────────────────────────────────────────────────────┘

1. User clicks "Start Talking"
   ↓
2. Browser records audio from microphone (WebM format)
   ↓
3. User clicks "Stop" - audio sent to backend
   ↓
4. Backend: Whisper transcribes audio to text
   ↓
5. Backend: Groq LLM generates AI response
   ↓
6. Backend: ElevenLabs converts response to speech (MP3)
   ↓
7. Frontend: Plays audio response
   ↓
8. User hears AI speaking - conversation continues
```

## API Endpoints Used

The frontend communicates with these backend endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/voice/transcribe` | POST | Convert speech to text |
| `/api/voice/chat` | POST | Get AI conversation response |
| `/api/voice/tts` | POST | Convert text to speech |
| `/api/voice/health` | GET | Check service status |

## Supported Languages

- **English** (en) - Default
- **Tamil** (ta) - தமிழ்
- **Hindi** (hi) - हिंदी
- **Malayalam** (ml) - മലയാളം
- **Telugu** (te) - తెలుగు

More languages supported by the backend - select your language in the dropdown!

## Browser Compatibility

✅ **Chrome/Edge** - Fully supported (recommended)
✅ **Firefox** - Fully supported
✅ **Safari** - Supported (may need permissions)
⚠️ **Mobile Browsers** - Works but desktop is recommended

## Demo for Hackathon

This interface is **perfect for hackathon demonstrations** because:

1. ✅ **No Phone Required** - Judges can test instantly on their laptop
2. ✅ **Live Transcript** - See what the AI understands in real-time
3. ✅ **Visual Feedback** - Status indicators show processing steps
4. ✅ **Multilingual Demo** - Switch languages instantly to showcase capability
5. ✅ **Professional UI** - Modern, clean interface with smooth animations

## Troubleshooting

### Microphone Not Working

- Check browser permissions (click the 🔒 icon in address bar)
- Make sure no other app is using the microphone
- Try refreshing the page

### API Connection Error

- Verify backend is running: `http://localhost:5000`
- Check if CORS is enabled in backend (already configured)
- Open browser console (F12) to see error details

### Audio Not Playing

- Check your speakers/volume
- Make sure browser allows audio playback
- Some browsers require user interaction before playing audio

### Transcription Quality Issues

- Speak clearly and at normal pace
- Reduce background noise
- Use a good quality microphone
- Try selecting the correct language before speaking

## Integration with Admin Portal

This customer-facing voice bot is separate from the admin management portal (`frontend/` folder).

**Customer Voice Bot** (this folder):
- Customers interact with AI
- Real-time voice conversations
- Multilingual support

**Admin Portal** (`frontend/` folder):
- Admins view call history
- Approve/reject actions
- Analytics and insights

Both systems work together to provide a complete solution!

## Development

### File Structure

```
customer-frontend/
├── index.html          # Main HTML page
├── style.css           # Styling and animations
├── voice-chat.js       # Voice chat logic
└── README.md           # This file
```

### Customization

**Change Voice or Language:**
Edit `voice-chat.js` and modify the TTS request parameters.

**Update UI Colors:**
Edit `style.css` and change the gradient colors or theme.

**Add More Features:**
- Show sentiment in real-time
- Add conversation export
- Implement voice activity detection
- Add more language options

## Cost Estimate

For 100 customer conversations (5 min average each):

- **Whisper (OpenAI)**: Free (running locally)
- **Groq API**: Free tier (generous limits)
- **ElevenLabs**: ~$1-2 for TTS (pay-as-you-go)
- **Total**: ~$1-2 per 100 conversations

Much cheaper than phone-based solutions! 📉

## Support

For issues or questions:
1. Check browser console (F12) for errors
2. Verify backend logs
3. Test API endpoints directly with curl/Postman

Happy chatting! 🎉
