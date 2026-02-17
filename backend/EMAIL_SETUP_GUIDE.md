# Email Setup Guide - Gmail SMTP Configuration

## Overview
This guide explains how to configure Gmail SMTP for sending automated emails from the Call Intelligence Platform.

---

## Step 1: Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** section
3. Find **2-Step Verification** and enable it
4. Follow the prompts to set up 2FA (SMS or Authenticator app)

---

## Step 2: Generate App Password

1. Once 2FA is enabled, go back to **Security** section
2. Find **App passwords** (under 2-Step Verification section)
3. Click on **App passwords**
4. Select:
   - **App**: Mail
   - **Device**: Other (Custom name)
5. Enter name: "Call Intelligence Platform"
6. Click **Generate**
7. **IMPORTANT**: Copy the 16-character password immediately
   - Format: `xxxx xxxx xxxx xxxx`
   - You won't be able to see it again

---

## Step 3: Configure Environment Variables

1. Navigate to `backend/` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file and add your credentials:
   ```env
   SENDER_EMAIL=naveenarul111@gmail.com
   SENDER_PASSWORD=your_16_char_app_password_here
   ```

4. **Remove spaces** from the app password when pasting

---

## Step 4: Test Email Service

### Test from Python:

```bash
cd backend
python -c "from services.email_service import EmailService; es = EmailService(); print(es.sender_email)"
```

### Test sending email:

```python
from services.email_service import EmailService

email_service = EmailService()

# Test email
result = email_service.send_email(
    to_email="naveenarul111@gmail.com",
    subject="Test Email from Call Intelligence Platform",
    html_content="<h1>Test successful!</h1><p>Email service is working.</p>"
)

print(result)
```

---

## Step 5: Start Reminder Scheduler

Run the reminder scheduler as a background service:

```bash
cd backend
python reminder_scheduler.py
```

This will:
- Check for pending calls every 15 minutes
- Send reminder emails based on priority:
  - **Urgent**: 2 hours after creation
  - **High**: 6 hours
  - **Medium**: 24 hours
  - **Low**: 48 hours

---

## Troubleshooting

### "Authentication failed" error

**Solution 1**: Check if 2FA is enabled
- App passwords only work with 2FA enabled

**Solution 2**: Verify app password
- Copy-paste without spaces
- Generate new app password if needed

**Solution 3**: Check email address
- Make sure `SENDER_EMAIL` matches the Google account

### "Connection refused" error

**Solution**: Check firewall/network
- Port 587 (SMTP) must be open
- Some corporate networks block SMTP

### "Less secure app access" error

**This is outdated**: Google removed this option
- You MUST use App Passwords now (no alternative)

---

## Email Features

### 1. Action Notification Email
Sent after call processing with:
- Recommended action
- Priority score
- Sentiment analysis
- Full transcript preview
- AI reasoning

### 2. Reminder Email
Sent for pending actions with:
- Priority banner
- Pending action details
- Urgency indicator
- Direct link to dashboard

---

## Security Best Practices

1. **Never commit `.env` file** to git
   - Already in `.gitignore`

2. **Use App Passwords** (not account password)
   - Safer and can be revoked

3. **Rotate passwords periodically**
   - Revoke and regenerate every 3-6 months

4. **For production**: Use dedicated email service
   - SendGrid, AWS SES, Mailgun, etc.
   - Gmail has sending limits (500/day for free accounts)

---

## Gmail Sending Limits

- **Free Gmail**: 500 emails/day
- **Google Workspace**: 2000 emails/day
- **Rate limit**: ~100 emails/hour

For high-volume usage, consider:
- **SendGrid**: 100 emails/day free, then paid
- **AWS SES**: $0.10 per 1000 emails
- **Mailgun**: 5000 emails/month free

---

## Alternative: Using SendGrid (Recommended for Production)

1. Sign up: https://signup.sendgrid.com/
2. Get API key
3. Update `email_service.py`:
   ```python
   import sendgrid
   from sendgrid.helpers.mail import Mail

   sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
   ```

---

## Testing Email Templates

Preview email templates without sending:

```python
from services.email_service import EmailService

email_service = EmailService()

# Generate HTML (doesn't send)
html = email_service.create_action_email(
    call_data={...},  # Your call data
    recipient_email="test@example.com"
)

# Save to file for preview
with open("email_preview.html", "w") as f:
    f.write(html)
```

Open `email_preview.html` in browser to preview.

---

## Troubleshooting Connection Issues

### Error: "Email server connection timeout"

This error means the application cannot connect to Gmail's SMTP server. Common causes:

**1. Firewall Blocking**
- Windows Firewall may block ports 587 (TLS) or 465 (SSL)
- Corporate firewall restrictions
- Antivirus software blocking outbound connections

**Solution:**
```powershell
# Allow Python through Windows Firewall (Run as Administrator)
New-NetFirewallRule -DisplayName "Python SMTP" -Direction Outbound -Program "C:\Python\python.exe" -Action Allow

# Or temporarily disable firewall to test
# Control Panel → Windows Defender Firewall → Turn Windows Defender Firewall on or off
```

**2. Network Restrictions**
- Using corporate/school network that blocks SMTP
- VPN interfering with connections
- ISP blocking email ports

**Solution:**
- Try from different network (home WiFi, mobile hotspot)
- Disable VPN temporarily
- Contact network administrator

**3. Gmail SMTP Not Accessible**
- Gmail servers temporarily down
- Regional restrictions

**Solution:**
- Check https://www.google.com/appsstatus (Gmail status)
- Try again after few minutes

**4. Incorrect Credentials**
- Using regular Gmail password instead of App Password
- Typo in SENDER_PASSWORD

**Solution:**
- Regenerate App Password
- Copy-paste carefully (remove spaces)
- Verify SENDER_EMAIL is correct

### ⚠️ Email is OPTIONAL

**The platform works perfectly without email configured!**

If you cannot set up email:
1. Call processing still works
2. All analysis features work
3. Only email notifications are disabled

The system will show a warning but continue working:
```
"Email feature disabled. Configure SENDER_EMAIL and SENDER_PASSWORD to enable."
```

### Testing Email Connection

Create a test script:

```python
# test_email_connection.py
import smtplib
import ssl

SMTP_SERVER = "smtp.gmail.com"
EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"

print("Testing TLS (port 587)...")
try:
    with smtplib.SMTP(SMTP_SERVER, 587, timeout=10) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        print("✅ TLS Connection successful!")
except Exception as e:
    print(f"❌ TLS Failed: {e}")

print("\nTesting SSL (port 465)...")
try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, 465, timeout=10, context=context) as server:
        server.login(EMAIL, PASSWORD)
        print("✅ SSL Connection successful!")
except Exception as e:
    print(f"❌ SSL Failed: {e}")
```

Run:
```bash
cd backend
python test_email_connection.py
```

---

## Support

For issues:
1. Check `.env` configuration
2. Verify Google account settings
3. Review `backend/logs/` for errors
4. Test with simple email first

---

**Setup Complete!** ✅

Your email system is now configured for:
- Real-time action notifications
- Automated reminders
- CRM integration alerts
