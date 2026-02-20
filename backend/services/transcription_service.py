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
        Transcribes an audio file with automatic language detection.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing:
                - transcript: Full text transcription (original language)
                - segments: List of timestamped segments
                - processing_time: Time taken to process (seconds)
                - language: Detected language code (e.g., 'en', 'ta', 'hi')
                - language_name: Full language name (e.g., 'English', 'Tamil')
        """
        try:
            start_time = time.time()
            
            logger.info(f"🎙️ Transcribing audio: {audio_path}")
            # Auto-detect language (no language parameter = auto-detect)
            result = self.model.transcribe(audio_path)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            # Detect language
            detected_language = result.get("language", "en")
            
            # Map language codes to full names
            language_names = {
                "en": "English",
                "ta": "Tamil",
                "hi": "Hindi",
                "te": "Telugu",
                "ml": "Malayalam",
                "kn": "Kannada",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "zh": "Chinese",
                "ja": "Japanese",
                "ar": "Arabic",
                "ru": "Russian",
                "pt": "Portuguese",
                "it": "Italian"
            }
            
            language_name = language_names.get(detected_language, detected_language.upper())
            
            # Structure segments with timestamps
            segments = [
                {
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "text": segment["text"].strip()
                }
                for segment in result.get("segments", [])
            ]
            
            logger.info(f"✅ Transcription completed in {processing_time}s - Language: {language_name} ({detected_language})")
            
            return {
                "transcript": result["text"].strip(),
                "segments": segments,
                "language": detected_language,
                "language_name": language_name,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise Exception(f"Transcription error: {str(e)}")
