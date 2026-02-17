"""
Email Connection Test Script
Tests SMTP connectivity to Gmail servers
"""

import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
EMAIL = os.getenv("SENDER_EMAIL", "naveenarul111@gmail.com")
PASSWORD = os.getenv("SENDER_PASSWORD", "")

print("=" * 60)
print("📧 EMAIL CONNECTION DIAGNOSTIC TEST")
print("=" * 60)
print()

# Check configuration
print("1️⃣ Checking Configuration...")
print(f"   Email: {EMAIL}")
print(f"   Password: {'*' * len(PASSWORD) if PASSWORD else '❌ NOT SET'}")
print()

if not PASSWORD:
    print("⚠️  WARNING: SENDER_PASSWORD not configured in .env file")
    print("   Email features will be disabled.")
    print()
    print("   To fix: Add SENDER_PASSWORD to backend/.env file")
    print("   See EMAIL_SETUP_GUIDE.md for instructions")
    exit(1)

# Test TLS connection
print("2️⃣ Testing TLS Connection (port 587)...")
try:
    with smtplib.SMTP(SMTP_SERVER, 587, timeout=10) as server:
        print("   📡 Connected to SMTP server")
        server.starttls()
        print("   🔒 TLS encryption started")
        server.login(EMAIL, PASSWORD)
        print("   ✅ Authentication successful!")
        print("   ✅ TLS CONNECTION WORKS!")
        print()
        print("=" * 60)
        print("✅ Email is configured correctly!")
        print("=" * 60)
        exit(0)
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ Authentication failed: {e}")
    print()
    print("   Possible fixes:")
    print("   - Make sure you're using an App Password, NOT your Gmail password")
    print("   - Regenerate App Password in Google Account settings")
    print("   - See EMAIL_SETUP_GUIDE.md for instructions")
    print()
except ConnectionRefusedError:
    print("   ❌ Connection refused")
    print("   Firewall may be blocking port 587")
    print()
except TimeoutError:
    print("   ❌ Connection timeout")
    print("   Cannot reach Gmail SMTP server on port 587")
    print()
except Exception as e:
    print(f"   ❌ TLS connection failed: {e}")
    print()

# Test SSL connection
print("3️⃣ Testing SSL Connection (port 465)...")
try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, 465, timeout=10, context=context) as server:
        print("   📡 Connected to SMTP server via SSL")
        server.login(EMAIL, PASSWORD)
        print("   ✅ Authentication successful!")
        print("   ✅ SSL CONNECTION WORKS!")
        print()
        print("=" * 60)
        print("✅ Email is configured correctly (using SSL)!")
        print("=" * 60)
        exit(0)
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ Authentication failed: {e}")
    print()
except Exception as e:
    print(f"   ❌ SSL connection failed: {e}")
    print()

# Both failed
print("=" * 60)
print("❌ BOTH TLS AND SSL CONNECTIONS FAILED")
print("=" * 60)
print()
print("Possible causes:")
print("1. 🔥 Firewall blocking ports 587 and 465")
print("   → Check Windows Firewall settings")
print("   → Try temporarily disabling firewall to test")
print()
print("2. 🌐 Network restrictions")
print("   → Corporate/school network blocking SMTP")
print("   → Try from different network (mobile hotspot)")
print()
print("3. 🔑 Incorrect credentials")
print("   → Verify SENDER_EMAIL and SENDER_PASSWORD in .env")
print("   → Use App Password, not regular Gmail password")
print()
print("4. 🛡️ Antivirus software blocking connections")
print("   → Check antivirus logs")
print("   → Temporarily disable to test")
print()
print("📖 See EMAIL_SETUP_GUIDE.md for detailed instructions")
print()
print("💡 Note: Email is OPTIONAL - the platform works without it!")
