"""
Text-to-Speech Service using ElevenLabs API
Converts AI text responses to natural voice audio
"""

import os
import logging
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TTSService:
    """
    Text-to-Speech service using ElevenLabs for natural voice generation
    """
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ ELEVENLABS_API_KEY not found in .env - TTS will be disabled")
            self.enabled = False
            self.client = None
        else:
            self.enabled = True
            # Initialize ElevenLabs client
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info("✅ ElevenLabs TTS Service initialized")
        
        # Default voice settings - Indian English accent available
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear, neutral
        # Alternative: "pNInz6obpgDQGcFmaJgB" for Adam (male voice)
        
    def text_to_speech(
        self,
        text: str,
        voice_id: str = None,
        language: str = "en",
        output_path: str = None
    ) -> bytes:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (optional, uses default if not provided)
            language: Language code for voice selection
            output_path: Optional path to save audio file
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        if not self.enabled or not self.client:
            logger.error("TTS Service is disabled - API key not configured")
            return None
        
        try:
            # Select voice based on language
            voice_to_use = voice_id or self._get_voice_for_language(language)
            
            logger.info(f"🎤 Generating speech for text: '{text[:50]}...'")
            
            # Generate audio using ElevenLabs API (correct method)
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_to_use,
                text=text,
                model_id="eleven_multilingual_v2",  # Supports multiple languages including Indian accents
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            # Convert generator to bytes
            audio_bytes = b''.join(audio_generator)
            
            # Save to file if path provided
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"💾 Audio saved to {output_path}")
            
            logger.info("✅ Speech generated successfully")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {str(e)}")
            return None
    
    def _get_voice_for_language(self, language: str) -> str:
        """
        Get appropriate voice ID for given language
        
        Args:
            language: Language code (en, ta, hi, ml, etc.)
            
        Returns:
            ElevenLabs voice ID
        """
        # Voice mapping for different languages/accents
        voice_map = {
            "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel - clear English
            "ta": "21m00Tcm4TlvDq8ikWAM",  # Tamil - use multilingual model
            "hi": "21m00Tcm4TlvDq8ikWAM",  # Hindi - use multilingual model
            "ml": "21m00Tcm4TlvDq8ikWAM",  # Malayalam - use multilingual model
            "te": "21m00Tcm4TlvDq8ikWAM",  # Telugu - use multilingual model
        }
        
        return voice_map.get(language, self.default_voice_id)
    
    def stream_text_to_speech(self, text: str, voice_id: str = None):
        """
        Stream TTS audio in chunks (for real-time playback)
        
        Args:
            text: Text to convert
            voice_id: Optional voice ID
            
        Yields:
            Audio chunks
        """
        if not self.enabled or not self.client:
            logger.error("TTS Service is disabled")
            return
        
        try:
            voice_to_use = voice_id or self.default_voice_id
            
            # Generate streaming audio (new API)
            audio_stream = self.client.generate(
                text=text,
                voice=voice_to_use,
                model="eleven_multilingual_v2",
                stream=True
            )
            
            for chunk in audio_stream:
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming TTS error: {str(e)}")
            return

# Global instance
tts_service = TTSService()
