"""
Voice of Customer (VOC) Insights Service
Analyzes aggregate patterns across all calls to extract business intelligence.
"""

from typing import Dict, List, Any
from collections import Counter
import re


class VOCService:
    """
    Service for extracting Voice of Customer insights from call data.
    Provides word clouds, feature requests, competitor analysis, and topic trends.
    """
    
    def __init__(self):
        """Initialize VOC service"""
        # Common stopwords to exclude from word cloud
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their',
            'this', 'that', 'these', 'those', 'am', 'want', 'need', 'like', 'get',
            'im', 'id', 'ill', 'ive', 'dont', 'cant', 'wont', 'wouldnt', 'couldnt'
        }
        
        # Feature request patterns
        self.feature_patterns = [
            r"need .+ (?:feature|functionality|option|ability)",
            r"would like (?:to|a|an) .+",
            r"wish .+ had .+",
            r"(?:add|include|provide) .+",
            r"feature request",
            r"(?:mobile|desktop|web) app",
            r"integration with .+",
            r"api (?:access|support)",
            r"better .+",
            r"improve .+"
        ]
        
        # Competitor name patterns (common SaaS/business software)
        self.competitor_keywords = [
            "salesforce", "hubspot", "zendesk", "freshworks", "intercom",
            "zoho", "pipedrive", "monday", "asana", "slack", "teams",
            "competitor", "alternative", "other tool", "other platform"
        ]
    
    def generate_insights(self, calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive VOC insights from call data.
        
        Args:
            calls: List of call documents from database
            
        Returns:
            {
                "word_cloud": {word: count},
                "top_topics": [{topic, mentions, percentage}],
                "feature_requests": [{request, count}],
                "competitor_mentions": [{competitor, count, context}],
                "product_feedback": {positive, negative, neutral},
                "common_pain_points": [pain_point],
                "total_calls_analyzed": int
            }
        """
        
        if not calls:
            return self._empty_insights()
        
        # Aggregate all transcripts and keywords
        all_transcripts = []
        all_keywords = {}
        sentiment_breakdown = {"positive": 0, "neutral": 0, "negative": 0}
        feature_requests_raw = []
        competitor_mentions = []
        
        for call in calls:
            transcript = call.get("transcript", "")
            all_transcripts.append(transcript)
            
            # Aggregate keywords
            nlp = call.get("nlp_analysis", {})
            keywords = nlp.get("keywords", {})
            for category, words in keywords.items():
                if category not in all_keywords:
                    all_keywords[category] = []
                all_keywords[category].extend(words)
            
            # Sentiment breakdown
            sentiment_label = nlp.get("sentiment", {}).get("sentiment_label", "neutral")
            sentiment_breakdown[sentiment_label] = sentiment_breakdown.get(sentiment_label, 0) + 1
            
            # Extract feature requests
            feature_requests_raw.extend(self._extract_feature_requests(transcript))
            
            # Extract competitor mentions
            competitor_mentions.extend(self._extract_competitor_mentions(transcript))
        
        # Generate word cloud
        word_cloud = self._generate_word_cloud(all_transcripts)
        
        # Top topics from keywords
        top_topics = self._calculate_top_topics(all_keywords, len(calls))
        
        # Aggregate feature requests
        feature_requests = self._aggregate_feature_requests(feature_requests_raw)
        
        # Aggregate competitor mentions
        competitor_analysis = self._aggregate_competitors(competitor_mentions)
        
        # Extract common pain points
        pain_points = self._extract_pain_points(all_keywords, calls)
        
        return {
            "word_cloud": word_cloud,
            "top_topics": top_topics,
            "feature_requests": feature_requests,
            "competitor_mentions": competitor_analysis,
            "product_feedback": sentiment_breakdown,
            "common_pain_points": pain_points,
            "total_calls_analyzed": len(calls),
            "date_range": {
                "from": min([c.get("created_at", "") for c in calls]) if calls else "",
                "to": max([c.get("created_at", "") for c in calls]) if calls else ""
            }
        }
    
    def _generate_word_cloud(self, transcripts: List[str], top_n: int = 50) -> Dict[str, int]:
        """Generate word frequency data for word cloud."""
        word_counter = Counter()
        
        for transcript in transcripts:
            words = re.findall(r'\b[a-z]{3,}\b', transcript.lower())
            filtered_words = [w for w in words if w not in self.stopwords]
            word_counter.update(filtered_words)
        
        return dict(word_counter.most_common(top_n))
    
    def _calculate_top_topics(self, all_keywords: Dict, total_calls: int) -> List[Dict]:
        """Calculate top mentioned topics."""
        topic_counts = {}
        
        for category, words in all_keywords.items():
            topic_counts[category] = len(words)
        
        # Sort by count
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        top_topics = []
        for topic, count in sorted_topics[:10]:
            top_topics.append({
                "topic": topic,
                "mentions": count,
                "percentage": round((count / max(total_calls, 1)) * 100, 1)
            })
        
        return top_topics
    
    def _extract_feature_requests(self, transcript: str) -> List[str]:
        """Extract potential feature requests from transcript."""
        requests = []
        transcript_lower = transcript.lower()
        
        for pattern in self.feature_patterns:
            matches = re.findall(pattern, transcript_lower, re.IGNORECASE)
            requests.extend(matches)
        
        # Common feature request phrases
        if "mobile app" in transcript_lower:
            requests.append("mobile app")
        if "api" in transcript_lower or "api access" in transcript_lower:
            requests.append("api access")
        if "integration" in transcript_lower:
            requests.append("integration support")
        if "reporting" in transcript_lower or "reports" in transcript_lower:
            requests.append("better reporting")
        if "export" in transcript_lower:
            requests.append("export functionality")
        
        return requests
    
    def _extract_competitor_mentions(self, transcript: str) -> List[str]:
        """Extract competitor mentions from transcript."""
        mentions = []
        transcript_lower = transcript.lower()
        
        for competitor in self.competitor_keywords:
            if competitor in transcript_lower:
                mentions.append(competitor)
        
        return mentions
    
    def _aggregate_feature_requests(self, requests: List[str]) -> List[Dict]:
        """Aggregate and rank feature requests."""
        if not requests:
            return []
        
        counter = Counter(requests)
        aggregated = []
        
        for request, count in counter.most_common(10):
            aggregated.append({
                "request": request.strip(),
                "count": count
            })
        
        return aggregated
    
    def _aggregate_competitors(self, mentions: List[str]) -> List[Dict]:
        """Aggregate competitor mentions."""
        if not mentions:
            return []
        
        counter = Counter(mentions)
        aggregated = []
        
        for competitor, count in counter.most_common(10):
            aggregated.append({
                "competitor": competitor.title(),
                "mentions": count
            })
        
        return aggregated
    
    def _extract_pain_points(self, all_keywords: Dict, calls: List[Dict]) -> List[str]:
        """Extract common pain points from negative sentiment calls."""
        pain_points = []
        
        # Look at complaint keywords
        if "complaint" in all_keywords:
            pain_points.append("Customer complaints detected")
        
        if "cancellation" in all_keywords:
            pain_points.append("Cancellation requests")
        
        # Count negative sentiment calls
        negative_count = sum(1 for call in calls 
                           if call.get("nlp_analysis", {}).get("sentiment", {}).get("sentiment_label") == "negative")
        
        if negative_count > len(calls) * 0.3:
            pain_points.append(f"High negative sentiment ({negative_count} calls)")
        
        # Check for pricing objections
        if "pricing" in all_keywords and len(all_keywords["pricing"]) > len(calls) * 0.3:
            pain_points.append("Frequent pricing concerns")
        
        # Technical issues
        if "complaint" in all_keywords:
            complaint_words = all_keywords["complaint"]
            if any("technical" in w or "bug" in w or "error" in w for w in complaint_words):
                pain_points.append("Technical issues reported")
        
        return pain_points[:5]  # Top 5 pain points
    
    def _empty_insights(self) -> Dict[str, Any]:
        """Return empty insights structure."""
        return {
            "word_cloud": {},
            "top_topics": [],
            "feature_requests": [],
            "competitor_mentions": [],
            "product_feedback": {"positive": 0, "neutral": 0, "negative": 0},
            "common_pain_points": [],
            "total_calls_analyzed": 0,
            "date_range": {"from": "", "to": ""}
        }
