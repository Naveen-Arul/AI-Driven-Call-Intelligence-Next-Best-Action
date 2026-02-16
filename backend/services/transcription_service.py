"""
Transcription Service
Handles audio-to-text conversion using OpenAI Whisper.
"""

import whisper
import time
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Service for transcribing audio files using Whisper STT.
    Model is loaded once at initialization for efficiency.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize transcription service with Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribes an audio file and returns structured data.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing:
                - transcript: Full text transcription
                - segments: List of timestamped segments
                - processing_time: Time taken to process (seconds)
                - language: Detected language
        """
        try:
            start_time = time.time()
            
            logger.info(f"Transcribing audio: {audio_path}")
            result = self.model.transcribe(audio_path)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            # Structure segments with timestamps
            segments = [
                {
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "text": segment["text"].strip()
                }
                for segment in result.get("segments", [])
            ]
            
            logger.info(f"Transcription completed in {processing_time}s")
            
            return {
                "transcript": result["text"].strip(),
                "segments": segments,
                "language": result.get("language", "unknown"),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise Exception(f"Transcription error: {str(e)}")
