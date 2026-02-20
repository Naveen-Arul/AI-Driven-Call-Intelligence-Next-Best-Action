"""
AI-Powered NLP Service
Uses Groq LLM for sentiment analysis, intent detection, and keyword extraction.
Supports multilingual analysis with few-shot learning.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class AINLPService:
    """
    AI-based NLP service using Groq LLM for all analysis.
    Replaces hardcoded VADER with intelligent sentiment analysis.
    """
    
    def __init__(self):
        """Initialize Groq client for AI-based NLP"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        logger.info("✅ AI NLP Service initialized with Groq LLM")
    
    def analyze(self, transcript: str, segments: List[Dict] = None, language: str = "en", language_name: str = "English") -> Dict:
        """
        AI-powered analysis of call transcript in ANY language.
        
        Args:
            transcript: Full text transcript (in original language - Tamil, Hindi, Malayalam, etc.)
            segments: Optional timestamped segments
            language: ISO language code (ta, hi, ml, en, etc.)
            language_name: Full language name (Tamil, Hindi, Malayalam, English, etc.)
            
        Returns:
            {
                "sentiment": {
                    "compound": float,
                    "sentiment_label": str,
                    "explanation": str
                },
                "keywords": {
                    "category": [list]
                },
                "entities": [{"text": str, "label": str}],
                "intent": str,
                "segment_sentiments": []
            }
        """
        
        try:
            logger.info(f"🤖 Starting AI-powered NLP analysis for {language_name}...")
            
            # Build multilingual few-shot prompt
            prompt = self._build_multilingual_analysis_prompt(transcript, language, language_name)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert NLP analyst fluent in multiple languages including English, Tamil, Hindi, Malayalam, Telugu, Spanish, French, and many others.
Analyze business call transcripts in ANY language and provide accurate sentiment, intent, keywords, and entities.
You understand cultural nuances and business contexts across languages.
Always return valid JSON with English field names, but analyze the content in its original language."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            # Validate and normalize
            normalized = self._normalize_analysis(analysis, transcript)
            
            # Add segment-level sentiment if segments provided
            if segments:
                normalized["segment_sentiments"] = self._analyze_segments(segments)
            else:
                normalized["segment_sentiments"] = []
            
            logger.info(f"✅ AI NLP completed - Sentiment: {normalized['sentiment']['sentiment_label']}, Intent: {normalized['intent']}")
            
            return normalized
            
        except Exception as e:
            logger.error(f"❌ AI NLP analysis failed: {e}")
            # Return minimal fallback
            return self._fallback_analysis(transcript)
    
    def _build_multilingual_analysis_prompt(self, transcript: str, language: str, language_name: str) -> str:
        """Build few-shot prompt with multilingual examples"""
        
        prompt = f"""Analyze this business call transcript in {language_name} and extract structured insights.

**MULTILINGUAL FEW-SHOT EXAMPLES:**

Example 1 (English - Positive Interest):
Transcript: "Hello, I'm very interested in your product. Can you schedule a demo next week?"
Analysis:
{{
  "sentiment": {{
    "compound": 0.85,
    "sentiment_label": "positive",
    "explanation": "Customer shows strong interest and proactive engagement"
  }},
  "intent": "demo_request",
  "keywords": {{
    "demo": ["demo", "schedule"],
    "interest": ["interested"],
    "product_inquiry": ["product"]
  }},
  "entities": [
    {{"text": "next week", "label": "TIMELINE"}}
  ]
}}

Example 2 (Tamil - Complaint):
Transcript: "உங்கள் சேவை சரியாக வேலை செய்யவில்லை. மிகவும் வருத்தமாக இருக்கிறது."
Translation meaning: "Your service is not working properly. Very frustrated."
Analysis:
{{
  "sentiment": {{
    "compound": -0.75,
    "sentiment_label": "negative", 
    "explanation": "Customer expresses frustration about service malfunction"
  }},
  "intent": "complaint",
  "keywords": {{
    "complaint": ["சேவை", "வேலை செய்யவில்லை", "வருத்தமாக"],
    "product_inquiry": ["சேவை"]
  }},
  "entities": [
    {{"text": "சேவை", "label": "PRODUCT"}}
  ]
}}

Example 3 (Hindi - Pricing Inquiry):
Transcript: "मुझे उत्पाद की कीमत और विशेषताओं के बारे में जानना है"
Translation meaning: "I want to know about product price and features"
Analysis:
{{
  "sentiment": {{
    "compound": 0.35,
    "sentiment_label": "neutral",
    "explanation": "Customer seeking information without strong emotion"
  }},
  "intent": "pricing_inquiry",
  "keywords": {{
    "pricing": ["कीमत"],
    "product_inquiry": ["उत्पाद", "विशेषताओं"]
  }},
  "entities": []
}}

Example 4 (Malayalam - Information Request):
Transcript: "ഞാൻ ഉത്പന്നത്തെക്കുറിച്ച് കൂടുതൽ അറിയാൻ ആഗ്രഹിക്കുന്നു"
Translation meaning: "I want to know more about the product"
Analysis:
{{
  "sentiment": {{
    "compound": 0.40,
    "sentiment_label": "neutral",
    "explanation": "Customer expressing curiosity and interest in learning more"
  }},
  "intent": "information_request",
  "keywords": {{
    "product_inquiry": ["ഉത്പന്നം"],
    "interest": ["അറിയാൻ ആഗ്രഹിക്കുന്നു"]
  }},
  "entities": []
}}

**NOW ANALYZE THIS {language_name.upper()} TRANSCRIPT:**

Language: {language_name} ({language})
Transcript: {transcript}

**RETURN JSON with this exact structure:**
{{
  "sentiment": {{
    "compound": <float between -1.0 (very negative) and 1.0 (very positive)>,
    "sentiment_label": "positive" | "neutral" | "negative",
    "explanation": "<brief explanation in English>"
  }},
  "intent": "<primary intent: demo_request | complaint | pricing_inquiry | cancellation | information_request | interest_declaration | objection | other>",
  "keywords": {{
    "<category>": ["<word1>", "<word2>"]
  }},
  "entities": [
    {{"text": "<entity text in original language>", "label": "<PERSON|PRODUCT|COMPANY|TIMELINE|MONEY|OTHER>"}}
  ]
}}

**CRITICAL RULES:**
- Understand the text in its ORIGINAL language ({language_name})
- Do NOT translate - analyze the original meaning directly
- compound score: -1.0 (very negative) to +1.0 (very positive)  
- sentiment_label: positive (>0.2), neutral (-0.2 to 0.2), negative (<-0.2)
- Extract keywords in their ORIGINAL language
- Identify entities in their ORIGINAL language
- Be culturally aware and context-sensitive
- explanation: Write in English to explain the sentiment"""

        return prompt
    
    def _normalize_analysis(self, analysis: Dict, transcript: str) -> Dict:
        """Normalize and validate AI analysis output"""
        
        # Ensure sentiment structure
        sentiment = analysis.get("sentiment", {})
        if not isinstance(sentiment, dict):
            sentiment = {
                "compound": 0.0,
                "sentiment_label": "neutral",
                "explanation": "No sentiment detected"
            }
        
        # Validate compound score
        compound = sentiment.get("compound", 0.0)
        if not isinstance(compound, (int, float)):
            compound = 0.0
        compound = max(-1.0, min(1.0, compound))  # Clamp to [-1, 1]
        
        # Validate sentiment label
        label = sentiment.get("sentiment_label", "neutral")
        if label not in ["positive", "neutral", "negative"]:
            if compound > 0.2:
                label = "positive"
            elif compound < -0.2:
                label = "negative"
            else:
                label = "neutral"
        
        # Ensure keywords structure
        keywords = analysis.get("keywords", {})
        if not isinstance(keywords, dict):
            keywords = {}
        
        # Ensure entities structure
        entities = analysis.get("entities", [])
        if not isinstance(entities, list):
            entities = []
        
        # Validate intent
        valid_intents = [
            "demo_request", "complaint", "pricing_inquiry", "cancellation",
            "information_request", "interest_declaration", "objection", "other"
        ]
        intent = analysis.get("intent", "other")
        if intent not in valid_intents:
            intent = "other"
        
        return {
            "sentiment": {
                "compound": compound,
                "sentiment_label": label,
                "explanation": sentiment.get("explanation", ""),
                # Add legacy VADER-style scores for compatibility
                "pos": max(0.0, compound) if compound > 0 else 0.0,
                "neu": 1.0 if abs(compound) < 0.2 else 0.0,
                "neg": abs(min(0.0, compound)) if compound < 0 else 0.0
            },
            "keywords": keywords,
            "entities": entities,
            "intent": intent
        }
    
    def _analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Analyze sentiment for each segment (for timeline view).
        Uses batch processing for efficiency.
        """
        
        if not segments or len(segments) == 0:
            return []
        
        try:
            # Batch analyze segments (limit to first 10 for performance)
            analyzed_segments = []
            for segment in segments[:10]:
                text = segment.get("text", "")
                if not text or len(text) < 5:
                    continue
                
                # Quick sentiment analysis using simple prompt
                prompt = f"""Analyze sentiment briefly:

