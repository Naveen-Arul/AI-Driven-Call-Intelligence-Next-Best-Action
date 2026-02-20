"""
ElevenLabs Text-to-Speech Service
Converts AI text responses to natural speech for voice bot
"""

from elevenlabs import generate, set_api_key, voices, Voice
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ElevenLabsTTSService:
    """
    Service for converting text to speech using ElevenLabs API
    """
    
    def __init__(self):
        """
        Initialize ElevenLabs TTS service
        """
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not self.api_key:
            logger.warning("⚠️ ElevenLabs API key not found in .env")
            self.enabled = False
        else:
            set_api_key(self.api_key)
            self.enabled = True
            logger.info("✅ ElevenLabs TTS Service initialized")
        
        # Default voice settings
        self.default_voice = "Rachel"  # Clear, professional female voice
        self.available_voices = None
    
    def get_available_voices(self):
        """
        Get list of available voices from ElevenLabs
        """
        if not self.enabled:
            return []
        
        try:
            if self.available_voices is None:
                self.available_voices = voices()
            return self.available_voices
        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}")
            return []
    
    def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        language: str = "en"
    ) -> bytes:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            voice: Voice name (default: Rachel)
            language: Language code for multilingual support
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not self.enabled:
            logger.error("ElevenLabs TTS not enabled - missing API key")
            return b""
        
        try:
            # Use default voice if not specified
            if not voice:
                voice = self.default_voice
            
            logger.info(f"🎙️ Generating speech with voice: {voice}")
            logger.info(f"📝 Text: {text[:100]}...")
            
            # Generate speech
            audio = generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2" if language != "en" else "eleven_monolingual_v1"
            )
            
            logger.info(f"✅ Speech generated successfully ({len(audio)} bytes)")
            return audio
            
        except Exception as e:
            logger.error(f"Text-to-speech generation failed: {str(e)}")
            return b""
    
    def text_to_speech_multilingual(
        self,
        text: str,
        language: str = "en",
        language_name: str = "English"
    ) -> bytes:
        """
        Generate speech in customer's language (Tamil, Hindi, Malayalam, etc.)
        
        Args:
            text: Text in target language
            language: Language code (ta, hi, ml, te, etc.)
            language_name: Full language name
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not self.enabled:
            return b""
        
        try:
            # Multilingual voices for Indian languages
            language_voice_map = {
                "ta": "Adam",      # Tamil
                "hi": "Bella",     # Hindi
                "ml": "Rachel",    # Malayalam
                "te": "Domi",      # Telugu
                "en": "Rachel",    # English
                "es": "Matilda",   # Spanish
                "fr": "Charlotte"  # French
            }
            
            voice = language_voice_map.get(language, "Rachel")
            
            logger.info(f"🌐 Generating {language_name} speech")
            
            audio = generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2"
            )
            
            logger.info(f"✅ {language_name} speech generated")
            return audio
            
        except Exception as e:
            logger.error(f"Multilingual TTS failed: {str(e)}")
            return b""
    
    def save_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Save audio bytes to file
        
        Args:
            audio_bytes: Audio data
            filename: Output filename (without extension)
            
        Returns:
            Full file path
        """
        try:
            output_path = f"uploads/{filename}.mp3"
            
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            logger.info(f"💾 Audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save audio: {str(e)}")
            return ""


# Global instance
tts_service = ElevenLabsTTSService()
