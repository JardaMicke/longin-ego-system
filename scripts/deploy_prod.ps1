$ErrorActionPreference = "Stop"

try {
    docker compose -f docker-compose.release.yml up -d --build
} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}

try {
    powershell -ExecutionPolicy Bypass -File .\scripts\check_prod.ps1
} catch {
    Write-Error "Availability check failed: $($_.Exception.Message)"
    exit 1
}
