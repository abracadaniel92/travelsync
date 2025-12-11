# Documents to Calendar - Complete Summary & Raspberry Pi Deployment

## What We Built

A web application that:
- ✅ Extracts travel information from documents (PDFs and images) using Google Gemini AI
- ✅ Automatically creates calendar events in Google Calendar
- ✅ Supports PDF and image uploads
- ✅ Has a web interface for document upload
- ✅ Uses JWT authentication
- ✅ Runs in Docker containers

## Features Implemented

1. **Document Processing**
   - PDF support (converts to images using PyMuPDF)
   - Image support (JPG, PNG)
   - AI-powered extraction using Google Gemini
   - Dynamic model selection (handles API changes)

2. **Google Calendar Integration**
   - OAuth 2.0 authentication
   - Automatic event creation
   - Supports custom calendar IDs

3. **Authentication**
   - Password-based login
   - JWT tokens
   - Secure password hashing

4. **Email Forwarding** (optional, not used in your deployment)
   - IMAP email checking
   - Automatic attachment processing
   - Background email monitoring

## Project Structure

```
DocumentsToCalendar/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── auth.py                    # Authentication logic
│   ├── models.py                  # Database models
│   ├── services/
│   │   ├── calendar_service.py    # Google Calendar integration
│   │   ├── document_processor.py  # AI document processing
│   │   └── email_service.py       # Email processing (optional)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── main.js
│       ├── test.js
│       └── email.js
├── docker-compose.yml
├── Dockerfile
├── credentials.json               # Google Calendar OAuth (not in git)
├── token.pickle                   # OAuth token (not in git)
└── documents_calendar.db         # SQLite database
```

## GitHub Secrets Required

Add these to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `GOOGLE_API_KEY` | Gemini API key | From Google AI Studio |
| `CREDENTIALS_JSON` | Base64 encoded credentials.json | See encoding steps below |
| `ADMIN_PASSWORD` | Admin login password | Choose a secure password |
| `JWT_SECRET_KEY` | 256-bit random string | Generate with `openssl rand -hex 32` |

## Pre-Deployment Steps

### Step 1: Encode credentials.json

**On your local machine (PowerShell):**
```powershell
cd C:\Users\Admin\Desktop\Cursor\documentstocalendar\DocumentsToCalendar

# Encode to base64
$content = Get-Content ".\credentials.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

# Copy the output (it's one long string)
$base64
```

**Add to GitHub:** Copy the entire base64 string → Add as `CREDENTIALS_JSON` secret

### Step 2: Generate JWT Secret

```powershell
openssl rand -hex 32
```

**Add to GitHub:** Copy the 64-character hex string → Add as `JWT_SECRET_KEY` secret

### Step 3: Create token.pickle (One-Time)

**On your local machine:**
```powershell
cd C:\Users\Admin\Desktop\Cursor\documentstocalendar\DocumentsToCalendar
.\start_server.ps1

# In browser: http://127.0.0.1:8000
# Log in → Click "Test Calendar Connection"
# Authenticate with Google → This creates token.pickle
```

**Save token.pickle** - You'll need to copy this to your Pi later

## Raspberry Pi Deployment Steps

### Phase 1: Prepare Your Pi

**1.1 SSH into Pi**
```bash
ssh pi@your-pi-ip-address
```

**1.2 Install Docker (if not installed)**
```bash
# Check if installed
docker --version

# If not, install:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Log out and back in
exit
# SSH back in
```

### Phase 2: Deploy Application

**2.1 Clone Repository**
```bash
cd ~
git clone https://github.com/your-username/DocumentsToCalendar.git
cd DocumentsToCalendar
```

**2.2 Create .env File**
```bash
nano .env
```

**Add this content (replace with your actual values):**
```env
GOOGLE_API_KEY=your-gemini-api-key-from-github-secrets
CREDENTIALS_JSON=your-base64-encoded-credentials-from-github-secrets
ADMIN_PASSWORD=your-admin-password
JWT_SECRET_KEY=your-64-char-hex-string-from-github-secrets
GOOGLE_CALENDAR_HEADLESS=true
```

**Save:** Ctrl+X, then Y, then Enter

**2.3 Copy token.pickle to Pi**

**From your Windows machine (PowerShell):**
```powershell
cd C:\Users\Admin\Desktop\Cursor\documentstocalendar\DocumentsToCalendar
scp .\token.pickle pi@your-pi-ip:~/DocumentsToCalendar/
```

