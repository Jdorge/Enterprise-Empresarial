# 🏢 Enterprise Empresarial v2.0.0

<div align="center">

![Enterprise Empresarial](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![n8n](https://img.shields.io/badge/n8n-enterprise-orange.svg)
![AI](https://img.shields.io/badge/AI-powered-purple.svg)

**Plataforma Enterprise de Automação Inteligente e Orquestração de Processos**

[Início Rápido](#-início-rápido) • [Arquitetura](#-arquitetura) • [Documentação](#-documentação) • [Contribuindo](#-contribuindo)

</div>

---

## 🎯 Visão Geral

O **Enterprise Empresarial** é uma plataforma completa de automação empresarial que combina:

- 🤖 **Inteligência Artificial** - Agentes autônomos com MCP e integração multi-LLM
- ⚙️ **Automação de Processos** - Workflows n8n para Comercial, Financeiro, Operações
- 📊 **Observabilidade** - Monitoramento em tempo real com Grafana e Prometheus
- 🏗️ **Infraestrutura como Código** - Terraform + Kubernetes para deploy escalável
- 🔒 **Segurança Enterprise** - Autenticação, criptografia e auditoria completa

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ENTERPRISE EMPRESARIAL                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   CLIENTS   │  │   API GW    │  │   AUTH      │  │   CACHE     │   │
│  │  (Web/API)  │──│   (Kong)    │──│   (JWT)     │──│   (Redis)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           ORCHESTRATION LAYER                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         n8n WORKFLOWS                            │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │  LEADS  │ │   OPS   │ │FINANCE  │ │KNOWLEDGE│ │MONITOR  │   │   │
│  │  │  SW1    │ │   SW2   │ │  SW3    │ │   SW4   │ │   SW5   │   │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │   │
│  │       └───────────┴───────────┼───────────┴───────────┘         │   │
│  │                               │                                   │   │
│  │                    ┌──────────┴──────────┐                       │   │
│  │                    │   CORE ROUTER       │                       │   │
│  │                    │   (WF_CORE)         │                       │   │
│  │                    └─────────────────────┘                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                            AI AGENTS LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  MCP Server │  │   Router    │  │  Temporal   │  │  Qdrant     │   │
│  │  (Agents)   │──│   Agent     │──│  (Durable)  │──│  (Vector)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           DATA & STORAGE LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ PostgreSQL  │  │   Notion    │  │   HubSpot   │  │   Slack     │   │
│  │  (Primary)  │  │   (Docs)    │  │   (CRM)     │  │   (Comms)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                          OBSERVABILITY LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Prometheus  │──│   Grafana   │──│ Alertmanager│──│   Loki      │   │
│  │  (Metrics)  │  │ (Dashboards)│  │  (Alerts)   │  │   (Logs)    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Início Rápido

### Pré-requisitos

- **Docker** >= 20.10 & Docker Compose
- **Node.js** >= 18.0 & npm >= 9.0
- **Python** >= 3.10 (para agentes IA)
- **Git** para versionamento

### Instalação em 3 Passos

```bash
# 1. Clone e configure
git clone https://github.com/Jdorge/enterprise-empresarial.git
cd "Enterprise Empresarial"

# 2. Configure credenciais
cp .env.example .env.local
# Edite .env.local com suas API keys

# 3. Inicie tudo
./scripts/setup.ps1  # Windows
# ou
docker-compose up -d  # Linux/Mac
```

### Verificação

```bash
# Verificar serviços
docker ps

# Testar workflows
cd n8n-workflows
npm install && npm test
```

---

## 📂 Estrutura do Projeto

```
Enterprise Empresarial/
│
├── 📄 docker-compose.yml           # Orquestração de containers
├── 📄 .env.example                  # Template de variáveis
├── 📄 pyproject.toml                # Configuração Python
│
├── 📁 n8n-workflows/                # ⚙️ MOTOR DE AUTOMAÇÃO
│   ├── core/                        # Workflow principal (Router)
│   ├── workflows/                   # 5 sub-workflows especializados
│   ├── scripts/                     # Deploy, test, backup, validate
│   └── docs/                        # Documentação dos workflows
│
├── 📁 enterprise-ecosystem/         # 🧠 INTELIGÊNCIA ARTIFICIAL
│   ├── orchestration/               # MCP Server e orquestração
│   ├── agents/                      # Agentes especializados
│   └── integrations/                # E2B, LLMs
│
├── 📁 monitoring/                   # 👁️ OBSERVABILIDADE
│   ├── grafana/                     # Dashboards profissionais
│   ├── prometheus/                  # Métricas e regras de alerta
│   └── alertmanager/                # Gestão de alertas
│
├── 📁 infrastructure/               # 🏗️ INFRAESTRUTURA
│   ├── kubernetes/                  # Manifestos K8s
│   ├── terraform/                   # IaC para cloud
│   └── docker/                      # Dockerfiles customizados
│
├── 📁 config/                       # ⚙️ CONFIGURAÇÕES
│   ├── ai-agents/                   # Configs de agentes
│   └── credentials/                 # Templates de credenciais
│
├── 📁 docs/                         # 📚 DOCUMENTAÇÃO
│   ├── business/                    # Propostas, ROI, contratos
│   ├── technical/                   # Arquitetura, APIs, manuais
│   └── knowledge-base/              # Base de conhecimento
│
├── 📁 scripts/                      # 🛠️ AUTOMAÇÃO
│   ├── setup/                       # Scripts de setup
│   ├── deployment/                  # CI/CD scripts
│   ├── backup/                      # Backup e restore
│   └── utilities/                   # Utilitários diversos
│
└── 📁 tests/                        # 🧪 TESTES
    ├── unit/                        # Testes unitários
    ├── integration/                 # Testes de integração
    └── e2e/                         # Testes end-to-end
```

---

## 🔌 Serviços e Portas

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| **n8n** | 5678 | http://localhost:5678 | Automação visual de workflows |
| **Grafana** | 3000 | http://localhost:3000 | Dashboards de monitoramento |
| **Prometheus** | 9090 | http://localhost:9090 | Coleta de métricas |
| **Temporal** | 7233/8088 | http://localhost:8088 | Orquestração durável |
| **PostgreSQL** | 5432 | - | Banco de dados principal |
| **MCP Server** | 8080 | http://localhost:8080 | Agentes de IA |
| **Qdrant** | 6333 | http://localhost:6333 | Vector database |

---

## 📊 Workflows Disponíveis

### WF_CORE_ROUTER (Router Central)
O cérebro do sistema. Recebe requisições e roteia para sub-workflows especializados.

### SW1_LEADS_COMERCIAL
- Captura de leads multi-canal
- Lead scoring automático (0-100)
- Integração HubSpot + Notion + Slack
- Qualificação: Hot/Warm/Cold

### SW2_OPERACOES
- Gestão de tarefas e projetos
- Priorização automática
- Alertas de urgência
- SLA tracking

### SW3_FINANCEIRO
- Registro de transações
- Cálculo de impostos
- Alertas de alto valor
- Relatórios automáticos

### SW4_CONHECIMENTO
- Base de conhecimento
- Busca semântica
- Categorização automática
- Análise de conteúdo

### SW5_MONITORAMENTO
- Health checks automáticos
- Coleta de métricas
- Alertas multi-nível
- Dashboard em tempo real

---

## 🔒 Segurança

### Recursos de Segurança
- ✅ Autenticação JWT em todas as APIs
- ✅ Criptografia de dados em repouso e trânsito
- ✅ Gestão de secrets via variáveis de ambiente
- ✅ Rate limiting e proteção contra DDoS
- ✅ Logs de auditoria completos
- ✅ RBAC (Role-Based Access Control)

### Boas Práticas
```bash
# Nunca commitar credenciais!
# Use sempre .env.local (ignorado pelo git)
cp .env.example .env.local
```

---

## 📚 Documentação

- [📖 Guia de Setup](./docs/technical/SETUP_GUIDE.md)
- [🏗️ Arquitetura Detalhada](./docs/technical/ARCHITECTURE.md)
- [🔌 API Reference](./docs/technical/API_REFERENCE.md)
- [🔧 Troubleshooting](./docs/technical/TROUBLESHOOTING.md)
- [💼 Propostas Comerciais](./docs/business/)

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para mais detalhes.

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja [LICENSE](./LICENSE) para detalhes.

---

## 📞 Suporte

- 📧 Email: suporte@enterprise-empresarial.com
- 📚 Docs: [docs/](./docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/Jdorge/enterprise-empresarial/issues)

---

<div align="center">

**Enterprise Empresarial** - *Excelência em Automação e Inteligência Artificial*

Made with ❤️ by Enterprise Team

</div>
