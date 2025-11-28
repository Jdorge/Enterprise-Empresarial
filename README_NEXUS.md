# 🚀 Nexus Enterprise v2 - Setup Integrado

**Enterprise-grade AI Agents Orchestration Platform**

Sistema completo de orquestração de agentes de IA com execução durável via Temporal, RAG com Qdrant, integração n8n e observabilidade completa.

---

## ✨ Características Principais

- ✅ **Workflows Duráveis**: Temporal para execução resistente a falhas
- ✅ **LLM Unificado**: OpenRouter com 300+ modelos (GPT-4, Claude, Gemini, etc)
- ✅ **RAG Vetorial**: Qdrant para memória contextual
- ✅ **Aprovação Humana**: Human-in-the-loop via n8n
- ✅ **Observabilidade**: Prometheus + Grafana com alertas
- ✅ **Segurança**: Gestão segura de secrets, zero hardcoding
- ✅ **Testado**: Suite completa de testes automatizados

---

## 🎯 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                   NEXUS ENTERPRISE V2                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │   Workflows (Temporal)                          │  │
│  │   - Propostas Comerciais                        │  │
│  │   - Pesquisa e Análise                          │  │
│  │   - Aprovações Humanas                          │  │
│  └──────────────────┬──────────────────────────────┘  │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐  │
│  │   Activities                                    │  │
│  │   - LLM (OpenRouter)                            │  │
│  │   - RAG (Qdrant)                                │  │
│  │   - n8n (Webhooks)                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │   Infraestrutura                                │  │
│  │   - Postgres (Estado)                           │  │
│  │   - Qdrant (Vetores)                            │  │
│  │   - Prometheus/Grafana (Métricas)               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (5 minutos)

### 1. Pré-requisitos

- **Docker** (20.10+)
- **Python** (3.10+)
- **Poetry** (recomendado) ou pip

### 2. Setup Automático

```powershell
# Clone o repositório (se ainda não tiver)
git clone <repo-url>
cd "Enterprise Empresarial"

# Execute o setup automatizado
.\scripts\setup.ps1
```

O script irá:
1. ✅ Validar dependências
2. ✅ Criar `.env.local` a partir do template
3. ✅ Instalar pacotes Python
4. ✅ Iniciar infraestrutura Docker
5. ✅ Executar testes
6. ✅ Exibir URLs dos serviços

### 3. Configurar API Keys

Edite `.env.local` e preencha:

```bash
# OBRIGATÓRIO
OPENROUTER_API_KEY=sk-or-v1-...  # Obtenha em: https://openrouter.ai/keys
POSTGRES_PASSWORD=senha_segura
N8N_PASSWORD=senha_segura
GRAFANA_PASSWORD=senha_segura
JWT_SECRET=<gere com: python -c "import secrets; print(secrets.token_urlsafe(32))">
ENCRYPTION_KEY=<gere com: python -c "import secrets; print(secrets.token_urlsafe(32))">
```

### 4. Iniciar Worker

```powershell
cd apps\nexus-engine\src
poetry run python main.py
```

**Pronto!** 🎉 O sistema está rodando.

---

## 📊 Serviços Disponíveis

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Temporal UI** | http://localhost:7234 | Sem autenticação |
| **Grafana** | http://localhost:3000 | admin / [sua senha do .env] |
| **Prometheus** | http://localhost:9090 | Sem autenticação |
| **n8n** | http://localhost:5678 | admin / [sua senha do .env] |
| **Qdrant** | http://localhost:6333/dashboard | Sem autenticação |

---

## 📂 Estrutura do Projeto

```
Enterprise-Empresarial/
├── apps/
│   └── nexus-engine/               # Temporal workers
│       └── src/
│           ├── workflows/          # Workflows duráveis
│           ├── activities/         # Activities (LLM, RAG, n8n)
│           └── main.py             # Worker entrypoint
│
├── packages/
│   ├── nexus_core/                 # Configuração e modelos
│   ├── nexus_llm_factory/          # LLM via OpenRouter
│   └── nexus_guardrails/           # Segurança IA (futuro)
│
├── infrastructure/
│   ├── docker-compose.yml          # Stack completa
│   └── monitoring/                 # Prometheus/Grafana
│
├── n8n-workflows/                  # Workflows n8n existentes
│
├── tests/
│   ├── unit/                       # Testes unitários
│   └── integration/                # Testes de integração
│
├── docs/
│   ├── technical/                  # Documentação técnica
│   │   ├── NEXUS_VALIDATION_REPORT.md
│   │   ├── NEXUS_CORRECTION_PLAN.md
│   │   └── INTEGRATION_PLAN_FINAL.md
│   └── business/                   # Documentação de negócio
│
├── .env.example                    # Template de configuração
├── pyproject.toml                  # Dependências Poetry
└── README.md                       # Este arquivo
```

