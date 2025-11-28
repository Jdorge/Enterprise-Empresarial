# Nexus Enterprise v2 - Automated Setup

Write-Host "Nexus Enterprise v2 - Automated Setup" -ForegroundColor Cyan
Write-Host "========================================"

# 1. Check dependencies
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow

# Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] Docker installed" -ForegroundColor Green
}
else {
    Write-Host "  [ERROR] Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
}
else {
    Write-Host "  [ERROR] Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Poetry
if (Get-Command poetry -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] Poetry installed" -ForegroundColor Green
    $usePoetry = $true
}
else {
    Write-Host "  [WARN] Poetry not found (using pip)" -ForegroundColor Yellow
    $usePoetry = $false
}

# 2. Configure .env
Write-Host "`nConfiguring environment variables..." -ForegroundColor Yellow

if (-Not (Test-Path ".env.local")) {
    Write-Host "  Creating .env.local from .env.example..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env.local"
    
    Write-Host "`nATTENTION!" -ForegroundColor Red
    Write-Host "  Please fill in .env.local variables before continuing:" -ForegroundColor Yellow
    Write-Host "    - OPENROUTER_API_KEY (required)" -ForegroundColor White
    Write-Host "    - POSTGRES_PASSWORD (required)" -ForegroundColor White
    
    notepad ".env.local"
    $null = Read-Host "`nPress Enter after filling .env.local (or Ctrl+C to cancel)"
}

# Validate .env.local
Write-Host "  Validating variables..." -ForegroundColor Cyan

$envContent = Get-Content ".env.local"
$required = @("OPENROUTER_API_KEY", "POSTGRES_PASSWORD", "N8N_PASSWORD", "GRAFANA_PASSWORD", "JWT_SECRET", "ENCRYPTION_KEY")
$missing = @()

foreach ($var in $required) {
    $found = $envContent | Select-String -Pattern "^$var=.+"
    if (-Not $found) {
        $missing += $var
    }
}

if ($missing.Count -gt 0) {
    Write-Host "  [ERROR] Missing variables:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "  [OK] All variables configured" -ForegroundColor Green

# 3. Install Python dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow

if ($usePoetry) {
    poetry install
}
else {
    pip install -e packages/nexus_core
    pip install -e packages/nexus_llm_factory
    pip install temporalio httpx tenacity qdrant-client pydantic pydantic-settings
}

Write-Host "  [OK] Dependencies installed" -ForegroundColor Green

# 4. Start Docker infrastructure
Write-Host "`nStarting Docker containers..." -ForegroundColor Yellow

Set-Location infrastructure
docker-compose up -d
Set-Location..

# 5. Wait for services
Write-Host "`nWaiting for services to be ready..." -ForegroundColor Yellow

Start-Sleep -Seconds 15

# Check Temporal
$temporalReady = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:7234" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $temporalReady = $true
            break
        }
    }
    catch {}
    Write-Host "  Waiting for Temporal... ($i/10)" -ForegroundColor Cyan
    Start-Sleep -Seconds 3
}

if ($temporalReady) {
    Write-Host "  [OK] Temporal ready" -ForegroundColor Green
}
else {
    Write-Host "  [WARN] Temporal still initializing" -ForegroundColor Yellow
}

# 6. Run tests
if ($usePoetry -and (Test-Path "tests")) {
    Write-Host "`nRunning tests..." -ForegroundColor Yellow
    poetry run pytest tests/unit -v
}

# 7. Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`nAvailable Services:" -ForegroundColor Yellow
Write-Host "  Temporal UI:   http://localhost:7234" -ForegroundColor White
Write-Host "  Grafana:       http://localhost:3000" -ForegroundColor White
Write-Host "  Prometheus:    http://localhost:9090" -ForegroundColor White
Write-Host "  n8n:           http://localhost:5678" -ForegroundColor White
Write-Host "  Qdrant:        http://localhost:6333/dashboard" -ForegroundColor White

Write-Host "`nTo start the Temporal Worker:" -ForegroundColor Yellow
Write-Host "  cd apps\nexus-engine\src" -ForegroundColor White
if ($usePoetry) {
    Write-Host "  poetry run python main.py" -ForegroundColor White
}
else {
    Write-Host "  python main.py" -ForegroundColor White
}

Write-Host "`nFull documentation in docs/technical/" -ForegroundColor Cyan
Write-Host ""
