# 🚀 Guia de Operação: Enterprise Empresarial no Antigravity

**Versão:** 1.0  
**Data:** 27/11/2025  
**Status:** Operacional

---

## 🎯 1. Visão Geral
Este guia descreve o fluxo de trabalho passo a passo para iniciar, operar e evoluir a plataforma **Enterprise Empresarial** utilizando o ambiente **Antigravity**.

---

## 🏁 2. Inicialização (Start-up)

### **Passo 1: Preparação do Ambiente**
Sempre que iniciar uma nova sessão no Antigravity:

1. **Navegue para o diretório do projeto:**
   ```bash
   cd "Enterprise Empresarial"
   ```

2. **Verifique as credenciais:**
   - Certifique-se de que o arquivo `.env` existe e está populado.
   - Se não existir: `cp .env.example .env` e peça ao agente para ajudar a preencher.

3. **Verifique o estado do Docker:**
   ```bash
   docker-compose ps
   ```

### **Passo 2: Subindo a Infraestrutura**
Para iniciar todo o ecossistema (n8n, AI Agents, Banco de Dados, Monitoramento):

1. **Comando de Start:**
   ```bash
   docker-compose up -d
   ```
   *O agente pode executar isso para você.*

2. **Validação de Saúde:**
   Peça ao agente: *"Verifique se todos os serviços estão rodando e saudáveis."*
   O agente verificará:
   - N8N (Porta 5678)
   - Grafana (Porta 3000)
   - Prometheus (Porta 9090)
   - Temporal (Porta 7233)

---

## 🤖 3. Execução de Agentes e Workflows

### **Cenário A: Executar um Agente de IA**
Para rodar um agente específico (ex: Agente Comercial):

1. **Via Terminal (Antigravity):**
   ```bash
   python enterprise-ecosystem/agents/commercial_agent.py --task "Gerar proposta para Cliente X"
   ```

2. **Via Comando Natural:**
   Diga ao agente: *"Execute o Agente Comercial para criar uma proposta para a empresa Acme Corp, setor de tecnologia, 500 funcionários."*

### **Cenário B: Disparar Workflow n8n**
Para iniciar uma automação:

1. **Via Webhook (Simulado pelo Agente):**
   ```bash
   curl -X POST http://localhost:5678/webhook/lead-entry -d '{"name": "Teste", "email": "teste@email.com"}'
   ```

2. **Via Interface:**
   Peça ao agente: *"Abra o n8n e verifique o status do workflow de Vendas."*

---

## 🛠️ 4. Desenvolvimento e Manutenção

### **Criar Novo Agente**
1. Diga: *"Crie um novo agente chamado 'Agente de RH' baseado no template `base_agent.py`."*
2. O agente criará o arquivo em `enterprise-ecosystem/agents/rh_agent.py`.
3. O agente registrará o novo agente no `router.py`.

### **Monitorar Performance**
1. Diga: *"Gere um relatório de performance dos últimos 30 minutos."*
2. O agente lerá os logs ou consultará a API do Prometheus/Grafana e resumirá para você.

### **Backup e Segurança**
1. Diga: *"Execute o script de backup agora."*
2. O agente rodará `./scripts/deployment/backup-restore.sh`.

---

## 🔄 5. Ciclo de Encerramento

Ao finalizar o trabalho:

1. **Parar Serviços (Opcional):**
   ```bash
   docker-compose stop
   ```
   *(Recomendado manter rodando se for um servidor, mas parar se for desenvolvimento local)*

2. **Commitar Alterações:**
   Diga: *"Faça commit e push de todas as alterações de hoje."*
   O agente executará o fluxo Git completo.

---

## 🆘 Troubleshooting Comum

| Problema | Solução via Agente |
|----------|-------------------|
| **Erro de Porta em Uso** | *"Verifique o que está rodando na porta 5678 e mate o processo."* |
| **Agente Falhando** | *"Leia os logs do container `enterprise-ai-router` e me diga o erro."* |
| **Banco de Dados Cheio** | *"Verifique o espaço em disco e limpe logs antigos do Docker."* |

---

**Antigravity Ready** 🚀
Este ambiente está configurado para permitir controle total via linguagem natural.
