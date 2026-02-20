"""
Voice API Endpoints for Customer Voice Bot
Handles web-based voice chat functionality
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import logging
from services.transcription_service import TranscriptionService
from services.conversation_service import ConversationService
from services.tts_service import TTSService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services
transcription_service = TranscriptionService(model_size="base")  # Use base for speed
conversation_service = ConversationService()
tts_service = TTSService()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    language: str
    sentiment: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    language: str = "en"

class SaveCallRequest(BaseModel):
    session_id: str
    transcript: str
    customer_queries: List[str]
    agent_responses: List[str]
    conversation_history: List[dict]
    language: str
    duration: int
    timestamp: str
    audio_files: Optional[List[str]] = []  # Paths to saved audio recordings

# Endpoints

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using Whisper
    
    Args:
        audio: Audio file (webm, mp3, wav, ogg, etc.)
    
    Returns:
        JSON with transcription text and detected language
    """
    temp_path = None
    try:
        # Read audio content
        content = await audio.read()
        
        # Validate file size
        if len(content) < 100:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")
        
        # Determine file extension from content type or filename
        file_extension = ".webm"
        if audio.content_type:
            if "ogg" in audio.content_type:
                file_extension = ".ogg"
            elif "mp4" in audio.content_type:
                file_extension = ".mp4"
            elif "mpeg" in audio.content_type or "mp3" in audio.content_type:
                file_extension = ".mp3"
        elif audio.filename:
            import os as path_os
            _, ext = path_os.splitext(audio.filename)
            if ext:
                file_extension = ext
        
        # Save to temporary file for transcription
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Also save permanently in uploads/audio/ directory
        import datetime
        audio_dir = os.path.join(os.path.dirname(__file__), "audio_recordings")
        os.makedirs(audio_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        permanent_filename = f"recording_{timestamp}{file_extension}"
        permanent_path = os.path.join(audio_dir, permanent_filename)
        
        # Copy to permanent location
        with open(permanent_path, 'wb') as f:
            f.write(content)
        
        print(f"📁 Saved audio: {len(content)} bytes as {temp_path}")
        print(f"💾 Permanently stored: {permanent_path}")
        
        # Transcribe with auto language detection
        result = transcription_service.transcribe(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if not result.get("transcript"):
            raise HTTPException(status_code=400, detail="Could not transcribe audio - no speech detected")
        
        return {
            "text": result["transcript"],
            "language": result.get("language", "unknown"),
            "language_name": result.get("language_name", "Unknown"),
            "audio_file": permanent_filename  # Return filename for frontend to track
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        import traceback
        error_detail = f"Transcription error: {str(e)}"
        print(f"❌ {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Get AI response for user message
    
    Args:
        request: Chat request with message, language, session_id
    
    Returns:
        AI response with sentiment analysis
    """
    try:
        # Start conversation if new session
        if not conversation_service.active_conversations.get(request.session_id):
            conversation_service.start_conversation(
                call_sid=request.session_id,
                customer_phone="web_customer",
                language=request.language
            )
        
        # Get AI response (pass language for dynamic updates)
        ai_response = conversation_service.get_ai_response(
            call_sid=request.session_id,
            customer_input=request.message,
            language=request.language
        )
        
        return ChatResponse(
            response=ai_response["response"],
            language=request.language,
            sentiment=ai_response.get("sentiment", "neutral")
        )
    
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using ElevenLabs
    
    Args:
        request: TTS request with text and language
    
    Returns:
        Audio stream (MP3)
    """
    try:
        # Generate audio
        audio_data = tts_service.text_to_speech(
            text=request.text,
            language=request.language
        )
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Could not generate audio")
        
        # Return as streaming response
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=response.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/end-session")
async def end_session(session_id: str):
    """
    End a conversation session
    
    Args:
        session_id: Session ID to end
    
    Returns:
        Conversation summary
    """
    try:
        summary = conversation_service.get_conversation_summary(session_id)
        conversation_service.end_conversation(session_id)
        
        return {
            "status": "ended",
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session end error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "transcription": "ready",
            "conversation": "ready",
            "tts": "ready"
        }
    }


@router.post("/save-call")
async def save_call(request: SaveCallRequest):
    """
    Save completed voice call to database with AI analysis
    
    This processes the full conversation, generates AI summary and sentiment analysis,
    and saves to MongoDB so it appears in the admin dashboard
    
    Args:
        request: Call data including transcript, queries, responses
    
    Returns:
        Saved call information with call_id
    """
    try:
        from services.ai_nlp_service import AINLPService
        from services.llm_service import LLMService
        from services.action_engine import ActionEngine
        from services.database_service import DatabaseService
        
        # Initialize services
        nlp_service = AINLPService()
        llm_service = LLMService()
        action_engine = ActionEngine()
        db_service = DatabaseService()
        
        # Ensure database connection
        if not hasattr(db_service, 'calls_collection') or db_service.calls_collection is None:
            db_service.connect()
        
        # Step 1: Analyze transcript using AI NLP
        nlp_analysis = nlp_service.analyze(request.transcript, request.language)
        
        # Step 2: Generate AI summary and insights
        llm_output = llm_service.generate_intelligence(
            transcript=request.transcript,
            nlp_analysis=nlp_analysis
        )
        
        # Step 3: Apply business rules and determine actions
        final_decision = action_engine.evaluate(
            nlp_analysis=nlp_analysis,
            llm_output=llm_output
        )
        
        # Step 4: Prepare call data for database
        call_data = {
            "call_id": request.session_id,
            "transcript": request.transcript,
            "customer_queries": request.customer_queries,
            "agent_responses": request.agent_responses,
            "conversation_history": request.conversation_history,
            "audio_files": request.audio_files,  # Store audio file paths
            "language": request.language,
            "detected_language_name": get_language_name(request.language),
            "duration": request.duration,
            "nlp_analysis": nlp_analysis,
            "llm_output": llm_output,
            "final_decision": final_decision,
            "status": "pending_review",
            "source": "voice_bot",
            "created_at": request.timestamp,
            "updated_at": request.timestamp
        }
        
        # Step 5: Save to MongoDB
        result = db_service.save_call(call_data)
        
        return {
            "success": True,
            "call_id": request.session_id,
            "status": "saved",
            "priority": final_decision.get("priority_score", 50),
            "urgent": final_decision.get("urgent_flag", False),
            "sentiment": nlp_analysis.get("sentiment", {}).get("sentiment_label", "neutral"),
            "message": "Call saved successfully and visible in admin dashboard"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save call error: {str(e)}")


def get_language_name(code):
    """Get language name from code"""
    names = {
        'en': 'English',
        'ta': 'Tamil',
        'hi': 'Hindi',
        'ml': 'Malayalam',
        'te': 'Telugu',
        'auto': 'Auto Detected'
    }
    return names.get(code, code.upper())


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve saved audio recordings
    
    Args:
        filename: Audio file name
    
    Returns:
        Audio file stream
    """
    try:
        audio_dir = os.path.join(os.path.dirname(__file__), "audio_recordings")
        file_path = os.path.join(audio_dir, filename)
        
        # Security: prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(audio_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Determine content type
        content_type = "audio/webm"
        if filename.endswith(".ogg"):
            content_type = "audio/ogg"
        elif filename.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif filename.endswith(".mp4"):
            content_type = "audio/mp4"
        
        # Stream the file
        def iterfile():
            with open(file_path, mode="rb") as f:
                yield from f
        
        return StreamingResponse(iterfile(), media_type=content_type)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio serving error: {str(e)}")
