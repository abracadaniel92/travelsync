# Quick Start Guide - Raspberry Pi Setup

## What I've Fixed

✅ **Fixed docker-compose.yml** - Removed obsolete `version` field (Docker Compose v5 compatibility)
✅ **Created env.template** - Template file for environment variables
✅ **Created quick_setup.sh** - Automated setup script
✅ **Created SETUP_PI.md** - Detailed setup guide
✅ **Created necessary directories** - uploads/ and temp/ folders

## Current Status

Your project is ready to configure! Here's what you need to do:

## Step 1: Create .env File

```bash
cd "/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1"
cp env.template .env
nano .env
```

Fill in these **required** values:
- `GOOGLE_API_KEY` - Get from https://aistudio.google.com/app/apikey
- `CREDENTIALS_JSON` - Base64 encoded credentials.json (see below)
- `ADMIN_PASSWORD` - Choose a secure password
- `JWT_SECRET_KEY` - Generate with: `openssl rand -hex 32`

## Step 2: Get Google Calendar Credentials

### If you have credentials.json:
```bash
base64 -i credentials.json | tr -d '\n'
```
Copy the output and paste it as `CREDENTIALS_JSON` in your `.env` file.

### If you don't have credentials.json:
1. Go to https://console.cloud.google.com/
2. Create/select a project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json
6. Encode it as above

## Step 3: Get Google Calendar Token

You need to authenticate once with Google Calendar. This creates `token.pickle`.

**Option A: Authenticate on your local machine (Recommended)**
1. On your local machine, run the app and authenticate
2. Copy `token.pickle` to your Pi:
   ```bash
   scp token.pickle goce@your-pi-ip:"/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1/"
   ```

**Option B: Authenticate on Pi (if it has display)**
1. Set `GOOGLE_CALENDAR_HEADLESS=false` in `.env`
2. Run the container and authenticate
3. Set it back to `true`

## Step 4: Run Setup Script

```bash
cd "/home/goce/Desktop/Cursor projects/DocumentsToCalendar-1"
./quick_setup.sh
```

Or manually:
```bash
# Build and start
docker compose build
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

## Step 5: Configure Caddy (Optional)

Add to your Caddyfile:
```caddy
documents.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Then reload:
```bash
sudo caddy reload
```

## Step 6: Test

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Access web interface
# http://localhost:8000
# or http://your-pi-ip:8000
```

## Troubleshooting

### Container won't start
```bash
docker compose logs
```

### Missing environment variables
Check that all required variables are in `.env`:
- GOOGLE_API_KEY
- CREDENTIALS_JSON
- ADMIN_PASSWORD
- JWT_SECRET_KEY

### Token authentication errors
- Ensure `token.pickle` exists
- If expired, delete it and re-authenticate
- Check file permissions: `ls -la token.pickle`

## Useful Commands

```bash
# View logs
docker compose logs -f app

# Restart
docker compose restart

# Stop
docker compose down

# Rebuild
docker compose build --no-cache
docker compose up -d
```

## Next Steps

1. ✅ Create `.env` file with your credentials
2. ✅ Get `token.pickle` (authenticate with Google Calendar)
3. ✅ Run `./quick_setup.sh` or manually build/start
4. ✅ Configure Caddy reverse proxy (optional)
5. ✅ Test the application

For more details, see `SETUP_PI.md`.

