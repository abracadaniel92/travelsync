# Google Calendar Authentication Guide

## URL for Authentication

The application runs on **port 8000**, not 8080.

### Direct Access:
```
http://your-pi-ip-address:8000
```

### Via Caddy (if configured):
If you've configured Caddy to proxy this app, use your domain or Caddy's port (8080).

## Authentication Steps

### Method 1: Via Web Interface (Recommended)

1. **Start the container** (if not already running):
   ```bash
   cd /mnt/ssd/docker-projects/documents-to-calendar
   docker compose up -d
   ```

2. **Access the web interface**:
   - Open browser: `http://your-pi-ip:8000`
   - Or if Caddy is configured: `http://your-domain` or `http://your-pi-ip:8080`

3. **Log in** with your admin credentials (from `.env` file)

4. **Click "Test Calendar Connection"** button

5. **OAuth Flow**:
   - The app will start the OAuth authentication
   - If `GOOGLE_CALENDAR_HEADLESS=false` in your `.env`, it will try to open a browser
   - **In Docker, the browser won't open automatically**, so you need to:
     - Check the Docker logs: `docker compose logs -f`
     - Look for a line like: `Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...`
     - Copy that URL and open it in your browser
     - Complete the Google authentication
     - The token will be saved to `data/token.pickle`

### Method 2: Authenticate Locally First (Easier)

1. **On your local machine** (not the Pi):
   - Run the app locally (not in Docker)
   - Authenticate with Google Calendar
   - This creates `token.pickle`

2. **Copy token.pickle to Pi**:
   ```bash
   scp token.pickle goce@raspberrypi:/mnt/ssd/docker-projects/documents-to-calendar/data/
   ```

3. **Set headless mode** in `.env`:
   ```
   GOOGLE_CALENDAR_HEADLESS=true
   ```

## Current Configuration

- **App Port**: `8000`
- **Caddy Port**: `8080` (if you have Caddy configured)
- **Headless Mode**: Currently set to `false` (allows browser-based auth)

## Quick Check

To see what IP address to use:
```bash
hostname -I
```

Then access: `http://<that-ip>:8000`

## Troubleshooting

### Can't access the web interface
```bash
# Check if container is running
docker compose ps

# Check if port 8000 is accessible
curl http://localhost:8000/api/health

# Check firewall
sudo ufw status
sudo ufw allow 8000  # if needed
```

### OAuth URL not opening
- Check Docker logs: `docker compose logs -f`
- Look for the authorization URL in the logs
- Copy and paste it manually into your browser

### Token not saving
- Make sure `data/` directory exists and is writable
- Check file permissions: `ls -la data/`
- Check Docker logs for errors

