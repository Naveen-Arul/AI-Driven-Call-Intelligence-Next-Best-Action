# Quick Start - Voice Bot

## 🚀 Fast Setup (5 Minutes)

### Step 1: Install Dependencies (1 min)
```bash
cd backend
pip install twilio elevenlabs
```

### Step 2: Add Twilio Credentials to .env (1 min)
Open `backend/.env` and add:
```env
TWI LIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
BASE_URL=will-add-after-ngrok
```

Get these from: https://console.twilio.com/

### Step 3: Start Backend (30 sec)
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Start Ngrok in New Terminal (30 sec)
```bash
ngrok http 8000
```

Copy the URL: `https://abc123.ngrok.io`

### Step 5: Update .env with Ngrok URL (30 sec)
```env
BASE_URL=https://abc123.ngrok.io
```

Restart backend (Ctrl+C then run uvicorn command again)

### Step 6: Configure Twilio (2 min)
1. Go to: https://console.twilio.com/
2. Click: Phone Numbers → Manage → Active Numbers
3. Click your phone number
4. Under "Voice Configuration":
   - A CALL COMES IN: `https://your-ngrok-url.ngrok.io/voice/incoming` (POST)
5. Click **Save**

### Step 7: Test! (30 sec)
Call your Twilio phone number! 📞

---

## 🎯 What Should Happen:

1. You call the Twilio number
2. AI greets you: "Hello! Welcome to our customer service..."
3. You speak: "I have a question about pricing"
4. AI responds with helpful information
5. Conversation continues until you hang up
6. Call automatically appears in your admin dashboard!

---

## 🐛 Quick Troubleshooting:

**Call drops immediately?**
- Check ngrok is running
- Verify Twilio webhook URL is correct

**No AI response?**
- Check GROQ_API_KEY in .env
- Check backend terminal for errors

**Can't hear AI voice?**
- Verify ELEVENLABS_API_KEY in .env

---

## 📊 Monitoring:

Watch your backend terminal for logs:
```
✅ Voice Bot initialized
📞 Call ACxxx: Customer said: 'I need help'
🤖 AI Response: 'I'd be happy to help...'
```

---

## 📱 Test Script:

**Call your number and say:**

1. "I want to know about your pricing" → Should get info
2. "I'm having a technical issue" → Should offer help
3. "I want to speak to a manager" → Should escalate
4. "I want to cancel" → Should show empathy and escalate

---

## ✅ You're Done!

Your voice bot is live! Every call will:
- Be handled by AI
- Get recorded
- Auto-upload to admin system
- Show in dashboard with full analysis

See VOICE_BOT_SETUP.md for detailed documentation.
