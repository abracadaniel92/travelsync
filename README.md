# TravelSync

A beautiful web application that extracts travel information from documents (tickets, boarding passes, hotel reservations, etc.) and automatically adds them to your Google Calendar. Supports multiple languages and automatically detects timezones.

**TravelSync** - Sync your travel documents to your calendar effortlessly.

## Features

- 🔐 Simple password-based authentication
- 📄 Document upload (PDF, images) with drag & drop
- 🌍 Multi-language support - automatically translates non-English documents
- 🕐 Smart timezone detection - preserves correct times regardless of your location
- 📧 Email forwarding support - automatically process travel documents from email
- 🤖 AI-powered extraction using Google Gemini (extracts ticket numbers, passenger info, prices, notes, etc.)
- 📅 Automatic calendar integration (Google Calendar)
- 🎨 Beautiful travel-themed UI with glassmorphism design
- 🐳 Docker deployment ready
- 🔒 Secure API key management via environment variables

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini API
- **Database**: SQLite (for user auth)
- **Deployment**: Docker + Caddy reverse proxy

## Setup

### Prerequisites

- Python 3.9+ (or Docker)
- Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- Google Calendar API credentials (optional, for calendar integration)

### Quick Start with Docker

1. **Create environment file**:
   ```bash
   # Copy the template
   cp env.template .env
   ```
   
   Edit `.env` with your values:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
   CREDENTIALS_JSON=your-base64-encoded-google-calendar-credentials
   ```

2. **Run with Docker Compose**:
   ```bash
   docker compose up -d
   ```

3. **Access the application**:
   - Open `http://localhost:8000`
   - Login with the admin credentials you set

### Running Locally (Without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_key
export ADMIN_PASSWORD=your_password
export JWT_SECRET_KEY=your_secret

# Run the server
uvicorn main:app --reload
```

The backend serves the frontend automatically at the root URL.

### Google Calendar Integration

1. **Enable Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download `credentials.json`

2. **Add credentials to environment**:
   ```bash
   # Option 1: Base64 encode and add to .env
   base64 -i credentials.json | tr -d '\n' > credentials_base64.txt
   # Then add to .env: CREDENTIALS_JSON=<content>
   
   # Option 2: Place in data/ directory (for Docker)
   mkdir -p data
   cp credentials.json data/
   ```

3. **Authenticate via web interface**:
   - After starting the app, go to the "Google Calendar" section
   - Click "Test Calendar Connection"
   - If authentication is needed, click "Start Authentication"
   - Follow the OAuth flow in your browser
   - Paste the authorization code to complete authentication

### Email Forwarding (Optional)

Automatically process travel documents sent via email:

1. **Set up email credentials**:
   ```bash
   export EMAIL_ADDRESS=your-email@gmail.com
   export EMAIL_PASSWORD=your-app-password  # Gmail App Password
   export EMAIL_IMAP_SERVER=imap.gmail.com  # Optional, defaults to Gmail
   export EMAIL_IMAP_PORT=993                # Optional, defaults to 993
   ```

2. **For Gmail, create an App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password (not your regular password)

3. **Check emails manually via API**:
   ```bash
   curl -X POST http://localhost:8000/api/email/check \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

4. **Email processing**:
   - The service checks for emails with image/PDF attachments
   - Processes each attachment with Gemini AI
   - Automatically creates calendar events
   - Moves processed emails to "Processed" folder
   - Moves failed emails to "Failed" folder

### Deployment to Raspberry Pi

1. **Build and push Docker image** (or build on Pi):
   ```bash
   docker build -t documents-to-calendar .
   ```

2. **Set up Caddy reverse proxy**:
   Add to your Caddyfile:
   ```
   your-domain.com {
       reverse_proxy localhost:8000
   }
   ```

3. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```

4. **Use GitHub Secrets in CI/CD**:
   - Set up GitHub Actions to pull secrets
   - Or use environment variables from your deployment system

## Project Structure

```
TravelSync/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── auth.py          # Authentication logic
│   ├── models.py        # Database models
│   ├── services/        # Business logic
│   │   ├── calendar_service.py    # Google Calendar integration
│   │   ├── document_processor.py  # Gemini AI document processing
│   │   └── email_service.py        # Email forwarding
│   └── requirements.txt
├── frontend/            # Web frontend (HTML/CSS/JS)
│   ├── index.html      # Main app page
│   ├── landing.html    # Landing page
│   ├── login.html      # Login page
│   ├── css/
│   │   └── style.css   # Styling
│   ├── js/
│   │   ├── auth.js     # Authentication
│   │   ├── main.js     # Document upload
│   │   ├── test.js     # API testing
│   │   └── email.js    # Email features
│   └── images/         # Frontend assets
├── mobile/              # React Native iOS app
│   ├── src/
│   │   ├── screens/    # Screen components
│   │   ├── components/ # Reusable components
│   │   ├── context/    # React context
│   │   ├── services/   # API services
│   │   └── assets/     # Mobile assets
│   ├── App.js
│   └── package.json
├── docs/                # Documentation
│   ├── SETUP.md
│   ├── QUICK_START.md
│   ├── TROUBLESHOOTING.md
│   └── ... (all .md files)
├── scripts/             # Utility scripts
│   ├── start_server.ps1
│   ├── quick_setup.sh
│   ├── deploy_pi.sh
│   └── ... (all scripts)
├── docker-compose.yml   # Docker configuration
├── Dockerfile
├── env.template        # Environment variables template
└── README.md
```

## Security

- API keys stored as GitHub Actions secrets
- Password hashing with bcrypt
- JWT token authentication
- Rate limiting on API endpoints
- File upload validation

## License

MIT

