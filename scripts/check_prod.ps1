$ErrorActionPreference = "Stop"

$apiBase = $env:LONGIN_API_BASE
if (-not $apiBase) {
    $apiBase = "http://localhost:8000"
}

$uiBase = $env:LONGIN_UI_BASE
if (-not $uiBase) {
    $uiBase = "http://localhost:3000"
}

$maxAttempts = 10

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "$apiBase/v1/health" -Method Get -TimeoutSec 10
        if ($health.status -ne "ok") {
            throw "Health status not ok"
        }
        break
    } catch {
        if ($attempt -eq $maxAttempts) {
            Write-Error "Health check failed: $($_.Exception.Message)"
            exit 1
        }
        Start-Sleep -Seconds 3
    }
}

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        $ready = Invoke-RestMethod -Uri "$apiBase/v1/ready" -Method Get -TimeoutSec 10
        if ($ready.status -notin @("ok", "degraded")) {
            throw "Readiness status invalid"
        }
        break
    } catch {
        if ($attempt -eq $maxAttempts) {
            Write-Error "Readiness check failed: $($_.Exception.Message)"
            exit 1
        }
        Start-Sleep -Seconds 3
    }
}

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        $ui = Invoke-WebRequest -Uri $uiBase -Method Get -TimeoutSec 10
        if ($ui.StatusCode -ne 200) {
            throw "UI status code $($ui.StatusCode)"
        }
        break
    } catch {
        if ($attempt -eq $maxAttempts) {
            Write-Error "UI check failed: $($_.Exception.Message)"
            exit 1
        }
        Start-Sleep -Seconds 3
    }
}
