# 📚 API Reference - Enterprise Empresarial v2.0.0

## Visão Geral

Esta documentação descreve todas as APIs disponíveis no Enterprise Empresarial.

---

## 🔐 Autenticação

### Bearer Token (JWT)

Todas as requisições devem incluir um token JWT válido:

```http
Authorization: Bearer <your-jwt-token>
```

### Obter Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}
```

**Resposta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600,
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## 🔀 Core Router API

### POST /webhook/process-request

Endpoint principal para rotear requisições aos sub-workflows.

**Request:**
```json
{
  "domain": "comercial|operations|finance|knowledge|monitoring",
  "intent": "string - descrição da intenção",
  "data": {
    // Dados específicos do domínio
  },
  "source": "api|webhook|manual",
  "priority": "low|medium|high|critical"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "requestId": "REQ-1701234567890-abc123",
  "message": "Request processed successfully",
  "result": {
    "domain": "comercial",
    "intent": "new_lead",
    "workflow": "SW1_LEADS_COMERCIAL",
    "status": "completed",
    "duration": "1.25s"
  },
  "data": {},
  "timestamp": "2024-12-04T18:00:00.000Z",
  "version": "2.0.0"
}
```

**Headers de Resposta:**
| Header | Descrição |
|--------|-----------|
| `X-Request-ID` | ID único da requisição |
| `X-Processing-Time-Ms` | Tempo de processamento em ms |
| `X-Enterprise-Version` | Versão da API |

---

## 📈 SW1 - Leads Comerciais

### POST /webhook/leads/create

Cria um novo lead no sistema.

**Request:**
```json
{
  "lead": {
    "name": "João Silva",
    "email": "joao@empresa.com",
    "phone": "+5511999999999",
    "company": "Empresa LTDA",
    "position": "CEO",
    "source": "website|linkedin|referral|ads"
  },
  "metadata": {
    "campaign": "black-friday-2024",
    "landing_page": "/enterprise-trial"
  }
}
```

**Response:**
```json
{
  "success": true,
  "leadId": "lead_abc123",
  "score": 75,
  "classification": "hot",
  "assignedTo": "sales-rep-001",
  "nextAction": "schedule_call",
  "hubspotDealId": "12345678",
  "notionPageId": "page_xyz789"
}
```

### GET /webhook/leads/:leadId

Obtém detalhes de um lead.

### PUT /webhook/leads/:leadId/qualify

Qualifica/atualiza score de um lead.

### POST /webhook/leads/:leadId/convert

Converte lead em cliente.

---

## ⚙️ SW2 - Operações

### POST /webhook/operations/tasks/create

Cria uma nova tarefa.

**Request:**
```json
{
  "task": {
    "title": "Implementar feature X",
    "description": "Descrição detalhada...",
    "priority": "high",
    "dueDate": "2024-12-10T18:00:00Z",
    "assignee": "user@company.com",
    "project": "projeto-alpha",
    "tags": ["backend", "urgent"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "taskId": "task_abc123",
  "status": "pending",
  "sla": {
    "deadline": "2024-12-10T18:00:00Z",
    "hoursRemaining": 48,
    "priority": "high"
  },
  "notificationSent": true
}
```

### GET /webhook/operations/tasks

Lista tarefas com filtros.

**Query Parameters:**
| Param | Tipo | Descrição |
|-------|------|-----------|
| `status` | string | pending, in_progress, completed |
| `priority` | string | low, medium, high, critical |
| `assignee` | string | Email do responsável |
| `project` | string | Nome do projeto |
| `limit` | number | Máximo de resultados (default: 50) |
| `offset` | number | Offset para paginação |

### PUT /webhook/operations/tasks/:taskId/status

Atualiza status de uma tarefa.

---

## 💰 SW3 - Financeiro

### POST /webhook/finance/transactions

Registra uma transação financeira.

**Request:**
```json
{
  "transaction": {
    "type": "income|expense|transfer",
    "amount": 15000.00,
    "currency": "BRL",
    "category": "sales|services|operational|taxes",
    "description": "Venda de licença Enterprise",
    "reference": "INV-2024-001",
    "date": "2024-12-04"
  },
  "metadata": {
    "client": "Empresa XYZ",
    "contract": "CTR-2024-123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "transactionId": "txn_abc123",
  "recorded": true,
  "tax": {
    "calculated": true,
    "amount": 2250.00,
    "rate": 0.15
  },
  "alerts": [
    {
      "type": "high_value",
      "message": "Transaction exceeds R$10,000 threshold"
    }
  ]
}
```

### GET /webhook/finance/reports/daily

Relatório diário de finanças.

### GET /webhook/finance/reports/monthly

Relatório mensal consolidado.

---

## 📚 SW4 - Base de Conhecimento

### POST /webhook/knowledge/articles

Cria um novo artigo.

**Request:**
```json
{
  "article": {
    "title": "Como configurar n8n Webhooks",
    "content": "# Introdução\n\nConteúdo em Markdown...",
    "category": "technical|business|tutorial|faq",
    "tags": ["n8n", "webhooks", "automation"],
    "language": "pt-BR"
  }
}
```

**Response:**
```json
{
  "success": true,
  "articleId": "kb_abc123",
  "embedding": {
    "generated": true,
    "vectorId": "vec_xyz789"
  },
  "searchable": true
}
```

### GET /webhook/knowledge/search

Busca semântica na base de conhecimento.

**Query Parameters:**
| Param | Tipo | Descrição |
|-------|------|-----------|
| `q` | string | Query de busca |
| `category` | string | Filtro por categoria |
| `limit` | number | Máximo de resultados |

---

## 🔍 SW5 - Monitoramento

### POST /webhook/monitoring/health-check

Executa health check em todos os serviços.

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-12-04T18:00:00.000Z",
  "services": {
    "n8n": { "status": "healthy", "latency": 45 },
    "postgres": { "status": "healthy", "latency": 12 },
    "redis": { "status": "healthy", "latency": 3 },
    "notion": { "status": "healthy", "latency": 250 },
    "hubspot": { "status": "healthy", "latency": 180 }
  },
  "overall": "healthy"
}
```

### GET /webhook/monitoring/metrics

Obtém métricas do sistema.

### POST /webhook/monitoring/alerts

Cria um alerta manual.

---

## 📊 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| `VALIDATION_ERROR` | Dados de entrada inválidos |
| `UNAUTHORIZED` | Token inválido ou expirado |
| `FORBIDDEN` | Sem permissão para este recurso |
| `NOT_FOUND` | Recurso não encontrado |
| `RATE_LIMITED` | Limite de requisições excedido |
| `SERVICE_UNAVAILABLE` | Serviço externo indisponível |
| `INTERNAL_ERROR` | Erro interno do servidor |

**Formato de Erro:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'email' is required",
    "details": {
      "field": "email",
      "constraint": "required"
    }
  },
  "timestamp": "2024-12-04T18:00:00.000Z"
}
```

---

## 🔒 Rate Limiting

| Tier | Limite | Janela |
|------|--------|--------|
| Free | 100 req | 1 min |
| Pro | 1000 req | 1 min |
| Enterprise | Ilimitado | - |

**Headers de Rate Limit:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701360000
```

---

## 📡 Webhooks

### Configurar Webhook

```http
POST /api/webhooks/subscribe
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["lead.created", "task.completed", "transaction.recorded"],
  "secret": "your-webhook-secret"
}
```

### Eventos Disponíveis

| Evento | Descrição |
|--------|-----------|
| `lead.created` | Novo lead criado |
| `lead.qualified` | Lead qualificado |
| `lead.converted` | Lead convertido |
| `task.created` | Nova tarefa criada |
| `task.completed` | Tarefa concluída |
| `task.sla_breach` | SLA violado |
| `transaction.recorded` | Transação registrada |
| `alert.triggered` | Alerta disparado |

---

## 🔗 SDKs Disponíveis

- [JavaScript/TypeScript SDK](./sdks/javascript)
- [Python SDK](./sdks/python)
- [Go SDK](./sdks/go)

---

**Versão da API:** 2.0.0  
**Base URL:** `https://api.enterprise-empresarial.com`  
**Suporte:** api-support@enterprise-empresarial.com
