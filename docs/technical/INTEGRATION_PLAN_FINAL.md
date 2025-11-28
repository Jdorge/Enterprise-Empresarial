# 🎯 Plano de Integração Final: Enterprise Empresarial + Nexus Corrected

**Data:** 2025-11-28  
**Status:** EXECUTÁVEL  
**Prioridade:** CRÍTICA

---

## 📋 Resumo Executivo

**Estratégia:** Manter "Enterprise Empresarial" como base, integrar componentes válidos do Nexus Corrected.

### Componentes a Integrar:
1. ✅ LLMFactory multimodelo (corrigido)
2. ✅ Workflows Temporal com retry/timeout
3. ✅ Activities do Temporal
4. ✅ Prometheus/Grafana (observabilidade)
5. ✅ Guardrails de IA
6. ✅ Gestão segura de secrets

### Componentes a Manter (Enterprise Empresarial):
1. ✅ n8n workflows existentes
2. ✅ Estrutura de documentação
3. ✅ Integração PHD
4. ✅ Governança e templates

---

## 🚨 CORREÇÕES CRÍTICAS (Executar AGORA)

### 1. Segurança - Remover Credenciais Expostas

```bash
# URGENTE: Verificar se .env está commitado
cd "C:\Users\Leandro\OneDrive\Desktop\DEVops\PHD_Setup_Clone_20250820_2108\Enterprise Empresarial"

# Se .env existe no Git, REMOVER IMEDIATAMENTE:
git rm --cached .env
git rm --cached .env.local

# Atualizar .gitignore
cat >> .gitignore << 'EOF'

# ============ SECRETS (NUNCA COMMITAR) ============
.env
.env.local
.env.production
.env.*.local
secrets/
*.key
*.pem
**/api_keys.txt
EOF

# Commit
git add .gitignore
git commit -m "🔒 Security: Remove exposed credentials and update .gitignore"
```

### 2. Criar Estrutura de Secrets Segura

```bash
# Criar diretório de secrets (fora do Git)
mkdir -p secrets
echo "secrets/" >> .gitignore

# Template seguro
cat > .env.example << 'EOF'
# ============ LLM APIs ============
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# ============ Database ============
POSTGRES_PASSWORD=
QDRANT_API_KEY=

# ============ Services ============
N8N_PASSWORD=
GRAFANA_PASSWORD=
JWT_SECRET=

# ============ Temporal ============
TEMPORAL_HOST=temporal:7233
TEMPORAL_NAMESPACE=default
EOF
```

---

## 📁 Estrutura Unificada Final

```
Enterprise-Empresarial/
├── apps/
│   ├── nexus-engine/           # Temporal workers
│   │   ├── src/
│   │   │   ├── workflows/      # Workflows Temporal
│   │   │   ├── activities/     # Activities (LLM, Qdrant, etc)
│   │   │   └── main.py         # Worker entrypoint
│   │   └── Dockerfile
│   │
│   └── api-gateway/            # FastAPI (fire-and-forget)
│       ├── routers/
│       └── main.py
│
├── packages/
│   ├── nexus_core/             # Modelos compartilhados
│   ├── nexus_llm_factory/      # LLM multimodelo
│   └── nexus_guardrails/       # Segurança IA
│
├── infrastructure/
│   ├── docker-compose.yml      # Stack completa
│   ├── kubernetes/             # K8s (futuro)
│   └── monitoring/
│       ├── prometheus.yml
│       ├── alerts.yml
│       └── grafana/
│           └── dashboards/
│
├── n8n-workflows/              # MANTER workflows n8n existentes
│   └── (workflows atuais)
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── docs/                       # MANTER documentação existente
    ├── technical/
    └── business/
```

---

## 🔧 Implementação por Fase

### **FASE 1: Segurança e Base (Dias 1-2)**

**Arquivo:** `packages/nexus_core/config.py`

```python
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from pathlib import Path

class Settings(BaseSettings):
    # LLM APIs
    openai_api_key: SecretStr = Field(...)
    anthropic_api_key: SecretStr = Field(...)
    gemini_api_key: SecretStr = Field(...)
    
    # Temporal
    temporal_host: str = "temporal:7233"
    temporal_namespace: str = "default"
    
    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    
    model_config = {
        "env_file": ".env.local",
        "case_sensitive": False
    }
```

