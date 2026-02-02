# Script to copy assets to mobile app
Write-Host "Setting up TravelSync mobile app assets..." -ForegroundColor Green

$sourceDir = "..\frontend\images"
$destDir = "src\assets"

# Create assets directory if it doesn't exist
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

# Copy logo
if (Test-Path "$sourceDir\logo2.png") {
    Copy-Item "$sourceDir\logo2.png" -Destination "$destDir\logo2.png" -Force
    Write-Host "✓ Copied logo2.png" -ForegroundColor Green
} else {
    Write-Host "⚠ logo2.png not found in $sourceDir" -ForegroundColor Yellow
}

# Copy background image (convert AVIF to JPG if needed, or copy as-is)
if (Test-Path "$sourceDir\photo-1559627712-fa1c99c217a8.avif") {
    # Note: You may need to convert AVIF to JPG manually or use a converter
    # For now, we'll note that the user needs to convert it
    Write-Host "⚠ Background image is AVIF format. Please convert to JPG and save as $destDir\background.jpg" -ForegroundColor Yellow
    Write-Host "  You can use an online converter or ImageMagick: magick convert photo-1559627712-fa1c99c217a8.avif background.jpg" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Background image not found" -ForegroundColor Yellow
}

Write-Host "`nAsset setup complete!" -ForegroundColor Green
Write-Host "Don't forget to:" -ForegroundColor Yellow
Write-Host "  1. Convert background.avif to background.jpg" -ForegroundColor Yellow
Write-Host "  2. Update API_BASE in src/services/api.js with your backend URL" -ForegroundColor Yellow
