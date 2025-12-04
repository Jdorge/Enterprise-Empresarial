<#
.SYNOPSIS
    Enterprise Empresarial v2.0.0 - Setup Automatizado Enterprise-Grade

.DESCRIPTION
    Script completo de configuração e inicialização da plataforma Enterprise Empresarial.
    Inclui verificação de dependências, configuração de ambiente, inicialização de serviços
    e validação completa do sistema.

.PARAMETER Mode
    Modo de execução: quick (rápido), full (completo), dev (desenvolvimento), prod (produção)

.PARAMETER SkipDocker
    Pula a inicialização dos containers Docker

.PARAMETER SkipTests
    Pula a execução dos testes automatizados

.PARAMETER Verbose
    Ativa modo verbose com logs detalhados

.EXAMPLE
    ./setup.ps1 -Mode full
    
.EXAMPLE
    ./setup.ps1 -Mode dev -SkipDocker

.NOTES
    Autor: Enterprise Team
    Versão: 2.0.0
    Data: Dezembro 2024
#>

param(
    [ValidateSet("quick", "full", "dev", "prod")]
    [string]$Mode = "full",
    
    [switch]$SkipDocker,
    [switch]$SkipTests,
    [switch]$VerboseOutput
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$script:StartTime = Get-Date
$script:LogFile = "logs/setup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Cores
$Colors = @{
    Success = "Green"
    Error   = "Red"
    Warning = "Yellow"
    Info    = "Cyan"
    Header  = "Magenta"
    Detail  = "Gray"
}

# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Criar diretório de logs se não existir
    $logDir = Split-Path $script:LogFile -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $script:LogFile -Value $logEntry -ErrorAction SilentlyContinue
    
    $color = switch ($Level) {
        "SUCCESS" { $Colors.Success }
        "ERROR" { $Colors.Error }
        "WARNING" { $Colors.Warning }
        "DEBUG" { $Colors.Detail }
        default { $Colors.Info }
    }
    
    Write-Host $logEntry -ForegroundColor $color
}

function Write-Banner {
    $banner = @"

╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███████╗███╗   ██╗████████╗███████╗██████╗ ██████╗ ██████╗ ██╗███████╗     ║
║   ██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║██╔════╝     ║
║   █████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝██████╔╝██████╔╝██║███████╗     ║
║   ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔═══╝ ██╔══██╗██║╚════██║     ║
║   ███████╗██║ ╚████║   ██║   ███████╗██║  ██║██║     ██║  ██║██║███████║     ║
║   ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝     ║
║                                                                               ║
║                    ENTERPRISE EMPRESARIAL v2.0.0                              ║
║              Plataforma de Automação Inteligente Enterprise                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

"@
    Write-Host $banner -ForegroundColor $Colors.Header
}

