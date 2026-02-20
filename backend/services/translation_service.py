"""
Translation Service
Translates non-English transcripts to English using Groq LLM.
"""

from groq import Groq
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for translating transcripts to English using Groq LLM.
    Uses Llama 3.1 for high-quality translation.
    """
    
    def __init__(self):
        """Initialize translation service with Groq client"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        logger.info("✅ Translation service initialized with Groq Llama 3.1")
    
    def translate_to_english(
        self, 
        text: str, 
        source_language: str,
        source_language_name: str = None
    ) -> Dict[str, str]:
        """
        Translate text to English if not already in English.
        
        Args:
            text: Original text to translate
            source_language: ISO language code (e.g., 'ta', 'hi', 'en')
            source_language_name: Full language name (e.g., 'Tamil', 'Hindi')
            
        Returns:
            {
                "translated_text": str,
                "source_language": str,
                "was_translated": bool
            }
        """
        # Skip translation if already English
        if source_language.lower() in ["en", "english"]:
            logger.info("📝 Text is already in English - skipping translation")
            return {
                "translated_text": text,
                "source_language": source_language,
                "was_translated": False
            }
        
        # Perform translation
        logger.info(f"🌐 Translating from {source_language_name or source_language} to English...")
        
        try:
            # Build translation prompt with few-shot examples in multiple languages
            lang_name = source_language_name or source_language.upper()
            
            # Use direct translation with examples
            prompt = f"""Examples:
Tamil: "விளக்கங்கள்" → "lights"
Hindi: "उत्पाद" → "product"
Malayalam: "സേവനം" → "service"

Translate to English: {text}"""

            # Call Groq API with strict system message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a translator. Translate ANY text to English. NEVER say 'I cannot' or 'I am unable'. ALWAYS provide translation. Return ONLY the English text, nothing else."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Slightly higher for better cross-language understanding
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Check for refusal patterns
            refusal_patterns = [
                'i am unable',
                'i cannot',
                'unable to',
                'cannot verify',
                'cannot translate',
                'don\'t understand',
                'not able to'
            ]
            
            is_refusal = any(pattern in translated_text.lower() for pattern in refusal_patterns)
            
            # If it's a refusal, try a different approach
            if is_refusal or len(translated_text) > len(text) * 3:
                logger.warning(f"⚠️ Got refusal or oversized response, retrying with simpler prompt...")
                
                # Retry with even simpler prompt
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Translate to English:"
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    temperature=0.4,
                    max_tokens=2000
                )
                
                translated_text = response.choices[0].message.content.strip()
            
            # Clean up common prefixes
            prefixes_to_remove = [
                'english:',
                'translation:',
                'english translation:',
                'here is the translation:',
                'the translation is:',
                'translated:'
            ]
            
            for prefix in prefixes_to_remove:
                if translated_text.lower().startswith(prefix):
                    translated_text = translated_text[len(prefix):].strip()
            
            # Clean up lines
            lines = [l.strip() for l in translated_text.split('\n') if l.strip()]
            if lines:
                # Remove instruction lines
                clean_lines = []
                for line in lines:
                    if not any(skip in line.lower() for skip in [
                        'important instruction',
                        'please provide',
                        'maintain the',
                        'preserve',
                        'do not add',
                        'return only',
                        '---'
                    ]):
                        clean_lines.append(line)
                
                if clean_lines:
                    translated_text = ' '.join(clean_lines)
            
            # Final check - if still looks like a refusal, return a descriptive translation
            if any(pattern in translated_text.lower() for pattern in refusal_patterns):
                logger.error(f"❌ Still got refusal after retry. Using descriptive text.")
                translated_text = f"[Original text in {lang_name}: {text[:50]}...]"
            
            logger.info(f"✅ Translation completed - {len(text)} chars → {len(translated_text)} chars")
            
            return {
                "translated_text": translated_text,
                "source_language": source_language,
                "was_translated": True
            }
            
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            # Fallback: return original text
            return {
                "translated_text": text,
                "source_language": source_language,
                "was_translated": False,
                "translation_error": str(e)
            }
    
    def translate_segments(
        self,
        segments: list,
        source_language: str,
        source_language_name: str = None
    ) -> list:
        """
        Translate individual segments (for timeline sentiment analysis).
        
        Args:
            segments: List of segment dictionaries with 'text' field
            source_language: ISO language code
            source_language_name: Full language name
            
        Returns:
            List of segments with added 'translated_text' field
        """
        # Skip if English
        if source_language.lower() in ["en", "english"]:
            for segment in segments:
                segment["translated_text"] = segment["text"]
            return segments
        
        logger.info(f"🌐 Translating {len(segments)} segments from {source_language_name or source_language}...")
        
        translated_segments = []
        for i, segment in enumerate(segments):
            try:
                result = self.translate_to_english(
                    segment["text"],
                    source_language,
                    source_language_name
                )
                
                segment_copy = segment.copy()
                segment_copy["translated_text"] = result["translated_text"]
                translated_segments.append(segment_copy)
                
            except Exception as e:
                logger.warning(f"⚠️ Segment {i} translation failed: {e}")
                segment_copy = segment.copy()
                segment_copy["translated_text"] = segment["text"]  # Fallback to original
                translated_segments.append(segment_copy)
        
        logger.info(f"✅ Segment translation completed")
        return translated_segments
