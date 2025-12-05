# 🔧 Guia de Troubleshooting - Enterprise Empresarial

## Problemas Comuns e Soluções

---

## 🐳 Docker

### Container não inicia

**Sintoma:** `docker-compose up` falha ou container fica em restart loop.

**Soluções:**

1. **Verificar logs:**
```bash
docker-compose logs <service-name>
docker-compose logs n8n
docker-compose logs postgres
```

2. **Verificar variáveis de ambiente:**
```bash
# Verificar se .env.local existe e tem os valores obrigatórios
cat .env.local | grep -E "^[^#]"
```

3. **Limpar e reiniciar:**
```bash
docker-compose down -v
docker system prune -f
docker-compose up -d
```

### Erro de porta em uso

**Sintoma:** `Error: bind: address already in use`

**Solução:**
```bash
# Windows
netstat -ano | findstr :5678
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5678
kill -9 <PID>
```

### Permissão negada em volumes

**Solução:**
```bash
# Linux
sudo chown -R 1000:1000 ./n8n-data
sudo chmod -R 755 ./n8n-data
```

---

## ⚙️ n8n

### Workflow não executa

**Verificações:**

1. **Workflow está ativo?**
   - Acesse n8n UI → Verifique toggle de ativação

2. **Webhook URL correta?**
   - Verifique `N8N_WEBHOOK_URL` no `.env.local`

3. **Credenciais configuradas?**
```bash
# Verificar variáveis
echo $NOTION_SECRET
echo $HUBSPOT_API_KEY
echo $SLACK_BOT_TOKEN
```

### Erro de conexão com Notion

**Sintoma:** `401 Unauthorized` ou `403 Forbidden`

**Soluções:**

1. **Verificar API Key:**
   - Acesse https://www.notion.so/my-integrations
   - Copie o "Internal Integration Secret"
   - Atualize `NOTION_SECRET` no `.env.local`

2. **Verificar permissões do database:**
   - Abra o database no Notion
   - Clique em "..." → "Add connections" → Selecione sua integração

3. **Verificar formato do ID:**
```
# Correto (32 chars, sem hífens)
abc123def456...

# Incorreto (com hífens da URL)
abc123-def456-...
```

### Erro de conexão com HubSpot

**Sintoma:** `401 Unauthorized`

**Soluções:**

1. **Verificar Private App Token:**
   - Settings → Integrations → Private Apps
   - Verifique escopos necessários: `crm.objects.contacts.read`, `crm.objects.deals.write`

2. **Regenerar token se necessário**

### Erro de conexão com Slack

**Sintoma:** Mensagens não enviadas

**Verificações:**

1. **Bot Token válido?**
   - Acesse https://api.slack.com/apps
   - OAuth & Permissions → Bot User OAuth Token

2. **Bot adicionado ao canal?**
   - No canal: `/invite @YourBotName`

3. **Escopos corretos?**
   - `chat:write`, `chat:write.public`, `channels:read`

---

## 🗄️ Database (PostgreSQL)

### Conexão recusada

**Sintoma:** `ECONNREFUSED 127.0.0.1:5432`

**Soluções:**

1. **Container rodando?**
```bash
docker ps | grep postgres
```

2. **Verificar credenciais:**
```bash
docker exec -it enterprise-postgres psql -U admin -d enterprise_db
```

3. **Verificar network:**
```bash
docker network inspect enterprise-network
```

### Tabelas não existem

**Solução:**
```bash
# Executar migrations
docker exec -it enterprise-postgres psql -U admin -d enterprise_db -f /docker-entrypoint-initdb.d/init.sql
```

---

## 📊 Monitoramento

### Grafana não mostra dados

**Verificações:**

1. **Prometheus coletando métricas?**
   - Acesse http://localhost:9090/targets
   - Todos os targets devem estar "UP"

2. **Data source configurado?**
   - Grafana → Configuration → Data Sources
   - Prometheus URL: `http://prometheus:9090`

3. **Dashboard importado?**
   - Grafana → Dashboards → Import
   - Use os JSONs em `monitoring/grafana/dashboards/`

### Alertas não disparam

**Verificações:**

1. **Alertmanager configurado?**
```bash
docker logs enterprise-alertmanager
```

2. **Regras de alerta carregadas?**
   - Prometheus → Status → Rules
   - Verifique se as regras aparecem

3. **Canais de notificação configurados?**
   - Verifique `monitoring/alertmanager/alertmanager.yml`

---

## 🔐 Autenticação

### Token JWT expirado

**Sintoma:** `401 Unauthorized - Token expired`

**Solução:**
```javascript
// Renovar token
const newToken = await fetch('/api/auth/refresh', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${refreshToken}` }
});
```

### CORS bloqueado

**Solução:**
```javascript
// Adicionar origem permitida no server
app.use(cors({
  origin: ['http://localhost:3000', 'https://your-domain.com'],
  credentials: true
}));
```

---

## 🔄 Git & Deploy

### Push para GitHub falha

**Sintoma:** `Connection was reset`

**Soluções:**

1. **Aumentar buffer:**
```bash
git config http.postBuffer 524288000
```

2. **Usar SSH em vez de HTTPS:**
```bash
git remote set-url origin git@github.com:Jdorge/enterprise-empresarial.git
```

3. **Verificar conexão:**
```bash
ssh -T git@github.com
```

### Vercel build falha

**Verificações:**

1. **Verificar logs no Vercel Dashboard**

2. **Build local funciona?**
```bash
npm run build
```

3. **Variáveis de ambiente configuradas?**
   - Vercel → Project → Settings → Environment Variables

---

## 🧪 Testes

### Testes falhando

**Comandos de debug:**

```bash
# Ver logs detalhados
npm test -- --verbose

# Rodar teste específico
npm test -- --grep "should create lead"

# Verificar cobertura
npm run test:coverage
```

---

## 📞 Obter Ajuda

Se nenhuma das soluções acima resolver:

1. **Verifique a documentação:** `docs/`
2. **Abra uma Issue:** https://github.com/Jdorge/enterprise-empresarial/issues
3. **Colete informações:**
   - Versões (node, docker, n8n)
   - Logs de erro completos
   - Steps para reproduzir

---

## 🔍 Comandos Úteis de Debug

```bash
# Status de todos os containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f

# Executar comando dentro do container
docker exec -it enterprise-n8n sh

# Verificar variáveis de ambiente do container
docker exec enterprise-n8n env

# Verificar conectividade
docker exec enterprise-n8n ping postgres

# Restart de serviço específico
docker-compose restart n8n

# Rebuild de imagem
docker-compose build --no-cache mcp-server
```
