"""
BaseAgent
=========

Este módulo define a classe abstrata `BaseAgent`, que estabelece um
contrato comum para todos os agentes especializados do ecossistema.
Os agentes responsáveis por domínios (Comercial, Varejo, Industrial,
Agência) devem herdar desta classe e implementar o método
`handle()`, encapsulando a lógica de negócio específica.

Principais responsabilidades do `BaseAgent`:

- Prover um *entry point* (`__call__`) único para execução,
  registrando tempo de processamento, tokens e custo estimado.
- Encapsular tratamento de exceções e tentativas de nova execução
  através de um decorador de *retry*, evitando que erros internos
  derrubem o sistema.
- Exportar métricas (latência, número de tokens, custo) para uma
  infraestrutura de monitoramento (Prometheus, Grafana).
- Registrar logs estruturados em um webhook (/log‑workflow) para
  rastreabilidade e auditoria de cada execução.

Os agentes especializados devem retornar um objeto `AgentResult`
contendo status, mensagem, payload de dados e métricas. Isso
garante uniformidade nas respostas e facilita a orquestração pelo
Mega Agente e pelo n8n.

Nota: Este código é apenas um exemplo; adapte para integrar com
suas bibliotecas de observabilidade e back‑end.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time
import uuid

# Exemplo de importações de utilitários. Substitua pelos seus wrappers.
try:
    from shared.observability import metrics as obs_metrics
    from shared.observability import logging as obs_logging
    from shared.utils.retry import retry
except Exception:
    # Fallback simples se utilitários não estiverem presentes
    class DummyMetrics:
        def counter(self, *_args, **_kwargs):
            class _Counter:
                def inc(self, *_args, **_kwargs):
                    pass
            return _Counter()

        def histogram(self, *_args, **_kwargs):
            class _Histogram:
                def observe(self, *_args, **_kwargs):
                    pass
            return _Histogram()

    class DummyLogger:
        def __init__(self, name: str) -> None:
            self.name = name

        def exception(self, *args, **kwargs):
            pass

        def info(self, *args, **kwargs):
            pass

    def retry(max_attempts: int = 1, backoff_seconds: float = 0.0):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    obs_metrics = DummyMetrics()

    def get_logger(name: str) -> DummyLogger:
        return DummyLogger(name)
    obs_logging = type("obs_logging", (), {"get_logger": staticmethod(get_logger)})


@dataclass
class AgentMetrics:
    """Armazena métricas de uma execução de agente.

    Attributes:
        agent_name: Nome do agente executado.
        status: Status da execução (success | error).
        latency_ms: Latência total em milissegundos.
        tokens_prompt: Número de tokens de prompt consumidos.
        tokens_completion: Número de tokens de completion consumidos.
        cost_usd_estimated: Custo estimado em USD da chamada ao modelo.
        business_success: Indicador se houve sucesso de negócio (opcional).
        human_override: Flag indicando se foi necessária intervenção humana.
    """

    agent_name: str
    status: str
    latency_ms: int
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd_estimated: float = 0.0
    business_success: Optional[bool] = None
    human_override: Optional[bool] = None

    def to_labels(self) -> Dict[str, str]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
        }


@dataclass
class AgentResult:
    """Encapsula o resultado de uma execução de agente.

    Attributes:
        status: Status final da execução (success | error).
        message: Mensagem humanizada ou informativa.
        data: Payload estruturado (dict) com dados de saída (CSV,
            valores, links, etc.).
        metrics: Métricas de execução correspondentes.
        execution_id: Identificador único da execução.
    """

    status: str
    message: str
    data: Dict[str, Any]
    metrics: AgentMetrics
    execution_id: str


class BaseAgent(ABC):
    """Classe abstrata que define a interface e comportamento base.

    Para implementar um agente, herde de `BaseAgent` e implemente
    `handle()`. Não modifique o comportamento de `__call__`, a menos
    que saiba o que está fazendo; ele é responsável por medir
    latência, registrar logs e exportar métricas.
    """

    name: str = "base"

    def __init__(
        self,
        mcp_client,
        csv_service,
        workflow_logger,
        metrics_client: Optional[Any] = None,
        logger: Optional[Any] = None,
    ) -> None:
        self.mcp = mcp_client
        self.csv_service = csv_service
        self.workflow_logger = workflow_logger
        self.metrics_client = metrics_client or obs_metrics
        self.logger = logger or obs_logging.get_logger(self.__class__.__name__)

    def __call__(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        context = context or {}
        execution_id = context.get("execution_id") or str(uuid.uuid4())
        start_time = time.time()

        tokens_prompt = 0
        tokens_completion = 0
        cost_usd = 0.0

        try:
            result = self._safe_handle(
                query=query, context=context, execution_id=execution_id
            )
            status = result.status
            business_success = result.metrics.business_success
            human_override = result.metrics.human_override
            tokens_prompt = result.metrics.tokens_prompt
            tokens_completion = result.metrics.tokens_completion
            cost_usd = result.metrics.cost_usd_estimated
        except Exception as exc:  # noqa: BLE001
            status = "error"
            business_success = None
            human_override = True
            result = AgentResult(
                status="error",
                message=f"Erro interno no agente {self.name}: {exc}",
                data={},
                metrics=AgentMetrics(
                    agent_name=self.name,
                    status="error",
                    latency_ms=0,
                ),
                execution_id=execution_id,
            )
            self.logger.exception(
                "Exceção não tratada no agente", extra={"agent": self.name, "execution_id": execution_id}
            )

        latency_ms = int((time.time() - start_time) * 1000)
        result.metrics.latency_ms = latency_ms
        result.metrics.status = status

        # Exporta métricas
        self._export_metrics(
            metrics=result.metrics,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=cost_usd,
        )

        # Logging para /log-workflow
        self._log_to_workflow_logger(query=query, result=result, context=context)

        return result

    @retry(max_attempts=3, backoff_seconds=0.5)
    def _safe_handle(
        self,
        query: str,
        context: Dict[str, Any],
        execution_id: str,
    ) -> AgentResult:
        return self.handle(query=query, context=context, execution_id=execution_id)

    @abstractmethod
    def handle(
        self,
        query: str,
        context: Dict[str, Any],
        execution_id: str,
    ) -> AgentResult:
        """Implementar a lógica de negócio do agente.

        Deve devolver um `AgentResult` com os campos preenchidos.
        """
        raise NotImplementedError

    def _export_metrics(
        self,
        metrics: AgentMetrics,
        tokens_prompt: int,
        tokens_completion: int,
        cost_usd: float,
    ) -> None:
        labels = metrics.to_labels()
        # Contador de chamadas
        self.metrics_client.counter(
            "agent_requests_total", "Total de requisições atendidas por agente"
        ).inc(labels)
        # Histograma de latência
        self.metrics_client.histogram(
            "agent_latency_ms", "Latência de execução (ms) por agente"
        ).observe(labels, metrics.latency_ms)
        # Contagem de erros
        if metrics.status == "error":
            self.metrics_client.counter(
                "agent_errors_total", "Quantidade de erros por agente"
            ).inc(labels)
        # Histograma de tokens consumidos
        self.metrics_client.histogram(
            "agent_tokens_prompt_total", "Tokens de prompt consumidos"
        ).observe(labels, tokens_prompt)
        self.metrics_client.histogram(
            "agent_tokens_completion_total", "Tokens de completion consumidos"
        ).observe(labels, tokens_completion)
        # Histograma de custo
        self.metrics_client.histogram(
            "agent_cost_usd", "Custo estimado (USD) por execução"
        ).observe(labels, cost_usd)
        # Métrica de sucesso de negócio
        if metrics.business_success is not None:
            self.metrics_client.counter(
                "agent_business_success_total", "Sucesso de negócio por agente"
            ).inc({**labels, "business_success": str(metrics.business_success)})

    def _log_to_workflow_logger(
        self,
        query: str,
        result: AgentResult,
        context: Dict[str, Any],
    ) -> None:
        try:
            payload = {
                "workflow_name": context.get(
                    "workflow_name", f"AGENT_{self.name.capitalize()}"
                ),
                "execution_id": result.execution_id,
                "status": result.status,
                "response_time_ms": result.metrics.latency_ms,
                "agent_name": self.name,
                "input_data": {
                    "raw_query": query,
                    "context": context,
                },
                "output_data": {
                    "summary_message": result.message,
                    "data_preview": list(result.data.keys()),
                },
                "metrics": asdict(result.metrics),
                "environment": context.get("environment", "production"),
            }
            self.workflow_logger.log_workflow(payload)
        except Exception:  # noqa: BLE001
            # Mesmo que falhe o log, não lança exceção; apenas registra internamente
            self.logger.exception(
                "Falha ao registrar workflow", extra={"agent": self.name, "execution_id": result.execution_id}
            )
