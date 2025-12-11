# Email Forwarding Setup Guide

This guide explains how to set up email forwarding so you can forward travel documents to your service and have them automatically processed.

## Option 1: Dedicated Email Inbox (Recommended)

Set up a dedicated email address that receives forwarded emails, and the service monitors it automatically.

### Step 1: Create a Dedicated Email Account

1. **Create a new Gmail account** (e.g., `documents-to-calendar@gmail.com`)
   - Or use any email provider that supports IMAP
   - This will be your "forwarding destination"

2. **Set up App Password** (for Gmail):
   - Go to Google Account → Security → App passwords
   - Generate a password for "Mail"
   - Save the 16-character password

### Step 2: Configure the Service

Set environment variables to point to your dedicated inbox:

```powershell
# PowerShell
$env:EMAIL_ADDRESS = "documents-to-calendar@gmail.com"
$env:EMAIL_PASSWORD = "your-16-char-app-password"
$env:EMAIL_AUTO_CHECK = "true"  # Enable automatic checking
$env:EMAIL_CHECK_INTERVAL = "300"  # Check every 5 minutes (in seconds)
```

Or in `.env` file:
```env
EMAIL_ADDRESS=documents-to-calendar@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_AUTO_CHECK=true
EMAIL_CHECK_INTERVAL=300
```

### Step 3: Forward Emails to the Dedicated Address

**From Gmail:**
1. Go to Settings → Forwarding and POP/IMAP
2. Click "Add a forwarding address"
3. Enter your dedicated email: `documents-to-calendar@gmail.com`
4. Verify the forwarding address
5. Select "Forward a copy of incoming mail to"
6. Save changes

**From Outlook:**
1. Go to Settings → Mail → Forwarding
2. Enable forwarding
3. Enter your dedicated email address
4. Save

**From any email:**
- Simply forward emails with travel document attachments to your dedicated address
- The service will automatically process them

### Step 4: Start the Service

The service will automatically check for new emails every 5 minutes (or your configured interval) and process them.

## Option 2: Webhook Endpoint (Advanced)

For services like SendGrid or Mailgun that can send webhooks.

### Step 1: Set Webhook API Key

```env
EMAIL_WEBHOOK_API_KEY=your-secure-api-key-here
```

### Step 2: Configure Email Service

Set up your email service (SendGrid, Mailgun, etc.) to send webhooks to:
```
https://your-domain.com/api/email/webhook
```

Include the API key in the header:
```
X-API-Key: your-secure-api-key-here
```

### Step 3: Configure Inbound Parse

**SendGrid:**
1. Go to Settings → Inbound Parse
2. Add a hostname
3. Set POST URL to: `https://your-domain.com/api/email/webhook`
4. Add header: `X-API-Key: your-secure-api-key-here`

**Mailgun:**
1. Go to Receiving → Routes
2. Create a route
3. Set action to: `https://your-domain.com/api/email/webhook`
4. Add header: `X-API-Key: your-secure-api-key-here`

## How It Works

### Automatic Processing (Option 1)

1. **Email Received**: Forwarded email arrives at dedicated inbox
2. **Auto-Check**: Service checks inbox every X minutes (configurable)
3. **Detection**: Finds emails with image/PDF attachments
4. **Processing**: Each attachment processed through Gemini AI
5. **Calendar**: Travel info automatically added to calendar
6. **Organization**: Emails moved to "Processed" or "Failed" folders

### Webhook Processing (Option 2)

1. **Email Received**: Email service receives email
2. **Webhook**: Service sends POST request to your webhook endpoint
3. **Processing**: Attachments extracted and processed immediately
4. **Calendar**: Travel info added to calendar
5. **Response**: Service returns processing results

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_ADDRESS` | Email address to monitor | Required |
| `EMAIL_PASSWORD` | App password for email | Required |
| `EMAIL_IMAP_SERVER` | IMAP server address | `imap.gmail.com` |
| `EMAIL_IMAP_PORT` | IMAP server port | `993` |
| `EMAIL_AUTO_CHECK` | Enable automatic checking | `false` |
| `EMAIL_CHECK_INTERVAL` | Check interval in seconds | `300` (5 min) |
| `EMAIL_PROCESSED_FOLDER` | Folder for processed emails | `Processed` |
| `EMAIL_FAILED_FOLDER` | Folder for failed emails | `Failed` |
| `EMAIL_WEBHOOK_API_KEY` | API key for webhook endpoint | Optional |

## Testing

### Test Email Connection

```bash
curl -X POST http://localhost:8000/api/email/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Manually Check Emails

```bash
curl -X POST http://localhost:8000/api/email/check \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Webhook

```bash
curl -X POST http://localhost:8000/api/email/webhook \
  -H "X-API-Key: your-api-key" \
  -F "sender=test@example.com" \
  -F "subject=Test" \
  -F "attachment-1=@document.pdf"
```

## Best Practices

1. **Use a Dedicated Email**: Don't use your personal email - create a separate account
2. **Enable Auto-Check**: Set `EMAIL_AUTO_CHECK=true` for automatic processing
3. **Set Reasonable Interval**: 5 minutes (300 seconds) is usually good
4. **Monitor Logs**: Check server logs to see processing status
5. **Use App Passwords**: Never use your main email password
6. **Secure Webhooks**: Always use API keys for webhook endpoints

## Troubleshooting

### Emails Not Being Processed

- Check that `EMAIL_AUTO_CHECK=true` is set
- Verify email credentials are correct
- Check server logs for errors
- Manually trigger check via API to test

### Webhook Not Working

- Verify API key matches in header
- Check webhook URL is accessible
- Verify email service is sending correct format
- Check server logs for incoming requests

### Rate Limits

- Remember Gemini API has daily limits
- Each attachment = 1 API call
- Monitor your usage in Google AI Studio

## Example Workflow

1. You receive a flight confirmation email
2. Forward it to `documents-to-calendar@gmail.com`
3. Service checks inbox every 5 minutes
4. Finds the forwarded email with PDF attachment
5. Processes PDF through Gemini AI
6. Extracts: Flight date, time, destination, etc.
7. Creates calendar event automatically
8. Moves email to "Processed" folder
9. You get a calendar notification! ✈️


