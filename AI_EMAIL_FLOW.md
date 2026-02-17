# AI-Generated Email System 🤖📧

## How It Works

Your email system now uses **AI to generate the entire email content dynamically** when the "Send Email" button is clicked. No more hardcoded templates!

## Flow Diagram

```
User Clicks "Send Email" Button
         ↓
Frontend calls: POST /send-email {call_id, recipient_email}
         ↓
Backend app.py: send_email endpoint
         ↓
1. Fetch call_data from MongoDB (includes transcript, sentiment, AI analysis)
         ↓
2. Pass to EmailService.send_action_notification()
         ↓
3. EmailService calls LLMService.generate_action_email(call_data)
         ↓
4. LLM receives prompt with:
   - Full transcript
   - Call summary  
   - Sentiment analysis
   - Recommended action
   - AI reasoning
   - Priority & risk levels
         ↓
5. AI (Groq Llama 3.1) generates professional HTML email content
         ↓
6. Email sent via Gmail SMTP with AI-generated content
         ↓
Customer receives personalized email about THEIR specific call
```

## Key Components

### 1. **LLMService.generate_action_email()** 
Location: `backend/services/llm_service.py` (lines 208-310)

**What it does:**
- Takes call_data (transcript, sentiment, analysis)
- Builds a prompt asking AI to write a professional email
- Calls Groq API with temperature=0.4 for creative writing
- Returns HTML email content

**Prompt includes:**
```python
- Transcript excerpt (first 500 chars)
- Call summary from previous AI analysis
- Sentiment percentages (Positive/Neutral/Negative)
- Recommended action
- AI reasoning
- Priority and risk levels
```

**AI is instructed to:**
- Write professional business email
- Use emojis and visual formatting
- Include bullet points for key insights
- Explain WHY action is needed
- Show urgency based on priority
- Use inline CSS styling

### 2. **EmailService.send_action_notification()**
Location: `backend/services/email_service.py` (lines 55-75)

**What it does:**
- Receives call_data from API endpoint
- Calls LLM to generate email content
- Falls back to simple template if AI fails
- Sends email via Gmail SMTP

**Fallback system:**
- If AI generation fails → uses simple HTML template
- If LLM service not available → uses basic email with key info

### 3. **Backend Initialization**
Location: `backend/app.py` (line 69)

```python
# LLM service is passed to EmailService
email_service = EmailService(llm_service=llm_service)
```

This connection allows EmailService to call AI for content generation.

## Example AI Prompt

```
You are writing a professional business email to notify a team member about 
an important customer call that needs action.

CALL INFORMATION:
- Transcript: "Hello, I'm calling about canceling my subscription..."
- Call Summary: Customer expressing frustration with billing issues
- Sentiment: Positive 10%, Neutral 30%, Negative 60%
- Recommended Action: Escalate to retention team within 24 hours
- AI Reasoning: High churn risk detected due to billing complaints
- Priority: urgent
- Risk Level: high

TASK: Write a professional, well-formatted HTML email that explains what 
happened, why action is needed, and what to do next...
```

## Benefits vs Hardcoded Template

### ❌ Old Way (Hardcoded Template)
- Fixed HTML structure
- Same layout every time
- Only data values change
- Generic feel

### ✅ New Way (AI-Generated)
- Dynamic content and structure
- Contextual explanations
- Personalized tone based on call severity
- Flexible formatting
- More human-like communication

## Testing the System

1. **Process a call** (upload audio)
2. **Click "Send Email"** on the call detail page
3. **AI generates email** based on that specific call
4. **Check your inbox** - email content will be unique to that call

## Error Handling

- AI generation fails → Uses fallback template with key info
- Network error → Returns error message to frontend
- Invalid call_data → Shows basic call info

## Configuration

**Environment Variables Required:**
```env
GROQ_API_KEY=your_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**LLM Settings:**
- Model: `llama-3.1-8b-instant`
- Temperature: `0.4` (slightly creative for email writing)
- Max Tokens: `1200` (enough for full email)

## Summary

**No hardcoded email content anymore!** 

When you click send email:
1. AI reads the call data
2. AI writes a professional email about THAT specific call
3. Email is sent with unique, contextual content

Every email is different because every call is different! 🎉
