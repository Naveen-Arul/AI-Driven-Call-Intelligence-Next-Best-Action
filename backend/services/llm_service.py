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
        Generate a professional HTML email with AI-written detailed content.
        Uses the website's blue-teal gradient design with rich, contextual information.
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
        
        # Build AI prompt for detailed email content
        prompt = f"""You are writing a detailed professional business email about a customer call analysis.

CALL DATA:
- Transcript: "{transcript_text[:600]}"
- Call Summary: {call_summary}
- Sentiment: Positive {sentiment.get('positive', 0)*100:.0f}%, Neutral {sentiment.get('neutral', 0)*100:.0f}%, Negative {sentiment.get('negative', 0)*100:.0f}%
- Sentiment Label: {sentiment.get('sentiment_label', 'neutral')}
- Intent: {intent}
- Keywords Detected: {', '.join([k for cat in keywords.values() for k in cat][:5]) if keywords else 'None'}
- Recommended Action: {recommended_action}
- AI Reasoning: {reasoning}
- Priority: {priority_level}
- Risk Level: {risk_level}

TASK: Write a DETAILED, CONVERSATIONAL email with these sections:

1. **Customer Call Update Title** - Creative title based on the call type (e.g., "Monitoring Opportunity", "Urgent Action Required", "Sales Opportunity")

2. **Call Summary Section** - Write 2-3 sentences summarizing what happened in the call. Be specific and conversational.

3. **Key Highlights** - Create 3-5 bullet points with emojis about specific things mentioned in the call (topics, products, concerns, requests). Use actual details from the transcript.

4. **Customer Sentiment Section** - Explain the sentiment scores in detail. Discuss what this means for churn risk and sales potential. Use percentages.

5. **Action Required Section** - Clearly state what needs to be done next. Be specific and actionable.

6. **Why This Action?** - Explain the reasoning behind the recommendation. Connect it to the call content and sentiment.

7. **Priority and Risk Section** - Explain why this priority and risk level were assigned.

8. **Next Steps** - Provide clear next steps for the team member.

FORMAT REQUIREMENTS:
- Use HTML with inline styles
- Use website colors: Blue (#0284c7), Teal (#0891b2), Orange (#f59e0b), Red (#dc2626), Green (#10b981)
- Use emojis throughout (🍔, 💬, 📊, 🎯, ⚠️, etc.)
- Make bullet points with <li> tags
- Use <strong> for emphasis
- Keep paragraphs clear with good spacing
- Be conversational but professional
- Include specific details from the transcript

IMPORTANT: Return ONLY the email content HTML (div elements with inline styles). No <html>, <head>, or <body> tags. Start directly with a div."""

        try:
            logger.info("Generating AI-powered detailed email content")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business email writer who creates detailed, engaging emails with specific insights from customer calls. You write in a friendly but professional tone with clear structure and actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # More creative for detailed content
                max_tokens=1500   # Longer for detailed email
            )
            
            ai_content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if ai_content.startswith("```html") or ai_content.startswith("```"):
                ai_content = ai_content.replace("```html", "").replace("```", "").strip()
            
            logger.info("Detailed email content generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating detailed email content: {str(e)}")
            # Fallback to basic content
            ai_content = f"""
            <div style="padding: 20px;">
                <h2 style="color: #0284c7;">📞 Customer Call Update</h2>
                <p><strong>Call Summary:</strong> {call_summary}</p>
                <p><strong>Recommended Action:</strong> {recommended_action}</p>
                <p><strong>Priority:</strong> {priority_level.upper()} | <strong>Risk:</strong> {risk_level.upper()}</p>
            </div>
            """
        
        # Priority color matching website design
        priority_colors = {
            "urgent": "#dc2626",
            "high": "#ea580c",
            "medium": "#f59e0b",
            "low": "#10b981"
        }
        priority_color = priority_colors.get(priority_level.lower(), "#0891b2")
        
        # Wrap AI content in website-styled email template
        call_id = str(call_data.get("_id", ""))
        filename = call_data.get("filename", "N/A")
        # Wrap AI content in website-styled email template
        call_id = str(call_data.get("_id", ""))
        filename = call_data.get("filename", "N/A")
        
        email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Intelligence Platform - Call Analysis</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
    
    <!-- Main Container -->
    <table role="presentation" style="width: 100%; border-collapse: collapse; padding: 40px 20px;">
        <tr>
            <td>
                <!-- Email Card -->
                <div style="max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);">
                    
                    <!-- Header with Gradient (matching website) -->
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); padding: 40px 30px; text-align: center;">
                        <div style="display: inline-block; background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 50%; margin-bottom: 20px;">
                            <svg width="50" height="50" viewBox="0 0 24 24" fill="#ffffff">
                                <path d="M12 14l9-5-9-5-9 5 9 5z"/>
                                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
                            </svg>
                        </div>
                        <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                            Call Intelligence Platform
                        </h1>
                        <p style="margin: 10px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 16px; font-weight: 500;">
                            AI-Powered Call Analysis Report
                        </p>
                    </div>
                    
                    <!-- Priority Banner -->
                    <div style="background-color: {priority_color}; padding: 16px 30px; text-align: center;">
                        <span style="color: #ffffff; font-weight: 700; font-size: 14px; letter-spacing: 0.5px; text-transform: uppercase;">
                            ⚡ Priority: {priority_level.upper()} | Risk: {risk_level.upper()}
                        </span>
                    </div>
                    
                    <!-- AI-Generated Content -->
                    <div style="padding: 35px 30px; color: #1f2937; line-height: 1.7; font-size: 15px;">
                        {ai_content}
                    </div>
                    
                    <!-- Interactive Button -->
                    <div style="padding: 0 30px 30px 30px; text-align: center;">
                        <a href="http://localhost:3000/calls/{call_id}" 
                           style="display: inline-block; 
                                  background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); 
                                  color: #ffffff; 
                                  padding: 16px 40px; 
                                  text-decoration: none; 
                                  border-radius: 8px; 
                                  font-weight: 700; 
                                  font-size: 16px; 
                                  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
                                  letter-spacing: 0.3px;">
                            View Full Call Details in Platform →
                        </a>
                    </div>
                    
                    <!-- Call Metadata -->
                    <div style="background: #f9fafb; padding: 20px 30px; border-top: 1px solid #e5e7eb;">
                        <table style="width: 100%; font-size: 12px; color: #6b7280;">
                            <tr>
                                <td style="padding: 5px 0;">📅 <strong>Processed:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 5px 0;">🆔 <strong>Call ID:</strong> {call_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 5px 0;">📞 <strong>File:</strong> {filename}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); padding: 25px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 14px; font-weight: 600;">
                            Call Intelligence Platform
                        </p>
                        <p style="margin: 0; color: #9ca3af; font-size: 12px; line-height: 1.5;">
                            Transforming call recordings into automated business intelligence<br>
                            <em>This is an automated AI-generated email based on call analysis</em>
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