**Arquivo:** `infrastructure/docker-compose.yml` (corrigido)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD obrigatório}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  temporal:
    image: temporalio/auto-setup:1.25
    environment:
      - DB=postgresql
      - POSTGRES_USER=nexus
      - POSTGRES_PWD=${POSTGRES_PASSWORD}
      - POSTGRES_SEEDS=postgres:5432
    ports:
      - "7233:7233"
    depends_on:
      postgres:
        condition: service_healthy

  n8n:
    image: n8nio/n8n:latest
    environment:
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:?N8N_PASSWORD obrigatório}
    ports:
      - "5678:5678"
    volumes:
      - ./n8n-workflows:/home/node/.n8n  # Monta workflows existentes

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:?GRAFANA_PASSWORD obrigatório}
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  qdrant_data:
```

---

### **FASE 2: LLMFactory Corrigido (Dias 3-4)**

**Arquivo:** `packages/nexus_llm_factory/factory.py`

```python
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
import time

class LLMFactory:
    """Factory multimodelo com fallback e métricas."""
    
    def __init__(self, settings):
        from openai import AsyncOpenAI
        from anthropic import AsyncAnthropic
        
        self.clients = {
            "openai": AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value()),
            "anthropic": AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value()),
        }
        self.total_cost = 0.0
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """Gera resposta com fallback."""
        
        # Tenta OpenAI primeiro
        try:
            return await self._call_openai(messages, response_model)
        except Exception as e:
            print(f"OpenAI falhou: {e}")
        
        # Fallback: Anthropic
        try:
            return await self._call_anthropic(messages, response_model)
        except Exception as e:
            print(f"Anthropic falhou: {e}")
            raise Exception("Todos os modelos falharam")
    
    async def _call_openai(self, messages, response_model):
        client = self.clients["openai"]
        
        if response_model:
            import instructor
            client = instructor.from_openai(client)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_model=response_model,
            )
            return response
        else:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            return response.choices[0].message.content
    
    async def _call_anthropic(self, messages, response_model):
        client = self.clients["anthropic"]
        
        # Anthropic usa messages.create
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=messages,
        )
        
        return response.content[0].text
```

---

### **FASE 3: Testes Básicos (Dia 5)**

**Arquivo:** `tests/unit/test_llm_factory.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from nexus_llm_factory.factory import LLMFactory
from pydantic import SecretStr

class MockSettings:
    openai_api_key = SecretStr("sk-test")
    anthropic_api_key = SecretStr("sk-ant-test")

@pytest.mark.asyncio
async def test_openai_success():
    with patch("nexus_llm_factory.factory.AsyncOpenAI") as mock_openai:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock(message=AsyncMock(content="Test"))]
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        
        factory = LLMFactory(MockSettings())
        result = await factory.generate([{"role": "user", "content": "Hi"}])
        
        assert result == "Test"
```

**Executar testes:**
```bash
pytest tests/ -v
```

---

## 🎯 Script de Setup Rápido

**Arquivo:** `scripts/setup_unified.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Setup Integrado: Enterprise Empresarial + Nexus"

# 1. Validar .env
if [ ! -f .env.local ]; then
    echo "❌ .env.local não encontrado!"
    echo "📝 Copie .env.example para .env.local e preencha"
    cp .env.example .env.local
    exit 1
fi

# 2. Instalar dependências
poetry install

# 3. Subir infraestrutura
docker-compose -f infrastructure/docker-compose.yml up -d

# 4. Aguardar serviços
echo "⏳ Aguardando serviços..."
sleep 15

# 5. Executar testes
poetry run pytest tests/ -v

echo "✅ Setup completo!"
echo "📊 Acesse:"
echo "   - Grafana: http://localhost:3000"
echo "   - n8n: http://localhost:5678"
echo "   - Prometheus: http://localhost:9090"
```

---

## ✅ Checklist Final

- [ ] .env.local criado (SEM commitar)
- [ ] Credenciais antigas REVOGADAS
- [ ] Docker Compose sobe sem erros
- [ ] Testes básicos passando
- [ ] n8n workflows funcionando
- [ ] Prometheus coletando métricas
- [ ] Documentação atualizada

---

## 📞 Próximos Passos

1. **Executar agora:** `scripts/setup_unified.sh`
2. **Validar:** Todos os serviços rodando
3. **Testar:** Workflow end-to-end
4. **Documentar:** Atualizar README.md
