"""
Email Service for Call Intelligence Platform
Sends professional HTML emails with AI-generated content based on call analysis
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, llm_service=None):
        self.sender_email = os.getenv("SENDER_EMAIL", "naveenarul111@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587  # TLS
        self.smtp_port_ssl = 465  # SSL fallback
        self.llm_service = llm_service  # For AI-generated email content
        self.enabled = bool(self.sender_password)  # Only enable if password is set
        
        if not self.enabled:
            logger.warning("⚠️ Email service disabled: SENDER_PASSWORD not configured")
        
    def send_email(self, to_email: str, subject: str, html_content: str) -> Dict:
        """Send HTML email via Gmail SMTP with multiple retry strategies"""
        
        # Check if email is configured
        if not self.enabled:
            logger.warning("Email not sent: Service not configured (missing SENDER_PASSWORD)")
            return {
                "status": "warning",
                "message": "Email feature disabled. Configure SENDER_EMAIL and SENDER_PASSWORD in .env to enable. See EMAIL_SETUP_GUIDE.md",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"Call Intelligence Platform <{self.sender_email}>"
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Strategy 1: Try TLS on port 587
        try:
            logger.info(f"Attempting to send email via TLS (port 587)...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return {
                "status": "success",
                "message": f"Email sent to {to_email}",
                "timestamp": datetime.now().isoformat()
            }
        except smtplib.SMTPAuthenticationError:
            logger.error("Authentication failed")
            return {
                "status": "error",
                "message": "Email authentication failed. For Gmail, use an App Password (not your regular password). See EMAIL_SETUP_GUIDE.md for setup instructions.",
                "timestamp": datetime.now().isoformat()
            }
        except (TimeoutError, OSError, ConnectionError) as e:
            logger.warning(f"TLS connection failed: {str(e)}, trying SSL...")
            
            # Strategy 2: Try SSL on port 465
            try:
                logger.info(f"Attempting to send email via SSL (port 465)...")
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl, timeout=15, context=context) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
                
                logger.info(f"✅ Email sent successfully to {to_email} via SSL")
                return {
                    "status": "success",
                    "message": f"Email sent to {to_email} (SSL)",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as ssl_error:
                logger.error(f"SSL connection also failed: {str(ssl_error)}")
                return {
                    "status": "error",
                    "message": f"Cannot connect to Gmail SMTP server. Possible causes: 1) Firewall blocking ports 587/465, 2) No internet connection, 3) Corporate network restrictions. Error: {str(ssl_error)[:100]}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return {
                "status": "error",
                "message": f"Email error: {str(e)[:200]}",
                "timestamp": datetime.now().isoformat()
            }
    
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
        """
        Send action notification email with AI-generated content based on call data.
        The email content is dynamically generated by AI when this method is called.
        """
        priority_level = call_data.get("final_decision", {}).get("priority_level", "MEDIUM")
        subject = f"🎯 Action Required: {priority_level.upper()} Priority Call"
        
        # Generate email content using AI
        if self.llm_service:
            try:
                html_content = self.llm_service.generate_action_email(call_data)
            except Exception as e:
                # Fallback to simple template if AI generation fails
                html_content = self._create_fallback_email(call_data)
        else:
            html_content = self._create_fallback_email(call_data)
        
        return self.send_email(recipient_email, subject, html_content)
    
    def _create_fallback_email(self, call_data: Dict) -> str:
        """Customer-facing fallback email if LLM generation fails"""
        final_decision = call_data.get("final_decision", {})
        llm_result = call_data.get("llm_output", call_data.get("llm_result", {}))
        call_id = str(call_data.get("_id", ""))
        
        return f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6;">
    <table role="presentation" style="width: 100%; padding: 40px 20px;">
        <tr>
            <td>
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%); padding: 40px 30px; text-align: center;">
                        <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: 700;">
                            Thank You for Your Call! 📞
                        </h1>
                        <p style="margin: 10px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 15px;">
                            We appreciate you taking the time to speak with us
                        </p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 35px;">
                        <p style="color: #1f2937; font-size: 15px; line-height: 1.7; margin: 0 0 20px 0;">
                            Dear Valued Customer,
                        </p>
                        
                        <p style="color: #1f2937; font-size: 15px; line-height: 1.7; margin: 0 0 20px 0;">
                            Thank you for your recent call with our team. We wanted to follow up and let you know that we've received your inquiry and are working on it.
                        </p>
                        
                        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-left: 4px solid #0284c7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin: 0 0 10px 0; color: #0c4a6e; font-size: 16px;">📋 What We Discussed</h3>
                            <p style="margin: 0; color: #0369a1; font-size: 14px; line-height: 1.6;">
                                {llm_result.get('call_summary', 'We discussed your inquiry and concerns during our conversation.')}
                            </p>
                        </div>
                        
                        <p style="color: #1f2937; font-size: 15px; line-height: 1.7; margin: 20px 0;">
                            Our team is reviewing your request and will get back to you shortly with next steps.
                        </p>
                    </div>
                    
                    <!-- Contact Section -->
                    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 25px 35px; border-top: 1px solid #e5e7eb;">
                        <h3 style="margin: 0 0 10px 0; color: #0c4a6e; font-size: 16px;">📧 Need Help?</h3>
                        <p style="margin: 0; color: #0369a1; font-size: 14px; line-height: 1.6;">
                            If you have any questions, please reply to this email or contact our support team.
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background: #f9fafb; padding: 25px 35px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0 0 5px 0; color: #6b7280; font-size: 14px; font-weight: 600;">
                            Call Intelligence Platform
                        </p>
                        <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                            Transforming customer conversations into exceptional service
                        </p>
                    </div>
                    
                </div>
            </td>
        </tr>
    </table>
</body>
</html>
        """
    
    def send_reminder(self, call_data: Dict, recipient_email: str, reminder_type: str = "follow_up") -> Dict:
        """Send reminder email"""
        subject = f"⏰ Reminder: Pending Action on Call {call_data.get('filename', 'N/A')}"
        html_content = self.create_reminder_email(call_data, reminder_type)
        return self.send_email(recipient_email, subject, html_content)

# Global instance
email_service = EmailService()
