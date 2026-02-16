import requests
import json

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