Text: "{text}"

Return JSON:
{{
  "compound": <-1.0 to 1.0>,
  "emotion_label": "positive|neutral|negative"
}}"""

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=100,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                
                analyzed_segments.append({
                    "start_time": segment.get("start", 0),
                    "end_time": segment.get("end", 0),
                    "text": text,
                    "sentiment": {
                        "compound": result.get("compound", 0.0)
                    },
                    "emotion_label": result.get("emotion_label", "neutral")
                })
            
            return analyzed_segments
            
        except Exception as e:
            logger.error(f"Segment analysis failed: {e}")
            return []
    
    def _fallback_analysis(self, transcript: str) -> Dict:
        """Fallback analysis if AI fails"""
        
        logger.warning("Using fallback analysis")
        
        # Simple keyword detection
        text_lower = transcript.lower()
        
        # Detect intent
        intent = "other"
        if any(word in text_lower for word in ["demo", "demonstration", "show me"]):
            intent = "demo_request"
        elif any(word in text_lower for word in ["price", "cost", "pricing"]):
            intent = "pricing_inquiry"
        elif any(word in text_lower for word in ["issue", "problem", "not working"]):
            intent = "complaint"
        elif any(word in text_lower for word in ["cancel", "stop", "terminate"]):
            intent = "cancellation"
        
        # Basic sentiment
        positive_words = ["good", "great", "excellent", "happy", "interested", "love"]
        negative_words = ["bad", "poor", "terrible", "frustrated", "angry", "hate"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        compound = (pos_count - neg_count) / max(1, pos_count + neg_count + 1)
        
        if compound > 0.2:
            label = "positive"
        elif compound < -0.2:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "sentiment": {
                "compound": compound,
                "sentiment_label": label,
                "explanation": "Fallback analysis",
                "pos": max(0, compound),
                "neu": 0.5,
                "neg": max(0, -compound)
            },
            "keywords": {},
            "entities": [],
            "intent": intent,
            "segment_sentiments": []
        }
