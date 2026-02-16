"""
AI-Driven Call Intelligence Platform
FastAPI Backend - Complete Product v5.0
Full pipeline with MongoDB persistence and RAG-enhanced LLM
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from pathlib import Path
import shutil
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

from services.transcription_service import TranscriptionService
from services.nlp_service import NLPService
from services.llm_service import LLMService
from services.action_engine import ActionEngine
from services.database_service import DatabaseService
from services.rag_service import RAGService
from services.email_service import EmailService
from services.crm_service import CRMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory (for temporary storage only)
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize services (loaded once at startup)
transcription_service = None
nlp_service = None
llm_service = None
action_engine = None
db_service = None
rag_service = None
email_service = None
crm_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global transcription_service, nlp_service, llm_service, action_engine, db_service, rag_service, email_service, crm_service
    logger.info("Starting Call Intelligence API v5.0...")
    
    # Initialize all services
    transcription_service = TranscriptionService(model_size="base")
    nlp_service = NLPService()
    llm_service = LLMService()
    action_engine = ActionEngine()
    
    # Initialize database service
    db_service = DatabaseService()
    db_service.connect()
    
    # Initialize RAG service
    rag_service = RAGService()
    rag_service.initialize()
    
    # Initialize email and CRM services
    email_service = EmailService()
    crm_service = CRMService()
    
    logger.info("✅ All services initialized successfully")
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    db_service.disconnect()


# Initialize FastAPI app
app = FastAPI(
    title="Call Intelligence API",
    description="AI-powered call transcription, analysis, and decision platform with MongoDB persistence",
    version="5.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class TranscriptionSegment(BaseModel):
    start_time: float
    end_time: float
    text: str


class TranscriptionResponse(BaseModel):
    transcript: str
    segments: List[TranscriptionSegment]
    language: str
    processing_time: float


class AnalyzeRequest(BaseModel):
    transcript: str


class SentimentResult(BaseModel):
    compound: float
    positive: float
    neutral: float
    negative: float
    sentiment_label: str


class EntityResult(BaseModel):
    text: str
    label: str


class AnalyzeResponse(BaseModel):
    sentiment: SentimentResult
    keywords: dict
    entities: List[EntityResult]
    intent: str


class IntelligenceRequest(BaseModel):
    transcript: str
    nlp_analysis: dict


class IntelligenceResponse(BaseModel):
    call_summary_short: str
    call_summary_detailed: str
    risk_level: str
    opportunity_level: str
    recommended_action: str
    priority_score: int
    reasoning: str


class DecisionRequest(BaseModel):
    nlp_analysis: dict
    llm_output: dict


class DecisionResponse(BaseModel):
    final_action: str
    priority_score: int
    risk_level: str
    opportunity_level: str
    escalation_required: bool
    urgent_flag: bool
    revenue_opportunity: bool
    confidence_score: int
    reasoning: str
    rules_applied: List[str]
    intent: str
    sentiment_label: str


# New models for complete product backend
class CompanyContextRequest(BaseModel):
    company_policy_text: str
    metadata: Optional[dict] = None


class CompanyContextResponse(BaseModel):
    success: bool
    chunks_stored: Optional[int] = None
    total_documents: Optional[int] = None
    error: Optional[str] = None


class CallResponse(BaseModel):
    call_id: str
    transcript: str
    nlp_analysis: dict
    llm_output: dict
    final_decision: dict
    status: str
    created_at: str
    updated_at: str


class CallListResponse(BaseModel):
    calls: List[dict]
    total: int
    limit: int


class SendEmailRequest(BaseModel):
    call_id: str
    recipient_email: str
    email_type: str = "action"  # "action" or "reminder"


class CRMSyncRequest(BaseModel):
    call_id: str
    actions: List[str] = ["create_lead", "create_task", "log_activity"]  # CRM actions to perform
    skip: int


class MetricsResponse(BaseModel):
    total_calls: int
    high_risk_calls: int
    revenue_opportunities: int
    avg_priority_score: float
    sentiment_distribution: dict
    status_distribution: dict
    last_updated: str


class ApprovalRequest(BaseModel):
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    success: bool
    call_id: str
    new_status: str
    message: str


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI-Driven Call Intelligence Platform",
        "version": "5.0.0",
        "features": [
            "Speech-to-Text (Whisper)",
            "NLP Analysis (Sentiment + Intent + Entities)",
            "LLM Intelligence (Groq Llama 3.1)",
            "Business Rules Engine",
            "MongoDB Persistence",
            "RAG-Enhanced Context (ChromaDB)"
        ],
        "endpoints": {
            "process_call": "POST /process-call",
            "list_calls": "GET /calls",
            "get_call": "GET /calls/{call_id}",
            "metrics": "GET /dashboard/metrics",
            "approve": "POST /approve-action/{call_id}",
            "reject": "POST /reject-action/{call_id}",
            "company_context": "POST /company-context"
        }
    }


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file to text using Whisper STT.
    
    Args:
        file: Audio file (wav, mp3, m4a, etc.)
        
    Returns:
        Structured transcription with timestamps
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file extension
    allowed_extensions = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file
    file_path = UPLOAD_FOLDER / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Transcribe audio
        result = transcription_service.transcribe(str(file_path))
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Cleaned up temporary file: {file.filename}")


@app.get("/health")
async def health_check():
    """Detailed health check"""
    rag_count = 0
    if rag_service and rag_service.collection is not None:
        try:
            rag_count = rag_service.collection.count()
        except:
            rag_count = 0
    
    db_count = 0
    if db_service and db_service.calls_collection is not None:
        try:
            db_count = db_service.calls_collection.count_documents({})
        except:
            db_count = 0
    
    return {
        "status": "healthy",
        "version": "5.0.0",
        "services": {
            "transcription_service": "ready",
            "nlp_service": "ready",
            "llm_service": "ready",
            "action_engine": "ready",
            "database_service": "ready" if (db_service and db_service.calls_collection is not None) else "disabled",
            "rag_service": "ready" if (rag_service and rag_service.collection is not None) else "disabled"
        },
        "database": {
            "total_calls": db_count
        },
        "rag": {
            "total_documents": rag_count
        }
    }


@app.post("/intelligence")
async def generate_intelligence(request: IntelligenceRequest):
    """
    Generate AI-powered intelligence from transcript and NLP analysis.
    
    Args:
        request: JSON body containing transcript and nlp_analysis
        
    Returns:
        Structured intelligence including summary, risk/opportunity assessment,
        recommended action, priority score, and reasoning
    """
    if not request.transcript or request.transcript.strip() == "":
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    if not request.nlp_analysis:
        raise HTTPException(status_code=400, detail="NLP analysis is required")
    
    try:
        logger.info("Generating LLM intelligence...")
        result = llm_service.generate_intelligence(
            request.transcript,
            request.nlp_analysis
        )
        
        # Check for errors
        if "error" in result:
            logger.error(f"LLM intelligence error: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Intelligence generation failed: {result.get('error')}"
            )
        
        logger.info(f"Intelligence generated - Priority: {result.get('priority_score')}")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligence generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decision", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """
    Apply business rules and validate LLM recommendations to produce final decision.
    
    Args:
        request: JSON body containing nlp_analysis and llm_output
        
    Returns:
        Final validated decision with confidence score, business rules applied,
        escalation flags, and CRM-ready action
    """
    if not request.nlp_analysis:
        raise HTTPException(status_code=400, detail="NLP analysis is required")
    
    if not request.llm_output:
        raise HTTPException(status_code=400, detail="LLM output is required")
    
    try:
        logger.info("Applying business rules to generate final decision...")
        
        # Apply business rules and validation
        decision = action_engine.evaluate(
            nlp_analysis=request.nlp_analysis,
            llm_output=request.llm_output
        )
        
        logger.info(
            f"Decision finalized - Action: {decision.get('final_action')[:50]}..., "
            f"Priority: {decision.get('priority_score')}, "
            f"Confidence: {decision.get('confidence_score')}, "
            f"Escalation: {decision.get('escalation_required')}"
        )
        
        return JSONResponse(content=decision)
        
    except Exception as e:
        logger.error(f"Decision generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(request: AnalyzeRequest):
    """
    Analyze a transcript using NLP to extract sentiment, keywords, entities, and intent.
    
    Args:
        request: JSON body containing transcript text
        
    Returns:
        Structured NLP analysis including sentiment, keywords, entities, and intent
    """
    if not request.transcript or request.transcript.strip() == "":
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        logger.info("Analyzing transcript...")
        result = nlp_service.analyze(request.transcript)
        logger.info(f"Analysis complete - Intent: {result['intent']}")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPLETE PRODUCT ENDPOINTS (v5.0) - MongoDB + RAG + Full Pipeline
# ============================================================================


@app.post("/process-call")
async def process_call(file: UploadFile = File(...)):
    """
    🚀 COMPLETE PIPELINE: Process audio from start to finish.
    
    Steps:
    1. Transcribe audio (Whisper STT)
    2. Analyze transcript (NLP)
    3. Generate intelligence (LLM with RAG context)
    4. Apply business rules (Action Engine)
    5. Store in MongoDB
    6. Return final decision
    
    Args:
        file: Audio file (wav, mp3, m4a, etc.)
        
    Returns:
        Complete call intelligence document with MongoDB ID
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        logger.info(f"🎙️ Processing call: {file.filename}")
        
        # Read file into memory (no disk storage)
        audio_bytes = await file.read()
        
        # Save temporarily for Whisper processing
        temp_path = UPLOAD_FOLDER / file.filename
        with temp_path.open("wb") as f:
            f.write(audio_bytes)
        
        # Step 1: Transcribe
        logger.info("Step 1/5: Transcribing audio...")
        transcription_result = transcription_service.transcribe(str(temp_path))
        transcript = transcription_result["transcript"]
        
        # Clean up temp file immediately
        temp_path.unlink()
        
        # Step 2: NLP Analysis
        logger.info("Step 2/5: Analyzing transcript (NLP)...")
        nlp_analysis = nlp_service.analyze(transcript)
        
        # Step 3: Get company context from RAG
        logger.info("Step 3/5: Retrieving company context (RAG)...")
        company_context = rag_service.get_context_for_llm(transcript, nlp_analysis)
        
        # Step 4: LLM Intelligence (with RAG context)
        logger.info("Step 4/5: Generating intelligence (LLM + RAG)...")
        llm_output = llm_service.generate_intelligence(
            transcript,
            nlp_analysis,
            company_context=company_context
        )
        
        if "error" in llm_output:
            raise HTTPException(
                status_code=500,
                detail=f"LLM intelligence failed: {llm_output.get('error')}"
            )
        
        # Step 5: Apply business rules
        logger.info("Step 5/5: Applying business rules...")
        final_decision = action_engine.evaluate(
            nlp_analysis=nlp_analysis,
            llm_output=llm_output
        )
        
        # Step 6: Store in MongoDB
        logger.info("💾 Storing in MongoDB...")
        call_id = db_service.store_call(
            transcript=transcript,
            nlp_analysis=nlp_analysis,
            llm_output=llm_output,
            final_decision=final_decision,
            audio_filename=file.filename
        )
        
        logger.info(f"✅ Call processed successfully - ID: {call_id}")
        
        return JSONResponse(content={
            "call_id": call_id,
            "transcript": transcript,
            "nlp_analysis": nlp_analysis,
            "llm_output": llm_output,
            "final_decision": final_decision,
            "status": "pending",
            "message": "Call processed and stored successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Call processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calls")
async def get_calls(
    limit: int = 100,
    skip: int = 0,
    status: Optional[str] = None
):
    """
    📋 Get list of all processed calls.
    
    Args:
        limit: Max number of calls to return (default: 100)
        skip: Number of calls to skip for pagination (default: 0)
        status: Filter by status (pending/approved/rejected)
        
    Returns:
        List of calls sorted by priority score (descending)
    """
    try:
        calls = db_service.get_all_calls(
            limit=limit,
            skip=skip,
            status_filter=status
        )
        
        return JSONResponse(content={
            "calls": calls,
            "total": len(calls),
            "limit": limit,
            "skip": skip,
            "status_filter": status
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calls/{call_id}")
async def get_call(call_id: str):
    """
    🔍 Get full details of a specific call.
    
    Args:
        call_id: MongoDB ObjectId
        
    Returns:
        Complete call document
    """
    try:
        call = db_service.get_call(call_id)
        
        if not call:
            raise HTTPException(status_code=404, detail=f"Call {call_id} not found")
        
        return JSONResponse(content=call)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """
    📊 Get dashboard KPIs and analytics.
    
    Returns:
        - Total calls
        - High risk calls
        - Revenue opportunities
        - Average priority score
        - Sentiment distribution
        - Status distribution
    """
    try:
        metrics = db_service.get_dashboard_metrics()
        return JSONResponse(content=metrics)
        
    except Exception as e:
        logger.error(f"Failed to calculate metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve-action/{call_id}")
async def approve_action(call_id: str, request: Optional[ApprovalRequest] = None):
    """
    ✅ Approve a recommended action for a call.
    
    Args:
        call_id: MongoDB ObjectId
        request: Optional notes about approval
        
    Returns:
        Success confirmation
    """
    try:
        notes = request.notes if request else None
        success = db_service.update_call_status(
            call_id=call_id,
            status="approved",
            notes=notes
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Call {call_id} not found or update failed"
            )
        
        logger.info(f"✅ Call {call_id} approved")
        
        return JSONResponse(content={
            "success": True,
            "call_id": call_id,
            "new_status": "approved",
            "message": "Action approved successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reject-action/{call_id}")
async def reject_action(call_id: str, request: Optional[ApprovalRequest] = None):
    """
    ❌ Reject a recommended action for a call.
    
    Args:
        call_id: MongoDB ObjectId
        request: Optional notes about rejection
        
    Returns:
        Success confirmation
    """
    try:
        notes = request.notes if request else None
        success = db_service.update_call_status(
            call_id=call_id,
            status="rejected",
            notes=notes
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Call {call_id} not found or update failed"
            )
        
        logger.info(f"❌ Call {call_id} rejected")
        
        return JSONResponse(content={
            "success": True,
            "call_id": call_id,
            "new_status": "rejected",
            "message": "Action rejected successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/company-context")
async def store_company_context(request: CompanyContextRequest):
    """
    🧠 Store company policy/knowledge for RAG-enhanced LLM decisions.
    
    Args:
        request: Company policy text and optional metadata
        
    Returns:
        Storage confirmation with chunk count
    """
    try:
        if not request.company_policy_text or len(request.company_policy_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Company policy text must be at least 10 characters"
            )
        
        logger.info("📚 Storing company context in RAG...")
        result = rag_service.store_company_context(
            policy_text=request.company_policy_text,
            metadata=request.metadata
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store context: {result.get('error')}"
            )
        
        logger.info(f"✅ Stored {result['chunks_stored']} chunks in ChromaDB")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to store company context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/stats")
async def get_rag_stats():
    """
    📚 Get RAG service statistics.
    
    Returns:
        Total documents, embedding model, collection name
    """
    try:
        stats = rag_service.get_stats()
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Failed to get RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-email")
async def send_email(request: SendEmailRequest):
    """
    📧 Send email notification for call action.
    
    Args:
        request: Call ID, recipient email, and email type
        
    Returns:
        Email delivery status
    """
    try:
        logger.info(f"📧 Sending email for call {request.call_id} to {request.recipient_email}")
        
        # Get call data from database
        call_data = db_service.get_call_by_id(request.call_id)
        
        if not call_data:
            raise HTTPException(
                status_code=404,
                detail=f"Call {request.call_id} not found"
            )
        
        # Send appropriate email type
        if request.email_type == "reminder":
            result = email_service.send_reminder(call_data, request.recipient_email)
        else:
            result = email_service.send_action_notification(call_data, request.recipient_email)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {result.get('message')}"
            )
        
        # Log email sent in database
        db_service.calls_collection.update_one(
            {"_id": call_data["_id"]},
            {
                "$push": {
                    "emails_sent": {
                        "recipient": request.recipient_email,
                        "type": request.email_type,
                        "sent_at": result.get("timestamp"),
                        "status": "sent"
                    }
                }
            }
        )
        
        logger.info(f"✅ Email sent successfully to {request.recipient_email}")
        
        return JSONResponse(content={
            "success": True,
            "call_id": request.call_id,
            "email_sent_to": request.recipient_email,
            "email_type": request.email_type,
            "timestamp": result.get("timestamp")
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crm/sync")
async def sync_to_crm(request: CRMSyncRequest):
    """
    🔄 Sync call data to CRM system.
    
    Args:
        request: Call ID and list of CRM actions to perform
        
    Returns:
        CRM sync results with action details
    """
    try:
        logger.info(f"🔄 Syncing call {request.call_id} to CRM...")
        
        # Get call data from database
        call_data = db_service.get_call_by_id(request.call_id)
        
        if not call_data:
            raise HTTPException(
                status_code=404,
                detail=f"Call {request.call_id} not found"
            )
        
        # Perform CRM sync
        result = crm_service.sync_to_crm(call_data, request.actions)
        
        # Log CRM sync in database
        db_service.calls_collection.update_one(
            {"_id": call_data["_id"]},
            {
                "$set": {
                    "crm_synced": True,
                    "crm_sync_timestamp": result.get("timestamp"),
                    "crm_actions": result.get("actions_performed")
                }
            }
        )
        
        logger.info(f"✅ CRM sync completed for call {request.call_id}")
        
        return JSONResponse(content={
            "success": True,
            "call_id": request.call_id,
            "crm_results": result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync to CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crm/status/{call_id}")
async def get_crm_status(call_id: str):
    """
    📊 Get CRM sync status for a call.
    
    Args:
        call_id: Call identifier
        
    Returns:
        CRM sync status and action history
    """
    try:
        call_data = db_service.get_call_by_id(call_id)
        
        if not call_data:
            raise HTTPException(
                status_code=404,
                detail=f"Call {call_id} not found"
            )
        
        return JSONResponse(content={
            "call_id": call_id,
            "crm_synced": call_data.get("crm_synced", False),
            "crm_sync_timestamp": call_data.get("crm_sync_timestamp"),
            "crm_actions": call_data.get("crm_actions", []),
            "emails_sent": call_data.get("emails_sent", [])
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get CRM status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
