# MCP Manager - Script de Gerenciamento Unificado
# Autor: Jorge OS
# Versão: 1.0.0

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'status', 'test', 'logs', 'update', 'backup')]
    [string]$Action = 'status',
    
    [Parameter(Position=1)]
    [ValidateSet('all', 'scrapeless', 'zapier', 'filesystem', 'memory')]
    [string]$Server = 'all'
)

# Carregar variáveis de ambiente
if (Test-Path "$HOME\.env.mcp") {
    Get-Content "$HOME\.env.mcp" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
        }
    }
}

# Cores para output
$colors = @{
    Success = 'Green'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
}

function Write-Status {
    param($Message, $Type = 'Info')
    Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] " -NoNewline
    Write-Host $Message -ForegroundColor $colors[$Type]
}

function Start-MCPServer {
    param($ServerName)
    
    Write-Status "Iniciando servidor $ServerName..." "Info"
    
    switch ($ServerName) {
        'scrapeless' {
            $process = Start-Process -FilePath "node" `
                -ArgumentList "$HOME\scrapeless-mcp-server\build\index.js", "--port=9593" `
                -PassThru -WindowStyle Hidden
            Write-Status "Scrapeless iniciado na porta 9593 (PID: $($process.Id))" "Success"
        }
        'zapier' {
            $process = Start-Process -FilePath "node" `
                -ArgumentList "$HOME\mcp_zapier_server\robust_server.js" `
                -PassThru -WindowStyle Hidden
            Write-Status "Zapier server iniciado (PID: $($process.Id))" "Success"
        }
        'filesystem' {
            $process = Start-Process -FilePath "npx" `
                -ArgumentList "-y", "@modelcontextprotocol/server-filesystem", "$HOME" `
                -PassThru -WindowStyle Hidden
            Write-Status "Filesystem server iniciado (PID: $($process.Id))" "Success"
        }
        'memory' {
            $process = Start-Process -FilePath "npx" `
                -ArgumentList "-y", "@modelcontextprotocol/server-memory" `
                -PassThru -WindowStyle Hidden
            Write-Status "Memory server iniciado (PID: $($process.Id))" "Success"
        }
    }
}

function Stop-MCPServer {
    param($ServerName)
    
    Write-Status "Parando servidor $ServerName..." "Warning"
    
    switch ($ServerName) {
        'scrapeless' {
            Get-Process -Name "node" -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -like "*scrapeless-mcp-server*" } | 
                Stop-Process -Force
        }
        'zapier' {
            Get-Process -Name "node" -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -like "*mcp_zapier_server*" } | 
                Stop-Process -Force
        }
        default {
            Get-Process -Name "node" -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -like "*$ServerName*" } | 
                Stop-Process -Force
        }
    }
    Write-Status "Servidor $ServerName parado" "Success"
}

function Get-MCPStatus {
    Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         MCP SERVERS STATUS               ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar MCP CLI
    $mcpVersion = mcp version 2>$null
    if ($mcpVersion) {
        Write-Status "MCP CLI: $mcpVersion" "Success"
    } else {
        Write-Status "MCP CLI: Não encontrado" "Error"
    }
    
    # Verificar processos
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    
    $servers = @{
        'Scrapeless' = '*scrapeless-mcp-server*'
        'Zapier' = '*mcp_zapier_server*'
        'Filesystem' = '*server-filesystem*'
        'Memory' = '*server-memory*'
    }
    
    foreach ($server in $servers.GetEnumerator()) {
        $running = $nodeProcesses | Where-Object { $_.CommandLine -like $server.Value }
        if ($running) {
            Write-Status "$($server.Key): ✅ Rodando (PID: $($running.Id))" "Success"
        } else {
            Write-Status "$($server.Key): ❌ Parado" "Warning"
        }
    }
    
    # Verificar porta 9593
    $portCheck = Test-NetConnection -ComputerName localhost -Port 9593 -WarningAction SilentlyContinue
    if ($portCheck.TcpTestSucceeded) {
        Write-Status "Porta 9593: ✅ Aberta" "Success"
    } else {
        Write-Status "Porta 9593: ❌ Fechada" "Warning"
    }
}

function Test-MCPServers {
    Write-Status "Testando servidores MCP..." "Info"
    
    # Teste básico do Scrapeless
    if (Test-Path "$HOME\scrapeless-mcp-server\build\index.js") {
        Write-Status "Scrapeless: Arquivos OK" "Success"
    } else {
        Write-Status "Scrapeless: Arquivos não encontrados" "Error"
    }
    
    # Teste de conectividade
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9593/health" -TimeoutSec 2 -ErrorAction Stop
        Write-Status "Endpoint de saúde: ✅ Respondendo" "Success"
    } catch {
        Write-Status "Endpoint de saúde: ⚠️ Não respondendo (servidor pode estar offline)" "Warning"
    }
}

function Show-MCPLogs {
    param($Lines = 50)
    
    Write-Status "Últimas $Lines linhas de logs:" "Info"
    
    $logFiles = @(
        "$HOME\mcp.log",
        "$HOME\scrapeless-mcp-server\server.log",
        "$HOME\mcp_zapier_server\zapier.log"
    )
    
    foreach ($logFile in $logFiles) {
        if (Test-Path $logFile) {
            Write-Host "`n--- $logFile ---" -ForegroundColor Yellow
            Get-Content $logFile -Tail $Lines
        }
    }
}

function Update-MCPServers {
    Write-Status "Atualizando servidores MCP..." "Info"
    
    # Atualizar MCP principal
    Write-Status "Atualizando MCP CLI..." "Info"
    pip install --upgrade mcp fastmcp
    
    # Atualizar Scrapeless
    if (Test-Path "$HOME\scrapeless-mcp-server") {
        Write-Status "Atualizando Scrapeless..." "Info"
        Push-Location "$HOME\scrapeless-mcp-server"
        npm update
        npm run build
        Pop-Location
    }
    
    # Atualizar SDKs globais
    Write-Status "Atualizando SDKs Node.js..." "Info"
    npm update -g @modelcontextprotocol/sdk
    
    Write-Status "Atualização completa!" "Success"
}

function Backup-MCPConfig {
    $backupDir = "$HOME\mcp-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-Status "Criando backup em $backupDir..." "Info"
    
    # Copiar configurações
    $filesToBackup = @(
        "$HOME\.env.mcp",
        "$HOME\AppData\Roaming\Claude\claude_desktop_config.json",
        "$HOME\MCP_Setup_Report_2025.md"
    )
    
    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            Copy-Item $file $backupDir
            Write-Status "Backup: $(Split-Path $file -Leaf)" "Success"
        }
    }
    
    # Criar ZIP
    Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
    Write-Status "Backup comprimido: $backupDir.zip" "Success"
}

# Executar ação solicitada
switch ($Action) {
    'start' {
        if ($Server -eq 'all') {
            @('scrapeless', 'zapier') | ForEach-Object { Start-MCPServer $_ }
        } else {
            Start-MCPServer $Server
        }
    }
    'stop' {
        if ($Server -eq 'all') {
            @('scrapeless', 'zapier', 'filesystem', 'memory') | ForEach-Object { Stop-MCPServer $_ }
        } else {
            Stop-MCPServer $Server
        }
    }
    'status' {
        Get-MCPStatus
    }
    'test' {
        Test-MCPServers
    }
    'logs' {
        Show-MCPLogs
    }
    'update' {
        Update-MCPServers
    }
    'backup' {
        Backup-MCPConfig
    }
}

Write-Host "`n✨ MCP Manager - Operação completa" -ForegroundColor Green
