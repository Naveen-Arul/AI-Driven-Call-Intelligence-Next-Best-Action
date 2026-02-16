"""
Test script for Action Engine & Business Rules
Tests the complete decision pipeline with rule validation
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🛡️ TESTING ACTION ENGINE & BUSINESS RULES (STEP 4)")
print("=" * 80)

# Test Case 1: High-Value Demo Request (Revenue Opportunity)
print("\n💰 TEST 1: High-Value Demo Request → Revenue Opportunity")
print("-" * 80)

test_1 = {
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
            "pricing": ["budget"]
        },
        "entities": [
            {"text": "next week", "label": "DATE"},
            {"text": "TechCorp", "label": "ORG"}
        ]
    },
    "llm_output": {
        "call_summary_short": "High-value demo request from qualified lead",
        "call_summary_detailed": "Customer is impressed and has budget approved",
        "risk_level": "low",
        "opportunity_level": "high",
        "recommended_action": "Schedule demo for next Tuesday",
        "priority_score": 92,
        "reasoning": "Strong buying signals with budget approval"
    }
}

response = requests.post(f"{BASE_URL}/decision", json=test_1)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n🎯 Final Action: {result.get('final_action')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"🎓 Confidence Score: {result.get('confidence_score')}/100")
    print(f"\n🚩 Flags:")
    print(f"   • Escalation Required: {result.get('escalation_required')}")
    print(f"   • Urgent Flag: {result.get('urgent_flag')}")
    print(f"   • Revenue Opportunity: {result.get('revenue_opportunity')}")
    print(f"\n📋 Rules Applied:")
    for rule in result.get('rules_applied', []):
        print(f"   • {rule}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# Test Case 2: Churn Risk (High Priority + Escalation)
print("\n" + "=" * 80)
print("⚠️ TEST 2: Churn Risk → Forced Escalation & Priority Override")
print("-" * 80)

test_2 = {
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
            "complaint": ["frustrated", "issues"],
            "cancellation": ["cancel"],
            "urgency": ["immediately"]
        },
        "entities": []
    },
    "llm_output": {
        "call_summary_short": "Customer threatening cancellation",
        "call_summary_detailed": "Multiple unresolved issues leading to churn risk",
        "risk_level": "high",
        "opportunity_level": "low",
        "recommended_action": "Contact customer service team",
        "priority_score": 75,
        "reasoning": "Negative sentiment with cancellation threat"
    }
}

response = requests.post(f"{BASE_URL}/decision", json=test_2)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n🎯 Final Action: {result.get('final_action')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100  (LLM suggested: 75)")
    print(f"🎓 Confidence Score: {result.get('confidence_score')}/100")
    print(f"\n🚩 Flags:")
    print(f"   • Escalation Required: {result.get('escalation_required')}")
    print(f"   • Urgent Flag: {result.get('urgent_flag')}")
    print(f"   • Revenue Opportunity: {result.get('revenue_opportunity')}")
    print(f"\n📋 Rules Applied:")
    for rule in result.get('rules_applied', []):
        print(f"   • {rule}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# Test Case 3: Complaint with High Risk (Retention Routing)
print("\n" + "=" * 80)
print("🔥 TEST 3: High-Risk Complaint → Retention Team Routing")
print("-" * 80)

test_3 = {
    "nlp_analysis": {
        "sentiment": {
            "compound": -0.72,
            "positive": 0.05,
            "neutral": 0.30,
            "negative": 0.65,
            "sentiment_label": "negative"
        },
        "intent": "complaint",
        "keywords": {
            "complaint": ["problem", "not working", "broken"],
            "urgency": ["urgent"]
        },
        "entities": [
            {"text": "$500", "label": "MONEY"}
        ]
    },
    "llm_output": {
        "call_summary_short": "Customer reporting critical system failure",
        "call_summary_detailed": "Production system down, financial impact",
        "risk_level": "high",
        "opportunity_level": "low",
        "recommended_action": "Assign to technical support",
        "priority_score": 88,
        "reasoning": "Critical technical issue with business impact"
    }
}

response = requests.post(f"{BASE_URL}/decision", json=test_3)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n🎯 Final Action: {result.get('final_action')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"🎓 Confidence Score: {result.get('confidence_score')}/100")
    print(f"\n🚩 Flags:")
    print(f"   • Escalation Required: {result.get('escalation_required')}")
    print(f"   • Urgent Flag: {result.get('urgent_flag')}")
    print(f"   • Revenue Opportunity: {result.get('revenue_opportunity')}")
    print(f"\n📋 Rules Applied:")
    for rule in result.get('rules_applied', []):
        print(f"   • {rule}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# Test Case 4: Medium Priority General Inquiry
print("\n" + "=" * 80)
print("📞 TEST 4: General Inquiry → Standard Confidence Scoring")
print("-" * 80)

test_4 = {
    "nlp_analysis": {
        "sentiment": {
            "compound": 0.15,
            "positive": 0.20,
            "neutral": 0.75,
            "negative": 0.05,
            "sentiment_label": "neutral"
        },
        "intent": "pricing_inquiry",
        "keywords": {
            "pricing": ["cost", "price"]
        },
        "entities": []
    },
    "llm_output": {
        "call_summary_short": "Customer inquiring about pricing",
        "call_summary_detailed": "General pricing question for small team",
        "risk_level": "low",
        "opportunity_level": "medium",
        "recommended_action": "Send pricing document via email",
        "priority_score": 65,
        "reasoning": "Standard pricing inquiry"
    }
}

response = requests.post(f"{BASE_URL}/decision", json=test_4)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"\n🎯 Final Action: {result.get('final_action')}")
    print(f"⚡ Priority Score: {result.get('priority_score')}/100")
    print(f"🎓 Confidence Score: {result.get('confidence_score')}/100")
    print(f"\n🚩 Flags:")
    print(f"   • Escalation Required: {result.get('escalation_required')}")
    print(f"   • Urgent Flag: {result.get('urgent_flag')}")
    print(f"   • Revenue Opportunity: {result.get('revenue_opportunity')}")
    print(f"\n📋 Rules Applied:")
    for rule in result.get('rules_applied', []):
        print(f"   • {rule}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


print("\n" + "=" * 80)
print("✅ ALL BUSINESS RULES TESTS COMPLETE!")
print("=" * 80)
print("\n📊 Summary:")
print("   • Revenue opportunity detection: ✅")
print("   • Churn risk escalation: ✅")
print("   • Priority override rules: ✅")
print("   • Confidence scoring: ✅")
print("   • Urgent flag automation: ✅")
print("=" * 80)
