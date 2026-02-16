"""
Email Service for Call Intelligence Platform
Sends professional HTML emails with call analysis results
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL", "naveenarul111@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_email(self, to_email: str, subject: str, html_content: str) -> Dict:
        """Send HTML email via Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"Call Intelligence Platform <{self.sender_email}>"
            message["To"] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return {
                "status": "success",
                "message": f"Email sent to {to_email}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def create_action_email(self, call_data: Dict, recipient_email: str) -> str:
        """Generate HTML email for recommended action"""
        
        final_decision = call_data.get("final_decision", {})
        nlp = call_data.get("nlp_analysis", {})
        sentiment = nlp.get("sentiment", {})
        
        # Color based on priority
        priority_colors = {
            "urgent": "#dc2626",
            "high": "#ea580c",
            "medium": "#f59e0b",
            "low": "#10b981"
        }
        priority_level = final_decision.get("priority_level", "medium")
        priority_color = priority_colors.get(priority_level, "#0891b2")
        
        # Risk badge color
        risk_colors = {
            "high": "#dc2626",
            "medium": "#f59e0b",
            "low": "#10b981"
        }
        risk_level = call_data.get("llm_result", {}).get("risk_level", "medium")
        risk_color = risk_colors.get(risk_level, "#6b7280")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); padding: 40px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                🎯 Action Required
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #e0f2fe; font-size: 16px;">
                                Call Intelligence Platform - Automated Analysis
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Priority Banner -->
                    <tr>
                        <td style="padding: 0;">
                            <div style="background-color: {priority_color}; color: #ffffff; padding: 16px 40px; text-align: center; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">
                                ⚡ Priority: {priority_level} | Score: {final_decision.get('priority_score', 0)}/100
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <!-- Recommended Action -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 24px; border-radius: 8px; border-left: 4px solid #0284c7;">
                                        <h2 style="margin: 0 0 12px 0; color: #0c4a6e; font-size: 18px; font-weight: 600;">
                                            📋 Recommended Action
                                        </h2>
                                        <p style="margin: 0; color: #0369a1; font-size: 16px; line-height: 1.6; font-weight: 500;">
                                            {final_decision.get('final_action', 'No action specified')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Key Insights Grid -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="width: 50%; padding-right: 8px;">
                                        <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; text-align: center;">
                                            <div style="font-size: 14px; color: #92400e; font-weight: 600; margin-bottom: 8px;">ASSIGNED TO</div>
                                            <div style="font-size: 18px; color: #78350f; font-weight: 700;">{final_decision.get('assigned_to', 'N/A')}</div>
                                        </div>
                                    </td>
                                    <td style="width: 50%; padding-left: 8px;">
                                        <div style="background-color: {risk_color}22; padding: 20px; border-radius: 8px; text-align: center;">
                                            <div style="font-size: 14px; color: {risk_color}; font-weight: 600; margin-bottom: 8px;">RISK LEVEL</div>
                                            <div style="font-size: 18px; color: {risk_color}; font-weight: 700; text-transform: uppercase;">{risk_level}</div>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Call Summary -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="background-color: #f9fafb; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                                        <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 16px; font-weight: 600;">
                                            💬 Call Summary
                                        </h3>
                                        <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.6;">
                                            {call_data.get('llm_result', {}).get('call_summary', 'No summary available')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Sentiment Analysis -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td>
                                        <h3 style="margin: 0 0 16px 0; color: #1f2937; font-size: 16px; font-weight: 600;">
                                            📊 Sentiment Analysis
                                        </h3>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <table role="presentation" style="width: 100%;">
                                            <tr>
                                                <td style="width: 33.33%; padding: 12px; background-color: #dcfce7; border-radius: 6px; text-align: center;">
                                                    <div style="font-size: 12px; color: #166534; margin-bottom: 4px;">Positive</div>
                                                    <div style="font-size: 20px; color: #15803d; font-weight: 700;">{int(sentiment.get('positive', 0) * 100)}%</div>
                                                </td>
                                                <td style="width: 33.33%; padding: 12px; background-color: #fef3c7; border-radius: 6px; text-align: center;">
                                                    <div style="font-size: 12px; color: #92400e; margin-bottom: 4px;">Neutral</div>
                                                    <div style="font-size: 20px; color: #a16207; font-weight: 700;">{int(sentiment.get('neutral', 0) * 100)}%</div>
                                                </td>
                                                <td style="width: 33.33%; padding: 12px; background-color: #fee2e2; border-radius: 6px; text-align: center;">
                                                    <div style="font-size: 12px; color: #991b1b; margin-bottom: 4px;">Negative</div>
                                                    <div style="font-size: 20px; color: #b91c1c; font-weight: 700;">{int(sentiment.get('negative', 0) * 100)}%</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Transcript Preview -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="background-color: #f9fafb; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                                        <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 16px; font-weight: 600;">
                                            📝 Transcript Preview
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 13px; line-height: 1.6; font-style: italic;">
                                            {call_data.get('transcript', {}).get('transcript', 'No transcript available')[:300]}...
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Reasoning -->
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                        <h3 style="margin: 0 0 12px 0; color: #78350f; font-size: 16px; font-weight: 600;">
                                            🧠 AI Reasoning
                                        </h3>
                                        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
                                            {final_decision.get('reasoning', 'No reasoning provided')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Action Button -->
                            <table role="presentation" style="width: 100%; margin-bottom: 20px;">
                                <tr>
                                    <td style="text-align: center; padding: 20px 0;">
                                        <a href="http://localhost:3000/calls" style="display: inline-block; background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); color: #ffffff; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(2,132,199,0.3);">
                                            View Full Details →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Processing Info -->
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td style="padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
                                        <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                            📅 Processed: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
                                            🆔 Call ID: {call_data.get('_id', 'N/A')}<br>
                                            📞 Filename: {call_data.get('filename', 'N/A')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; font-weight: 600;">
                                Call Intelligence Platform
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                Transforming call recordings into automated business intelligence
                            </p>
                            <p style="margin: 16px 0 0 0; color: #9ca3af; font-size: 11px;">
                                This is an automated message. Please do not reply to this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        return html
    
    def create_reminder_email(self, call_data: Dict, reminder_type: str = "follow_up") -> str:
        """Generate HTML email for reminders"""
        
        final_decision = call_data.get("final_decision", {})
        
        reminder_titles = {
            "follow_up": "⏰ Follow-Up Reminder",
            "urgent": "🚨 Urgent Action Required",
            "escalation": "⚠️ Escalation Reminder"
        }
        
        title = reminder_titles.get(reminder_type, "📅 Reminder")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%); padding: 40px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                {title}
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #fef2f2; font-size: 16px;">
                                This action requires your immediate attention
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); padding: 24px; border-radius: 8px; border-left: 4px solid #dc2626;">
                                        <h2 style="margin: 0 0 12px 0; color: #7f1d1d; font-size: 18px; font-weight: 600;">
                                            ⏰ Pending Action
                                        </h2>
                                        <p style="margin: 0; color: #991b1b; font-size: 16px; line-height: 1.6; font-weight: 500;">
                                            {final_decision.get('final_action', 'No action specified')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">
                                This call was processed on <strong>{datetime.now().strftime('%B %d, %Y')}</strong> 
                                and requires action from <strong>{final_decision.get('assigned_to', 'your team')}</strong>.
                            </p>
                            
                            <table role="presentation" style="width: 100%; margin-bottom: 30px;">
                                <tr>
                                    <td style="text-align: center; padding: 20px 0;">
                                        <a href="http://localhost:3000/calls" style="display: inline-block; background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%); color: #ffffff; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(220,38,38,0.3);">
                                            Take Action Now →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="color: #6b7280; font-size: 12px; text-align: center; margin: 0;">
                                🆔 Call ID: {call_data.get('_id', 'N/A')}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                Call Intelligence Platform - Automated Reminders
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        return html
    
    def send_action_notification(self, call_data: Dict, recipient_email: str) -> Dict:
        """Send action notification email"""
        subject = f"🎯 Action Required: {call_data.get('final_decision', {}).get('priority_level', 'MEDIUM').upper()} Priority Call"
        html_content = self.create_action_email(call_data, recipient_email)
        return self.send_email(recipient_email, subject, html_content)
    
    def send_reminder(self, call_data: Dict, recipient_email: str, reminder_type: str = "follow_up") -> Dict:
        """Send reminder email"""
        subject = f"⏰ Reminder: Pending Action on Call {call_data.get('filename', 'N/A')}"
        html_content = self.create_reminder_email(call_data, reminder_type)
        return self.send_email(recipient_email, subject, html_content)

# Global instance
email_service = EmailService()
