# 🤖 Voice Bot Setup Guide

## Complete Setup Instructions for Customer-Facing AI Voice Assistant

---

## 📋 Prerequisites

1. ✅ Twilio Account with phone number (You have this!)
2. ✅ ElevenLabs API Key (Already in .env)
3. ✅ Groq API Key (Already in .env)
4. ✅ Your existing backend running on port 8000

---

## 🔧 Step 1: Install Dependencies

```bash
cd backend

# Install voice bot dependencies
pip install -r voice_bot_requirements.txt

# Install ngrok (for exposing localhost to Twilio)
# Windows: Download from https://ngrok.com/download
# Or use: choco install ngrok
```

---

## 🔑 Step 2: Update .env File

Add these new environment variables to your `.env` file:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_number_here

# ElevenLabs (already have this)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Backend URL for auto-upload
BACKEND_URL=http://localhost:8000
```

### Where to Find Twilio Credentials:

1. Go to: https://console.twilio.com/
2. **Account SID** and **Auth Token**: Dashboard home page
3. **Phone Number**: Phone Numbers → Manage → Active Numbers

---

## 🚀 Step 3: Run the Servers

### Terminal 1: Run Main Backend (Already Running)

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Run Voice Bot Server

```bash
cd backend
python voice_bot.py
```

You should see:
```
🚀 Starting Voice Bot Server...
📞 Twilio Number: +1234567890
🔄 Backend URL: http://localhost:8000
🌐 Server will be available at: http://localhost:5050
```

### Terminal 3: Expose with Ngrok

```bash
ngrok http 5050
```

You'll see output like:
```
Forwarding    https://abcd1234.ngrok.io -> http://localhost:5050
```

**IMPORTANT:** Copy the `https://abcd1234.ngrok.io` URL - you'll need it!

---

## 📱 Step 4: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
2. Click your phone number
3. Scroll to **Voice Configuration**
4. Under "A CALL COMES IN":
   - Select: **Webhook**
   - Enter: `https://your-ngrok-url.ngrok.io/voice/incoming`
   - Method: **HTTP POST**
5. Scroll to **Recording Status Callback**:
   - Enter: `https://your-ngrok-url.ngrok.io/voice/recording-complete`
6. Click **Save**

Example:
```
Webhook: https://abcd1234.ngrok.io/voice/incoming
Recording: https://abcd1234.ngrok.io/voice/recording-complete
```

---

## 📞 Step 5: Test the System!

### Option A: Call from Your Phone

1. Dial your Twilio number
2. You'll hear: "Hello! Thank you for calling. I'm your AI assistant. How can I help you today?"
3. Speak your question
4. AI will respond with voice
5. Continue conversation
6. Say "goodbye" to hang up

### Option B: Test from Twilio Console

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
2. Click your number
3. Under "Voice & Fax" → Click "Test"
4. Make a test call

---

## 🔍 How It Works

```
┌──────────────────────────────────────────────────────┐
│  Customer Calls Twilio Number                        │
│            ↓                                          │
│  Twilio → Webhook → Your Voice Bot (via ngrok)       │
│            ↓                                          │
│  AI Greets Customer                                   │
│            ↓                                          │
│  Customer Speaks                                      │
│            ↓                                          │
│  Twilio Speech-to-Text (real-time)                   │
│            ↓                                          │
│  Groq LLM Generates Response                          │
│            ↓                                          │
│  AI Responds with Voice (Twilio TTS)                  │
│            ↓                                          │
│  [Loop until customer says goodbye]                   │
│            ↓                                          │
│  Call Recording Saved                                 │
│            ↓                                          │
│  Auto-Upload to Admin Backend                         │
│            ↓                                          │
│  Process with Whisper + AI Analysis                   │
│            ↓                                          │
│  Show in Admin Dashboard                              │
│            ↓                                          │
│  If Urgent → Alert Admin! 🚨                          │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring

### Voice Bot Server Logs
Watch Terminal 2 for:
```
📞 Incoming call: CA123... from +1234567890
🎤 Customer said: I need help with my order
🤖 AI Response: I'd be happy to help you with your order...
✅ Call CA123... completed. Duration: 45s
📼 Recording URL: https://...
⬇️ Downloading recording for call CA123...
💾 Recording saved: uploads/call_CA123_20260220_120345.wav
📤 Uploading to admin backend...
✅ Call uploaded successfully! Call ID: 65d4e8f...
```

### Check Admin Dashboard
1. Go to: http://localhost:3000/dashboard
2. New call will appear automatically
3. If urgent → You'll see high priority indicator

---

## 🎯 Conversation Flow Examples

### Example 1: Product Inquiry
```
Customer: "What are your pricing plans?"
AI: "We offer three pricing plans: Starter at $29/month, 
     Professional at $99/month, and Enterprise with custom 
     pricing. Which one would you like to know more about?"

