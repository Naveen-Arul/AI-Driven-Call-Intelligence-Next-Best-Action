"""
Test script to verify the transcription API is working
"""

import requests

# Test health endpoint
print("Testing API health endpoint...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test health check
print("\nTesting detailed health check...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
