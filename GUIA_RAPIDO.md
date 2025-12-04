# 🚀 Enterprise Empresarial - Guia de Implementação Rápida

## 📋 O Que Você Tem Agora

Uma **plataforma empresarial completa** que integra:
- ✅ **N8N** para automação visual
- ✅ **Agentes de IA** especializados (Comercial, Varejo, Router)
- ✅ **Temporal.io** para orquestração durável
- ✅ **Grafana + Prometheus** para monitoramento total
- ✅ **PostgreSQL** como banco central

---

## 🎯 Como Começar em 5 Passos

### **Passo 1: Configurar Credenciais** (5 minutos)

```bash
# 1. Copiar arquivo de exemplo
cp .env.example .env

# 2. Editar com suas credenciais
notepad .env  # Windows
# ou
nano .env     # Linux/Mac

# OBRIGATÓRIO configurar:
# - POSTGRES_PASSWORD
# - N8N_PASSWORD
# - GRAFANA_PASSWORD
# - OPENAI_API_KEY
```

### **Passo 2: Subir a Plataforma** (2 minutos)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f
```

### **Passo 3: Acessar Interfaces** (1 minuto)

Abra no navegador:
- **N8N**: http://localhost:5678 (automações)
- **Grafana**: http://localhost:3000 (dashboards)
- **Prometheus**: http://localhost:9090 (métricas brutas)
- **Temporal UI**: http://localhost:8088 (workflows duráveis)

### **Passo 4: Importar Dashboards** (3 minutos)

#### No Grafana (http://localhost:3000):
1. Login: `admin` / senha do `.env`
2. Ir em **Dashboards** > **Import**
3. Importar os 4 dashboards:
   - `monitoring/grafana/dashboards/dashboard-overview-executivo.json`
   - `monitoring/grafana/dashboards/dashboard-performance-latencia.json`
   - `monitoring/grafana/dashboards/dashboard-erros-qualidade.json`
   - `monitoring/grafana/dashboards/ai-agents-metrics.json`

### **Passo 5: Testar o Sistema** (5 minutos)

```bash
# Testar N8N
curl http://localhost:5678/healthz

# Testar MCP Server (AI)
curl http://localhost:8080/health

# Testar Grafana
curl http://localhost:3000/api/health

# Ver workflows ativos
docker exec enterprise-temporal temporal workflow list
```

---

## 📊 Estrutura do Projeto

```
Enterprise Empresarial/
│
├── 🧠 enterprise-ecosystem/      # Agentes de IA
│   ├── agents/                   # Código dos agentes
│   │   ├── base_agent.py
│   │   ├── router_agent.py
│   │   ├── commercial_agent.py
│   │   └── retail_agent.py
│   ├── orchestration/
│   │   ├── mcp-server/          # MCP Protocol
│   │   └── temporal-workers/     # Temporal.io
│   └── integrations/
│       ├── e2b/                  # Code Execution
│       └── llm-gateways/         # OpenAI, Anthropic
│
├── ⚙️ n8n-workflows/             # Automações
│   ├── core/                     # WF_CORE_ROUTER_v2.0.0.json
│   ├── commercial/               # Vendas
│   ├── financial/                # Financeiro
│   └── operations/               # Operações
│
├── 👁️ monitoring/                 # Observabilidade
│   ├── grafana/
│   │   └── dashboards/           # 4 dashboards prontos
│   └── prometheus/
│       ├── prometheus.yml
│       └── rules/                # Regras de alerta
│
├── 📚 docs/                       # Documentação
│   ├── business/                 # Propostas, contratos
│   ├── knowledge-base/           # PDFs técnicos
│   └── technical/                # Manuais
│
├── 🛠️ scripts/                    # DevOps
│   ├── backup/
│   ├── deployment/
│   └── setup/
│
└── 💾 config/                     # Configurações
    ├── ai-agents/                # Prompts e configs IA
    └── n8n/                      # Configurações n8n
