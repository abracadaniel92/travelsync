# Raspberry Pi Setup Guide

This guide will help you set up DocumentsToCalendar on your Raspberry Pi with Docker and Caddy.

## Prerequisites Checklist

- [ ] Docker and Docker Compose installed (you have Docker Compose v5.0.0 ✅)
- [ ] Caddy running (you have Caddy running ✅)
- [ ] Google Gemini API key
- [ ] Google Calendar OAuth credentials (credentials.json)
- [ ] Google Calendar authentication token (token.pickle)

## Step 1: Create Environment File

1. Copy the example environment file:
   ```bash
   cd "/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1"
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual values:
   ```bash
   nano .env
   ```

3. Fill in these **required** values:
   - `GOOGLE_API_KEY` - Your Gemini API key from Google AI Studio
   - `CREDENTIALS_JSON` - Base64 encoded credentials.json (see Step 2)
   - `ADMIN_PASSWORD` - Choose a secure password
   - `JWT_SECRET_KEY` - Generate with: `openssl rand -hex 32`

## Step 2: Prepare Google Calendar Credentials

### Option A: You have credentials.json file

1. Encode it to base64:
   ```bash
   base64 -i credentials.json | tr -d '\n' > credentials_base64.txt
   cat credentials_base64.txt
   ```

2. Copy the entire output and paste it as the value for `CREDENTIALS_JSON` in your `.env` file

### Option B: You need to create credentials.json

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download credentials.json
6. Follow Option A above to encode it

## Step 3: Get Google Calendar Token (token.pickle)

You need to authenticate with Google Calendar once. This creates `token.pickle`.

### Option A: Authenticate on your local machine (Recommended)

1. On your local machine (Windows/Mac/Linux):
   ```bash
   # Install Python dependencies
   pip install -r backend/requirements.txt
   
   # Set environment variables temporarily
   export GOOGLE_CALENDAR_HEADLESS=false
   export GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials.json
   
   # Run the app
   python -m uvicorn backend.main:app --reload
   ```

2. Open browser: http://localhost:8000
3. Log in and click "Test Calendar Connection"
4. Authenticate with Google - this creates `token.pickle`
5. Copy `token.pickle` to your Pi:
   ```bash
   scp token.pickle goce@your-pi-ip:"/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1/"
   ```

### Option B: Authenticate directly on Pi (if it has display)

1. Temporarily set `GOOGLE_CALENDAR_HEADLESS=false` in `.env`
2. Run the container and authenticate
3. Set it back to `true` after authentication

## Step 4: Build and Start Docker Container

```bash
cd "/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1"

# Build the image
docker compose build

# Start the container
docker compose up -d

# Check if it's running
docker compose ps

# View logs
docker compose logs -f
```

## Step 5: Verify Installation

1. Check container status:
   ```bash
   docker ps | grep documents-to-calendar
   ```

2. Test health endpoint:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"healthy"}`

3. Access the web interface:
   - Local: http://localhost:8000
   - Network: http://your-pi-ip:8000

## Step 6: Configure Caddy Reverse Proxy

Since you already have Caddy running, add this to your Caddyfile:

```caddy
# Add this to your existing Caddyfile
# Replace 'documents.yourdomain.com' with your desired subdomain

documents.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Or if you want to use a path instead:

```caddy
yourdomain.com {
    # Your existing static site config...
    
    handle /documents/* {
        uri strip_prefix /documents
        reverse_proxy localhost:8000
    }
}
```

Then reload Caddy:
```bash
sudo caddy reload
```

## Step 7: Test the Application

1. Access via your domain or http://your-pi-ip:8000
2. Log in with your admin credentials
3. Upload a test document (PDF or image)
4. Check your Google Calendar for the new event

## Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker compose logs

# Check environment variables
docker compose config
```

### "Credentials not found" error

- Verify `CREDENTIALS_JSON` in `.env` is base64 encoded correctly
- Make sure it's one long string with no line breaks
- Check logs: `docker compose logs app | grep -i credential`

### "Token not found" or authentication errors

- Ensure `token.pickle` exists in the project directory
- If token expired, delete it and re-authenticate
- Check file permissions: `ls -la token.pickle`

### Can't access from network

```bash
# Check if port 8000 is open
sudo netstat -tulpn | grep 8000

# If using firewall, allow port 8000
sudo ufw allow 8000
```

### Caddy reverse proxy not working

- Check Caddy logs: `sudo journalctl -u caddy -f`
- Verify the container is running: `docker ps`
- Test direct access: `curl http://localhost:8000/api/health`

## Useful Commands

```bash
# View logs
docker compose logs -f app

# Restart service
docker compose restart

# Stop service
docker compose down

# Rebuild after code changes
docker compose build --no-cache
docker compose up -d

# Check container resource usage
docker stats documents-to-calendar
```

## Auto-Start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/documents-to-calendar.service
```

Add:
```ini
[Unit]
Description=Documents to Calendar Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=goce
Group=goce

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable documents-to-calendar.service
sudo systemctl start documents-to-calendar.service
```

## Next Steps

1. ✅ Set up `.env` file with all required variables
2. ✅ Get `token.pickle` (authenticate with Google Calendar)
3. ✅ Build and start Docker container
4. ✅ Configure Caddy reverse proxy
5. ✅ Test the application

Good luck! 🚀

