# SSD Setup Summary

Your DocumentsToCalendar project is now configured on your SSD at:
```
/mnt/ssd/docker-projects/documents-to-calendar
```

## ✅ What's Been Configured

1. **docker-compose.yml** - Updated and fixed:
   - Removed obsolete `version` field (Docker Compose v5 compatible)
   - Uses `data/` directory for credentials and tokens (organized approach)
   - All paths configured correctly for SSD location

2. **.env file** - Already exists with all your configuration ✅

3. **Directory Structure**:
   ```
   /mnt/ssd/docker-projects/documents-to-calendar/
   ├── .env                    # Your environment variables (already configured)
   ├── docker-compose.yml      # Fixed and ready
   ├── Dockerfile              # Docker build file
   ├── data/                   # Credentials and tokens
   │   ├── credentials.json    # Google Calendar OAuth credentials
   │   └── token.pickle        # (needs to be created after auth)
   ├── uploads/               # Document uploads
   ├── temp/                   # Temporary files
   ├── documents_calendar.db   # SQLite database (created automatically)
   ├── backend/                # Backend code
   ├── frontend/               # Frontend code
   └── quick_setup.sh          # Setup script
   ```

## 📋 Next Steps

### 1. Get Google Calendar Token (token.pickle)

You need to authenticate with Google Calendar once. The token will be saved in `data/token.pickle`.

**Option A: Authenticate on your local machine (Recommended)**
```bash
# On your local machine, run the app and authenticate
# Then copy token.pickle to Pi:
scp token.pickle goce@raspberrypi:/mnt/ssd/docker-projects/documents-to-calendar/data/
```

**Option B: Authenticate directly on Pi**
- Your `.env` currently has `GOOGLE_CALENDAR_HEADLESS=false` which is correct for authentication
- After authentication, you can set it to `true` for headless operation

### 2. Build and Start

```bash
cd /mnt/ssd/docker-projects/documents-to-calendar

# Option 1: Use the setup script
./quick_setup.sh

# Option 2: Manual commands
docker compose build
docker compose up -d
```

### 3. Verify It's Working

```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f

# Test health endpoint
curl http://localhost:8000/api/health
```

### 4. Configure Caddy (Optional)

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

## 🔧 Current Configuration

- **Location**: `/mnt/ssd/docker-projects/documents-to-calendar`
- **Port**: `8000`
- **Container Name**: `documents-to-calendar`
- **Data Directory**: `./data/` (for credentials and tokens)
- **Database**: `./documents_calendar.db` (SQLite, created automatically)

## 📝 Environment Variables

Your `.env` file is already configured with:
- ✅ `GOOGLE_API_KEY` - Set
- ✅ `CREDENTIALS_JSON` - Set (base64 encoded)
- ✅ `ADMIN_PASSWORD` - Set
- ✅ `JWT_SECRET_KEY` - Set
- ⚠️ `GOOGLE_CALENDAR_HEADLESS=false` - Set to `true` after authentication

## 🚀 Quick Commands

```bash
# Navigate to project
cd /mnt/ssd/docker-projects/documents-to-calendar

# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart
docker compose restart

# Rebuild after code changes
docker compose build --no-cache
docker compose up -d
```

## ⚠️ Important Notes

1. **Token Authentication**: You need `data/token.pickle` for Google Calendar to work. Authenticate once and it will be saved.

2. **Headless Mode**: After authentication, you can set `GOOGLE_CALENDAR_HEADLESS=true` in `.env` for headless operation.

3. **Data Persistence**: All data (database, uploads, tokens) is stored on your SSD and will persist across container restarts.

4. **Backup**: Important files to backup:
   - `data/token.pickle` - Google Calendar authentication
   - `documents_calendar.db` - User database
   - `.env` - Environment variables (contains secrets!)

## 🐛 Troubleshooting

### Container won't start
```bash
docker compose logs
```

### Missing token.pickle
- Authenticate with Google Calendar (see step 1 above)
- Token will be saved to `data/token.pickle`

### Can't access from network
```bash
# Check if port is open
sudo netstat -tulpn | grep 8000

# Allow port in firewall (if using ufw)
sudo ufw allow 8000
```

Everything is ready on your SSD! 🎉

