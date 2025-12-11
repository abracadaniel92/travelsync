# Documents to Calendar

A web application that extracts travel information from documents (tickets, boarding passes, etc.) and automatically adds them to your calendar.

## Features

- 🔐 Simple password-based authentication
- 📄 Document upload (PDF, images)
- 📧 Email forwarding support - automatically process travel documents from email
- 🤖 AI-powered extraction using Google Gemini
- 📅 Automatic calendar integration (Google Calendar)
- 🐳 Docker deployment ready
- 🔒 Secure API key management via GitHub Secrets

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

1. **Set up GitHub Secrets** (for production):
   - Go to your repository settings → Secrets and variables → Actions
   - Add `GOOGLE_API_KEY` with your Gemini API key
   - Add `ADMIN_PASSWORD` with your desired admin password (plain text, will be hashed automatically)
   - Add `JWT_SECRET_KEY` with a strong random string

2. **Create environment file** (for local development):
   ```bash
   # Copy and edit
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
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

### Google Calendar Integration (Optional)

1. **Enable Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Place credentials file**:
   ```bash
   cp credentials.json ./credentials.json
   ```

3. **First run authentication**:
   - On first document upload, the app will open a browser for OAuth
   - Authorize access to your Google Calendar
   - Token will be saved for future use

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
   documents.gmojsoski.com {
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
DocumentsToCalendar/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application
│   ├── auth.py       # Authentication logic
│   ├── models.py     # Database models
│   ├── services/     # Business logic
│   └── requirements.txt
├── frontend/         # Static frontend
│   ├── index.html
│   ├── login.html
│   ├── css/
│   └── js/
├── docker-compose.yml
├── Dockerfile
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

