# Robust Deployment Script for Campo
# Handles retries for network timeouts on Fly.io API

$APP_NAME = "campo"
$MAX_RETRIES = 3
$RETRY_COUNT = 0
$SUCCESS = $false

Write-Host "🚀 Starting targeted deployment for $APP_NAME..." -ForegroundColor Cyan

while (-not $SUCCESS -and $RETRY_COUNT -lt $MAX_RETRIES) {
    $RETRY_COUNT++
    Write-Host "Attempt $RETRY_COUNT of $MAX_RETRIES..." -ForegroundColor Yellow
    
    # Run fly deploy with targeted flags to minimize API chatter
    fly deploy --app $APP_NAME --remote-only --ha=false --strategy immediate --detach
    
    if ($LASTEXITCODE -eq 0) {
        $SUCCESS = $true
        Write-Host "✅ Deployment initiated successfully!" -ForegroundColor Green
    } else {
        if ($RETRY_COUNT -lt $MAX_RETRIES) {
            Write-Host "⚠️ Deployment failed. Retrying in 10 seconds..." -ForegroundColor Magenta
            Start-Sleep -Seconds 10
        } else {
            Write-Host "❌ Deployment failed after $MAX_RETRIES attempts. Please check your network connection." -ForegroundColor Red
        }
    }
}

if ($SUCCESS) {
    Write-Host "`nTo check the status of your rollout, run:" -ForegroundColor Cyan
    Write-Host "fly status --app $APP_NAME"
    Write-Host "`nTo monitor logs (and see the database repair script run), run:" -ForegroundColor Cyan
    Write-Host "fly logs --app $APP_NAME"
}
