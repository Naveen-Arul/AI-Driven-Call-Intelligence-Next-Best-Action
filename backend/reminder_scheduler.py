"""
Reminder Scheduler for Call Intelligence Platform
Automatically sends reminder emails for pending actions
Run this script as a background service
"""

import time
import logging
from datetime import datetime, timedelta
from services.database_service import DatabaseService
from services.email_service import EmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REMINDER_EMAIL = "naveenarul111@gmail.com"  # Default recipient
CHECK_INTERVAL_MINUTES = 15  # Check every 15 minutes

# Priority-based reminder schedules (hours after creation)
REMINDER_SCHEDULE = {
    "urgent": 2,    # Remind after 2 hours if still pending
    "high": 6,      # Remind after 6 hours
    "medium": 24,   # Remind after 1 day
    "low": 48       # Remind after 2 days
}

class ReminderScheduler:
    def __init__(self):
        self.db_service = DatabaseService()
        self.email_service = EmailService()
        self.db_service.connect()
        logger.info("✅ Reminder Scheduler initialized")
    
    def get_pending_calls_needing_reminder(self):
        """Find pending calls that need reminders"""
        pending_calls = list(self.db_service.calls_collection.find({
            "approval_status": "pending_approval"
        }))
        
        calls_needing_reminder = []
        current_time = datetime.now()
        
        for call in pending_calls:
            # Get priority level
            priority = call.get("final_decision", {}).get("priority_level", "medium")
            
            # Calculate reminder threshold
            reminder_hours = REMINDER_SCHEDULE.get(priority, 24)
            
            # Check if call was created more than threshold hours ago
            created_at = datetime.fromisoformat(call.get("created_at"))
            time_since_creation = current_time - created_at
            
            if time_since_creation >= timedelta(hours=reminder_hours):
                # Check if reminder already sent
                reminders_sent = call.get("reminders_sent", [])
                last_reminder = reminders_sent[-1] if reminders_sent else None
                
                # Send reminder if no previous reminder, or if last reminder was > 24 hours ago
                should_send = True
                if last_reminder:
                    last_reminder_time = datetime.fromisoformat(last_reminder.get("sent_at"))
                    time_since_last = current_time - last_reminder_time
                    should_send = time_since_last >= timedelta(hours=24)
                
                if should_send:
                    calls_needing_reminder.append(call)
        
        return calls_needing_reminder
    
    def send_reminders(self):
        """Send reminder emails for pending calls"""
        try:
            calls = self.get_pending_calls_needing_reminder()
            
            if not calls:
                logger.info("No pending calls need reminders at this time")
                return
            
            logger.info(f"📧 Sending reminders for {len(calls)} pending call(s)...")
            
            for call in calls:
                try:
                    # Determine reminder type based on priority
                    priority = call.get("final_decision", {}).get("priority_level", "medium")
                    reminder_type = "urgent" if priority == "urgent" else "follow_up"
                    
                    # Send reminder email
                    result = self.email_service.send_reminder(
                        call_data=call,
                        recipient_email=REMINDER_EMAIL,
                        reminder_type=reminder_type
                    )
                    
                    if result.get("status") == "success":
                        # Log reminder in database
                        self.db_service.calls_collection.update_one(
                            {"_id": call["_id"]},
                            {
                                "$push": {
                                    "reminders_sent": {
                                        "sent_at": datetime.now().isoformat(),
                                        "recipient": REMINDER_EMAIL,
                                        "type": reminder_type
                                    }
                                }
                            }
                        )
                        logger.info(f"✅ Reminder sent for call {call.get('_id')}")
                    else:
                        logger.error(f"❌ Failed to send reminder for call {call.get('_id')}: {result.get('message')}")
                
                except Exception as e:
                    logger.error(f"Error sending reminder for call {call.get('_id')}: {str(e)}")
                    continue
            
            logger.info(f"✅ Reminder batch complete. Sent {len(calls)} reminder(s)")
        
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {str(e)}")
    
    def run(self):
        """Main loop - check and send reminders periodically"""
        logger.info(f"🚀 Reminder Scheduler started. Checking every {CHECK_INTERVAL_MINUTES} minutes...")
        logger.info(f"📧 Default recipient: {REMINDER_EMAIL}")
        logger.info(f"⏰ Reminder schedule: {REMINDER_SCHEDULE}")
        
        try:
            while True:
                logger.info(f"🔍 Checking for pending calls... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                self.send_reminders()
                
                # Wait for next check
                logger.info(f"💤 Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
        
        except KeyboardInterrupt:
            logger.info("⏹️  Reminder Scheduler stopped by user")
            self.db_service.disconnect()
        except Exception as e:
            logger.error(f"Fatal error in scheduler: {str(e)}")
            self.db_service.disconnect()

if __name__ == "__main__":
    scheduler = ReminderScheduler()
    scheduler.run()
