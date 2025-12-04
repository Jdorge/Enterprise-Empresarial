# Script de Backup Completo - Setup PHD Edition (V2)
# Autor: WARP Executor | Data: 2025-11-27

$ErrorActionPreference = "Stop"
$currentDir = Get-Location
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = Join-Path $currentDir "Backups\PHD_Setup_$timestamp"

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     BACKUP COMPLETO - SETUP PHD EDITION     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Criar diretório de backup
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
Write-Host "[1/8] Diretório de backup criado: $backupRoot" -ForegroundColor Yellow

# Lista de arquivos e diretórios para backup
$itemsToBackup = @{
    "Enterprise_Ecosystem" = @(
        "enterprise-ecosystem"
    );
    "Scripts_Python"       = @(
        "03_SCRIPTS_PYTHON",
        "glm45v_phd_edition.py",
        "monitoring_dashboard_phd.py",
        "ai_warp_integration.py",
        "metrics_agent.py",
        "test_openai_diagnostico.py",
        "test_openai_sdk.py"
    );
    "Scripts_PowerShell"   = @(
        "backup_setup_phd.ps1",
        "mcp-manager.ps1",
        "optimize_system_phd.ps1",
        "liberar_onedrive.ps1"
    );
    "Configuracoes"        = @(
        "04_CONFIGURACOES",
        ".env"
    );
    "Integracoes"          = @(
        "e2b_integration",
        "parlant-data"
    );
    "Documentacao"         = @(
        "Warp_Outputs\Docs"
    )
}

# Função para copiar
function Copy-Safe {
    param($Source, $Destination)
    
    $fullSource = Join-Path $currentDir $Source
    
    if (Test-Path $fullSource) {
        $parentDir = Split-Path $Destination -Parent
        if (!(Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        
        if ((Get-Item $fullSource).PSIsContainer) {
            Copy-Item -Path $fullSource -Destination $Destination -Recurse -Force
        }
        else {
            Copy-Item -Path $fullSource -Destination $Destination -Force
        }
        return $true
    }
    return $false
}

# Executar backup
$step = 2
$totalFiles = 0
$backedUpFiles = 0

foreach ($category in $itemsToBackup.Keys) {
    Write-Host "[$step/8] Fazendo backup de $category..." -ForegroundColor Yellow
    $categoryPath = Join-Path $backupRoot $category
    New-Item -ItemType Directory -Path $categoryPath -Force | Out-Null
    
    foreach ($item in $itemsToBackup[$category]) {
        $totalFiles++
        $itemName = Split-Path $item -Leaf
        $destPath = Join-Path $categoryPath $itemName
        
        $success = Copy-Safe -Source $item -Destination $destPath
        
        if ($success) {
            $backedUpFiles++
            Write-Host "  ✓ $itemName" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠ $itemName não encontrado" -ForegroundColor Yellow
        }
    }
    $step++
}

# Criar manifesto
Write-Host "[7/8] Criando manifesto..." -ForegroundColor Yellow
$manifest = @{
    "timestamp" = $timestamp;
    "date"      = Get-Date -Format "yyyy-MM-dd HH:mm:ss";
    "stats"     = @{
        "total"   = $totalFiles;
        "success" = $backedUpFiles
    }
}

$manifest | ConvertTo-Json | Out-File "$backupRoot\backup_manifest.json"
Write-Host "  ✓ Manifesto criado" -ForegroundColor Green

# Comprimir
Write-Host "[8/8] Comprimindo backup..." -ForegroundColor Yellow
$zipPath = "$backupRoot.zip"
try {
    Compress-Archive -Path $backupRoot -DestinationPath $zipPath -CompressionLevel Optimal
    Write-Host "  ✓ Backup ZIP criado: $zipPath" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Erro na compressão: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ BACKUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "📂 Local: $backupRoot"