Customer: "Tell me about the Professional plan"
AI: "The Professional plan at $99/month includes unlimited 
     calls, advanced analytics, CRM integration, and priority 
     support. Would you like me to schedule a demo?"

Customer: "Yes please"
AI: "Great! I'll have our sales team contact you to schedule 
     a convenient time. May I have your email address?"
```

### Example 2: Complaint
```
Customer: "I'm very frustrated with your service"
AI: "I sincerely apologize for your frustration. I'm here to 
     help resolve this. Can you tell me what specific issue 
     you're experiencing?"

Customer: "My calls are not being transcribed correctly"
AI: "I understand how important accurate transcription is. 
     I'm escalating this to our technical team right away. 
     They'll contact you within 2 hours. Can I get your 
     phone number for the callback?"
```

---

## 🚨 Troubleshooting

### "Call Not Connecting"
- ✅ Check ngrok is running: `ngrok http 5050`
- ✅ Verify webhook URL in Twilio console
- ✅ Check voice_bot.py logs for errors

### "No Response from AI"
- ✅ Verify Groq API key in .env
- ✅ Check `GROQ_API_KEY` is set
- ✅ Look for errors in voice bot logs

### "Recording Not Auto-Uploading"
- ✅ Verify main backend running on port 8000
- ✅ Check `BACKEND_URL=http://localhost:8000` in .env
- ✅ Look for "Auto-upload failed" in logs

### "Ngrok URL Expired"
- Ngrok free tier URLs expire after 2 hours
- Restart ngrok: `ngrok http 5050`
- Update webhook URL in Twilio console

---

## 💰 Cost Estimate

### Per Call (Average 3 minutes):
- Twilio Voice: $0.0085/min × 3 = **$0.026**
- Twilio Speech Recognition: $0.02/min × 3 = **$0.06**
- Groq LLM: ~$0.001 (5-10 API calls)
- ElevenLabs: (Using Twilio's built-in TTS - $0)

**Total per call: ~$0.09** (9 cents per call!)

### Monthly (100 calls):
- **$9/month** for 100 customer calls

Much cheaper than human agents! 💰

---

## 🎉 Success Checklist

Once you've completed setup, verify:

- [ ] Voice bot server running on port 5050
- [ ] Ngrok tunnel active and forwarding
- [ ] Twilio webhook configured
- [ ] Test call works end-to-end
- [ ] Recording auto-uploads to admin backend
- [ ] Call appears in dashboard
- [ ] Urgent calls show priority indicator

---

## 🔄 Daily Usage

### Start Everything:
```bash
# Terminal 1: Main Backend
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Voice Bot
cd backend
python voice_bot.py

# Terminal 3: Ngrok
ngrok http 5050

# Terminal 4: Frontend
cd frontend
npm start
```

### Stop Everything:
Press `Ctrl+C` in each terminal

---

## 📈 Next Steps

After basic testing works:

1. ✅ Add more personality to AI responses
2. ✅ Customize greeting for your business
3. ✅ Add multilingual support (Tamil, Hindi, etc.)
4. ✅ Implement real-time alerts to admin dashboard
5. ✅ Add CRM integration (auto-create leads)

---

## 🆘 Need Help?

Check logs in this order:
1. Voice bot terminal (Terminal 2)
2. Main backend terminal (Terminal 1)
3. Ngrok terminal (Terminal 3)
4. Twilio Console → Monitor → Logs

---

**🎉 You're ready to handle customer calls with AI!**

Call your Twilio number and start testing! 📞
