# Google Calendar Integration Setup Guide

This guide will walk you through connecting Google Calendar to automatically create events from travel documents.

## Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click **"New Project"**
4. Enter a project name (e.g., "Documents to Calendar")
5. Click **"Create"**
6. Wait for the project to be created and select it

### Step 2: Enable Google Calendar API

1. In your Google Cloud project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Calendar API"**
3. Click on **"Google Calendar API"**
4. Click **"Enable"**
5. Wait for the API to be enabled (usually takes a few seconds)

### Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, configure the OAuth consent screen first:
   - Choose **"External"** (unless you have a Google Workspace account)
   - Click **"Create"**
   - Fill in the required fields:
     - **App name**: Documents to Calendar
     - **User support email**: Your email
     - **Developer contact**: Your email
   - Click **"Save and Continue"**
   - On "Scopes" page, click **"Save and Continue"**
   - On "Test users" page, add your email if needed, then **"Save and Continue"**
   - Review and go back to credentials

5. Back at "Create OAuth client ID":
   - **Application type**: Select **"Desktop app"**
   - **Name**: Documents to Calendar (or any name you like)
   - Click **"Create"**

6. **Download the credentials**:
   - A dialog will show your Client ID and Client Secret
   - Click **"Download JSON"**
   - Save the file as `credentials.json`
   - **Important**: Keep this file secure and never commit it to git!

### Step 4: Place Credentials File

**Option A: In project root (recommended for local development)**
```powershell
# Copy the downloaded file to your project root
Copy-Item ~/Downloads/credentials.json DocumentsToCalendar/credentials.json
```

**Option B: Specify custom path**
Set environment variable:
```powershell
$env:GOOGLE_CALENDAR_CREDENTIALS_PATH = "C:\path\to\credentials.json"
```

### Step 5: First-Time Authentication

1. **Start your server** (if not already running):
   ```powershell
   cd DocumentsToCalendar
   .\start_server.ps1
   ```

2. **Upload a document** or trigger calendar access:
   - Go to `http://127.0.0.1:8000`
   - Log in
   - Upload a travel document
   - OR use the test endpoint (see below)

3. **Authorize access**:
   - A browser window will automatically open
   - Sign in with your Google account
   - Review the permissions (Calendar access)
   - Click **"Allow"** or **"Continue"**

4. **Token saved**:
   - The authorization token will be saved as `token.pickle`
   - You won't need to authorize again unless the token expires
   - The token automatically refreshes when needed

### Step 6: Verify Connection

Test the calendar connection:

**Via Web Interface:**
- Use the test endpoint in the web UI (if available)

**Via API:**
```powershell
# Get your JWT token from login, then:
curl http://127.0.0.1:8000/api/calendar/test `
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CALENDAR_CREDENTIALS_PATH` | Path to credentials.json | `credentials.json` |
| `GOOGLE_CALENDAR_TOKEN_PATH` | Path to save token | `token.pickle` |
| `GOOGLE_CALENDAR_ID` | Specific calendar ID | `primary` (your main calendar) |

### Using a Specific Calendar

To use a different calendar (not your primary one):

1. Get your calendar ID:
   - Go to [Google Calendar](https://calendar.google.com/)
   - Click the three dots next to your calendar
   - Select **"Settings and sharing"**
   - Scroll down to **"Integrate calendar"**
   - Copy the **"Calendar ID"** (looks like an email address)

2. Set environment variable:
   ```powershell
   $env:GOOGLE_CALENDAR_ID = "your-calendar-id@group.calendar.google.com"
   ```

## How It Works

1. **Document Processing**: When you upload a travel document, it's processed by Gemini AI
2. **Information Extraction**: Travel details are extracted (dates, location, etc.)
3. **Calendar Event**: An event is automatically created in your Google Calendar
4. **Event Details**: Includes:
   - Title (from document)
   - Start/End date and time
   - Location
   - Description (additional details from document)

## Troubleshooting

### "credentials.json not found"

- Make sure you downloaded the file from Google Cloud Console
- Check the file path is correct
- Verify the file is named exactly `credentials.json`

### "Browser didn't open for authentication"

- Make sure you're running the server locally (not in Docker without display)
- Try manually opening: `http://localhost:8080` (or the port shown in console)
- Copy the authorization URL from server logs

### "Token expired" or "Invalid credentials"

- Delete `token.pickle` file
- Restart the server
- Re-authenticate when prompted

### "Permission denied" or "Insufficient permissions"

- Make sure you enabled **Google Calendar API** in Google Cloud Console
- Check that OAuth consent screen is configured
- Verify you're using the correct Google account

### Events not appearing in calendar

- Check server logs for errors
- Verify the calendar ID is correct
- Make sure you authorized the correct Google account
- Check that dates are being parsed correctly from documents

### Docker/Remote Server Issues

If running on a remote server or Docker without a browser:

1. **Run authentication locally first**:
   - Run the server locally
   - Complete authentication
   - Copy `token.pickle` to your server

2. **Or use service account** (advanced):
   - Create a service account in Google Cloud Console
   - Download service account JSON
   - Share your calendar with the service account email
   - Modify code to use service account credentials

## Security Notes

- **Never commit** `credentials.json` or `token.pickle` to git
- These files contain sensitive authentication data
- Add to `.gitignore` (should already be there)
- Keep credentials secure and don't share them
- Revoke access from [Google Account Settings](https://myaccount.google.com/permissions) if needed

## Testing Calendar Connection

After setup, test by:

1. **Upload a test document** with travel information
2. **Check your Google Calendar** - you should see a new event
3. **Verify event details** match the document information

## Next Steps

Once connected:
- Upload travel documents and watch events appear automatically
- Forward emails with travel documents for automatic processing
- Events are created in your primary calendar by default

Enjoy automatic calendar management! 📅


