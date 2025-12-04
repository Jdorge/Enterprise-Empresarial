# 🔧 Plano de Correção: Nexus Enterprise

**Data de criação:** 2025-11-28  
**Prioridade:** CRÍTICA  
**Prazo:** 2 semanas  
**Responsável:** DevOps Team

---

## 📋 Checklist de Correções

### ⚠️ CRÍTICAS (Implementar imediatamente)

- [ ] **CRIT-01**: Remover credenciais hardcoded do Docker Compose
- [ ] **CRIT-02**: Corrigir imports quebrados (`packages.nexus-core` → `nexus_core`)
- [ ] **CRIT-03**: Criar arquivo `.env.example` completo
- [ ] **CRIT-05**: Implementar gestão segura de segredos

### 🔴 ALTA PRIORIDADE (Esta semana)

- [ ] **CRIT-04**: Implementar activities faltantes do Temporal
- [ ] **CRIT-06**: Adicionar suite de testes (pytest)
- [ ] **CRIT-10**: Implementar guardrails de IA
- [ ] **BUG-01**: Corrigir API da Anthropic no LLMFactory
- [ ] **BUG-02**: Corrigir API do Gemini no LLMFactory

### 🟡 MÉDIA PRIORIDADE (Próximas 2 semanas)

- [ ] **CRIT-07**: Documentar APIs com OpenAPI/Swagger
- [ ] **CRIT-08**: Adicionar `pyproject.toml` com Poetry
- [ ] **CRIT-09**: Expor métricas customizadas no Prometheus
- [ ] Criar dashboards do Grafana
- [ ] Configurar CI/CD (GitHub Actions)

---

## 🚀 Fase 1: Correções de Segurança (Dias 1-3)

### 1.1 Criar `.env.example`

```bash
# Localização: nexus-enterprise-corrected/.env.example

# ==============================================
# NEXUS ENTERPRISE - ENVIRONMENT VARIABLES
# ==============================================

# ============ Database ============
POSTGRES_USER=nexus
POSTGRES_PASSWORD=
POSTGRES_DB=nexus
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ============ Temporal ============
TEMPORAL_HOST=temporal
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=default

# ============ Qdrant Vector DB ============
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=

# ============ n8n Automation ============
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=
N8N_WEBHOOK_URL=http://n8n:5678/webhook

# ============ Monitoring ============
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=
PROMETHEUS_PORT=9090

# ============ LLM API Keys ============
# OpenAI
OPENAI_API_KEY=sk-
OPENAI_ORG_ID=

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-

# Google Gemini
GEMINI_API_KEY=

# OpenRouter (fallback)
OPENROUTER_API_KEY=

# ============ Security ============
# Secret for encrypting sensitive data
ENCRYPTION_KEY=
# JWT secret for API authentication
JWT_SECRET=

# ============ Application ============
LOG_LEVEL=INFO
ENVIRONMENT=development
MAX_WORKERS=4

# ============ Rate Limiting ============
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# ============ Cost Control ============
MAX_DAILY_COST_USD=100
ALERT_THRESHOLD_USD=50
```

### 1.2 Atualizar `docker-compose.yml`

**Arquivo:** `infrastructure/docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-nexus}
      POSTGRES_USER: ${POSTGRES_USER:-nexus}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD não definido}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-nexus}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - backend

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "${QDRANT_PORT:-6333}:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY:-}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    networks:
      - backend

  temporal:
    image: temporalio/auto-setup:1.25
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - DB=postgresql
      - POSTGRES_USER=${POSTGRES_USER:-nexus}
      - POSTGRES_PWD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD não definido}
      - POSTGRES_SEEDS=postgres:5432
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development.yaml
    ports:
      - "${TEMPORAL_PORT:-7233}:7233"
      - "7234:7234"  # UI
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "tctl", "--address", "temporal:7233", "cluster", "health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend
      - frontend

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD:?N8N_PASSWORD não definido}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB:-nexus}
      - DB_POSTGRESDB_USER=${POSTGRES_USER:-nexus}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - frontend
      - backend

  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    depends_on:
      - temporal
      - qdrant
    networks:
      - frontend
      - backend

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:?GRAFANA_PASSWORD não definido}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - frontend

  # API Gateway (a ser implementado)
  nexus-gateway:
    build:
      context: ../apps/nexus-gateway
      dockerfile: Dockerfile
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - TEMPORAL_HOST=${TEMPORAL_HOST:-temporal}
      - TEMPORAL_PORT=${TEMPORAL_PORT:-7233}
      - JWT_SECRET=${JWT_SECRET:?JWT_SECRET não definido}
    ports:
      - "8000:8000"
    depends_on:
      temporal:
        condition: service_healthy
    networks:
      - frontend
      - backend

volumes:
  postgres_data:
  qdrant_data:
  prometheus_data:
  grafana_data:
  n8n_data:

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

### 1.3 Criar script de validação de secrets

**Arquivo:** `scripts/validate_env.py`

```python
#!/usr/bin/env python3
"""Valida se todas as variáveis de ambiente obrigatórias estão definidas."""

