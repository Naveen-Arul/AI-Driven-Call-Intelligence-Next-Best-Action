"""
AI-Driven Call Intelligence Platform
FastAPI Backend - Step 3: LLM Intelligence Layer
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
import logging
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.transcription_service import TranscriptionService
from services.nlp_service import NLPService
from services.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize services (loaded once at startup)
transcription_service = None
nlp_service = None
llm_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global transcription_service, nlp_service, llm_service
    logger.info("Starting Call Intelligence API...")
    transcription_service = TranscriptionService(model_size="base")
    nlp_service = NLPService()
    llm_service = LLMService()
    logger.info("All services initialized successfully")
    yield
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Call Intelligence API",
    description="AI-powered call transcription and analysis platform",
    version="3.0.0",
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


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Call Intelligence API",
        "version": "3.0.0"
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
    return {
        "status": "healthy",
        "transcription_service": "ready",
        "nlp_service": "ready",
        "llm_service": "ready",
        "upload_folder": str(UPLOAD_FOLDER.absolute())
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
