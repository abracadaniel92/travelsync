#!/bin/bash
# Documents to Calendar - Raspberry Pi Deployment Script
# Run this on your Pi after SSH'ing in

set -e  # Exit on error

echo "=========================================="
echo "Documents to Calendar - Pi Deployment"
echo "=========================================="
echo ""

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo "⚠️  Warning: Not running as 'pi' user. Some commands may need sudo."
fi

# Step 1: Install Docker
echo "📦 Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "   Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker pi
    echo "   ✅ Docker installed. You may need to log out and back in."
    echo "   Run: exit (then SSH back in)"
    exit 0
else
    echo "   ✅ Docker already installed"
fi

# Step 2: Install Docker Compose
echo ""
echo "📦 Step 2: Checking Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    echo "   Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo "   ✅ Docker Compose installed"
else
    echo "   ✅ Docker Compose already installed"
fi

# Step 3: Clone/Update Repository
echo ""
echo "📥 Step 3: Setting up repository..."
if [ -d "$HOME/DocumentsToCalendar" ]; then
    echo "   Repository exists, pulling latest changes..."
    cd ~/DocumentsToCalendar
    git pull origin main
else
    echo "   Cloning repository..."
    cd ~
    git clone https://github.com/abracadaniel92/DocumentsToCalendar.git
    cd DocumentsToCalendar
fi
echo "   ✅ Repository ready"

# Step 4: Create .env file
echo ""
echo "⚙️  Step 4: Setting up environment variables..."
if [ -f ".env" ]; then
    echo "   .env file already exists"
    read -p "   Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Keeping existing .env file"
    else
        CREATE_ENV=true
    fi
else
    CREATE_ENV=true
fi

if [ "$CREATE_ENV" = true ]; then
    echo "   Creating .env file template..."
    cat > .env << 'ENVEOF'
# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here

# Google Calendar Credentials (base64 encoded)
CREDENTIALS_JSON=your-base64-encoded-credentials-here

# Admin Authentication
ADMIN_PASSWORD=your-admin-password-here
JWT_SECRET_KEY=your-64-char-hex-jwt-secret-here

# Google Calendar Settings
GOOGLE_CALENDAR_HEADLESS=true
ENVEOF
    echo "   ✅ .env file created"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env file with your actual values:"
    echo "   nano .env"
    echo ""
    read -p "   Press Enter after you've edited .env file..."
fi

# Step 5: Check for token.pickle
echo ""
echo "🔑 Step 5: Checking for token.pickle..."
if [ ! -f "token.pickle" ]; then
    echo "   ⚠️  token.pickle not found!"
    echo "   You need to copy token.pickle from your local machine:"
    echo "   From Windows: scp token.pickle pi@192.168.1.137:~/DocumentsToCalendar/"
    echo ""
    read -p "   Press Enter after you've copied token.pickle..."
else
    echo "   ✅ token.pickle found"
fi

# Step 6: Build Docker image
echo ""
echo "🔨 Step 6: Building Docker image..."
docker-compose build
echo "   ✅ Build complete"

# Step 7: Start services
echo ""
echo "🚀 Step 7: Starting services..."
docker-compose up -d
echo "   ✅ Services started"

# Step 8: Verify
echo ""
echo "✅ Step 8: Verifying deployment..."
sleep 3

if docker ps | grep -q documents-to-calendar; then
    echo "   ✅ Container is running"
    
    # Test health endpoint
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "   ✅ API is responding"
        echo ""
        echo "=========================================="
        echo "🎉 Deployment Successful!"
        echo "=========================================="
        echo ""
        echo "Access your application at:"
        echo "  http://192.168.1.137:8000"
        echo ""
        echo "View logs:"
        echo "  docker-compose logs -f"
        echo ""
        echo "Restart service:"
        echo "  docker-compose restart"
        echo ""
    else
        echo "   ⚠️  API not responding yet. Check logs:"
        echo "   docker-compose logs"
    fi
else
    echo "   ⚠️  Container not running. Check logs:"
    echo "   docker-compose logs"
fi

