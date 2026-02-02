# Setup Guide

## Initial Setup Steps

### 1. Get Google Gemini API Key

1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (you won't see it again!)

### 2. Set Up GitHub Secrets

For production deployment, store your API key securely:

1. Go to your repository: `https://github.com/abracadaniel92/DocumentsToCalendar`
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `ADMIN_PASSWORD`: Your desired admin password (plain text)
   - `JWT_SECRET_KEY`: Generate a strong random string (e.g., `openssl rand -hex 32`)

### 3. Local Development Setup

1. **Clone the repository** (if not already):
   ```bash
   git clone https://github.com/abracadaniel92/DocumentsToCalendar
   cd DocumentsToCalendar
   ```

2. **Create environment file**:
   ```bash
   # Create .env file in root directory
   cat > .env << EOF
   GOOGLE_API_KEY=your_gemini_api_key_here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password_here
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   DATABASE_URL=sqlite:///./documents_calendar.db
   EOF
   ```

3. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   # From the root directory
   uvicorn backend.main:app --reload
   ```

5. **Access the app**:
   - Open http://localhost:8000
   - Login with username: `admin` and your password

### 4. Docker Setup

1. **Build the image**:
   ```bash
   docker build -t documents-to-calendar .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

### 5. Email Forwarding Setup (Optional)

Automatically process travel documents from your email:

1. **For Gmail users**:
   - Enable 2-Step Verification in your Google Account
   - Go to Security → App passwords
   - Generate an app password for "Mail"
   - Copy the 16-character password

2. **Set environment variables**:
   ```bash
   export EMAIL_ADDRESS=your-email@gmail.com
   export EMAIL_PASSWORD=your-16-char-app-password
   # Optional - defaults shown:
   export EMAIL_IMAP_SERVER=imap.gmail.com
   export EMAIL_IMAP_PORT=993
   export EMAIL_PROCESSED_FOLDER=Processed
   export EMAIL_FAILED_FOLDER=Failed
   ```

3. **For other email providers**:
   - Update `EMAIL_IMAP_SERVER` and `EMAIL_IMAP_PORT` accordingly
   - Use your email provider's IMAP settings

4. **Check email status**:
   ```bash
   curl http://localhost:8000/api/email/status \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

5. **Process emails**:
   - Call `/api/email/check` endpoint to check for new emails
   - The service will:
     - Find emails with image/PDF attachments
     - Process each attachment
     - Create calendar events automatically
     - Organize emails into folders

### 6. Google Calendar Integration (Optional)

To enable automatic calendar event creation:

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create a new project

2. **Enable Calendar API**:
   - Navigate to APIs & Services → Library
   - Search for "Google Calendar API"
   - Click Enable

3. **Create OAuth Credentials**:
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download the JSON file

4. **Place credentials**:
   ```bash
   cp ~/Downloads/credentials.json ./credentials.json
   ```

5. **First authentication**:
   - When you upload your first document, the app will open a browser
   - Sign in and authorize access
   - Token will be saved automatically

### 7. Deployment to Raspberry Pi

1. **SSH into your Pi**:
   ```bash
   ssh pi@your-pi-hostname
   ```

2. **Clone repository**:
   ```bash
   git clone https://github.com/abracadaniel92/DocumentsToCalendar
   cd DocumentsToCalendar
   ```

3. **Set environment variables** (or use GitHub Secrets):
   ```bash
   export GOOGLE_API_KEY=your_key
   export ADMIN_PASSWORD=your_password
   export JWT_SECRET_KEY=your_secret
   ```

4. **Build and run**:
   ```bash
   docker-compose up -d
   ```

5. **Configure Caddy**:
   Add to your Caddyfile:
   ```
   your-domain.com {
       reverse_proxy localhost:8000
   }
   ```

6. **Reload Caddy**:
   ```bash
   docker exec caddy caddy reload
   ```

## Troubleshooting

### "GOOGLE_API_KEY not set" error
- Make sure you've set the environment variable
- Check that `.env` file exists and has the key
- For Docker, ensure environment variables are passed

### Email forwarding not working
- Verify `EMAIL_ADDRESS` and `EMAIL_PASSWORD` are set
- For Gmail, use an App Password (not your regular password)
- Check IMAP server settings match your email provider
- Ensure 2-Step Verification is enabled for Gmail
- Test IMAP connection manually if needed

### "Could not extract travel information"
- Check that your document is clear and readable
- Ensure the document contains travel information (dates, locations)
- Try a different image format (JPG instead of PNG)

### Calendar integration not working
- Verify `credentials.json` exists and is valid
- Check that Google Calendar API is enabled
- Ensure you've completed OAuth flow on first use

### Login not working
- Default username is `admin`
- Password is set via `ADMIN_PASSWORD` environment variable
- Check that database was initialized (should happen automatically)

## Security Notes

- Never commit `.env` file or `credentials.json` to git
- Use strong passwords for `ADMIN_PASSWORD`
- Generate a secure `JWT_SECRET_KEY` (use `openssl rand -hex 32`)
- In production, use GitHub Secrets or a secrets management service
- Consider adding rate limiting for production use

