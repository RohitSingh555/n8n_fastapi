# PowerShell script to start Docker services for n8n_automate
# Run this script once Docker Desktop is fully initialized

Write-Host "🚀 Starting n8n_automate Docker services..." -ForegroundColor Green

# Check if Docker is ready
Write-Host "📋 Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is ready!" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not ready yet. Please wait for Docker Desktop to fully initialize." -ForegroundColor Red
        Write-Host "💡 You can check Docker Desktop status in your system tray." -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not ready yet. Please wait for Docker Desktop to fully initialize." -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker compose down

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker compose up -d

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service status:" -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "🎉 Services started successfully!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Sample submission IDs for testing:" -ForegroundColor Yellow
Write-Host "   1. 126e4fc3-7920-46aa-b50d-8b89599674f0" -ForegroundColor White
Write-Host "   2. 1aa8641c-50b1-40ee-a0af-d542f00b0b5c" -ForegroundColor White
Write-Host "   3. daed7cbe-9d3a-4054-98fc-a13c512c2d31" -ForegroundColor White 