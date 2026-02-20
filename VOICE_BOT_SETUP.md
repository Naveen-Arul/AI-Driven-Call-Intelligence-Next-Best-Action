# Voice Bot Setup Guide

## 🎯 Overview

This guide will help you set up the AI Voice Bot that allows customers to call and interact with an AI assistant. All conversations are recorded and automatically processed through your existing admin system.

---

## 📋 Prerequisites

1. ✅ Twilio Account with phone number (you have this)
2. ✅ ElevenLabs API Key (already in `.env`)
3. ✅ Groq API Key (already configured)
4. ✅ Ngrok account (free) for tunneling

---

## 🔧 Step 1: Install Required Packages

```bash
cd backend
pip install twilio elevenlabs
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🔑 Step 2: Update .env File

Add these Twilio variables to your `backend/.env` file:

```env
# Existing variables...
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# NEW: Add these Twilio variables
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# NEW: Add base URL (will be your ngrok URL)
BASE_URL=https://your-ngrok-url.ngrok.io
```

**Where to find Twilio credentials:**
1. Go to https://console.twilio.com/
2. Copy **Account SID** and **Auth Token** from dashboard
3. Find your phone number under Phone Numbers → Manage → Active Numbers

---

## 🌐 Step 3: Install and Setup Ngrok

Ngrok creates a public URL for your local server so Twilio can reach it.

### Install Ngrok:

**Windows:**
```bash
# Download from https://ngrok.com/download
# Or use chocolatey:
choco install ngrok
```

**Alternative - Use Ngrok CLI:**
```bash
# Sign up at https://ngrok.com
# Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken

# Authenticate
ngrok authtoken YOUR_NGROK_AUTHTOKEN
```

---

## 🚀 Step 4: Start Your Backend Server

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Server should start at `http://localhost:8000`

---

## 🔗 Step 5: Start Ngrok Tunnel

Open a **NEW terminal** and run:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

**Copy this URL:** `https://abc123.ngrok.io`

---

## ⚙️ Step 6: Configure Twilio Webhooks

### Update .env with Ngrok URL:

```env
BASE_URL=https://abc123.ngrok.io
```

Restart your backend server to load the new BASE_URL.

### Configure Twilio Phone Number:

1. Go to https://console.twilio.com/
2. Click **Phone Numbers** → **Manage** → **Active Numbers**
3. Click on your phone number
4. Scroll to **Voice Configuration**
5. Set:
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://your-ngrok-url.ngrok.io/voice/incoming`
   - **HTTP**: POST
6. Scroll to **Call Status Changes**
7. Set:
   - **CALL STATUS CHANGES**: `https://your-ngrok-url.ngrok.io/voice/status`
   - **HTTP**: POST
   - Check: `completed`
8. Scroll down and click **Save Configuration**

---

## 📞 Step 7: Test the Voice Bot

### Make a Test Call:

1. Call your Twilio phone number from your mobile
2. You should hear: "Hello! Welcome to our customer service. How can I help you today?"
3. Speak your question or request
4. AI will respond using ElevenLabs voice
5. Continue the conversation
6. When you hang up, the call will be automatically processed

### Check Admin Dashboard:

1. Open your admin frontend: `http://localhost:3000`
2. Go to Dashboard or Calls List
3. You should see the voice call appear with full transcript and analysis
4. If the call was urgent/high-risk, you'll see an alert

---

## 🔍 Step 8: View Voice Bot Endpoints

Your voice bot exposes these endpoints:

### Customer-Facing (Twilio Webhooks):
- `POST /voice/incoming` - Handles incoming calls
- `POST /voice/process` - Processes customer speech
- `POST /voice/status` - Handles call status updates
- `POST /voice/recording` - Saves call recordings

### Admin Monitoring:
- `GET /voice/active-calls` - List active calls in progress
- `GET /voice/call/{call_sid}` - Get specific call details

---

## 📊 Step 9: Monitor Logs

Watch your backend terminal for real-time logs:

```
✅ Voice Bot initialized
📞 Call ACxxx: Customer said: 'I need help with my order'
🤖 AI Response: 'I'd be happy to help with your order...'
✅ Voice call ACxxx saved to database
```

---

## 🧪 Testing Checklist

- [ ] Backend server running (`uvicorn app:app --port 8000 --reload`)
- [ ] Ngrok tunnel active (`ngrok http 8000`)
- [ ] Twilio webhooks configured with ngrok URL
- [ ] .env file has all required keys
- [ ] Can call Twilio number
- [ ] AI responds with voice
- [ ] Call appears in admin dashboard after hangup

---

## 🐛 Troubleshooting

### Issue: "Call drops immediately"
**Fix:** Check Twilio webhook URL is correct and ngrok is running

### Issue: "AI doesn't respond"
**Fix:** Check GROQ_API_KEY in .env, check backend logs for errors

### Issue: "No voice response"
**Fix:** Verify ELEVENLABS_API_KEY in .env

### Issue: "Recording not appearing in admin"
**Fix:** Check backend logs for processing errors, verify MongoDB is running

### Issue: "Ngrok URL changed"
**Fix:** Ngrok free tier gets new URL each restart. Update BASE_URL in .env and restart backend. Update Twilio webhooks with new URL.

**Pro Tip:** Upgrade to ngrok paid ($8/month) to get a permanent URL

---

## 🎨 Customization

### Change AI Voice:

Edit `voice_bot.py`:
```python
response.say(
    text,
    voice="Polly.Aditi",  # Indian English female
    # Other options:
    # "Polly.Raveena" - Indian English female
    # "Polly.Joanna" - US English female
    # "Polly.Matthew" - US English male
    language="en-IN"
)
```

### Change Greeting Message:

Edit `voice_bot.handle_incoming_call()`:
```python
response.say(
    "Welcome to [Your Company Name]. How may I assist you?",
    voice="Polly.Aditi",
    language="en-IN"
)
```

---

## 💰 Cost Estimates

### Twilio:
- Phone number: $1/month
- Incoming calls: $0.0085/minute
- Recordings: $0.0025/minute

### ElevenLabs:
- Free: 10,000 characters/month
- Pro: $5/month for 30,000 characters

### Groq:
- Free tier: Very generous limits
- Essentially free for testing

### Example: 100 calls/month (avg 3 min each)
- Twilio: ~$3.50
- ElevenLabs: Free tier sufficient
- Total: **~$4.50/month**

---

## 🚀 Production Deployment

For production, instead of ngrok:

1. Deploy backend to cloud (AWS, Azure, GCP, Heroku)
2. Get public domain (api.yourcompany.com)
3. Update Twilio webhooks with production URL
4. Set up proper logging and monitoring
5. Use Redis instead of in-memory conversation store

---

## 📞 Support

If you encounter issues:
1. Check backend logs in terminal
2. Check Twilio logs: https://console.twilio.com/monitor/logs/calls
3. Verify all API keys are correct in .env
4. Ensure ngrok tunnel is active

---

## ✅ Next Steps

After voice bot is working:
1. Add multilingual support (Tamil, Hindi, Malayalam)
2. Implement call transfer to human agents
3. Add proactive alerts for urgent calls
4. Build live call monitoring dashboard
5. Integrate CRM for automatic ticket creation

---

**You're all set!** Call your Twilio number and test the voice bot! 🎉
