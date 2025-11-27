# Script Automatizado de Push para GitHub
# Execute este script após criar o repositório no GitHub

param(
    [Parameter(Mandatory = $true)]
    [string]$GithubUsername,
    
    [Parameter(Mandatory = $false)]
    [string]$RepoName = "enterprise-empresarial"
)

Write-Host "🚀 Enterprise Empresarial - Push Automatizado para GitHub" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (!(Test-Path ".git")) {
    Write-Host "❌ Erro: Execute este script dentro do diretório 'Enterprise Empresarial'" -ForegroundColor Red
    exit 1
}

# Configurar remote
$remoteUrl = "https://github.com/$GithubUsername/$RepoName.git"
Write-Host "📡 Configurando remote: $remoteUrl" -ForegroundColor Yellow

# Remover remote existente (se houver)
git remote remove origin 2>$null

# Adicionar novo remote
git remote add origin $remoteUrl

# Verificar remote
Write-Host ""
Write-Host "✅ Remote configurado:" -ForegroundColor Green
git remote -v

# Renomear branch para main
Write-Host ""
Write-Host "🔄 Renomeando branch para 'main'..." -ForegroundColor Yellow
git branch -M main

# Fazer push
Write-Host ""
Write-Host "📤 Fazendo push para o GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  Você precisará autenticar com:" -ForegroundColor Yellow
Write-Host "   Username: $GithubUsername" -ForegroundColor Cyan
Write-Host "   Password: SEU_PERSONAL_ACCESS_TOKEN (não a senha!)" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 PUSH CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Seu repositório está online em:" -ForegroundColor Green
    Write-Host "   https://github.com/$GithubUsername/$RepoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Acesse o repositório no navegador"
    Write-Host "   2. Configure GitHub Actions (CI/CD)"
    Write-Host "   3. Adicione colaboradores"
    Write-Host "   4. Configure branch protection"
}
else {
    Write-Host ""
    Write-Host "❌ Erro no push. Verifique:" -ForegroundColor Red
    Write-Host "   - Repositório foi criado no GitHub?"
    Write-Host "   - Username está correto?"
    Write-Host "   - Personal Access Token tem permissão 'repo'?"
    Write-Host ""
    Write-Host "📖 Consulte PUSH_TO_GITHUB.md para mais detalhes"
}
