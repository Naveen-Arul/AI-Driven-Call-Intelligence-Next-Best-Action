"""
Action Engine - Business Rules and Decision Validator
Applies business logic and governance rules on top of LLM recommendations.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ActionEngine:
    """
    Service for validating and enhancing LLM-generated actions with business rules.
    Provides governance, confidence scoring, and final decision validation.
    """
    
    def __init__(self):
        """Initialize the action engine with business rules configuration"""
        logger.info("Action Engine initialized")
        
        # Business rule thresholds
        self.HIGH_PRIORITY_THRESHOLD = 85
        self.CHURN_MINIMUM_PRIORITY = 90
        self.STRONG_SENTIMENT_THRESHOLD = 0.5
        
        # Confidence scoring weights
        self.BASE_CONFIDENCE = 70
        self.SENTIMENT_BONUS = 10
        self.KEYWORDS_BONUS = 10
        self.ENTITIES_BONUS = 10
    
    def evaluate(self, nlp_analysis: Dict, llm_output: Dict) -> Dict:
        """
        Evaluate LLM output against business rules and return final decision.
        
        Args:
            nlp_analysis: NLP analysis containing sentiment, intent, keywords, entities
            llm_output: LLM intelligence output with recommendations
            
        Returns:
            {
                "final_action": str,
                "priority_score": int,
                "risk_level": str,
                "opportunity_level": str,
                "escalation_required": bool,
                "urgent_flag": bool,
                "revenue_opportunity": bool,
                "confidence_score": int,
                "reasoning": str,
                "rules_applied": list
            }
        """
        
        logger.info("Evaluating action with business rules...")
        
        # Extract LLM outputs
        final_action = llm_output.get("recommended_action", "Review call manually")
        priority_score = llm_output.get("priority_score", 50)
        risk_level = llm_output.get("risk_level", "low")
        opportunity_level = llm_output.get("opportunity_level", "low")
        reasoning = llm_output.get("reasoning", "")
        
        # Extract NLP signals
        intent = nlp_analysis.get("intent", "general_inquiry")
        sentiment = nlp_analysis.get("sentiment", {})
        keywords = nlp_analysis.get("keywords", {})
        entities = nlp_analysis.get("entities", [])
        
        # Initialize flags
        escalation_required = False
        urgent_flag = False
        revenue_opportunity = False
        rules_applied = []
        
        # ========================================
        # BUSINESS RULES APPLICATION
        # ========================================
        
        # RULE 1: High Risk = Automatic Escalation
        if risk_level == "high":
            final_action = "Escalate to Senior Manager immediately"
            escalation_required = True
            rules_applied.append("RULE_1: High risk detected - forced escalation")
            logger.warning(f"High risk detected - forcing escalation. Original action: {llm_output.get('recommended_action')}")
        
        # RULE 2: Churn Risk = Minimum Priority 90
        if intent == "churn_risk":
            original_priority = priority_score
            priority_score = max(priority_score, self.CHURN_MINIMUM_PRIORITY)
            escalation_required = True
            rules_applied.append(f"RULE_2: Churn risk - priority elevated from {original_priority} to {priority_score}")
            logger.warning(f"Churn risk intent - elevating priority to {priority_score}")
        
        # RULE 3: High Opportunity + Low Risk = Revenue Opportunity
        if opportunity_level == "high" and risk_level == "low":
            revenue_opportunity = True
            rules_applied.append("RULE_3: High opportunity + low risk = revenue opportunity flagged")
            logger.info("Revenue opportunity identified")
        
        # RULE 4: Priority > 85 = Urgent Flag
        if priority_score > self.HIGH_PRIORITY_THRESHOLD:
            urgent_flag = True
            rules_applied.append(f"RULE_4: Priority {priority_score} > {self.HIGH_PRIORITY_THRESHOLD} - urgent flag set")
            logger.info(f"Urgent flag set for priority score {priority_score}")
        
        # RULE 5: Complaint + High Risk = Retention Team
        if intent == "complaint" and risk_level == "high":
            final_action = "Route to retention specialist with compensation authority"
            escalation_required = True
            rules_applied.append("RULE_5: Complaint + high risk - retention routing")
            logger.warning("High-risk complaint - routing to retention team")
        
        # RULE 6: Demo Request + High Opportunity = Fast-track
        if intent == "demo_request" and opportunity_level == "high":
            if "schedule demo" not in final_action.lower():
                final_action = "Fast-track demo scheduling with senior sales rep"
            rules_applied.append("RULE_6: High-value demo request - fast-track enabled")
            logger.info("High-value demo request detected - fast-tracking")
        
        # ========================================
        # CONFIDENCE SCORING
        # ========================================
        
        confidence_score = self._calculate_confidence(
            sentiment=sentiment,
            keywords=keywords,
            entities=entities
        )
        
        # ========================================
        # FINAL DECISION ASSEMBLY
        # ========================================
        
        decision = {
            "final_action": final_action,
            "priority_score": priority_score,
            "risk_level": risk_level,
            "opportunity_level": opportunity_level,
            "escalation_required": escalation_required,
            "urgent_flag": urgent_flag,
            "revenue_opportunity": revenue_opportunity,
            "confidence_score": confidence_score,
            "reasoning": reasoning,
            "rules_applied": rules_applied,
            "intent": intent,
            "sentiment_label": sentiment.get("sentiment_label", "neutral")
        }
        
        logger.info(f"Decision complete - Priority: {priority_score}, Confidence: {confidence_score}, Urgent: {urgent_flag}")
        
        return decision
    
    def _calculate_confidence(
        self,
        sentiment: Dict,
        keywords: Dict,
        entities: list
    ) -> int:
        """
        Calculate confidence score based on data quality signals.
        
        Args:
            sentiment: Sentiment analysis results
            keywords: Detected keywords
            entities: Extracted entities
            
        Returns:
            Confidence score (0-100)
        """
        
        confidence = self.BASE_CONFIDENCE
        
        # Strong sentiment signal (+10)
        compound_score = sentiment.get("compound", 0)
        if abs(compound_score) > self.STRONG_SENTIMENT_THRESHOLD:
            confidence += self.SENTIMENT_BONUS
            logger.debug(f"Strong sentiment detected ({compound_score:.2f}) - confidence +{self.SENTIMENT_BONUS}")
        
        # Keywords detected (+10)
        if keywords and len(keywords) > 0:
            confidence += self.KEYWORDS_BONUS
            logger.debug(f"Keywords detected ({len(keywords)} categories) - confidence +{self.KEYWORDS_BONUS}")
        
        # Entities extracted (+10)
        if entities and len(entities) > 0:
            confidence += self.ENTITIES_BONUS
            logger.debug(f"Entities extracted ({len(entities)}) - confidence +{self.ENTITIES_BONUS}")
        
        # Cap at 100
        confidence = min(confidence, 100)
        
        return confidence
    
    def validate_action_safety(self, action: str) -> Dict:
        """
        Validate that a proposed action is safe and doesn't violate policies.
        
        Args:
            action: Proposed action string
            
        Returns:
            {
                "is_safe": bool,
                "warnings": list,
                "modifications": list
            }
        """
        
        warnings = []
        modifications = []
        is_safe = True
        
        # Check for risky keywords
        risky_keywords = ["discount", "refund", "compensation", "free", "waive"]
        action_lower = action.lower()
        
        for keyword in risky_keywords:
            if keyword in action_lower:
                warnings.append(f"Action contains potentially risky keyword: '{keyword}'")
                logger.warning(f"Risky keyword detected in action: {keyword}")
        
        # Check for monetary amounts
        if "$" in action or "%" in action:
            warnings.append("Action contains monetary values - requires approval")
            is_safe = False
        
        return {
            "is_safe": is_safe,
            "warnings": warnings,
            "modifications": modifications
        }
