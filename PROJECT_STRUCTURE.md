# TravelSync Project Structure

## Overview

This project is organized into clear directories for better maintainability.

## Directory Structure

```
TravelSync/
├── backend/              # FastAPI backend application
│   ├── main.py          # Main FastAPI application
│   ├── auth.py          # Authentication logic
│   ├── models.py        # Database models
│   ├── services/        # Business logic services
│   │   ├── calendar_service.py    # Google Calendar integration
│   │   ├── document_processor.py  # Gemini AI document processing
│   │   └── email_service.py       # Email forwarding
│   └── requirements.txt # Python dependencies
│
├── frontend/            # Web frontend (HTML/CSS/JavaScript)
│   ├── index.html       # Main application page
│   ├── landing.html    # Landing page
│   ├── login.html       # Login page
│   ├── css/
│   │   └── style.css    # All styling
│   ├── js/
│   │   ├── auth.js      # Authentication logic
│   │   ├── main.js      # Document upload & processing
│   │   ├── email.js     # Email features
│   │   └── test.js      # API testing
│   └── images/          # Frontend assets (logos, backgrounds)
│
├── mobile/              # React Native iOS application
│   ├── src/
│   │   ├── screens/     # Screen components
│   │   │   ├── LandingScreen.js
│   │   │   ├── LoginScreen.js
│   │   │   └── MainScreen.js
│   │   ├── components/  # Reusable components
│   │   │   └── CollapsibleSection.js
│   │   ├── context/     # React context providers
│   │   │   └── AuthContext.js
│   │   ├── services/    # API service layer
│   │   │   └── api.js
│   │   └── assets/      # Mobile app assets
│   ├── App.js           # Main app entry point
│   ├── package.json     # Node.js dependencies
│   └── app.json         # Expo configuration
│
├── docs/                # All documentation
│   ├── README.md        # Documentation index
│   ├── SETUP.md         # Setup instructions
│   ├── QUICK_START.md   # Quick start guide
│   ├── TROUBLESHOOTING.md
│   └── ... (all .md files)
│
├── scripts/             # Utility scripts
│   ├── README.md        # Scripts documentation
│   ├── start_server.ps1 # Start development server (Windows)
│   ├── quick_setup.sh   # Quick setup script
│   ├── deploy_pi.sh     # Deploy to Raspberry Pi
│   ├── create_user.py   # Create new user
│   ├── set_admin_password.py
│   ├── test_upload.py   # Test document upload
│   └── ... (all utility scripts)
│
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── env.template        # Environment variables template
└── README.md           # Main project README
```

## Key Directories

### `backend/`
FastAPI Python backend. Contains all server-side logic, API endpoints, and business logic.

### `frontend/`
Web frontend using vanilla HTML, CSS, and JavaScript. Served by the FastAPI backend.

### `mobile/`
React Native iOS app. Uses Expo for development and building.

### `docs/`
All project documentation, guides, and troubleshooting information.

### `scripts/`
Utility scripts for setup, deployment, and maintenance. Scripts are designed to be run from the project root.

## Running Scripts

All scripts in the `scripts/` directory should be run from the **project root**, not from within the scripts directory:

```bash
# Windows
.\scripts\start_server.ps1

# Linux/Mac
./scripts/quick_setup.sh
python scripts/create_user.py
```

## Notes

- The `images/` folder in the root was removed (duplicate of `frontend/images/`)
- All documentation is now in `docs/`
- All utility scripts are in `scripts/`
- Scripts automatically adjust paths to work from project root
