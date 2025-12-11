# Start Documents to Calendar Server
$env:ADMIN_PASSWORD = "test123"
$env:JWT_SECRET_KEY = "test-secret"

# Check if GOOGLE_API_KEY is set
if (-not $env:GOOGLE_API_KEY) {
    Write-Host "WARNING: GOOGLE_API_KEY not set!" -ForegroundColor Yellow
    Write-Host "Set it with: `$env:GOOGLE_API_KEY='your-api-key-here'" -ForegroundColor Gray
    Write-Host "Example: `$env:GOOGLE_API_KEY='AIzaSy...'" -ForegroundColor Cyan
    Write-Host ""
}

# Optional: Email forwarding configuration
if (-not $env:EMAIL_ADDRESS) {
    Write-Host "INFO: Email forwarding not configured (optional)" -ForegroundColor Gray
    Write-Host "To enable: `$env:EMAIL_ADDRESS='your-email@gmail.com'" -ForegroundColor Gray
    Write-Host "          `$env:EMAIL_PASSWORD='your-app-password'" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Starting server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Login: admin / test123" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

