"""
LLM Intelligence Service
Uses Groq API to generate contextual intelligence and action recommendations.
"""

import os
import json
import logging
from typing import Dict, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for generating AI-powered call intelligence using Groq LLM.
    Combines transcript and NLP signals to produce structured insights.
    """
    
    def __init__(self):
        """Initialize Groq client and model configuration"""
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        self.temperature = 0.2
        self.max_tokens = 800
        
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    def generate_intelligence(self, transcript: str, nlp_analysis: Dict) -> Dict:
        """
        Generate structured intelligence from transcript and NLP analysis.
        
        Args:
            transcript: Full call transcript text
            nlp_analysis: Dictionary containing sentiment, keywords, entities, and intent
            
        Returns:
            {
                "call_summary_short": str,
                "call_summary_detailed": str,
                "risk_level": "low" | "medium" | "high",
                "opportunity_level": "low" | "medium" | "high",
                "recommended_action": str,
                "priority_score": int (0-100),
                "reasoning": str
            }
        """
        
        # Extract NLP signals
        sentiment = nlp_analysis.get("sentiment", {})
        intent = nlp_analysis.get("intent", "unknown")
        keywords = nlp_analysis.get("keywords", {})
        entities = nlp_analysis.get("entities", [])
        
        # Build structured prompt
        prompt = self._build_prompt(transcript, sentiment, intent, keywords, entities)
        
        try:
            logger.info(f"Generating intelligence for intent: {intent}")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an enterprise call intelligence AI. Analyze calls and provide structured business insights in JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            intelligence = json.loads(content)
            
            # Validate required fields
            required_fields = [
                "call_summary_short",
                "call_summary_detailed", 
                "risk_level",
                "opportunity_level",
                "recommended_action",
                "priority_score",
                "reasoning"
            ]
            
            for field in required_fields:
                if field not in intelligence:
                    intelligence[field] = "N/A"
            
            # Ensure priority_score is integer
            if isinstance(intelligence.get("priority_score"), str):
                try:
                    intelligence["priority_score"] = int(intelligence["priority_score"])
                except:
                    intelligence["priority_score"] = 50
            
            logger.info(f"Intelligence generated successfully - Priority: {intelligence.get('priority_score')}")
            
            return intelligence
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            return {
                "error": "JSON parsing failed",
                "details": str(e),
                "raw_response": content if 'content' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"LLM intelligence generation failed: {e}")
            return {
                "error": "LLM processing failed",
                "details": str(e)
            }
    
    def _build_prompt(
        self,
        transcript: str,
        sentiment: Dict,
        intent: str,
        keywords: Dict,
        entities: list
    ) -> str:
        """
        Build structured prompt for LLM.
        
        Args:
            transcript: Full transcript
            sentiment: Sentiment analysis results
            intent: Detected intent
            keywords: Detected keywords by category
            entities: Extracted entities
            
        Returns:
            Formatted prompt string
        """
        
        sentiment_label = sentiment.get("sentiment_label", "neutral")
        sentiment_score = sentiment.get("compound", 0.0)
        
        prompt = f"""Analyze this sales/support call and return structured intelligence.

**CALL TRANSCRIPT:**
{transcript}

**DETERMINISTIC NLP SIGNALS:**
- Sentiment: {sentiment_label} (score: {sentiment_score})
- Detected Intent: {intent}
- Keywords Found: {json.dumps(keywords, indent=2)}
- Entities Extracted: {json.dumps(entities, indent=2)}

**TASK:**
Return STRICT JSON with the following structure:

{{
  "call_summary_short": "One-sentence summary of the call",
  "call_summary_detailed": "Detailed paragraph summary with key points",
  "risk_level": "low | medium | high",
  "opportunity_level": "low | medium | high",
  "recommended_action": "Specific next action to take",
  "priority_score": <integer 0-100>,
  "reasoning": "Brief explanation of priority and recommendation"
}}

**RULES:**
- risk_level: Assess churn risk, complaint severity, or dissatisfaction
- opportunity_level: Assess sales potential, upsell chance, or qualified lead quality
- recommended_action: Be specific and actionable (e.g., "Schedule demo for next Tuesday", "Escalate to retention manager immediately")
- priority_score: 0=lowest, 100=highest urgency
- Consider: sentiment + intent + keywords when determining priority
- Churn risk = high priority
- Demo requests with positive sentiment = high opportunity
- Complaints = high risk + medium-high priority

Return ONLY valid JSON. No markdown, no explanation, just JSON.
"""
        
        return prompt
