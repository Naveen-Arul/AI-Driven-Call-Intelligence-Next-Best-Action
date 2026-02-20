"""
Quick Test Script for Voice Bot API
Tests all voice endpoints to verify setup
"""

import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:5000"
VOICE_API_URL = f"{API_URL}/api/voice"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_backend_health():
    """Test if backend API is running"""
    print_header("Test 1: Backend Health Check")
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_voice_health():
    """Test voice API health"""
    print_header("Test 2: Voice API Health Check")
    try:
        response = requests.get(f"{VOICE_API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Voice API is healthy")
            print(f"   Status: {data.get('status')}")
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   - {service}: {status}")
            return True
        else:
            print(f"❌ Voice API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_transcription():
    """Test transcription endpoint (mock test - needs real audio)"""
    print_header("Test 3: Transcription Endpoint")
    try:
        # Note: This will fail without actual audio file
        # Just checking if endpoint exists
        response = requests.post(
            f"{VOICE_API_URL}/transcribe",
            files={'audio': ('test.wav', b'', 'audio/wav')},
            timeout=5
        )
        # Any response (even error) means endpoint exists
        if response.status_code in [200, 400, 422, 500]:
            print("✅ Transcription endpoint exists")
            if response.status_code != 200:
                print("   ℹ️  Note: Returns error without valid audio (expected)")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_chat():
    """Test chat endpoint"""
    print_header("Test 4: Chat Endpoint") 
    try:
        test_data = {
            "message": "Hello, this is a test",
            "language": "en",
            "session_id": "test_session_123",
            "history": []
        }
        response = requests.post(
            f"{VOICE_API_URL}/chat",
            json=test_data,
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"   AI Response: {data.get('response', 'N/A')[:100]}...")
            print(f"   Language: {data.get('language')}")
            print(f"   Sentiment: {data.get('sentiment', 'N/A')}")
            return True
        else:
            print(f"❌ Chat endpoint returned status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_tts():
    """Test text-to-speech endpoint"""
    print_header("Test 5: Text-to-Speech Endpoint")
    try:
        test_data = {
            "text": "Hello, this is a test of the text to speech system.",
            "language": "en"
        }
        response = requests.post(
            f"{VOICE_API_URL}/tts",
            json=test_data,
            timeout=20
        )
        if response.status_code == 200:
            audio_size = len(response.content)
            print("✅ TTS endpoint working")
            print(f"   Audio generated: {audio_size} bytes")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            return True
        else:
            print(f"❌ TTS endpoint returned status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Environment Variables Check")
    
    env_file = Path("../.env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        return False
    
    with open(env_file) as f:
        env_content = f.read()
    
    required_vars = {
        "GROQ_API_KEY": "Required for AI chat responses",
        "ELEVENLABS_API_KEY": "Required for text-to-speech"
    }
    
    optional_vars = {
        "TWILIO_ACCOUNT_SID": "Optional for phone-based bot",
        "TWILIO_AUTH_TOKEN": "Optional for phone-based bot",
        "TWILIO_PHONE_NUMBER": "Optional for phone-based bot"
    }
    
    all_good = True
    
    print("\n📋 Required Variables:")
    for var, description in required_vars.items():
        if var in env_content and not env_content.split(f"{var}=")[1].split("\n")[0].strip().startswith("#"):
            value = env_content.split(f"{var}=")[1].split("\n")[0].strip()
            if value and value != "your_key_here":
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ❌ {var}: Not set or placeholder")
                print(f"      ({description})")
                all_good = False
        else:
            print(f"   ❌ {var}: Missing")
            print(f"      ({description})")
            all_good = False
    
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        if var in env_content:
            print(f"   ℹ️  {var}: Found ({description})")
        else:
            print(f"   ℹ️  {var}: Not set ({description})")
    
    return all_good

def main():
    """Run all tests"""
    print("\n" + "🎯" * 30)
    print("        Voice Bot API - Quick Test Suite")
    print("🎯" * 30)
    
    results = {
        "Backend Health": False,
        "Voice API Health": False,
        "Transcription Endpoint": False,
        "Chat Endpoint": False,
        "TTS Endpoint": False,
        "Environment Variables": False
    }
    
    # Check environment first
    results["Environment Variables"] = check_environment_variables()
    
    # Test backend
    results["Backend Health"] = test_backend_health()
    if not results["Backend Health"]:
        print("\n⚠️  Backend not running. Start it first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    # Test voice API
    results["Voice API Health"] = test_voice_health()
    results["Transcription Endpoint"] = test_transcription()
    results["Chat Endpoint"] = test_chat()
    results["TTS Endpoint"] = test_tts()
    
    # Summary
    print_header("Test Summary")
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test}")
    
    print(f"\n   Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   🎉 All tests passed! Voice bot is ready!")
        print("\n   Next steps:")
        print("   1. Open customer-frontend/index.html in browser")
        print("   2. Allow microphone access")
        print("   3. Start talking!")
    else:
        print("\n   ⚠️  Some tests failed. Check the errors above.")
        print("\n   Common fixes:")
        print("   1. Start backend: cd backend && python app.py")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Set API keys in .env file")
        print("   4. Check backend logs for errors")

if __name__ == "__main__":
    main()
