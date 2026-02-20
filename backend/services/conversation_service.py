"""
Conversation Service for Voice Bot
Handles multi-turn conversations with customer context and intelligent responses
"""

import logging
from typing import Dict, List
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ConversationService:
    """
    Manages conversations with customers during voice calls
    Maintains context and generates contextually relevant responses
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"
        self.active_conversations = {}  # Store conversation history by call_sid
        logger.info("✅ Conversation Service initialized with Groq LLM")
    
    def start_conversation(self, call_sid: str, language: str = "en", customer_phone: str = None):
        """
        Initialize a new conversation session
        
        Args:
            call_sid: Unique call identifier
            language: Customer's language
            customer_phone: Customer's phone number (optional)
        """
        self.active_conversations[call_sid] = {
            "messages": [],
            "language": language,
            "language_name": self._get_language_name(language),
            "customer_phone": customer_phone,
            "customer_info": {},
            "issues_discussed": [],
            "sentiment": "neutral"
        }
        logger.info(f"🆕 Started conversation {call_sid} in {language}")
    
    def get_ai_response(
        self,
        call_sid: str,
        customer_input: str,
        language: str = None
    ) -> Dict[str, str]:
        """
        Generate AI response to customer input
        
        Args:
            call_sid: Call session ID
            customer_input: What customer said
            language: Language code (optional - will use conversation's language if not provided)
            
        Returns:
            Dict with response, sentiment, and intent
        """
        try:
            # Get or create conversation context
            if call_sid not in self.active_conversations:
                self.start_conversation(call_sid, language or "en")
            
            conversation = self.active_conversations[call_sid]
            
            # Update language if provided and different
            if language and language != conversation["language"]:
                conversation["language"] = language
                conversation["language_name"] = self._get_language_name(language)
                logger.info(f"🔄 Updated conversation language to {language}")
            
            language_name = conversation["language_name"]
            
            # Add customer message to history
            conversation["messages"].append({
                "role": "user",
                "content": customer_input
            })
            
            # Build system prompt
            system_prompt = self._build_system_prompt(language_name)
            
            # Build conversation history for context
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation["messages"])
            
            logger.info(f"🤖 Generating AI response for: '{customer_input[:50]}...'")
            
            # Get AI response
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200,  # Keep responses concise for voice
                stream=False
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to history
            conversation["messages"].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Detect intent and sentiment
            analysis = self._analyze_input(customer_input)
            conversation["sentiment"] = analysis["sentiment"]
            
            logger.info(f"✅ AI Response: '{ai_response[:50]}...'")
            
            return {
                "response": ai_response,
                "sentiment": analysis["sentiment"],
                "intent": analysis["intent"],
                "should_escalate": analysis["should_escalate"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating AI response: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return fallback response instead of crashing
            return {
                "response": "I apologize, I'm having trouble processing your request. Could you please repeat that?",
                "sentiment": "neutral",
                "intent": "error",
                "should_escalate": False
            }
    
    def _build_system_prompt(self, language_name: str) -> str:
        """Build system prompt for AI assistant"""
        
        if language_name != "English":
            language_instruction = f"""
CRITICAL: Respond in {language_name} language ONLY.
The customer is speaking in {language_name}, so you must reply in {language_name}.
"""
        else:
            language_instruction = "Respond in English."
        
        return f"""You are a helpful customer service AI assistant for a company.

{language_instruction}

Your role:
1. Listen to customer questions, complaints, or requests
2. Provide helpful, empathetic, and professional responses
3. Keep responses CONCISE (2-3 sentences max) - this is a phone call
4. If you cannot resolve the issue, offer to escalate to a human agent
5. Be warm, friendly, and solution-oriented

Guidelines:
- ALWAYS respond in {language_name}
- For complaints: Show empathy, apologize, offer solutions
- For questions: Provide clear, helpful information
- For technical issues: Gather details, offer troubleshooting or escalation
- For sales inquiries: Highlight benefits, offer to connect with sales team
- Keep tone conversational and natural (this is voice, not text)
- Use simple language, avoid jargon
- If customer seems frustrated, offer immediate escalation

Remember: You're speaking on a phone call. Be concise and natural!"""
    
    def _analyze_input(self, text: str) -> Dict:
        """
        Quick sentiment and intent analysis
        
        Args:
            text: Customer input
            
        Returns:
            Dict with sentiment, intent, and escalation flag
        """
        text_lower = text.lower()
        
        # Sentiment detection (simple keyword-based)
        negative_words = ["angry", "frustrated", "terrible", "worst", "hate", "cancel", 
                         "refund", "complaint", "disappointed", "unacceptable"]
        positive_words = ["great", "excellent", "wonderful", "happy", "satisfied", 
                         "thank", "appreciate", "love", "perfect"]
        
        sentiment = "neutral"
        if any(word in text_lower for word in negative_words):
            sentiment = "negative"
        elif any(word in text_lower for word in positive_words):
            sentiment = "positive"
        
        # Intent detection
        intent = "general_inquiry"
        if "cancel" in text_lower or "refund" in text_lower:
            intent = "cancellation"
        elif "problem" in text_lower or "issue" in text_lower or "not working" in text_lower:
            intent = "technical_issue"
        elif "price" in text_lower or "cost" in text_lower or "buy" in text_lower:
            intent = "pricing_inquiry"
        elif "demo" in text_lower or "trial" in text_lower:
            intent = "demo_request"
        
        # Escalation logic
        should_escalate = False
        escalation_triggers = ["speak to manager", "human", "agent", "escalate", 
                              "not helping", "transfer"]
        if any(trigger in text_lower for trigger in escalation_triggers) or sentiment == "negative":
            should_escalate = True
        
        return {
            "sentiment": sentiment,
            "intent": intent,
            "should_escalate": should_escalate
        }
    
    def get_conversation_summary(self, call_sid: str) -> Dict:
        """
        Get summary of conversation for saving to database
        
        Args:
            call_sid: Call session ID
            
        Returns:
            Conversation summary
        """
        if call_sid not in self.active_conversations:
            return {}
        
        conversation = self.active_conversations[call_sid]
        
        # Build full transcript
        transcript = "\n\n".join([
            f"{'Customer' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in conversation["messages"]
        ])
        
        return {
            "transcript": transcript,
            "language": conversation["language"],
            "language_name": conversation["language_name"],
            "message_count": len(conversation["messages"]),
            "final_sentiment": conversation["sentiment"]
        }
    
    def end_conversation(self, call_sid: str):
        """
        Clean up conversation data
        
        Args:
            call_sid: Call session ID
        """
        if call_sid in self.active_conversations:
            del self.active_conversations[call_sid]
            logger.info(f"🔚 Ended conversation {call_sid}")
    
    def _get_language_name(self, lang_code: str) -> str:
        """Convert language code to full name"""
        lang_map = {
            "en": "English",
            "ta": "Tamil",
            "hi": "Hindi",
            "ml": "Malayalam",
            "te": "Telugu",
            "es": "Spanish",
            "fr": "French"
        }
        return lang_map.get(lang_code, "English")

# Global instance
conversation_service = ConversationService()
