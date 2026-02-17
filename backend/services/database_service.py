"""
MongoDB Database Service
Handles all database operations for call intelligence platform.
"""

from pymongo import MongoClient, DESCENDING
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from bson import ObjectId


class DatabaseService:
    """
    MongoDB service for persistent storage of call data and analytics.
    """
    
    def __init__(self, mongo_uri: str = None):
        """Initialize MongoDB connection."""
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = None
        self.db = None
        self.calls_collection = None
        
    def connect(self):
        """Establish MongoDB connection."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.call_intelligence
            self.calls_collection = self.db.calls
            
            # Create indexes for performance
            self.calls_collection.create_index([("created_at", DESCENDING)])
            self.calls_collection.create_index([("status", 1)])
            self.calls_collection.create_index([("final_decision.priority_score", DESCENDING)])
            
            print("✅ MongoDB connected successfully")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def _serialize_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize MongoDB document for JSON response.
        Converts ObjectId and datetime to strings.
        
        Args:
            call: MongoDB document
        
        Returns:
            JSON-serializable dictionary
        """
        if not call:
            return None
        
        # Convert ObjectId to string
        if "_id" in call:
            call["_id"] = str(call["_id"])
        
        # Convert datetime objects to ISO format strings
        if "created_at" in call and isinstance(call["created_at"], datetime):
            call["created_at"] = call["created_at"].isoformat()
        
        if "updated_at" in call and isinstance(call["updated_at"], datetime):
            call["updated_at"] = call["updated_at"].isoformat()
        
        return call
    
    def store_call(
        self,
        transcript: str,
        nlp_analysis: Dict[str, Any],
        llm_output: Dict[str, Any],
        final_decision: Dict[str, Any],
        audio_filename: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        transcription_segments: Optional[List[Dict]] = None
    ) -> str:
        """
        Store complete call processing result.
        
        Args:
            transcript: Full call transcript
            nlp_analysis: NLP service output
            llm_output: LLM service output
            final_decision: Action engine output
            audio_filename: Original audio filename (optional)
            audio_data: Audio file binary data (optional)
            transcription_segments: Timestamped segments (optional)
        
        Returns:
            call_id: MongoDB ObjectId as string
        """
        call_document = {
            "transcript": transcript,
            "nlp_analysis": nlp_analysis,
            "llm_output": llm_output,
            "final_decision": final_decision,
            "audio_filename": audio_filename,
            "audio_data": audio_data,  # Store audio binary data
            "transcription_segments": transcription_segments,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.calls_collection.insert_one(call_document)
        return str(result.inserted_id)
    
    def get_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a call by ID.
        
        Args:
            call_id: MongoDB ObjectId as string
        
        Returns:
            Call document or None
        """
        try:
            call = self.calls_collection.find_one({"_id": ObjectId(call_id)})
            return self._serialize_call(call)
        except Exception as e:
            print(f"Error retrieving call {call_id}: {e}")
            return None
    
    def get_call_by_id(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a call by ID (alias for get_call for compatibility).
        
        Args:
            call_id: MongoDB ObjectId as string
        
        Returns:
            Call document or None
        """
        return self.get_call(call_id)
    
    def get_all_calls(
        self,
        limit: int = 100,
        skip: int = 0,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all calls sorted by priority score.
        
        Args:
            limit: Max number of calls to return
            skip: Number of calls to skip (pagination)
            status_filter: Filter by status (pending/approved/rejected)
        
        Returns:
            List of call documents
        """
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        calls = list(
            self.calls_collection
            .find(query)
            .sort("final_decision.priority_score", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        
        # Serialize calls (convert ObjectIds and datetimes to strings)
        return [self._serialize_call(call) for call in calls]
    
    def update_call_status(
        self,
        call_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update call approval status.
        
        Args:
            call_id: MongoDB ObjectId as string
            status: New status (approved/rejected)
            notes: Optional notes about the decision
        
        Returns:
            Success boolean
        """
        try:
            update_doc = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if notes:
                update_doc["approval_notes"] = notes
            
            result = self.calls_collection.update_one(
                {"_id": ObjectId(call_id)},
                {"$set": update_doc}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating call status: {e}")
            return False
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Calculate dashboard KPIs and metrics.
        
        Returns:
            Dictionary with metrics
        """
        try:
            # Total calls
            total_calls = self.calls_collection.count_documents({})
            
            # High risk calls (risk_level = high)
            high_risk_calls = self.calls_collection.count_documents({
                "llm_output.risk_level": "high"
            })
            
            # Revenue opportunities (opportunity_level = high)
            revenue_opportunities = self.calls_collection.count_documents({
                "llm_output.opportunity_level": "high"
            })
            
            # Average priority score
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_priority": {"$avg": "$final_decision.priority_score"}
                    }
                }
            ]
            avg_result = list(self.calls_collection.aggregate(pipeline))
            avg_priority = round(avg_result[0]["avg_priority"], 2) if avg_result else 0
            
            # Sentiment distribution
            sentiment_pipeline = [
                {
                    "$group": {
                        "_id": "$nlp_analysis.sentiment.label",
                        "count": {"$sum": 1}
                    }
                }
            ]
            sentiment_data = list(self.calls_collection.aggregate(sentiment_pipeline))
            sentiment_distribution = {item["_id"]: item["count"] for item in sentiment_data}
            
            # Status distribution
            status_pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            status_data = list(self.calls_collection.aggregate(status_pipeline))
            status_distribution = {item["_id"]: item["count"] for item in status_data}
            
            return {
                "total_calls": total_calls,
                "high_risk_calls": high_risk_calls,
                "revenue_opportunities": revenue_opportunities,
                "avg_priority_score": avg_priority,
                "sentiment_distribution": sentiment_distribution,
                "status_distribution": status_distribution,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                "error": str(e),
                "total_calls": 0,
                "high_risk_calls": 0,
                "revenue_opportunities": 0,
                "avg_priority_score": 0,
                "sentiment_distribution": {},
                "status_distribution": {}
            }
    
    def search_calls(
        self,
        search_query: Optional[str] = None,
        sentiment: Optional[str] = None,
        priority_min: Optional[int] = None,
        priority_max: Optional[int] = None,
        risk_level: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search and filter calls with multiple criteria.
        
        Args:
            search_query: Text search in transcript
            sentiment: Filter by sentiment (positive/neutral/negative)
            priority_min: Minimum priority score
            priority_max: Maximum priority score
            risk_level: Filter by risk level (high/medium/low)
            date_from: Start date filter (ISO format)
            date_to: End date filter (ISO format)
            limit: Max results
        
        Returns:
            List of matching call documents
        """
        try:
            query = {}
            
            # Text search in transcript
            if search_query:
                query["$text"] = {"$search": search_query}
            
            # Sentiment filter
            if sentiment:
                query["nlp_analysis.sentiment.sentiment_label"] = sentiment
            
            # Priority range filter
            if priority_min is not None or priority_max is not None:
                priority_filter = {}
                if priority_min is not None:
                    priority_filter["$gte"] = priority_min
                if priority_max is not None:
                    priority_filter["$lte"] = priority_max
                query["final_decision.priority_score"] = priority_filter
            
            # Risk level filter
            if risk_level:
                query["llm_output.risk_level"] = risk_level
            
            # Date range filter
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = datetime.fromisoformat(date_from)
                if date_to:
                    date_filter["$lte"] = datetime.fromisoformat(date_to)
                query["created_at"] = date_filter
            
            calls = list(
                self.calls_collection
                .find(query)
                .sort("final_decision.priority_score", DESCENDING)
                .limit(limit)
            )
            
            return [self._serialize_call(call) for call in calls]
        except Exception as e:
            print(f"Error searching calls: {e}")
            return []
    
    def get_audio_data(self, call_id: str) -> Optional[bytes]:
        """
        Retrieve audio data for a call.
        
        Args:
            call_id: MongoDB ObjectId as string
        
        Returns:
            Audio binary data or None
        """
        try:
            call = self.calls_collection.find_one(
                {"_id": ObjectId(call_id)},
                {"audio_data": 1}
            )
            return call.get("audio_data") if call else None
        except Exception as e:
            print(f"Error retrieving audio data: {e}")
            return None
