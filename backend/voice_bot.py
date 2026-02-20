"""
Voice Bot Server - Customer-Facing AI Voice Assistant
Handles incoming calls, conversations, and auto-uploads recordings to admin system
"""

from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
import logging
import tempfile
import requests
from datetime import datetime
from dotenv import load_dotenv
from services.transcription_service import TranscriptionService
from services.llm_service import LLMService
from services.elevenlabs_service import tts_service
import base64

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for voice bot
voice_app = FastAPI(title="Voice Bot API", version="1.0")

# Initialize services
transcription_service = TranscriptionService(model_size="medium")  # Use medium for better accuracy
llm_service = LLMService()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Backend URL for auto-uploading recordings
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Store conversation context (in production use Redis)
conversation_store = {}


class VoiceBot:
    """
    AI Voice Bot for customer support and inquiries
    """
    
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None
        self.greeting = "Hello! Thank you for calling. I'm your AI assistant. How can I help you today?"
        self.system_prompt = """You are a helpful and friendly customer service AI assistant. 
        
Your personality:
- Warm, professional, and concise
- Patient and understanding
- Solution-oriented
- Never say you're an AI unless asked

Your capabilities:
- Answer product questions
- Help with pricing inquiries
- Schedule demos and callbacks
- Address complaints empathetically
- Provide company information
- Escalate urgent issues

Guidelines:
- Keep responses under 50 words
- Be conversational, not robotic
- Ask clarifying questions when needed
- Offer to transfer to human agent for complex issues
- End with a question to continue conversation

If customer wants to hang up, say: "Thank you for calling! Have a great day!"
"""
    
    def get_conversation_context(self, call_sid: str):
        """Get conversation history for this call"""
        if call_sid not in conversation_store:
            conversation_store[call_sid] = {
                "history": [],
                "start_time": datetime.now().isoformat(),
                "language": "en",
                "customer_info": {}
            }
        return conversation_store[call_sid]
    
    def add_to_conversation(self, call_sid: str, role: str, message: str):
        """Add message to conversation history"""
        context = self.get_conversation_context(call_sid)
        context["history"].append({
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_ai_response(self, call_sid: str, customer_query: str) -> str:
        """
        Generate AI response based on customer query and conversation history
        """
        try:
            context = self.get_conversation_context(call_sid)
            
            # Build conversation history for LLM
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history
            for msg in context["history"][-4:]:  # Last 4 exchanges for context
                messages.append({
                    "role": "user" if msg["role"] == "customer" else "assistant",
                    "content": msg["content"]
                })
            
            # Add current query
            messages.append({
                "role": "user",
                "content": customer_query
            })
            
            # Get LLM response
            response = llm_service.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=150  # Keep responses concise
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            logger.info(f"🤖 AI Response: {ai_response}")
            
            # Add to conversation history
            self.add_to_conversation(call_sid, "customer", customer_query)
            self.add_to_conversation(call_sid, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {str(e)}")
            return "I apologize, I'm having technical difficulties. Would you like me to connect you with a human agent?"


# Global voice bot instance
voice_bot = VoiceBot()


@voice_app.get("/")
async def voice_bot_home():
    """Voice bot server home"""
    return HTMLResponse(content="""
    <html>
        <head><title>Voice Bot Server</title></head>
        <body style="font-family: Arial; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #667eea;">🤖 AI Voice Bot Server</h1>
                <p style="color: #64748b; font-size: 18px;">Status: <strong style="color: #10b981;">Running</strong></p>
                
                <h2 style="color: #667eea; margin-top: 30px;">📞 Ready to Handle Calls</h2>
                <ul style="color: #64748b; line-height: 2;">
                    <li>✅ Twilio Voice Integration</li>
                    <li>✅ Whisper Speech Recognition</li>
                    <li>✅ Groq LLM Intelligence</li>
                    <li>✅ ElevenLabs Text-to-Speech</li>
                    <li>✅ Auto-Upload Recordings</li>
                </ul>
                
                <h3 style="color: #667eea; margin-top: 30px;">🔧 Webhook Endpoint:</h3>
                <code style="background: #f1f5f9; padding: 10px; display: block; border-radius: 6px;">
                    POST /voice/incoming
                </code>
                
                <p style="color: #64748b; margin-top: 20px;">
                    Configure this URL in Twilio Console → Phone Numbers → Voice & Fax → Webhook
                </p>
            </div>
        </body>
    </html>
    """)


@voice_app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """
    Twilio webhook - Called when customer calls the phone number
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    
    logger.info(f"📞 Incoming call: {call_sid} from {from_number}")
    
    # Initialize conversation
    voice_bot.get_conversation_context(call_sid)
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Start recording the call
    response.record(
        max_length=300,  # 5 minutes max
        recording_status_callback=f"{BACKEND_URL}/voice/recording-complete",
        recording_status_callback_event="completed"
    )
    
    # Greet the customer
    response.say(
        voice_bot.greeting,
        voice="Polly.Joanna",
        language="en-US"
    )
    
    # Listen for customer response
    gather = Gather(
        input='speech',
        action='/voice/process-speech',
        timeout=5,
        speech_timeout='auto',
        speech_model='experimental_conversations'
    )
    response.append(gather)
    
    # If customer doesn't say anything
    response.say("I didn't hear anything. Please say something or press any key.")
    response.redirect('/voice/incoming')
    
    return Response(content=str(response), media_type="application/xml")


@voice_app.post("/voice/process-speech")
async def process_customer_speech(request: Request):
    """
    Process what customer said and generate AI response
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    speech_result = form_data.get("SpeechResult")
    
    logger.info(f"🎤 Customer said: {speech_result}")
    
    # Check if customer wants to hang up
    end_keywords = ["goodbye", "bye", "thank you bye", "that's all", "hang up", "end call"]
    if any(keyword in speech_result.lower() for keyword in end_keywords):
        response = VoiceResponse()
        response.say("Thank you for calling! Have a great day. Goodbye!")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Generate AI response
    ai_response = voice_bot.generate_ai_response(call_sid, speech_result)
    
    # Create TwiML response
    response = VoiceResponse()
    response.say(ai_response, voice="Polly.Joanna", language="en-US")
    
    # Continue conversation
    gather = Gather(
        input='speech',
        action='/voice/process-speech',
        timeout=5,
        speech_timeout='auto'
    )
    gather.say("", voice="Polly.Joanna")  # Pause for customer
    response.append(gather)
    
    # If no response, check if they're still there
    response.say("Are you still there? If you need anything else, just let me know.")
    response.redirect('/voice/process-speech')
    
    return Response(content=str(response), media_type="application/xml")


@voice_app.post("/voice/recording-complete")
async def handle_recording_complete(request: Request, background_tasks: BackgroundTasks):
    """
    Called when call recording is complete - auto-upload to admin backend
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    recording_duration = form_data.get("RecordingDuration")
    
    logger.info(f"✅ Call {call_sid} completed. Duration: {recording_duration}s")
    logger.info(f"📼 Recording URL: {recording_url}")
    
    # Auto-upload to admin backend in background
    background_tasks.add_task(
        auto_upload_recording,
        call_sid,
        recording_url,
        recording_duration
    )
    
    return {"status": "success", "message": "Recording will be processed"}


async def auto_upload_recording(call_sid: str, recording_url: str, duration: str):
    """
    Download recording from Twilio and upload to admin backend
    """
    try:
        logger.info(f"⬇️ Downloading recording for call {call_sid}")
        
        # Download recording from Twilio
        recording_url_full = f"{recording_url}.wav"
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        recording_response = requests.get(recording_url_full, auth=auth)
        
        if recording_response.status_code != 200:
            logger.error(f"Failed to download recording: {recording_response.status_code}")
            return
        
        # Save temporarily
        temp_file = f"uploads/call_{call_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        with open(temp_file, "wb") as f:
            f.write(recording_response.content)
        
        logger.info(f"💾 Recording saved: {temp_file}")
        
        # Upload to admin backend
        logger.info(f"📤 Uploading to admin backend: {BACKEND_URL}/process_call")
        
        with open(temp_file, "rb") as audio_file:
            files = {"file": (temp_file, audio_file, "audio/wav")}
            upload_response = requests.post(
                f"{BACKEND_URL}/process_call",
                files=files,
                timeout=120
            )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            logger.info(f"✅ Call uploaded successfully! Call ID: {result.get('call_id')}")
            
            # Check if urgent
            priority_level = result.get("final_decision", {}).get("priority_level")
            if priority_level in ["urgent", "high"]:
                logger.warning(f"🚨 URGENT CALL DETECTED - Priority: {priority_level}")
                # TODO: Send real-time alert to admin dashboard
        else:
            logger.error(f"Failed to upload: {upload_response.status_code}")
            
    except Exception as e:
        logger.error(f"Auto-upload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Voice Bot Server...")
    logger.info(f"📞 Twilio Number: {TWILIO_PHONE_NUMBER}")
    logger.info(f"🔄 Backend URL: {BACKEND_URL}")
    logger.info("🌐 Server will be available at: http://localhost:5050")
    logger.info("⚠️ Remember to expose with ngrok for Twilio webhooks!")
    
    uvicorn.run(voice_app, host="0.0.0.0", port=5050, log_level="info")
