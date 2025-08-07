# PowerShell script to stop Docker services for n8n_automate

Write-Host "🛑 Stopping n8n_automate Docker services..." -ForegroundColor Yellow

# Stop and remove containers
docker compose down

Write-Host "✅ Services stopped successfully!" -ForegroundColor Green
Write-Host "💡 To start services again, run: .\start_docker_services.ps1" -ForegroundColor Cyan 