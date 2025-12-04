#!/bin/bash
# setup.sh - INSTALAÇÃO COMPLETA NEXUS N8N
# USO: bash scripts/setup.sh

set -e

echo "🚀 =========================================="
echo "   NEXUS N8N - SETUP COMPLETO"
echo "=========================================="

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. VALIDAR PRÉ-REQUISITOS
echo -e "\n${YELLOW}[1/8]${NC} Validando Pré-requisitos..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Instale em: https://www.docker.com/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker OK${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose OK${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git não encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git OK${NC}"

# 2. CRIAR .env SE NÃO EXISTIR
echo -e "\n${YELLOW}[2/8]${NC} Configurando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# BANCO DE DADOS
DB_PASSWORD=SecureN8nPass2025!

# REDIS
REDIS_PASSWORD=RedisN8n2025!

# GRAFANA
GRAFANA_PASSWORD=admin123

# N8N CONFIG
N8N_HOST=localhost
WEBHOOK_TUNNEL_URL=http://localhost:5678
GENERIC_TIMEZONE=America/Sao_Paulo

# NOTIFICAÇÕES (OPCIONAL)
SLACK_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
EMAIL_SMTP_HOST=
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=
EMAIL_SMTP_PASS=
EOF
    echo -e "${GREEN}✅ .env criado${NC}"
else
    echo -e "${GREEN}✅ .env já existe${NC}"
fi

# 3. CRIAR DIRETÓRIOS NECESSÁRIOS
echo -e "\n${YELLOW}[3/8]${NC} Criando estrutura de diretórios..."

mkdir -p .github/workflows
mkdir -p infrastructure/docker
mkdir -p infrastructure/terraform
mkdir -p infrastructure/kubernetes/manifests
mkdir -p infrastructure/monitoring/prometheus
mkdir -p infrastructure/monitoring/grafana
mkdir -p infrastructure/monitoring/alerting
mkdir -p scripts
mkdir -p templates
mkdir -p docs
mkdir -p tests/{unit,integration,load}
mkdir -p backup

echo -e "${GREEN}✅ Diretórios criados${NC}"

# 4. VALIDAR PERMISSÕES
echo -e "\n${YELLOW}[4/8]${NC} Ajustando permissões..."

chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.js 2>/dev/null || true

echo -e "${GREEN}✅ Permissões ajustadas${NC}"

# 5. INICIALIZAR GIT (SE NECESSÁRIO)
echo -e "\n${YELLOW}[5/8]${NC} Verificando Git..."

if [ ! -d ".git" ]; then
    git init
    git config user.email "nexus@n8n.local"
    git config user.name "NEXUS Bot"
    echo -e "${GREEN}✅ Git iniciado${NC}"
else
    echo -e "${GREEN}✅ Git já configurado${NC}"
fi

# 6. CONSTRUIR IMAGENS DOCKER
echo -e "\n${YELLOW}[6/8]${NC} Construindo imagens Docker..."

docker-compose build --no-cache 2>&1 || {
    echo -e "${YELLOW}⚠️  Build com cache${NC}"
    docker-compose build
}

echo -e "${GREEN}✅ Imagens construídas${NC}"

# 7. SUBIR CONTAINERS
echo -e "\n${YELLOW}[7/8]${NC} Iniciando serviços..."

docker-compose up -d

# Aguardar containers ficarem saudáveis
echo -e "\n${YELLOW}Aguardando serviços iniciarem...${NC}"
sleep 10

# 8. VALIDAR SAÚDE
echo -e "\n${YELLOW}[8/8]${NC} Validando saúde dos serviços..."

services_ok=true

# Validar PostgreSQL
if docker-compose exec -T postgres pg_isready -U n8n &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL OK${NC}"
else
    echo -e "${RED}❌ PostgreSQL FALHOU${NC}"
    services_ok=false
fi

# Validar Redis
if docker-compose exec -T redis redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✅ Redis OK${NC}"
else
    echo -e "${RED}❌ Redis FALHOU${NC}"
    services_ok=false
fi

# Validar n8n
if curl -s http://localhost:5678/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ n8n OK${NC}"
else
    echo -e "${RED}❌ n8n FALHOU${NC}"
    services_ok=false
fi

# Validar Prometheus
if curl -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus OK${NC}"
else
    echo -e "${RED}❌ Prometheus FALHOU${NC}"
    services_ok=false
fi

# Validar Grafana
if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana OK${NC}"
else
    echo -e "${RED}❌ Grafana FALHOU${NC}"
    services_ok=false
fi

echo -e "\n=========================================="
if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 NEXUS N8N SETUP COMPLETO!${NC}"
    echo -e "\n📍 Acessos:"
    echo -e "   n8n:        ${GREEN}http://localhost:5678${NC}"
    echo -e "   Prometheus: ${GREEN}http://localhost:9090${NC}"
    echo -e "   Grafana:    ${GREEN}http://localhost:3000${NC}"
    echo -e "   AlertMgr:   ${GREEN}http://localhost:9093${NC}"
    echo -e "\n📝 Próximos passos:"
    echo -e "   1. Acessar n8n e importar workflows"
    echo -e "   2. Conectar Grafana ao Prometheus"
    echo -e "   3. Configurar alertas no AlertManager"
    echo -e "   4. Fazer primeiro backup: ${YELLOW}bash scripts/backup-restore.sh backup${NC}"
else
    echo -e "${RED}⚠️  ALGUNS SERVIÇOS FALHARAM${NC}"
    echo -e "   Verifique logs: ${YELLOW}docker-compose logs${NC}"
fi
echo -e "=========================================="
