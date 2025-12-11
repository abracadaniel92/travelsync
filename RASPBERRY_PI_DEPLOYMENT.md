# Raspberry Pi Deployment Guide

This guide will help you deploy Documents to Calendar on your Raspberry Pi using Docker and GitHub Secrets.

## Prerequisites

- Raspberry Pi with Docker and Docker Compose installed
- GitHub repository with secrets configured
- SSH access to your Pi

## Step 1: Set Up GitHub Secrets

### 1.1 Add credentials.json as a Secret

Since `credentials.json` is a JSON file, you need to base64 encode it:

**On your local machine:**
```powershell
# PowerShell - Base64 encode the credentials file
$content = Get-Content "C:\Users\Admin\Desktop\Cursor\documentstocalendar\DocumentsToCalendar\credentials.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Set-Content "credentials_base64.txt"
# Copy the content from credentials_base64.txt
```

**Or on Linux/Mac:**
```bash
base64 -i credentials.json | tr -d '\n' > credentials_base64.txt
```

### 1.2 Add All Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add:

| Secret Name | Value | Notes |
|------------|-------|-------|
| `GOOGLE_API_KEY` | Your Gemini API key | From Google AI Studio |
| `GOOGLE_CALENDAR_CREDENTIALS_JSON` | Base64 encoded credentials.json | From step 1.1 |
| `ADMIN_PASSWORD` | Your admin password | Plain text |
| `JWT_SECRET_KEY` | Random string | Generate with `openssl rand -hex 32` |
| `EMAIL_ADDRESS` | Your email (optional) | For email forwarding |
| `EMAIL_PASSWORD` | App password (optional) | Gmail App Password |
| `EMAIL_AUTO_CHECK` | `true` or `false` | Enable auto email checking |

## Step 2: Deploy to Raspberry Pi

### 2.1 SSH into Your Pi

```bash
ssh pi@your-pi-ip-address
```

### 2.2 Clone Repository

```bash
cd ~
git clone https://github.com/your-username/DocumentsToCalendar.git
cd DocumentsToCalendar
```

### 2.3 Create Environment File from Secrets

Create a script to fetch secrets and create `.env` file:

```bash
# Create .env file
cat > .env << 'EOF'
# These will be set from GitHub Secrets or manually
GOOGLE_API_KEY=${GOOGLE_API_KEY}
GOOGLE_CALENDAR_CREDENTIALS_JSON=${GOOGLE_CALENDAR_CREDENTIALS_JSON}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
EMAIL_ADDRESS=${EMAIL_ADDRESS}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
EMAIL_AUTO_CHECK=${EMAIL_AUTO_CHECK:-false}
EMAIL_CHECK_INTERVAL=${EMAIL_CHECK_INTERVAL:-300}
GOOGLE_CALENDAR_HEADLESS=true
EOF
```

### 2.4 Set Environment Variables

**Option A: Manual (Quick Setup)**
```bash
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CALENDAR_CREDENTIALS_JSON="base64-encoded-json"
export ADMIN_PASSWORD="your-password"
export JWT_SECRET_KEY="your-jwt-secret"
# Optional
export EMAIL_ADDRESS="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_AUTO_CHECK="true"
```

**Option B: Use GitHub Secrets (Recommended)**

Create a script to pull secrets from GitHub Actions or use a secrets manager.

### 2.5 Authenticate Google Calendar (One-Time)

Since the Pi is headless, you need to authenticate once on your local machine:

1. **On your local machine:**
   ```bash
   # Run the app locally
   python -m uvicorn backend.main:app --reload
   # Test calendar connection - this will create token.pickle
   ```

2. **Copy token.pickle to Pi:**
   ```bash
   scp token.pickle pi@your-pi-ip:~/DocumentsToCalendar/
   ```

3. **Or manually authenticate on Pi** (if it has a display):
   - Set `GOOGLE_CALENDAR_HEADLESS=false` temporarily
   - Run the app and authenticate
   - Set it back to `true`

### 2.6 Build and Run with Docker

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2.7 Verify Deployment

```bash
# Check if container is running
docker ps

# Check logs
docker-compose logs app

# Test the API
curl http://localhost:8000/api/health
```

## Step 3: Set Up Reverse Proxy (Optional)

### 3.1 Using Caddy

Add to your Caddyfile:
```
documents.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Reload Caddy:
```bash
sudo caddy reload
```

### 3.2 Using Nginx

Create `/etc/nginx/sites-available/documents`:
```nginx
server {
    listen 80;
    server_name documents.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/documents /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 4: Auto-Start on Boot

### 4.1 Using systemd

Create `/etc/systemd/system/documents-to-calendar.service`:
```ini
[Unit]
Description=Documents to Calendar Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/DocumentsToCalendar
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable documents-to-calendar.service
sudo systemctl start documents-to-calendar.service
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check environment variables
docker-compose config
```

### Calendar authentication fails
- Make sure `token.pickle` exists in the project directory
- Verify `GOOGLE_CALENDAR_CREDENTIALS_JSON` is set correctly
- Check that credentials are base64 encoded properly

### Can't access from network
- Check firewall: `sudo ufw allow 8000`
- Verify Docker port mapping: `docker ps`
- Check if service is listening: `netstat -tulpn | grep 8000`

### Email forwarding not working
- Verify `EMAIL_ADDRESS` and `EMAIL_PASSWORD` are set
- Check `EMAIL_AUTO_CHECK=true` is set
- View logs: `docker-compose logs -f app`

## Updating the Application

```bash
cd ~/DocumentsToCalendar
git pull
docker-compose build
docker-compose up -d
```

## Security Best Practices

1. **Use strong passwords**: Generate secure `ADMIN_PASSWORD` and `JWT_SECRET_KEY`
2. **Keep secrets secure**: Never commit secrets to git
3. **Use HTTPS**: Set up SSL/TLS with Caddy or Let's Encrypt
4. **Firewall**: Only expose necessary ports
5. **Regular updates**: Keep Docker and system updated

## Monitoring

### View logs
```bash
docker-compose logs -f app
```

### Check resource usage
```bash
docker stats documents-to-calendar
```

### Restart service
```bash
docker-compose restart
```

## Backup

Important files to backup:
- `token.pickle` - Google Calendar authentication token
- `documents_calendar.db` - User database
- Environment variables/secrets

```bash
# Backup script
tar -czf backup-$(date +%Y%m%d).tar.gz \
  token.pickle \
  documents_calendar.db \
  .env
```


