#!/bin/bash
# Quick script to check build status

echo "=========================================="
echo "Build Status Check"
echo "=========================================="
echo ""

# Check if build is running
if pgrep -f "docker.*build" > /dev/null 2>&1; then
    echo "✅ Build is RUNNING"
    echo ""
    echo "Recent build output:"
    echo "-----------------------------------"
    tail -20 /tmp/build.log 2>/dev/null || echo "Waiting for output..."
else
    echo "❌ Build is NOT running"
    echo ""
    echo "Last build output:"
    echo "-----------------------------------"
    tail -30 /tmp/build.log 2>/dev/null || echo "No build log found"
    echo ""
    echo "To start build:"
    echo "  cd /mnt/ssd/docker-projects/documents-to-calendar"
    echo "  docker compose build"
fi

echo ""
echo "=========================================="