import os
import sys
from typing import List, Tuple

REQUIRED_VARS = [
    "POSTGRES_PASSWORD",
    "N8N_BASIC_AUTH_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "JWT_SECRET",
    "ENCRYPTION_KEY",
]

OPTIONAL_VARS = [
    "QDRANT_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENAI_ORG_ID",
]


def check_env() -> Tuple[List[str], List[str]]:
    """Verifica variáveis de ambiente."""
    missing = []
    empty = []
    
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if value is None:
            missing.append(var)
        elif not value.strip():
            empty.append(var)
    
    return missing, empty


def main():
    print("🔍 Validando variáveis de ambiente...\n")
    
    missing, empty = check_env()
    
    if missing:
        print("❌ ERRO: Variáveis obrigatórias não definidas:")
        for var in missing:
            print(f"   - {var}")
        print()
    
    if empty:
        print("⚠️  AVISO: Variáveis definidas mas vazias:")
        for var in empty:
            print(f"   - {var}")
        print()
    
    # Verifica opcionais
    optional_missing = [v for v in OPTIONAL_VARS if not os.getenv(v)]
    if optional_missing:
        print("ℹ️  Variáveis opcionais não definidas:")
        for var in optional_missing:
            print(f"   - {var}")
        print()
    
    if missing or empty:
        print("\n💡 Dica: Copie .env.example para .env e preencha os valores")
        print("   cp .env.example .env")
        sys.exit(1)
    else:
        print("✅ Todas as variáveis obrigatórias estão definidas!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 🔧 Fase 2: Correção de Bugs de Código (Dias 4-7)

### 2.1 Corrigir imports quebrados

**Problema:** Imports usam hífens (packages.nexus-core) em vez de underscores.

**Solução:** Renomear diretórios e corrigir imports.

```bash
# Script de renomeação
cd nexus-enterprise-corrected/packages

# Renomear diretórios
mv nexus-core nexus_core
mv nexus-llm-factory nexus_llm_factory

# Criar __init__.py se não existir
touch nexus_core/__init__.py
touch nexus_llm_factory/__init__.py
```

**Atualizar imports:**

```python
# Antes (ERRADO):
from packages.nexus-core.src.shared.models import ProposalRequest

# Depois (CORRETO):
from nexus_core.shared.models import ProposalRequest
```

### 2.2 Corrigir API da Anthropic

**Arquivo:** `packages/nexus_llm_factory/src/factory.py`

```python
async def _call_anthropic(
    self,
    config: ModelConfig,
    messages: List[Dict[str, Any]],
    response_model: Optional[Type[BaseModel]],
    temp: float,
) -> Dict[str, Any]:
    client = self.clients["anthropic"]
    
    # ✅ CORRETO: Usar messages.create
    response = await client.messages.create(
        model=config.name,
        max_tokens=config.max_tokens,
        messages=messages,
        temperature=temp,
    )
    
    # Calcular custo
    usage = {
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
    }
    
    # Extrair conteúdo
    content = response.content[0].text
    
    return {
        "content": content,
        "usage": usage,
        "cost": self._calculate_cost(config, usage),
    }
```

### 2.3 Corrigir API do Gemini

```python
async def _call_gemini(
    self,
    config: ModelConfig,
    messages: List[Dict[str, Any]],
    response_model: Optional[Type[BaseModel]],
    temp: float,
) -> Dict[str, Any]:
    import google.generativeai as genai
    
    # Configurar modelo
    model = genai.GenerativeModel(config.name)
    
    # Converter formato de mensagens OpenAI para Gemini
    prompt = self._convert_messages_to_gemini_format(messages)
    
    # Gerar resposta
    response = await model.generate_content_async(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=temp,
            max_output_tokens=config.max_tokens,
        ),
    )
    
    # Calcular tokens (Gemini usa count_tokens)
    usage = {
        "prompt_tokens": model.count_tokens(prompt).total_tokens,
        "completion_tokens": len(response.text.split()),  # Aproximação
    }
    
    return {
        "content": response.text,
        "usage": usage,
        "cost": self._calculate_cost(config, usage),
    }

def _convert_messages_to_gemini_format(self, messages: List[Dict[str, Any]]) -> str:
    """Converte mensagens do formato OpenAI para Gemini."""
    parts = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            parts.append(f"System: {content}")
        elif role == "user":
            parts.append(f"User: {content}")
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
    return "\n\n".join(parts)
```

---

## 🧪 Fase 3: Implementar Testes (Dias 8-10)

### 3.1 Estrutura de testes

```
nexus-enterprise-corrected/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Fixtures do pytest
│   ├── unit/
│   │   ├── test_llm_factory.py
│   │   ├── test_models.py
│   │   └── test_guardrails.py
│   ├── integration/
│   │   ├── test_temporal_workflow.py
│   │   └── test_qdrant_integration.py
│   └── e2e/
│       └── test_commercial_workflow_e2e.py
```

### 3.2 Testes do LLMFactory

**Arquivo:** `tests/unit/test_llm_factory.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from nexus_llm_factory.factory import LLMFactory, ModelConfig
from pydantic import BaseModel, SecretStr


class MockSettings:
    openai_api_key = SecretStr("sk-test-openai")
    anthropic_api_key = SecretStr("sk-ant-test")
    gemini_api_key = SecretStr("test-gemini")


class TestResponse(BaseModel):
    answer: str
    confidence: float


@pytest.fixture
def llm_factory():
    with patch("nexus_llm_factory.factory.AsyncOpenAI"), \
         patch("nexus_llm_factory.factory.AsyncAnthropic"), \
         patch("nexus_llm_factory.factory.genai"):
        factory = LLMFactory(settings=MockSettings())
        return factory


@pytest.mark.asyncio
async def test_fallback_on_openai_failure(llm_factory):
    """Testa fallback quando OpenAI falha."""
    # Mock: OpenAI falha, Anthropic funciona
    llm_factory.clients["openai"].chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )
    
    anthropic_response = MagicMock()
    anthropic_response.content = [MagicMock(text="Resposta do Claude")]
    anthropic_response.usage.input_tokens = 10
    anthropic_response.usage.output_tokens = 20
    
    llm_factory.clients["anthropic"].messages.create = AsyncMock(
        return_value=anthropic_response
    )
    
    messages = [{"role": "user", "content": "Olá"}]
    result = await llm_factory.generate(messages)
    
    assert result == "Resposta do Claude"
    assert llm_factory.call_counts["claude-3-5-sonnet-20241022"] == 1


@pytest.mark.asyncio
async def test_cost_tracking(llm_factory):
    """Testa rastreamento de custo."""
    openai_response = MagicMock()
    openai_response.choices = [MagicMock(message=MagicMock(content="Test"))]
    openai_response.usage.prompt_tokens = 100
    openai_response.usage.completion_tokens = 50
    
    llm_factory.clients["openai"].chat.completions.create = AsyncMock(
        return_value=openai_response
    )
    
    messages = [{"role": "user", "content": "Test"}]
    await llm_factory.generate(messages)
    
    metrics = llm_factory.get_metrics()
    assert metrics["total_cost_usd"] > 0
    assert metrics["calls_by_model"]["gpt-4o"] == 1


@pytest.mark.asyncio
async def test_prefer_cheap_model(llm_factory):
    """Testa se prefer_cheap=True prioriza modelos baratos."""
    gemini_response = MagicMock()
    gemini_response.text = "Gemini response"
    
    llm_factory.clients["google"].generate_content_async = AsyncMock(
        return_value=gemini_response
    )
    
    messages = [{"role": "user", "content": "Test"}]
    await llm_factory.generate(messages, prefer_cheap=True)
    
    # Gemini deve ser chamado primeiro por ser o mais barato
    assert llm_factory.call_counts["gemini-2.0-flash"] == 1
```

### 3.3 Testes do Workflow Temporal

**Arquivo:** `tests/integration/test_temporal_workflow.py`

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from apps.nexus_engine.workflows.commercial_agent import CommercialProposalWorkflow
from nexus_core.shared.models import ProposalRequest


@pytest.mark.asyncio
async def test_workflow_success():
    """Testa execução bem-sucedida do workflow."""
    async with await WorkflowEnvironment.start_local() as env:
        # Criar worker de teste
        async with Worker(
            env.client,
            task_queue="commercial-agents",
            workflows=[CommercialProposalWorkflow],
            activities=[],  # Mock activities
        ):
            request = ProposalRequest(
                request_id="test-001",
                user_id="user-123",
                customer_name="Test Corp",
                details="Test proposal",
            )
            
            result = await env.client.execute_workflow(
                CommercialProposalWorkflow.run,
                request,
                id="test-workflow-001",
                task_queue="commercial-agents",
            )
            
            assert result.request_id == "test-001"
            assert result.confidence_score >= 0.90


@pytest.mark.asyncio
async def test_workflow_low_verification_score():
    """Testa falha quando score de verificação é baixo."""
    # Implementar teste que força score < 0.90
    pass
```

### 3.4 Configuração do pytest

**Arquivo:** `tests/conftest.py`

```python
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Configura variáveis de ambiente para testes."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
```

**Arquivo:** `pyproject.toml` (configuração do pytest)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=apps",
    "--cov=packages",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--verbose",
]
asyncio_mode = "auto"
```

---

## 🛡️ Fase 4: Implementar Guardrails de IA (Dias 11-14)

### 4.1 Estrutura do pacote

```
packages/nexus_guardrails/
├── __init__.py
├── src/
│   ├── __init__.py
│   ├── validators.py        # Validadores principais
│   ├── pii_detector.py      # Detecção de PII
│   ├── content_filter.py    # Filtro de conteúdo
│   └── rate_limiter.py      # Rate limiting
└── tests/
    └── test_guardrails.py
```

### 4.2 Detector de PII

**Arquivo:** `packages/nexus_guardrails/src/pii_detector.py`

```python
from typing import List, Dict, Any
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PIIDetector:
    """Detecta e anonimiza informações pessoais (PII)."""
    
    # Entidades suportadas em PT-BR
    SUPPORTED_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "BR_CPF",
        "BR_CNPJ",
        "LOCATION",
        "DATE_TIME",
        "IP_ADDRESS",
    ]
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def detect_pii(self, text: str, language: str = "pt") -> List[Dict[str, Any]]:
        """Detecta PII no texto."""
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.SUPPORTED_ENTITIES,
        )
        
        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end],
            }
            for result in results
        ]
    
    def anonymize(
        self, 
        text: str, 
        language: str = "pt",
        operator: str = "mask"
    ) -> str:
        """Anonimiza PII detectado."""
        # Detecta
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.SUPPORTED_ENTITIES,
        )
        
        if not results:
            return text
        
        # Anonimiza
        operators = {entity: OperatorConfig(operator) for entity in self.SUPPORTED_ENTITIES}
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators,
        )
        
        return anonymized.text
    
    def has_pii(self, text: str, threshold: float = 0.5) -> bool:
        """Verifica se há PII com confiança acima do threshold."""
        results = self.detect_pii(text)
        return any(r["score"] >= threshold for r in results)
```

### 4.3 Filtro de Conteúdo

```python
from typing import List, Tuple
import re


class ContentFilter:
    """Filtra conteúdo inapropriado."""
    
    # Palavras proibidas (exemplo simplificado)
    BLOCKED_PATTERNS = [
        r'\b(senha|password)\s*[:=]\s*\S+',
        r'\b(token|api[-_]?key)\s*[:=]\s*\S+',
        r'\bselect\s+.*\s+from\s+',  # SQL injection
        r'<script.*?>.*?</script>',  # XSS
    ]
    
    INAPPROPRIATE_WORDS = [
        # Adicionar lista de palavras inadequadas
    ]
    
    def __init__(self):
        self.blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]
    
    def validate_input(self, text: str) -> Tuple[bool, List[str]]:
        """Valida entrada do usuário."""
        violations = []
        
        # Verifica patterns bloqueados
        for regex in self.blocked_regex:
            if regex.search(text):
                violations.append(f"Pattern proibido detectado: {regex.pattern}")
        
        # Verifica comprimento
        if len(text) > 10000:
            violations.append("Texto muito longo (máx: 10000 caracteres)")
        
        # Verifica palavras inadequadas
        text_lower = text.lower()
        for word in self.INAPPROPRIATE_WORDS:
            if word in text_lower:
                violations.append(f"Conteúdo inapropriado detectado")
                break
        
        return len(violations) == 0, violations
    
    def validate_output(self, text: str) -> Tuple[bool, List[str]]:
        """Valida saída do LLM."""
        violations = []
        
        # Verifica se há credenciais vazadas
        for regex in self.blocked_regex:
            if regex.search(text):
                violations.append("Possível vazamento de credenciais na resposta")
        
        return len(violations) == 0, violations
```

### 4.4 Rate Limiter

```python
import time
from collections import defaultdict
from typing import Dict


class RateLimiter:
    """Controla taxa de requisições por usuário."""
    
    def __init__(self, max_per_minute: int = 100, max_burst: int = 20):
        self.max_per_minute = max_per_minute
        self.max_burst = max_burst
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        """Verifica se usuário pode fazer requisição."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove requisições antigas
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if ts > minute_ago
        ]
        
        # Verifica limite
        count = len(self.requests[user_id])
        
        if count >= self.max_per_minute:
            return False
        
        # Verifica burst (últimos 10s)
        burst_window = now - 10
        burst_count = sum(1 for ts in self.requests[user_id] if ts > burst_window)
        
        if burst_count >= self.max_burst:
            return False
        
        # Registra requisição
        self.requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """Retorna número de requisições restantes."""
        now = time.time()
        minute_ago = now - 60
        
        recent = [ts for ts in self.requests[user_id] if ts > minute_ago]
        return max(0, self.max_per_minute - len(recent))
```

### 4.5 Integração com LLMFactory

```python
# Atualizar LLMFactory para usar guardrails

from nexus_guardrails.validators import GuardrailValidator

class LLMFactory:
    def __init__(self, settings: Any) -> None:
        # ... código existente ...
        self.guardrails = GuardrailValidator()
    
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        user_id: str,  # Adicionar user_id
        **kwargs
    ) -> Any:
        # 1. Validar input
        user_message = messages[-1]["content"]
        is_valid, cleaned_text = self.guardrails.validate_input(user_message)
        if not is_valid:
            raise ValueError(f"Input inválido: {cleaned_text}")
        
        # 2. Verificar rate limit
        if not self.guardrails.rate_limiter.is_allowed(user_id):
            raise ValueError("Rate limit excedido")
        
        # 3. Detectar PII
        if self.guardrails.pii_detector.has_pii(user_message):
            # Anonimizar
            cleaned_text = self.guardrails.pii_detector.anonymize(user_message)
            messages[-1]["content"] = cleaned_text
        
        # 4. Gerar resposta (código existente)
        result = await self._generate_with_fallback(messages, **kwargs)
        
        # 5. Validar output
        is_valid_output, _ = self.guardrails.content_filter.validate_output(result)
        if not is_valid_output:
            raise ValueError("Output do LLM contém conteúdo inadequado")
        
        return result
```

---

## 📊 Fase 5: Métricas e Observabilidade (Dias 15-17)

### 5.1 Expor métricas do LLMFactory

```python
from prometheus_client import Counter, Histogram, Gauge

# Definir métricas
llm_calls_total = Counter(
    'llm_calls_total',
    'Total de chamadas LLM',
    ['model', 'provider', 'status']
)

llm_cost_usd_total = Counter(
    'llm_cost_usd_total',
    'Custo total em USD'
)

llm_latency_seconds = Histogram(
    'llm_latency_seconds',
    'Latência das chamadas LLM',
    ['model']
)

llm_tokens_used = Counter(
    'llm_tokens_used_total',
    'Tokens usados',
    ['model', 'type']  # type: input/output
)

class LLMFactory:
    async def generate(self, ...):
        start_time = time.time()
        
        try:
            result = await self._generate_with_fallback(...)
            
            # Registrar métricas
            llm_calls_total.labels(
                model=config.name,
                provider=config.provider,
                status='success'
            ).inc()
            
            llm_cost_usd_total.inc(result["cost"])
            
            llm_tokens_used.labels(
                model=config.name,
                type='input'
            ).inc(usage.prompt_tokens)
            
            llm_tokens_used.labels(
                model=config.name,
                type='output'
            ).inc(usage.completion_tokens)
            
        except Exception as e:
            llm_calls_total.labels(
                model='unknown',
                provider='unknown',
                status='error'
            ).inc()
            raise
        finally:
            latency = time.time() - start_time
            llm_latency_seconds.labels(model=config.name).observe(latency)
```

### 5.2 Criar dashboard do Grafana

**Arquivo:** `infrastructure/monitoring/grafana/dashboards/llm-metrics.json`

```json
{
  "dashboard": {
    "title": "LLM Metrics Dashboard",
    "panels": [
      {
        "title": "Total Calls by Model",
        "targets": [
          {
            "expr": "sum(rate(llm_calls_total[5m])) by (model)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Cost Over Time",
        "targets": [
          {
            "expr": "rate(llm_cost_usd_total[1h]) * 720"
          }
        ],
        "type": "graph"
      },
      {
        "title": "P95 Latency by Model",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(llm_latency_seconds_bucket[5m])) by (model, le))"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

---

## 🚀 Scripts de Automação

### Script de setup completo

**Arquivo:** `scripts/setup.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Nexus Enterprise - Setup Automático"
echo "========================================"

# 1. Validar dependências
echo "📦 Verificando dependências..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não instalado"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 não instalado"; exit 1; }

# 2. Criar .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando .env a partir do .env.example..."
    cp .env.example .env
    echo "⚠️  ATENÇÃO: Preencha as variáveis em .env antes de continuar"
    exit 0
fi

# 3. Validar .env
echo "🔍 Validando variáveis de ambiente..."
python3 scripts/validate_env.py

# 4. Instalar dependências Python
echo "📦 Instalando dependências Python..."
poetry install

# 5. Subir infraestrutura
echo "🐳 Iniciando containers Docker..."
docker-compose -f infrastructure/docker-compose.yml up -d

# 6. Aguardar serviços ficarem saudáveis
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# 7. Executar testes
echo "🧪 Executando testes..."
poetry run pytest

echo ""
echo "✅ Setup concluído com sucesso!"
echo ""
echo "📊 Serviços disponíveis:"
echo "   - Temporal UI: http://localhost:7234"
echo "   - Grafana: http://localhost:3000 (admin/[senha do .env])"
echo "   - Prometheus: http://localhost:9090"
echo "   - n8n: http://localhost:5678"
echo ""
echo "🚀 Para iniciar o worker:"
echo "   poetry run python apps/nexus-engine/src/main.py"
```

---

## ✅ Checklist Final

Após implementar todas as correções, validar:

- [ ] Todos os testes passando (pytest)
- [ ] Coverage > 80%
- [ ] Nenhuma credencial hardcoded
- [ ] Docker Compose sobe sem erros
- [ ] Métricas sendo coletadas no Prometheus
- [ ] Dashboards do Grafana funcionando
- [ ] Workflow Temporal executa end-to-end
- [ ] Guardrails bloqueando inputs inválidos
- [ ] Rate limiting funcionando
- [ ] CI/CD configurado

---

**Próximo passo:** Executar `scripts/setup.sh` e validar o ambiente completo.
