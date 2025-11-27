# 🏢 Enterprise Empresarial v3.0
**Plataforma Unificada de Automação, IA e Monitoramento**

---

## 📋 Visão Geral
O **Enterprise Empresarial** é a evolução definitiva do ecossistema Nexus, unificando orquestração de Agentes IA, workflows n8n e observabilidade total em uma arquitetura modular e escalável.

### 🎯 Pilares do Sistema
1.  **Inteligência Artificial (`enterprise-ecosystem/`)**: Agentes autônomos, MCP e integração LLM.
2.  **Automação de Processos (`n8n-workflows/`)**: Fluxos de trabalho empresariais (Comercial, Financeiro, Ops).
3.  **Observabilidade (`monitoring/`)**: Grafana e Prometheus monitorando n8n, IA e Infra.
4.  **Infraestrutura (`infrastructure/`)**: IaC com Terraform e Kubernetes.

---

## 🏗️ Estrutura de Diretórios

```plaintext
Enterprise Empresarial/
├── 📄 docker-compose.yml         # Orquestração Global
├── 📄 .env                       # Segredos Centralizados
│
├── 📁 enterprise-ecosystem/      # 🧠 CÉREBRO (IA)
│   ├── agents/                   # Agentes (Base, Router, Varejo)
│   └── integrations/             # E2B, LLMs
│
├── 📁 n8n-workflows/             # ⚙️ MOTOR (Automação)
│   ├── core/                     # Workflows Críticos
│   └── commercial/               # Fluxos de Vendas
│
├── 📁 monitoring/                # 👁️ OLHOS (Observabilidade)
│   ├── grafana/                  # Dashboards Profissionais
│   └── prometheus/               # Métricas e Alertas
│
├── 📁 docs/                      # 📚 CONHECIMENTO
│   ├── business/                 # Propostas, ROI, Contratos
│   └── technical/                # Arquitetura e Manuais
│
└── 📁 scripts/                   # 🛠️ FERRAMENTAS
    ├── backup/                   # Scripts de Segurança
    └── deployment/               # CI/CD
```

---

## 🚀 Como Iniciar

### 1. Configuração Inicial
```bash
# 1. Configure as credenciais
cp config/.env.example .env

# 2. Execute o setup de ambiente
./scripts/setup/optimize_system_phd.ps1
```

### 2. Rodar a Plataforma
```bash
# Iniciar todos os serviços
docker-compose up -d
```

### 3. Acessar Serviços
- **n8n**: `http://localhost:5678`
- **Grafana**: `http://localhost:3000`
- **Prometheus**: `http://localhost:9090`
- **Agentes API**: `http://localhost:8000`

---

## 💼 Recursos de Consultoria
Acesse a pasta `docs/business/` para encontrar:
- 📄 Modelos de Proposta Comercial
- 📊 Calculadoras de ROI
- 📜 Minutas de Contrato
- 📘 Guia de Segmentação de Mercado

---

**Enterprise Empresarial** - *Excelência em Automação e Inteligência Artificial*
