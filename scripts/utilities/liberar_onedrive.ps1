# Script para liberar espaco do OneDrive
Write-Host "Liberando espaco do OneDrive..." -ForegroundColor Cyan

# 1. Parar OneDrive temporariamente
Write-Host "Parando OneDrive..." -ForegroundColor Yellow
taskkill /f /im OneDrive.exe 2>$null

Start-Sleep -Seconds 3

# 2. Configurar para arquivos sob demanda
Write-Host "Configurando arquivos sob demanda..." -ForegroundColor Yellow

# Registro para habilitar Files On-Demand
$regPath = "HKEY_CURRENT_USER\Software\Microsoft\OneDrive"
try {
    reg add $regPath /v FilesOnDemandEnabled /t REG_DWORD /d 1 /f | Out-Null
    Write-Host "Arquivos sob demanda habilitado!" -ForegroundColor Green
} catch {
    Write-Host "Erro ao configurar registro" -ForegroundColor Red
}

# 3. Limpar cache local
$oneDriveCache = "$env:LOCALAPPDATA\Microsoft\OneDrive"
if (Test-Path $oneDriveCache) {
    Write-Host "Limpando cache..." -ForegroundColor Yellow
    Get-ChildItem $oneDriveCache -Recurse -File | Where-Object {
        $_.Name -like "*.log" -or 
        $_.Name -like "*.tmp" -or 
        $_.Name -like "*.etl" -or
        $_.Extension -eq ".lock"
    } | Remove-Item -Force -ErrorAction SilentlyContinue
}

# 4. Liberacao forcada de espaco (modo agressivo)
Write-Host "Liberando espaco local do OneDrive..." -ForegroundColor Cyan

$oneDrivePath = "$env:USERPROFILE\OneDrive"
if (Test-Path $oneDrivePath) {
    # Comando para marcar arquivos como "somente online"
    try {
        # Use o utilitario attrib para liberar espaco
        attrib +U /S /D "$oneDrivePath\Documentos\*" 2>$null
        Write-Host "Documentos marcados como 'somente online'" -ForegroundColor Green
    } catch {
        Write-Host "Erro ao liberar Documentos" -ForegroundColor Yellow
    }
    
    try {
        # Liberar imagens tambem
        attrib +U /S /D "$oneDrivePath\Imagens\*" 2>$null
        Write-Host "Imagens marcadas como 'somente online'" -ForegroundColor Green
    } catch {
        Write-Host "Erro ao liberar Imagens" -ForegroundColor Yellow
    }
}

# 5. Reiniciar OneDrive
Write-Host "Reiniciando OneDrive..." -ForegroundColor Yellow
Start-Process "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe" -WindowStyle Hidden

Start-Sleep -Seconds 5

# 6. Verificar resultado
Write-Host "Verificando espaco liberado..." -ForegroundColor Cyan
$disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "C:"}
$freeGB = [math]::Round($disk.FreeSpace/1GB, 2)

Write-Host "RESULTADO:" -ForegroundColor Green
Write-Host "Espaco livre atual: $freeGB GB" -ForegroundColor White
Write-Host "OneDrive configurado para 'Arquivos sob demanda'" -ForegroundColor White
Write-Host "Cache limpo e arquivos grandes marcados como online" -ForegroundColor White

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Aguarde alguns minutos para OneDrive sincronizar" -ForegroundColor White
Write-Host "2. Verifique o espaco novamente" -ForegroundColor White
Write-Host "3. Se necessario, use interface do OneDrive para configurar pastas" -ForegroundColor White

Write-Host "Liberacao de espaco concluida!" -ForegroundColor Green
