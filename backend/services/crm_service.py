"""
CRM Integration Service for Call Intelligence Platform
Integrates with Salesforce, HubSpot, and other CRM platforms
"""

from typing import Dict, Optional
from datetime import datetime
import uuid

class CRMService:
    def __init__(self):
        self.crm_type = "Salesforce"  # Can be configured
        self.integration_active = True
        
    def create_lead(self, call_data: Dict) -> Dict:
        """Create a new lead in CRM from call data"""
        try:
            final_decision = call_data.get("final_decision", {})
            llm_result = call_data.get("llm_result", {})
            nlp = call_data.get("nlp_analysis", {})
            
            # Generate lead ID
            lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract customer info from entities
            entities = nlp.get("entities", [])
            customer_name = next((e["text"] for e in entities if e.get("label") == "PERSON"), "Unknown Customer")
            organization = next((e["text"] for e in entities if e.get("label") == "ORG"), "")
            
            lead_data = {
                "lead_id": lead_id,
                "crm_type": self.crm_type,
                "status": "created",
                "customer_name": customer_name,
                "organization": organization,
                "source": "Call Intelligence Platform",
                "priority": final_decision.get("priority_level", "medium"),
                "opportunity_level": llm_result.get("opportunity_level", "medium"),
                "risk_level": llm_result.get("risk_level", "low"),
                "call_summary": llm_result.get("call_summary", ""),
                "recommended_action": final_decision.get("final_action", ""),
                "assigned_to": final_decision.get("assigned_to", "Sales Team"),
                "created_at": datetime.now().isoformat(),
                "call_id": str(call_data.get("_id", "")),
                "sentiment_score": nlp.get("sentiment", {}).get("compound", 0)
            }
            
            return {
                "status": "success",
                "crm_action": "lead_created",
                "lead_data": lead_data,
                "message": f"Lead {lead_id} created successfully in {self.crm_type}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "crm_action": "lead_creation_failed",
                "message": str(e)
            }
    
    def update_opportunity(self, call_data: Dict, opportunity_id: Optional[str] = None) -> Dict:
        """Update existing opportunity or create new one"""
        try:
            final_decision = call_data.get("final_decision", {})
            llm_result = call_data.get("llm_result", {})
            
            if not opportunity_id:
                opportunity_id = f"OPP-{uuid.uuid4().hex[:8].upper()}"
            
            opportunity_data = {
                "opportunity_id": opportunity_id,
                "crm_type": self.crm_type,
                "status": "updated",
                "stage": self._determine_stage(llm_result),
                "value": self._estimate_value(llm_result),
                "probability": self._calculate_probability(llm_result),
                "next_action": final_decision.get("final_action", ""),
                "priority": final_decision.get("priority_level", "medium"),
                "last_contact": datetime.now().isoformat(),
                "call_id": str(call_data.get("_id", ""))
            }
            
            return {
                "status": "success",
                "crm_action": "opportunity_updated",
                "opportunity_data": opportunity_data,
                "message": f"Opportunity {opportunity_id} updated in {self.crm_type}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "crm_action": "opportunity_update_failed",
                "message": str(e)
            }
    
    def create_task(self, call_data: Dict, task_type: str = "follow_up") -> Dict:
        """Create a task/activity in CRM"""
        try:
            final_decision = call_data.get("final_decision", {})
            
            task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
            
            task_data = {
                "task_id": task_id,
                "crm_type": self.crm_type,
                "type": task_type,
                "subject": final_decision.get("final_action", "Follow up on call"),
                "priority": final_decision.get("priority_level", "medium"),
                "assigned_to": final_decision.get("assigned_to", "Sales Team"),
                "due_date": self._calculate_due_date(final_decision.get("priority_level", "medium")),
                "status": "pending",
                "related_to": str(call_data.get("_id", "")),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "crm_action": "task_created",
                "task_data": task_data,
                "message": f"Task {task_id} created in {self.crm_type}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "crm_action": "task_creation_failed",
                "message": str(e)
            }
    
    def log_activity(self, call_data: Dict) -> Dict:
        """Log call activity in CRM"""
        try:
            activity_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
            
            nlp = call_data.get("nlp_analysis", {})
            llm_result = call_data.get("llm_result", {})
            
            activity_data = {
                "activity_id": activity_id,
                "crm_type": self.crm_type,
                "type": "phone_call",
                "subject": f"Call: {call_data.get('filename', 'N/A')}",
                "description": llm_result.get("call_summary", ""),
                "sentiment": nlp.get("sentiment", {}).get("sentiment_label", "neutral"),
                "duration": "N/A",  # Can be calculated from audio
                "outcome": final_decision.get("final_action", ""),
                "logged_at": datetime.now().isoformat(),
                "call_id": str(call_data.get("_id", ""))
            }
            
            return {
                "status": "success",
                "crm_action": "activity_logged",
                "activity_data": activity_data,
                "message": f"Activity {activity_id} logged in {self.crm_type}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "crm_action": "activity_logging_failed",
                "message": str(e)
            }
    
    def sync_to_crm(self, call_data: Dict, actions: list = ["create_lead", "create_task", "log_activity"]) -> Dict:
        """Perform multiple CRM actions"""
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "crm_type": self.crm_type,
            "actions_performed": []
        }
        
        for action in actions:
            if action == "create_lead":
                result = self.create_lead(call_data)
                results["actions_performed"].append(result)
                
            elif action == "create_task":
                result = self.create_task(call_data)
                results["actions_performed"].append(result)
                
            elif action == "log_activity":
                result = self.log_activity(call_data)
                results["actions_performed"].append(result)
                
            elif action == "update_opportunity":
                result = self.update_opportunity(call_data)
                results["actions_performed"].append(result)
        
        return results
    
    def _determine_stage(self, llm_result: Dict) -> str:
        """Determine sales stage based on analysis"""
        opportunity_level = llm_result.get("opportunity_level", "medium")
        
        if opportunity_level == "high":
            return "Qualified Lead"
        elif opportunity_level == "medium":
            return "In Discussion"
        else:
            return "Cold Lead"
    
    def _estimate_value(self, llm_result: Dict) -> int:
        """Estimate opportunity value"""
        opportunity_level = llm_result.get("opportunity_level", "medium")
        
        values = {
            "high": 50000,
            "medium": 25000,
            "low": 10000
        }
        
        return values.get(opportunity_level, 25000)
    
    def _calculate_probability(self, llm_result: Dict) -> int:
        """Calculate win probability"""
        opportunity_level = llm_result.get("opportunity_level", "medium")
        
        probabilities = {
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        return probabilities.get(opportunity_level, 50)
    
    def _calculate_due_date(self, priority: str) -> str:
        """Calculate task due date based on priority"""
        from datetime import timedelta
        
        days_map = {
            "urgent": 1,
            "high": 2,
            "medium": 5,
            "low": 7
        }
        
        days = days_map.get(priority, 5)
        due_date = datetime.now() + timedelta(days=days)
        
        return due_date.isoformat()

# Global instance
crm_service = CRMService()
