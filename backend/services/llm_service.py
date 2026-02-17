"""
LLM Intelligence Service
Uses Groq API to generate contextual intelligence and action recommendations.
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime
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
    
    def generate_intelligence(
        self, 
        transcript: str, 
        nlp_analysis: Dict,
        company_context: Optional[str] = None
    ) -> Dict:
        """
        Generate structured intelligence from transcript and NLP analysis.
        
        Args:
            transcript: Full call transcript text
            nlp_analysis: Dictionary containing sentiment, keywords, entities, and intent
            company_context: Optional company policy context from RAG service
            
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
        prompt = self._build_prompt(transcript, sentiment, intent, keywords, entities, company_context)
        
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
        entities: list,
        company_context: Optional[str] = None
    ) -> str:
        """
        Build structured prompt for LLM.
        
        Args:
            transcript: Full transcript
            sentiment: Sentiment analysis results
            intent: Detected intent
            keywords: Detected keywords by category
            entities: Extracted entities
            company_context: Optional company policy context
            
        Returns:
            Formatted prompt string
        """
        
        sentiment_label = sentiment.get("sentiment_label", "neutral")
        sentiment_score = sentiment.get("compound", 0.0)
        
        # Add company context section if available
        context_section = ""
        if company_context:
            context_section = f"\n\n{company_context}\n"
        
        prompt = f"""Analyze this sales/support call and return structured intelligence.
{context_section}
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
    
    def generate_action_email(
        self,
        call_data: Dict
    ) -> str:
        """
        Generate a customer-facing email thanking them for their call and summarizing the conversation.
        This email is sent TO THE CUSTOMER, not internal team.
        """
        
        # Extract key information
        transcript = call_data.get("transcript", "")
        if isinstance(transcript, dict):
            transcript_text = transcript.get("transcript", "")
        else:
            transcript_text = transcript
            
        nlp_analysis = call_data.get("nlp_analysis", {})
        llm_result = call_data.get("llm_output", call_data.get("llm_result", {}))
        final_decision = call_data.get("final_decision", {})
        
        # Extract insights
        sentiment = nlp_analysis.get("sentiment", {})
        call_summary = llm_result.get("call_summary_short", llm_result.get("call_summary", ""))
        recommended_action = final_decision.get("final_action", llm_result.get("recommended_action", ""))
        reasoning = final_decision.get("reasoning", llm_result.get("reasoning", ""))
        priority_level = final_decision.get("priority_level", "medium")
        risk_level = llm_result.get("risk_level", "medium")
        keywords = nlp_analysis.get("keywords", {})
        intent = nlp_analysis.get("intent", "general_inquiry")
        
        # Build AI prompt for customer-facing email
        prompt = f"""You are writing a professional customer-facing email to someone who just had a call with our company.

CALL DETAILS:
- What the customer said: "{transcript_text[:600]}"
- Call Summary: {call_summary}
- Customer's Intent: {intent}
- Topics Discussed: {', '.join([k for cat in keywords.values() for k in cat][:5]) if keywords else 'General conversation'}
- Customer Sentiment: {sentiment.get('sentiment_label', 'neutral')}

TASK: Write a warm, professional email TO THE CUSTOMER with these sections:

1. **Greeting** - Warm greeting thanking them for their call. Use emojis like 👋, 😊, 💙

2. **Call Recap** - Summarize what was discussed in the call. Be specific about what they mentioned (products, concerns, requests, preferences). Write 2-3 sentences. Use relevant emojis like 💬, 🗣️, 📝, ✨

3. **Key Points** - Create 3-5 bullet points with colorful emojis (🎯, 💡, ⭐, 🔥, 🌟, 💎, 🚀, ✅, 📌, 🎨) highlighting:
   - What topics/products they asked about 📦 🛍️
   - Any concerns or questions they raised ❓ 🤔
   - Preferences they mentioned 💎 ❤️
   - Next steps or follow-ups promised ✅ 📅

4. **What We're Doing** - Explain what action we're taking based on their call (without using internal jargon). Be customer-friendly. Add emojis (⚡, 🚀, 👥, 💪, 🎁, 🌈).

5. **Next Steps for Customer** - Tell them what they can expect from us or what they should do next. Use emojis (📅, ⏰, 📞, 💌, 🎯).

6. **Closing** - Warm closing with contact information invitation. Add emojis (💙, 🌟, 👋, 😊, 🙏, ✨).

IMPORTANT REQUIREMENTS:
- Write TO the customer (use "you", "your call", "we're here to help")
- NO internal links or platform URLs
- NO admin/team language
- Friendly, conversational, customer-service tone
- Use LOTS of emojis throughout (at least 20-30 emojis total to make it engaging and fun!)
- Be specific about what was discussed
- Make the customer feel valued and heard
- Keep it concise but warm
- Add emojis to EVERY section, bullet point, and sentence where appropriate