```

---

## 💼 Casos de Uso Práticos

### **Caso 1: Automação Comercial com IA**

**Cenário**: Cliente manda mensagem no WhatsApp pedindo orçamento.

**Fluxo**:
1. n8n recebe via webhook
2. Router Agent (IA) classifica a intenção
3. Commercial Agent busca dados no Notion
4. IA gera proposta personalizada
5. n8n envia resposta via WhatsApp
6. Tudo registrado no PostgreSQL
7. Métricas aparecem no Grafana

**Implementar**:
- Importar `n8n-workflows/commercial/leads.json`
- Configurar credenciais Notion e WhatsApp no n8n
- Ativar workflow

### **Caso 2: Monitoramento Financeiro**

**Cenário**: Acompanhar métricas de vendas em tempo real.

**Fluxo**:
1. n8n executa workflows financeiros
2. Dados salvos no PostgreSQL
3. Grafana exibe em dashboards
4. Alertas automáticos se metas não atingidas

**Implementar**:
- Abrir dashboard `dashboard-overview-executivo.json` no Grafana
- Configurar data source PostgreSQL
- Criar alertas personalizados

### **Caso 3: Execução de Código Segura**

**Cenário**: Cliente pede análise de dados complexa.

**Fluxo**:
1. Retail Agent recebe solicitação
2. Gera código Python via IA
3. Executa em sandbox E2B (isolado)
4. Retorna resultado
5. Log completo para auditoria

**Implementar**:
- Configurar `E2B_API_KEY` no `.env`
- Ativar agente Varejo no Temporal

---

## 🔧 Comandos Úteis

### **Gerenciamento de Containers**

```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f [service-name]

# Reiniciar serviço específico
docker-compose restart n8n

# Parar tudo
docker-compose down

# Parar e limpar volumes
docker-compose down -v
```

### **Backup e Restore**

```bash
# Backup do banco
docker exec enterprise-postgres pg_dump -U admin enterprise_db > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i enterprise-postgres psql -U admin enterprise_db < backup_YYYYMMDD.sql

# Backup de workflows n8n
docker cp enterprise-n8n:/home/node/.n8n ./backup-n8n

# Backup de dashboards Grafana
docker cp enterprise-grafana:/var/lib/grafana ./backup-grafana
```

### **Monitoramento**

```bash
# Ver métricas Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Testar alertas
curl http://localhost:9090/api/v1/alerts

# Ver workflows Temporal
docker exec enterprise-temporal temporal workflow list

# Ver logs de AI Agent
docker logs enterprise-ai-router --tail 100
```

---

## 🐛 Troubleshooting

### **Problema: Container não sobe**

```bash
# Verificar logs
docker-compose logs [service-name]

# Verificar portas em uso
netstat -ano | findstr "5678"  # Windows
lsof -i :5678                  # Linux/Mac

# Liberar porta
# Identificar PID e matar processo
```

### **Problema: N8N não conecta no banco**

```bash
# Verificar se PostgreSQL está UP
docker-compose ps postgres

# Testar conexão
docker exec enterprise-postgres psql -U admin -d enterprise_db -c "SELECT 1;"

# Ver senha configurada
docker exec enterprise-n8n env | grep POSTGRES
```

### **Problema: Dashboards sem dados**

```bash
# Verificar data source no Grafana
curl http://admin:password@localhost:3000/api/datasources

# Testar query PostgreSQL
docker exec enterprise-postgres psql -U admin -d enterprise_db -c "SELECT COUNT(*) FROM workflow_logs;"

# Popular dados de teste
docker exec enterprise-n8n n8n execute workflow --name="Test Workflow"
```

---

## 📞 Próximos Passos

1. **Personalizar Agentes**:
   - Editar `enterprise-ecosystem/agents/*.py`
   - Ajustar prompts em `config/ai-agents/`

2. **Criar Workflows Customizados**:
   - Acessar n8n UI
   - Criar novo workflow
   - Exportar JSON para versionamento

3. **Configurar Alertas**:
   - Grafana > Alerting
   - Criar regras baseadas em métricas
   - Configurar Slack/Email

4. **Documentar Processos**:
   - Usar templates em `docs/business/`
   - Criar casos de uso específicos
   - Treinar equipe

---

## ✅ Checklist de Validação

- [ ] Todos os containers rodando (`docker-compose ps`)
- [ ] N8N acessível (http://localhost:5678)
- [ ] Grafana com dashboards (http://localhost:3000)
- [ ] PostgreSQL recebendo dados
- [ ] AI Agents respondendo
- [ ] Workflows importados
- [ ] Alertas configurados
- [ ] Backup testado
- [ ] Documentação atualizada
- [ ] Equipe treinada

---

**Pronto para uso! 🎉**

Para suporte: consulte `docs/technical/` ou abra uma issue no repositório.
