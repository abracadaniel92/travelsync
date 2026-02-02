#!/bin/bash
# Monitor Docker build progress

echo "=========================================="
echo "Docker Build Monitor"
echo "=========================================="
echo ""

# Check if build is running
if pgrep -f "docker.*build" > /dev/null; then
    echo "✅ Build is currently running..."
    echo ""
    echo "Current status:"
    docker compose ps
    echo ""
    echo "Recent build output (last 20 lines):"
    echo "-----------------------------------"
    tail -20 /tmp/build.log 2>/dev/null || echo "Waiting for build log..."
    echo ""
    echo "To see live progress, run:"
    echo "  tail -f /tmp/build.log"
    echo ""
    echo "Or check Docker build directly:"
    echo "  docker compose build"
else
    echo "❌ No build process found"
    echo ""
    echo "Checking if image exists:"
    docker images | grep documents-to-calendar || echo "No image found"
    echo ""
    echo "Checking container status:"
    docker compose ps
    echo ""
    echo "To start a build, run:"
    echo "  docker compose build"
fi

