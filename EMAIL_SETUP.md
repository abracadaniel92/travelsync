# Email Forwarding Setup Guide

This guide will help you set up email forwarding so you can automatically process travel documents sent via email.

## Quick Setup (Gmail)

### Step 1: Create a Gmail App Password

1. Go to your [Google Account](https://myaccount.google.com/)
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
   - If not enabled, enable it first (required for App Passwords)
4. After 2-Step Verification is enabled, go back to Security
5. Click **App passwords** (under "How you sign in to Google")
6. Select **Mail** as the app and **Other** as the device
7. Enter a name like "Documents to Calendar"
8. Click **Generate**
9. **Copy the 16-character password** (you won't see it again!)

### Step 2: Set Environment Variables

**PowerShell:**
```powershell
$env:EMAIL_ADDRESS = "your-email@gmail.com"
$env:EMAIL_PASSWORD = "your-16-char-app-password"
```

**Or add to your `.env` file:**
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
```

### Step 3: Test the Connection

1. Start your server
2. Log in to the web interface
3. Visit: `http://127.0.0.1:8000/api/email/test` (or use the API with your JWT token)
4. You should see a success message with your email info

### Step 4: Process Emails

**Option A: Via API (Manual Check)**
```bash
# Get your JWT token from login, then:
curl -X POST http://127.0.0.1:8000/api/email/check \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Option B: Forward Emails**
1. Forward any email with travel document attachments to your configured email
2. Call the `/api/email/check` endpoint
3. The system will:
   - Find emails with image/PDF attachments
   - Process each attachment with AI
   - Create calendar events automatically
   - Move processed emails to "Processed" folder
   - Move failed emails to "Failed" folder

## How It Works

1. **Email Check**: The system checks your inbox for unread emails
2. **Attachment Detection**: Finds emails with image or PDF attachments
3. **Processing**: Each attachment is processed through Gemini AI
4. **Calendar Creation**: Travel information is automatically added to your calendar
5. **Organization**: Emails are moved to "Processed" or "Failed" folders

## Other Email Providers

### Outlook/Hotmail
```env
EMAIL_IMAP_SERVER=outlook.office365.com
EMAIL_IMAP_PORT=993
```

### Yahoo
```env
EMAIL_IMAP_SERVER=imap.mail.yahoo.com
EMAIL_IMAP_PORT=993
```

### Custom IMAP
```env
EMAIL_IMAP_SERVER=your-imap-server.com
EMAIL_IMAP_PORT=993
EMAIL_ADDRESS=your-email@domain.com
EMAIL_PASSWORD=your-password
```

## Troubleshooting

### "EMAIL_ADDRESS and EMAIL_PASSWORD must be set"
- Make sure you've set both environment variables
- Check that they're set before starting the server

### "Authentication failed"
- For Gmail, make sure you're using an **App Password**, not your regular password
- Verify 2-Step Verification is enabled
- Check that the App Password is correct (16 characters, no spaces)

### "Connection refused" or "Cannot connect"
- Check your internet connection
- Verify IMAP server and port are correct
- Some networks block IMAP - try a different network or use a VPN

### "No emails found"
- Make sure you have unread emails with attachments
- Check that attachments are images or PDFs
- Verify the emails are in your inbox (not other folders)

## API Endpoints

### GET `/api/email/status`
Check if email is configured (requires authentication)

### POST `/api/email/test`
Test email connection (requires authentication)

### POST `/api/email/check`
Check for new emails and process them (requires authentication)

## Security Notes

- **Never commit** your email password to git
- Use App Passwords instead of your main password
- App Passwords can be revoked from Google Account settings
- Consider using environment variables or a secrets manager in production