**Or manually:** Copy `token.pickle` file to `~/DocumentsToCalendar/` on Pi

**2.4 Build and Start**
```bash
cd ~/DocumentsToCalendar

# Build Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check status
docker ps
```

**2.5 Verify**
```bash
# View logs
docker-compose logs -f

# Test API (in another terminal)
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}
```

**2.6 Access from Network**
```
http://your-pi-ip-address:8000
```

### Phase 3: Auto-Start on Boot (Optional)

**3.1 Create systemd Service**
```bash
sudo nano /etc/systemd/system/documents-to-calendar.service
```

**Add this content:**
```ini
[Unit]
Description=Documents to Calendar Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/DocumentsToCalendar
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

**3.2 Enable Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable documents-to-calendar.service
sudo systemctl start documents-to-calendar.service

# Check status
sudo systemctl status documents-to-calendar.service
```

### Phase 4: Reverse Proxy (Optional - If you have a domain)

**Using Caddy:**
```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Edit Caddyfile
sudo nano /etc/caddy/Caddyfile
```

**Add:**
```
documents.yourdomain.com {
    reverse_proxy localhost:8000
}
```

**Reload:**
```bash
sudo caddy reload
```

## Quick Reference Commands

**View logs:**
```bash
docker-compose logs -f app
```

**Restart service:**
```bash
docker-compose restart
```

**Stop service:**
```bash
docker-compose down
```

**Update application:**
```bash
cd ~/DocumentsToCalendar
git pull
docker-compose build
docker-compose up -d
```

**Check if running:**
```bash
docker ps
curl http://localhost:8000/api/health
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check environment variables
docker-compose config

# Verify .env file
cat .env
```

### Calendar doesn't work
- Ensure `token.pickle` exists in project directory
- Verify `CREDENTIALS_JSON` is set correctly in .env
- Check logs: `docker-compose logs app | grep -i calendar`

### Can't access from network
```bash
# Check firewall
sudo ufw allow 8000

# Verify port
sudo netstat -tulpn | grep 8000
```

### "Credentials not found" error
- Verify `CREDENTIALS_JSON` in .env matches your GitHub secret
- Make sure it's base64 encoded (one long string, no line breaks)
- Check logs for exact error message

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | - | Gemini API key |
| `CREDENTIALS_JSON` | ✅ Yes | - | Base64 encoded credentials.json |
| `ADMIN_PASSWORD` | ✅ Yes | - | Admin login password |
| `JWT_SECRET_KEY` | ✅ Yes | - | 256-bit hex string |
| `ADMIN_USERNAME` | ❌ No | `admin` | Admin username |
| `GOOGLE_CALENDAR_HEADLESS` | ❌ No | `true` | Set to true for Pi |
| `GOOGLE_CALENDAR_ID` | ❌ No | `primary` | Calendar ID to use |

## Files to Backup

Important files on your Pi:
- `token.pickle` - Google Calendar authentication token
- `documents_calendar.db` - User database
- `.env` - Environment variables (contains secrets!)

**Backup command:**
```bash
cd ~/DocumentsToCalendar
tar -czf backup-$(date +%Y%m%d).tar.gz token.pickle documents_calendar.db .env
```

## Security Notes

1. ✅ Never commit `.env`, `credentials.json`, or `token.pickle` to git
2. ✅ Use strong passwords for `ADMIN_PASSWORD` and `JWT_SECRET_KEY`
3. ✅ Keep GitHub secrets secure
4. ✅ Use HTTPS in production (via Caddy/Let's Encrypt)
5. ✅ Regularly update Docker images and system packages

## What's Next?

After deployment:
1. Access the app at `http://your-pi-ip:8000`
2. Log in with your admin credentials
3. Upload a travel document to test
4. Check your Google Calendar for the new event!

## Summary Checklist

**Before Deployment:**
- [ ] GitHub secrets configured (GOOGLE_API_KEY, CREDENTIALS_JSON, ADMIN_PASSWORD, JWT_SECRET_KEY)
- [ ] credentials.json base64 encoded
- [ ] JWT secret generated (256 bits / 64 hex chars)
- [ ] token.pickle created locally

**On Raspberry Pi:**
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] .env file created with all secrets
- [ ] token.pickle copied to project directory
- [ ] Docker container built and started
- [ ] Service verified (health check works)
- [ ] Auto-start enabled (optional)
- [ ] Reverse proxy configured (optional)

You're ready to deploy! 🚀