FORMAT:
- Use HTML with inline styles
- Use heading tags (<h2>, <h3>)
- Use bullet points (<ul>, <li>)
- Use colors: Blue (#0284c7), Teal (#0891b2) for accents
- Use <strong> for emphasis
- Good spacing between sections
- Add emojis inline with text

Return ONLY the email content HTML (starting with greeting). No outer html/body tags."""

        try:
            logger.info("Generating customer-facing email content")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly customer service representative writing follow-up emails to customers after their calls. You write warm, professional emails that make customers feel valued and clearly communicate next steps."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,  # More creative for customer-friendly tone
                max_tokens=1200
            )
            
            ai_content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if ai_content.startswith("```html") or ai_content.startswith("```"):
                ai_content = ai_content.replace("```html", "").replace("```", "").strip()
            
            logger.info("Customer email content generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating customer email: {str(e)}")
            # Fallback to basic customer-facing content
            ai_content = f"""
            <div style="padding: 20px;">
                <h2 style="color: #0284c7;">Thank You for Your Call! 📞</h2>
                <p>Dear Valued Customer,</p>
                <p>Thank you for taking the time to speak with us. We appreciate you reaching out to our team.</p>
                <p><strong>Call Summary:</strong> {call_summary}</p>
                <p>We're working on your request and will get back to you shortly.</p>
                <p>If you have any questions, please don't hesitate to contact us.</p>
                <p>Best regards,<br>Customer Service Team</p>
            </div>
            """
        
        # Priority color
        priority_colors = {
            "urgent": "#dc2626",
            "high": "#ea580c",
            "medium": "#f59e0b",
            "low": "#10b981"
        }
        priority_color = priority_colors.get(priority_level.lower(), "#0891b2")
        
        call_id = str(call_data.get("_id", ""))
        filename = call_data.get("filename", "N/A")
        call_id = str(call_data.get("_id", ""))
        filename = call_data.get("filename", "N/A")
        
        # Customer-facing email with company branding
        email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You for Your Call</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdf4 100%);">
    
    <!-- Email Container - Full Width -->
    <table role="presentation" style="width: 100%; border-collapse: collapse; padding: 30px 20px;">
        <tr>
            <td>
                <!-- Email Card - Full Width Responsive -->
                <div style="max-width: 1200px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); border: 1px solid rgba(2, 132, 199, 0.1);">
                    
                    <!-- Header with gradient (customer-friendly) -->
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); padding: 60px 40px; text-align: center; position: relative;">
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: url('data:image/svg+xml;utf8,<svg width=\"100\" height=\"100\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"50\" cy=\"50\" r=\"30\" fill=\"rgba(255,255,255,0.05)\"/></svg>') repeat; opacity: 0.3;"></div>
                        <div style="position: relative; z-index: 1;">
                            <div style="display: inline-block; background: rgba(255, 255, 255, 0.25); padding: 25px; border-radius: 50%; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
                                <svg width="70" height="70" viewBox="0 0 24 24" fill="#ffffff">
                                    <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                                </svg>
                            </div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 38px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                Thank You for Your Call! 📞 ✨
                            </h1>
                            <p style="margin: 20px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 19px; font-weight: 500;">
                                🎉 We appreciate you taking the time to speak with us! 💙
                            </p>
                        </div>
                    </div>
                    
                    <!-- Customer-facing content -->
                    <div style="padding: 50px; color: #1f2937; line-height: 1.8; font-size: 16px;">
                        {ai_content}
                    </div>
                    
                    <!-- Contact Section -->
                    <div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); padding: 35px 50px; border-top: 2px solid #10b981;">
                        <h3 style="margin: 0 0 15px 0; color: #065f46; font-size: 20px; font-weight: 700;">
                            💬 Questions or Need Help? 🤔
                        </h3>
                        <p style="margin: 0; color: #047857; font-size: 16px; line-height: 1.7;">
                            🤝 We're here to help! 🌟 If you have any questions or need further assistance, please don't hesitate to reach out to us. You can reply to this email or contact our support team anytime! 📞 💌
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); padding: 40px 50px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 18px; font-weight: 700;">
                            🚀 Call Intelligence Platform 🎯
                        </p>
                        <p style="margin: 0; color: #9ca3af; font-size: 14px; line-height: 1.7;">
                            ✨ Transforming customer conversations into exceptional service 💼 🌈
                        </p>
                        <p style="margin: 20px 0 0 0; color: #9ca3af; font-size: 12px;">
                            This email was sent to you because you recently had a call with us. 📧 ☎️<br>
                            © {datetime.now().year} Call Intelligence Platform. All rights reserved. 🌟 💫
                        </p>
                    </div>
                    
                </div>
            </td>
        </tr>
    </table>
    
</body>
</html>
        """
        
        return email_html.strip()
