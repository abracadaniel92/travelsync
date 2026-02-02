#!/bin/bash
# Quick setup script for DocumentsToCalendar on Raspberry Pi (SSD location)

set -e

echo "=========================================="
echo "DocumentsToCalendar - Quick Setup"
echo "Location: /mnt/ssd/docker-projects/documents-to-calendar"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ .env file created from env.template"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file with your actual values:"
        echo "   nano .env"
        echo ""
        echo "Required values:"
        echo "  - GOOGLE_API_KEY"
        echo "  - CREDENTIALS_JSON (base64 encoded)"
        echo "  - ADMIN_PASSWORD"
        echo "  - JWT_SECRET_KEY (generate with: openssl rand -hex 32)"
        echo ""
        read -p "Press Enter after you've edited .env file..."
    else
        echo "❌ env.template not found!"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Check for token.pickle in data directory - create empty file if it doesn't exist
if [ ! -f "data/token.pickle" ]; then
    echo ""
    echo "⚠️  token.pickle not found in data/ directory!"
    echo "Creating empty file (will be populated after authentication)..."
    mkdir -p data
    touch data/token.pickle
    echo "✅ Empty token.pickle created in data/ directory"
    echo ""
    echo "You need to authenticate with Google Calendar:"
    echo "  1. Copy token.pickle from your local machine:"
    echo "     scp token.pickle goce@your-pi-ip:\"$(pwd)/data/\""
    echo ""
    echo "  2. Or authenticate on this machine (requires display):"
    echo "     - Set GOOGLE_CALENDAR_HEADLESS=false in .env"
    echo "     - Run: docker compose up"
    echo "     - Authenticate in browser"
    echo "     - Set GOOGLE_CALENDAR_HEADLESS=true again"
    echo ""
    read -p "Press Enter to continue (you can add token.pickle later)..."
else
    echo "✅ token.pickle found in data/ directory"
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads temp data
echo "✅ Directories created"

# Build Docker image
echo ""
echo "🔨 Building Docker image..."
docker compose build

# Start container
echo ""
echo "🚀 Starting container..."
docker compose up -d

# Wait a moment
sleep 3

# Check status
echo ""
echo "📊 Checking status..."
if docker ps | grep -q documents-to-calendar; then
    echo "✅ Container is running!"
    echo ""
    echo "Test the API:"
    echo "  curl http://localhost:8000/api/health"
    echo ""
    echo "Access the web interface:"
    echo "  http://localhost:8000"
    echo "  or"
    echo "  http://$(hostname -I | awk '{print $1}'):8000"
    echo ""
    echo "View logs:"
    echo "  docker compose logs -f"
else
    echo "❌ Container is not running. Check logs:"
    echo "  docker compose logs"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
