"""
NLP Analysis Service
Performs deterministic sentiment, keyword, entity, and intent analysis.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List
import re

# Try to import spaCy, but make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Warning: spaCy not available ({e}). Entity extraction will use regex fallback.")
    SPACY_AVAILABLE = False


class NLPService:
    """
    Service for analyzing call transcripts using deterministic NLP methods.
    Provides sentiment, keyword detection, entity extraction, and intent classification.
    """
    
    def __init__(self):
        """Initialize NLP models and business keyword dictionary"""
        print("Loading NLP models...")
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Load spaCy model for entity recognition (if available)
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("spaCy model loaded successfully")
            except OSError:
                print("Warning: en_core_web_sm not found. Using regex-based entity extraction.")
                self.nlp = None
        else:
            self.nlp = None
        
        # Business keyword dictionary
        self.keyword_dict = {
            "demo": ["demo", "demonstration", "presentation", "walkthrough", "show me"],
            "pricing": ["price", "cost", "budget", "fee", "payment", "how much", "expensive", "cheap"],
            "complaint": ["issue", "problem", "not working", "broken", "error", "bug", "frustrated"],
            "cancellation": ["cancel", "terminate", "stop", "discontinue", "unsubscribe"],
            "competitor": ["competitor", "alternative", "other company", "versus", "compare"],
            "urgency": ["urgent", "asap", "immediately", "right now", "today", "emergency"],
            "interest": ["interested", "want to", "would like", "looking for", "need"],
            "objection": ["concerned", "worried", "not sure", "hesitant", "doubt"],
            "timeline": ["next week", "next month", "tomorrow", "soon", "later"],
            "decision_maker": ["manager", "boss", "team", "decision", "approval"]
        }
        
        print("NLP models loaded successfully")
    
    def analyze(self, transcript: str, segments: List[Dict] = None) -> Dict:
        """
        Analyze a call transcript and extract structured insights.
        
        Args:
            transcript: Full text transcript of the call
            segments: Optional list of timestamped segments for granular analysis
            
        Returns:
            {
                "sentiment": {
                    "compound": float,
                    "pos": float,
                    "neu": float,
                    "neg": float,
                    "sentiment_label": str
                },
                "keywords": {
                    "category": [list of detected words]
                },
                "entities": [
                    {"text": str, "label": str}
                ],
                "intent": str,
                "segment_sentiments": [
                    {
                        "start_time": float,
                        "end_time": float,
                        "text": str,
                        "sentiment": {...},
                        "emotion_label": str
                    }
                ]
            }
        """
        
        # --- Sentiment Analysis ---
        sentiment_scores = self.sentiment_analyzer.polarity_scores(transcript)
        compound = sentiment_scores["compound"]
        
        # Classify sentiment based on compound score
        if compound >= 0.05:
            sentiment_label = "positive"
        elif compound <= -0.05:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        sentiment_result = {
            "compound": sentiment_scores["compound"],
            "positive": sentiment_scores["pos"],
            "neutral": sentiment_scores["neu"],
            "negative": sentiment_scores["neg"],
            "sentiment_label": sentiment_label
        }
        
        # --- Segment-Level Sentiment Analysis ---
        segment_sentiments = []
        if segments:
            for segment in segments:
                seg_sentiment = self.sentiment_analyzer.polarity_scores(segment.get("text", ""))
                seg_compound = seg_sentiment["compound"]
                
                # Determine emotion label
                if seg_compound >= 0.5:
                    emotion = "happy"
                    emoji = "😊"
                elif seg_compound >= 0.05:
                    emotion = "satisfied"
                    emoji = "😌"
                elif seg_compound <= -0.5:
                    emotion = "angry"
                    emoji = "😠"
                elif seg_compound <= -0.05:
                    emotion = "frustrated"
                    emoji = "😐"
                else:
                    emotion = "neutral"
                    emoji = "😶"
                
                segment_sentiments.append({
                    "start_time": segment.get("start_time", 0),
                    "end_time": segment.get("end_time", 0),
                    "text": segment.get("text", ""),
                    "sentiment": {
                        "compound": seg_compound,
                        "positive": seg_sentiment["pos"],
                        "neutral": seg_sentiment["neu"],
                        "negative": seg_sentiment["neg"]
                    },
                    "emotion_label": emotion,
                    "emoji": emoji
                })
        
        # --- Keyword Detection ---
        transcript_lower = transcript.lower()
        detected_keywords = {}
        
        for category, keywords in self.keyword_dict.items():
            matches = [word for word in keywords if word in transcript_lower]
            if matches:
                detected_keywords[category] = matches
        
        # --- Entity Recognition ---
        if self.nlp is not None:
            # Use spaCy for entity extraction
            doc = self.nlp(transcript)
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "MONEY", "DATE", "GPE", "PRODUCT"]:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_
                    })
        else:
            # Fallback: regex-based entity extraction
            entities = self._extract_entities_regex(transcript)
        
        # --- Intent Classification (Rule-Based) ---
        intent = self._classify_intent(detected_keywords, sentiment_label)
        
        return {
            "sentiment": sentiment_result,
            "keywords": detected_keywords,
            "entities": entities,
            "intent": intent,
            "segment_sentiments": segment_sentiments
        }
    
    def _classify_intent(self, keywords: Dict, sentiment: str) -> str:
        """
        Classify call intent based on detected keywords and sentiment.
        
        Args:
            keywords: Detected keywords by category
            sentiment: Sentiment label (positive/neutral/negative)
            
        Returns:
            Intent classification string
        """
        
        # High priority - Churn risk
        if sentiment == "negative" and "cancellation" in keywords:
            return "churn_risk"
        
        # Demo request
        if "demo" in keywords:
            return "demo_request"
        
        # Pricing inquiry
        if "pricing" in keywords:
            return "pricing_inquiry"
        
        # Complaint
        if "complaint" in keywords or (sentiment == "negative" and len(keywords) > 0):
            return "complaint"
        
        # Interest/Lead
        if "interest" in keywords and sentiment == "positive":
            return "qualified_lead"
        
        # Objection handling needed
        if "objection" in keywords:
            return "objection_handling"
        
        # Competitor comparison
        if "competitor" in keywords:
            return "competitor_comparison"
        
        # Urgent follow-up
    
    def _extract_entities_regex(self, text: str) -> List[Dict]:
        """
        Fallback entity extraction using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            List of entities with text and label
        """
        entities = []
        
        # Money patterns ($100, $1,000, etc.)
        money_pattern = r'\$[\d,]+(?:\.\d{2})?'
        for match in re.finditer(money_pattern, text):
            entities.append({
                "text": match.group(),
                "label": "MONEY"
            })
        
        # Date patterns (simple)
        date_patterns = [
            r'\b(?:next|last)\s+(?:week|month|year|monday|tuesday|wednesday|thursday|friday)\b',
            r'\b(?:today|tomorrow|yesterday)\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
        ]
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "text": match.group(),
                    "label": "DATE"
                })
        
        return entities
        if "urgency" in keywords:
            return "urgent_followup"
        
        # Default
        return "general_inquiry"