---

## 🔧 Desenvolvimento

### Executar Testes

```powershell
# Todos os testes
poetry run pytest

# Apenas unitários
poetry run pytest tests/unit -v

# Com coverage
poetry run pytest --cov=packages --cov=apps
```

### Adicionar novo Workflow

1. Crie arquivo em `apps/nexus-engine/src/workflows/meu_workflow.py`
2. Implemente activities necessárias em `activities/`
3. Registre no `main.py`
4. Adicione testes em `tests/`

### Monitoramento

- **Métricas**: Acesse Grafana (localhost:3000)
- **Logs**: `docker-compose logs -f <servico>`
- **Alertas**: Configurados em `infrastructure/monitoring/alerts.yml`

---

## 📚 Documentação Completa

- **[Relatório de Validação](docs/technical/NEXUS_VALIDATION_REPORT.md)** - Análise técnica completa
- **[Plano de Correção](docs/technical/NEXUS_CORRECTION_PLAN.md)** - Correções implementadas
- **[Plano de Integração](docs/technical/INTEGRATION_PLAN_FINAL.md)** - Integração com sistemas existentes
- **[Executive Summary](docs/technical/EXECUTIVE_SUMMARY.md)** - Resumo executivo

---

## 🔐 Segurança

### Boas Práticas Implementadas

✅ **Sem credenciais hardcoded** - Tudo via `.env.local` (não versionado)  
✅ **SecretStr** do Pydantic para senhas em memória  
✅ **Docker secrets** suportado  
✅ **Rate limiting** para APIs  
✅ **Retry policies** inteligentes  
✅ **Validação de inputs** via Pydantic  

### Checklist de Segurança

- [ ] `.env.local` criado e **NÃO** commitado
- [ ] Chaves API válidas configuradas
- [ ] Senhas fortes para todos os serviços
- [ ] Secrets rotacionados regularmente
- [ ] Logs não expõem credenciais

---

## 💰 Custos Estimados

| Componente | Custo Mensal (dev) | Custo Mensal (prod) |
|------------|-------------------|---------------------|
| OpenRouter (LLM) | $20-50 | $100-500 |
| Infraestrutura (Cloud) | $0 (local) | $150-300 |
| Monitoring (Grafana Cloud) | $0 (self-hosted) | $49+ |
| **TOTAL estimado** | **$20-50** | **$300-850** |

💡 **Dica**: Use modelos `fast` (GPT-4o-mini) em dev e `balanced` (Claude) em produção.

---

## 📈 Roadmap

### ✅ Concluído (v2.0)
- [x] Workflows Temporal funcionais
- [x] LLM Factory com OpenRouter
- [x] RAG com Qdrant
- [x] Integração n8n
- [x] Observabilidade Prometheus/Grafana
- [x] Docker Compose completo
- [x] Testes automatizados

### 🚧 Próximas Releases

**v2.1 (2 semanas)**
- [ ] Guardrails de IA (PII detection, content filtering)
- [ ] API Gateway (FastAPI)
- [ ] CI/CD (GitHub Actions)
- [ ] Dashboards Grafana customizados

**v2.2 (1 mês)**
- [ ] Kubernetes manifests
- [ ] Multi-tenancy
- [ ] Cache de embeddings
- [ ] Cost optimization

---

## 🆘 Troubleshooting

### Temporal não inicia

```powershell
# Verificar logs
docker-compose -f infrastructure/docker-compose.yml logs temporal

# Recriar container
docker-compose -f infrastructure/docker-compose.yml up -d --force-recreate temporal
```

### Worker falha ao conectar

```powershell
# Verificar se Temporal está saudável
curl http://localhost:7234

# Verificar .env.local
cat .env.local | findstr TEMPORAL_HOST
```

### Qdrant não encontra resultados

```powershell
# Verificar coleções
curl http://localhost:6333/collections

# Recriar coleção
# (implementar script de reset)
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob licença proprietária. Todos os direitos reservados.

---

## 👥 Suporte

- 📧 Email: support@nexusenterprise.com
- 💬 Slack: #nexus-enterprise
- 📖 Wiki: [Internal Confluence](https://confluence.company.com/nexus)

---

**Feito com ❤️ pela equipe Nexus Enterprise**
