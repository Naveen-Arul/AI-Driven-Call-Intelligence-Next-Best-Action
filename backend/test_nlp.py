"""
Test script for NLP Analysis endpoint
"""

import requests
import json

# Test analyze endpoint with business conversation
print("=" * 60)
print("Testing /analyze endpoint")
print("=" * 60)

# Test Case 1: Demo Request (Positive)
print("\n📞 Test 1: Demo Request")
test_transcript_1 = """
Hi, I'm interested in your product. Could you schedule a demo for next week? 
I'd love to see how it works. The pricing also looks reasonable.
"""

response = requests.post(
    "http://localhost:8000/analyze",
    json={"transcript": test_transcript_1}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"Intent: {result['intent']}")
    print(f"Sentiment: {result['sentiment']['sentiment_label']} ({result['sentiment']['compound']})")
    print(f"Keywords: {result['keywords']}")
    print(f"Entities: {result['entities']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test Case 2: Complaint/Churn Risk (Negative)
print("\n" + "=" * 60)
print("📞 Test 2: Churn Risk")
test_transcript_2 = """
I'm very frustrated. This product is not working as expected.
I have serious issues and I'm considering canceling my subscription.
The problem needs to be fixed immediately.
"""

response = requests.post(
    "http://localhost:8000/analyze",
    json={"transcript": test_transcript_2}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"Intent: {result['intent']}")
    print(f"Sentiment: {result['sentiment']['sentiment_label']} ({result['sentiment']['compound']})")
    print(f"Keywords: {result['keywords']}")
    print(f"Entities: {result['entities']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test Case 3: Pricing Inquiry
print("\n" + "=" * 60)
print("📞 Test 3: Pricing Inquiry")
test_transcript_3 = """
Hello, I'm calling to ask about your pricing plans.
How much does it cost for a team of 10 people?
What's included in the budget plan?
"""

response = requests.post(
    "http://localhost:8000/analyze",
    json={"transcript": test_transcript_3}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"Intent: {result['intent']}")
    print(f"Sentiment: {result['sentiment']['sentiment_label']} ({result['sentiment']['compound']})")
    print(f"Keywords: {result['keywords']}")
    print(f"Entities: {result['entities']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test Case 4: Competitor Comparison
print("\n" + "=" * 60)
print("📞 Test 4: Competitor Comparison")
test_transcript_4 = """
We're currently evaluating your solution versus the competitor.
Can you tell me how your product compares to alternative options?
"""

response = requests.post(
    "http://localhost:8000/analyze",
    json={"transcript": test_transcript_4}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"Intent: {result['intent']}")
    print(f"Sentiment: {result['sentiment']['sentiment_label']} ({result['sentiment']['compound']})")
    print(f"Keywords: {result['keywords']}")
    print(f"Entities: {result['entities']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n" + "=" * 60)
print("✅ All tests complete!")
print("=" * 60)
