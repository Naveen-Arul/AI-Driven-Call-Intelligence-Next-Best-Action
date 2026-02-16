"""
Test script for LLM Intelligence endpoint
Tests the complete pipeline: Transcript → NLP → LLM Intelligence
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧠 TESTING LLM INTELLIGENCE ENGINE (STEP 3)")
print("=" * 70)

# Test Case 1: Demo Request (High Opportunity)
print("\n📞 TEST 1: Demo Request - High Opportunity")
print("-" * 70)

test_1 = {
    "transcript": """
    Hi, I'm Sarah from TechCorp. I'm really impressed with what I've seen so far. 
    We're a team of 50 people and we're looking for a solution exactly like yours.
    Could we schedule a demo for next week? I'd love to show this to our VP of Sales.
    The pricing looks reasonable and we have budget approved for Q1.
    """,
    "nlp_analysis": {
        "sentiment": {
            "compound": 0.89,
            "positive": 0.35,
            "neutral": 0.60,
            "negative": 0.05,
            "sentiment_label": "positive"
        },
        "intent": "demo_request",
        "keywords": {
            "demo": ["demo"],
            "interest": ["impressed", "looking for"],
            "timeline": ["next week"],
            "decision_maker": ["VP", "team"],
            "pricing": ["pricing", "budget"]
        },
        "entities": [
            {"text": "Sarah", "label": "PERSON"},
            {"text": "TechCorp", "label": "ORG"},
            {"text": "next week", "label": "DATE"}
        ]
    }
}

response = requests.post(f"{BASE_URL}/intelligence", json=test_1)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n📝 Summary: {result.get('call_summary_short')}")
    print(f"\n🎯 Risk Level: {result.get('risk_level')}")
    print(f"💎 Opportunity Level: {result.get('opportunity_level')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"\n🎬 Recommended Action:")
    print(f"   {result.get('recommended_action')}")
    print(f"\n💭 Reasoning:")
    print(f"   {result.get('reasoning')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# Test Case 2: Churn Risk (High Risk)
print("\n" + "=" * 70)
print("📞 TEST 2: Churn Risk - High Priority")
print("-" * 70)

test_2 = {
    "transcript": """
    I'm calling because I'm extremely frustrated. This is the third time I've had 
    issues with your product this month. Nothing is working as promised. 
    My team can't use it and we're losing productivity. If this isn't fixed 
    immediately, I'll have no choice but to cancel our subscription and switch 
    to a competitor. This is unacceptable.
    """,
    "nlp_analysis": {
        "sentiment": {
            "compound": -0.85,
            "positive": 0.05,
            "neutral": 0.25,
            "negative": 0.70,
            "sentiment_label": "negative"
        },
        "intent": "churn_risk",
        "keywords": {
            "complaint": ["frustrated", "issues", "problem", "not working"],
            "cancellation": ["cancel"],
            "competitor": ["competitor", "switch"],
            "urgency": ["immediately"],
            "decision_maker": ["team"]
        },
        "entities": []
    }
}

response = requests.post(f"{BASE_URL}/intelligence", json=test_2)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n📝 Summary: {result.get('call_summary_short')}")
    print(f"\n🎯 Risk Level: {result.get('risk_level')}")
    print(f"💎 Opportunity Level: {result.get('opportunity_level')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"\n🎬 Recommended Action:")
    print(f"   {result.get('recommended_action')}")
    print(f"\n💭 Reasoning:")
    print(f"   {result.get('reasoning')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# Test Case 3: Pricing Inquiry (Medium Opportunity)
print("\n" + "=" * 70)
print("📞 TEST 3: Pricing Inquiry - Medium Opportunity")
print("-" * 70)

test_3 = {
    "transcript": """
    Hi, I'm evaluating different solutions and I'd like to understand your pricing.
    What does it cost for a team of 10? Are there any discounts for annual contracts?
    I need to present this to my manager next week.
    """,
    "nlp_analysis": {
        "sentiment": {
            "compound": 0.15,
            "positive": 0.15,
            "neutral": 0.80,
            "negative": 0.05,
            "sentiment_label": "neutral"
        },
        "intent": "pricing_inquiry",
        "keywords": {
            "pricing": ["pricing", "cost"],
            "interest": ["evaluating", "need"],
            "decision_maker": ["manager", "team"],
            "timeline": ["next week"]
        },
        "entities": [
            {"text": "next week", "label": "DATE"}
        ]
    }
}

response = requests.post(f"{BASE_URL}/intelligence", json=test_3)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n📝 Summary: {result.get('call_summary_short')}")
    print(f"\n🎯 Risk Level: {result.get('risk_level')}")
    print(f"💎 Opportunity Level: {result.get('opportunity_level')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"\n🎬 Recommended Action:")
    print(f"   {result.get('recommended_action')}")
    print(f"\n💭 Reasoning:")
    print(f"   {result.get('reasoning')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


print("\n" + "=" * 70)
print("✅ ALL INTELLIGENCE TESTS COMPLETE!")
print("=" * 70)
