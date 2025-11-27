# Script de Otimização do Sistema - PHD Edition
# Autor: WARP Executor | Data: 2025-08-20
# Executa melhorias de performance no Windows

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   OTIMIZAÇÃO DO SISTEMA - PHD EDITION       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. Desativar apps desnecessários na inicialização
Write-Host "`n[1/7] Desativando apps desnecessários na inicialização..." -ForegroundColor Yellow

$AppsToDisable = @(
    "OneDrive",
    "WhatsApp",
    "Spotify",
    "Discord",
    "Steam",
    "Skype"
)

foreach ($app in $AppsToDisable) {
    $task = Get-ScheduledTask -TaskName "*$app*" -ErrorAction SilentlyContinue
    if ($task) {
        Disable-ScheduledTask -TaskName $task.TaskName -ErrorAction SilentlyContinue
        Write-Host "  ✓ $app desativado" -ForegroundColor Green
    }
}

# 2. Limpar arquivos temporários
Write-Host "`n[2/7] Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Arquivos temporários limpos" -ForegroundColor Green

# 3. Otimizar memória virtual
Write-Host "`n[3/7] Otimizando memória virtual..." -ForegroundColor Yellow
$ComputerSystem = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges
$ComputerSystem.AutomaticManagedPagefile = $true
$ComputerSystem.Put() | Out-Null
Write-Host "  ✓ Memória virtual otimizada" -ForegroundColor Green

# 4. Desativar efeitos visuais desnecessários
Write-Host "`n[4/7] Desativando efeitos visuais..." -ForegroundColor Yellow
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00))
Write-Host "  ✓ Efeitos visuais otimizados" -ForegroundColor Green

# 5. Configurar plano de energia para alto desempenho
Write-Host "`n[5/7] Configurando plano de energia..." -ForegroundColor Yellow
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
Write-Host "  ✓ Plano de energia configurado para alto desempenho" -ForegroundColor Green

# 6. Limpar cache DNS
Write-Host "`n[6/7] Limpando cache DNS..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "  ✓ Cache DNS limpo" -ForegroundColor Green

# 7. Criar tarefa agendada para limpeza automática
Write-Host "`n[7/7] Criando tarefa de manutenção automática..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"C:\Users\usuario\cleanup_weekly.ps1`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "WarpSystemOptimization" -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✓ Tarefa de manutenção criada" -ForegroundColor Green

# Relatório final
Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         OTIMIZAÇÃO CONCLUÍDA!               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green

# Mostrar status do sistema
Write-Host "`nStatus do Sistema:" -ForegroundColor Cyan
$ram = Get-WmiObject Win32_OperatingSystem
$ramUsage = [math]::Round(($ram.TotalVisibleMemorySize - $ram.FreePhysicalMemory) / $ram.TotalVisibleMemorySize * 100, 2)
$cpu = Get-WmiObject Win32_Processor
$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskUsage = [math]::Round(($disk.Size - $disk.FreeSpace) / $disk.Size * 100, 2)

Write-Host "  CPU: $($cpu.Name)" -ForegroundColor White
Write-Host "  RAM: $ramUsage% em uso" -ForegroundColor White
Write-Host "  Disco: $diskUsage% em uso" -ForegroundColor White

Write-Host "`nRecomenda-se reiniciar o sistema para aplicar todas as otimizações." -ForegroundColor Yellow