function Write-Section {
    param([string]$Title)
    
    Write-Host ""
    Write-Host ("═" * 80) -ForegroundColor $Colors.Header
    Write-Host "  $Title" -ForegroundColor $Colors.Header
    Write-Host ("═" * 80) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Test-Command {
    param([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-Port {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [int]$Port,
        [int]$TimeoutSeconds = 120
    )
    
    Write-Log "Aguardando $ServiceName (porta $Port)..." "INFO"
    
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-Port -Port $Port) {
            Write-Log "$ServiceName está pronto!" "SUCCESS"
            return $true
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
        Write-Host "." -NoNewline -ForegroundColor $Colors.Detail
    }
    
    Write-Host ""
    Write-Log "$ServiceName não respondeu após $TimeoutSeconds segundos" "WARNING"
    return $false
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICAÇÃO DE DEPENDÊNCIAS
# ═══════════════════════════════════════════════════════════════════════════════

function Test-Dependencies {
    Write-Section "🔍 VERIFICAÇÃO DE DEPENDÊNCIAS"
    
    $dependencies = @{
        "Docker"         = @{ Command = "docker"; Required = $true; MinVersion = "20.10" }
        "Docker Compose" = @{ Command = "docker-compose"; Required = $true }
        "Node.js"        = @{ Command = "node"; Required = $true; MinVersion = "18.0" }
        "npm"            = @{ Command = "npm"; Required = $true; MinVersion = "9.0" }
        "Python"         = @{ Command = "python"; Required = $false; MinVersion = "3.10" }
        "Poetry"         = @{ Command = "poetry"; Required = $false }
        "Git"            = @{ Command = "git"; Required = $true }
    }
    
    $allPassed = $true
    
    foreach ($dep in $dependencies.GetEnumerator()) {
        $name = $dep.Key
        $config = $dep.Value
        
        if (Test-Command $config.Command) {
            try {
                $versionOutput = & $config.Command --version 2>&1
                $version = ($versionOutput -split '\s+' | Where-Object { $_ -match '^\d+\.\d+' } | Select-Object -First 1)
                Write-Log "[OK] $name instalado (v$version)" "SUCCESS"
            }
            catch {
                Write-Log "[OK] $name instalado" "SUCCESS"
            }
        }
        else {
            if ($config.Required) {
                Write-Log "[ERRO] $name não encontrado (obrigatório)" "ERROR"
                $allPassed = $false
            }
            else {
                Write-Log "[WARN] $name não encontrado (opcional)" "WARNING"
            }
        }
    }
    
    # Verificar Docker daemon
    if (Test-Command "docker") {
        try {
            $null = docker info 2>&1
            Write-Log "[OK] Docker daemon está rodando" "SUCCESS"
        }
        catch {
            Write-Log "[ERRO] Docker daemon não está rodando" "ERROR"
            Write-Log "       Execute: Start-Process 'Docker Desktop'" "INFO"
            $allPassed = $false
        }
    }
    
    return $allPassed
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE AMBIENTE
# ═══════════════════════════════════════════════════════════════════════════════

function Initialize-Environment {
    Write-Section "⚙️ CONFIGURAÇÃO DE AMBIENTE"
    
    # Verificar/criar .env.local
    if (-not (Test-Path ".env.local")) {
        if (Test-Path ".env.example") {
            Write-Log "Criando .env.local a partir de .env.example..." "INFO"
            Copy-Item ".env.example" ".env.local"
            
            Write-Host ""
            Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Warning
            Write-Host "║                    ⚠️  CONFIGURAÇÃO NECESSÁRIA                    ║" -ForegroundColor $Colors.Warning
            Write-Host "╠═══════════════════════════════════════════════════════════════════╣" -ForegroundColor $Colors.Warning
            Write-Host "║  Edite o arquivo .env.local com suas credenciais:                 ║" -ForegroundColor $Colors.Warning
            Write-Host "║                                                                   ║" -ForegroundColor $Colors.Warning
            Write-Host "║  [OBRIGATÓRIO]                                                    ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • POSTGRES_PASSWORD      - Senha do banco de dados              ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • N8N_BASIC_AUTH_PASSWORD - Senha do n8n                        ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • GRAFANA_ADMIN_PASSWORD - Senha do Grafana                     ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • JWT_SECRET             - Chave de segurança                   ║" -ForegroundColor $Colors.Warning
            Write-Host "║                                                                   ║" -ForegroundColor $Colors.Warning
            Write-Host "║  [INTEGRAÇÕES]                                                    ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • NOTION_SECRET          - API key do Notion                    ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • HUBSPOT_API_KEY        - API key do HubSpot                   ║" -ForegroundColor $Colors.Warning
            Write-Host "║  • SLACK_BOT_TOKEN        - Token do bot do Slack               ║" -ForegroundColor $Colors.Warning
            Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Warning
            Write-Host ""
            
            # Abrir editor
            if (Test-Command "code") {
                code ".env.local"
            }
            elseif (Test-Command "notepad") {
                notepad ".env.local"
            }
            
            $continue = Read-Host "Pressione Enter após configurar .env.local (ou 'q' para cancelar)"
            if ($continue -eq 'q') {
                Write-Log "Setup cancelado pelo usuário" "WARNING"
                exit 0
            }
        }
        else {
            Write-Log "[ERRO] Arquivo .env.example não encontrado!" "ERROR"
            return $false
        }
    }
    
    # Validar variáveis obrigatórias
    Write-Log "Validando variáveis de ambiente..." "INFO"
    
    $envContent = Get-Content ".env.local" -ErrorAction SilentlyContinue
    $requiredVars = @(
        "POSTGRES_PASSWORD",
        "N8N_BASIC_AUTH_PASSWORD", 
        "GRAFANA_ADMIN_PASSWORD",
        "JWT_SECRET"
    )
    
    $missingVars = @()
    foreach ($var in $requiredVars) {
        $found = $envContent | Where-Object { $_ -match "^$var=.+" }
        if (-not $found) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Log "Variáveis obrigatórias não configuradas:" "ERROR"
        foreach ($var in $missingVars) {
            Write-Log "  - $var" "ERROR"
        }
        return $false
    }
    
    Write-Log "[OK] Todas as variáveis obrigatórias configuradas" "SUCCESS"
    
    # Criar diretórios necessários
    $directories = @(
        "logs",
        "logs/ai-agents",
        "backups",
        "n8n-workflows/backups",
        "monitoring/prometheus/rules",
        "monitoring/grafana/dashboards",
        "infrastructure/database/init-scripts"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Criado diretório: $dir" "DEBUG"
        }
    }
    
    Write-Log "[OK] Estrutura de diretórios verificada" "SUCCESS"
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

function Start-DockerServices {
    Write-Section "🐳 INICIANDO SERVIÇOS DOCKER"
    
    # Verificar portas em uso
    $ports = @(
        @{ Port = 5432; Service = "PostgreSQL" }
        @{ Port = 6379; Service = "Redis" }
        @{ Port = 5678; Service = "n8n" }
        @{ Port = 3000; Service = "Grafana" }
        @{ Port = 9090; Service = "Prometheus" }
        @{ Port = 7233; Service = "Temporal" }
    )
    
    foreach ($p in $ports) {
        if (Test-Port -Port $p.Port) {
            Write-Log "[WARN] Porta $($p.Port) já está em uso ($($p.Service))" "WARNING"
        }
    }
    
    # Iniciar containers
    Write-Log "Iniciando containers..." "INFO"
    
    try {
        # Carregar variáveis de ambiente
        if (Test-Path ".env.local") {
            $envVars = Get-Content ".env.local" | Where-Object { $_ -match "^[^#].*=.*" }
            foreach ($line in $envVars) {
                $parts = $line -split "=", 2
                if ($parts.Count -eq 2) {
                    [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
                }
            }
        }
        
        # Pull images primeiro
        Write-Log "Baixando imagens Docker..." "INFO"
        docker-compose pull --quiet 2>&1 | Out-Null
        
        # Iniciar serviços
        docker-compose up -d 2>&1 | ForEach-Object { Write-Log $_ "DEBUG" }
        
        Write-Log "[OK] Containers iniciados" "SUCCESS"
        
        # Aguardar serviços ficarem prontos
        Write-Host ""
        Wait-ForService -ServiceName "PostgreSQL" -Port 5432 -TimeoutSeconds 60
        Wait-ForService -ServiceName "Redis" -Port 6379 -TimeoutSeconds 30
        Wait-ForService -ServiceName "n8n" -Port 5678 -TimeoutSeconds 90
        Wait-ForService -ServiceName "Grafana" -Port 3000 -TimeoutSeconds 60
        
        return $true
    }
    catch {
        Write-Log "[ERRO] Falha ao iniciar containers: $_" "ERROR"
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALAÇÃO DE DEPENDÊNCIAS NODE
# ═══════════════════════════════════════════════════════════════════════════════

function Install-NodeDependencies {
    Write-Section "📦 INSTALAÇÃO DE DEPENDÊNCIAS"
    
    # n8n-workflows
    if (Test-Path "n8n-workflows/package.json") {
        Write-Log "Instalando dependências do n8n-workflows..." "INFO"
        Push-Location "n8n-workflows"
        try {
            npm install --silent 2>&1 | Out-Null
            Write-Log "[OK] Dependências do n8n-workflows instaladas" "SUCCESS"
        }
        catch {
            Write-Log "[WARN] Falha ao instalar algumas dependências" "WARNING"
        }
        Pop-Location
    }
    
    # Python dependencies (se Poetry estiver disponível)
    if ((Test-Command "poetry") -and (Test-Path "pyproject.toml")) {
        Write-Log "Instalando dependências Python..." "INFO"
        try {
            poetry install --no-interaction 2>&1 | Out-Null
            Write-Log "[OK] Dependências Python instaladas" "SUCCESS"
        }
        catch {
            Write-Log "[WARN] Falha ao instalar dependências Python (não crítico)" "WARNING"
        }
    }
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
# TESTES
# ═══════════════════════════════════════════════════════════════════════════════

function Invoke-Tests {
    Write-Section "🧪 EXECUTANDO TESTES"
    
    if (Test-Path "n8n-workflows/package.json") {
        Push-Location "n8n-workflows"
        try {
            Write-Log "Executando validação de workflows..." "INFO"
            npm run validate 2>&1 | ForEach-Object { Write-Log $_ "DEBUG" }
            
            Write-Log "Executando testes unitários..." "INFO"
            npm test 2>&1 | ForEach-Object { Write-Log $_ "DEBUG" }
            
            Write-Log "[OK] Testes concluídos" "SUCCESS"
        }
        catch {
            Write-Log "[WARN] Alguns testes falharam (verifique logs)" "WARNING"
        }
        Pop-Location
    }
    
    return $true
}

# ═══════════════════════════════════════════════════════════════════════════════
# SUMÁRIO FINAL
# ═══════════════════════════════════════════════════════════════════════════════

function Show-Summary {
    Write-Section "📊 RESUMO DA INSTALAÇÃO"
    
    $duration = (Get-Date) - $script:StartTime
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Success
    Write-Host "║              ✅ SETUP COMPLETADO COM SUCESSO!                     ║" -ForegroundColor $Colors.Success
    Write-Host "╠═══════════════════════════════════════════════════════════════════╣" -ForegroundColor $Colors.Success
    Write-Host "║                                                                   ║" -ForegroundColor $Colors.Success
    Write-Host "║  🌐 SERVIÇOS DISPONÍVEIS:                                         ║" -ForegroundColor $Colors.Success
    Write-Host "║  ─────────────────────────────────────────────────────────────    ║" -ForegroundColor $Colors.Success
    Write-Host "║  n8n:           http://localhost:5678                             ║" -ForegroundColor $Colors.Success
    Write-Host "║  Grafana:       http://localhost:3000                             ║" -ForegroundColor $Colors.Success
    Write-Host "║  Prometheus:    http://localhost:9090                             ║" -ForegroundColor $Colors.Success
    Write-Host "║  Temporal UI:   http://localhost:8088                             ║" -ForegroundColor $Colors.Success
    Write-Host "║  Qdrant:        http://localhost:6333/dashboard                   ║" -ForegroundColor $Colors.Success
    Write-Host "║                                                                   ║" -ForegroundColor $Colors.Success
    Write-Host "║  📋 PRÓXIMOS PASSOS:                                              ║" -ForegroundColor $Colors.Success
    Write-Host "║  ─────────────────────────────────────────────────────────────    ║" -ForegroundColor $Colors.Success
    Write-Host "║  1. Acesse n8n e importe os workflows de n8n-workflows/           ║" -ForegroundColor $Colors.Success
    Write-Host "║  2. Configure as credenciais no n8n (Notion, HubSpot, Slack)      ║" -ForegroundColor $Colors.Success
    Write-Host "║  3. Acesse Grafana e visualize os dashboards                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  4. Execute: npm run deploy:all (em n8n-workflows/)               ║" -ForegroundColor $Colors.Success
    Write-Host "║                                                                   ║" -ForegroundColor $Colors.Success
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Success
    Write-Host ""
    Write-Host "  ⏱️  Tempo total: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor $Colors.Detail
    Write-Host "  📄 Log completo: $script:LogFile" -ForegroundColor $Colors.Detail
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

function Main {
    Clear-Host
    Write-Banner
    
    Write-Log "Iniciando setup Enterprise Empresarial (Modo: $Mode)" "INFO"
    Write-Log "Sistema: $($PSVersionTable.OS)" "DEBUG"
    Write-Log "PowerShell: $($PSVersionTable.PSVersion)" "DEBUG"
    
    # 1. Verificar dependências
    if (-not (Test-Dependencies)) {
        Write-Log "Falha na verificação de dependências. Corrija os erros acima." "ERROR"
        exit 1
    }
    
    # 2. Configurar ambiente
    if (-not (Initialize-Environment)) {
        Write-Log "Falha na configuração de ambiente." "ERROR"
        exit 1
    }
    
    # 3. Iniciar Docker (se não skipado)
    if (-not $SkipDocker) {
        if (-not (Start-DockerServices)) {
            Write-Log "Falha ao iniciar serviços Docker." "ERROR"
            exit 1
        }
    }
    else {
        Write-Log "Docker skip habilitado - containers não iniciados" "WARNING"
    }
    
    # 4. Instalar dependências Node
    Install-NodeDependencies
    
    # 5. Executar testes (se não skipado)
    if (-not $SkipTests) {
        Invoke-Tests
    }
    else {
        Write-Log "Testes skip habilitados" "WARNING"
    }
    
    # 6. Mostrar resumo
    Show-Summary
}

# Executar
Main
