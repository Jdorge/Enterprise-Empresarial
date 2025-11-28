"""Workflow durável para geração de propostas comerciais usando Temporal."""
from __future__ import annotations

import logging
from datetime import timedelta
from temporalio import workflow
from temporalio.exceptions import ApplicationError

# Imports dos modelos (ajustado para novo caminho)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nexus_core.src.shared.models import ProposalRequest, ProposalResult, ApprovalSignal

logger = logging.getLogger(__name__)


@workflow.defn(name="commercial_proposal_workflow")
class CommercialProposalWorkflow:
    """
    Workflow durável para geração de propostas comerciais.
    
    Fluxo completo:
    1. Recupera contexto (RAG via Qdrant)
    2. Gera proposta comercial com LLM
    3. Verifica acurácia (Chain-of-Verification)
    4. Solicita aprovação humana se valor > threshold
    5. Armazena proposta no Qdrant
    """
    
    def __init__(self) -> None:
        self._human_approved: bool = False
        self._verification_score: float = 0.0
        self._proposal_value: float = 0.0
    
    @workflow.run
    async def run(self, request: ProposalRequest) -> ProposalResult:
        logger.info(
            f"🚀 Iniciando workflow para {request.customer_name} (ID: {request.request_id})"
        )
        
        # ETAPA 1: Recupera contexto via RAG
        context = await workflow.execute_activity(
            "retrieve_company_context",
            request,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=workflow.RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
                non_retryable_error_types=["ValidationError"],
            ),
        )
        
        # ETAPA 2: Gera proposta comercial
        proposal = await workflow.execute_activity(
            "generate_commercial_proposal",
            {"request": request, "context": context},
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
                backoff_coefficient=2.0,
                non_retryable_error_types=["ValidationError", "InvalidAPIKeyError"],
            ),
            heartbeat_timeout=timedelta(seconds=30),
        )
        
        self._proposal_value = proposal.get("total_amount", 0.0)
        
        # ETAPA 3: Verifica acurácia (Chain-of-Verification)
        self._verification_score = await workflow.execute_activity(
            "verify_proposal_accuracy",
            proposal,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )
        
        # Se nota insuficiente, aborta
        if self._verification_score < 0.90:
            raise ApplicationError(
                f"❌ Proposta falhou verificação (score: {self._verification_score:.2f}). "
                "Necessário refinamento."
            )
        
        # ETAPA 4: Aprovação humana para propostas de alto valor
        approval_threshold = request.max_value or 10000.0
        
        if self._proposal_value > approval_threshold:
            logger.info(
                f"⏸️ Proposta de ${self._proposal_value:.2f} requer aprovação humana"
            )
            
            # Envia notificação via n8n
            await workflow.execute_activity(
                "send_approval_notification",
                {
                    "proposal_id": request.request_id,
                    "customer_name": request.customer_name,
                    "amount": self._proposal_value,
                    "manager_email": "manager@company.com",
                },
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # Aguarda sinal de aprovação (até 48h)
            try:
                await workflow.wait_condition(
                    lambda: self._human_approved,
                    timeout=timedelta(hours=48),
                )
            except TimeoutError:
                raise ApplicationError(
                    f"⏱️ Timeout de aprovação humana (48h). Proposta cancelada."
                )
            
            if not self._human_approved:
                raise ApplicationError("❌ Proposta rejeitada por aprovador")
        
        # ETAPA 5: Armazena proposta no Qdrant
        storage_id = await workflow.execute_activity(
            "store_proposal_in_qdrant",
            proposal,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=workflow.RetryPolicy(
                maximum_attempts=5,
                initial_interval=timedelta(milliseconds=500),
            ),
        )
        
        logger.info(
            f"✅ Proposta armazenada (Qdrant ID: {storage_id}). "
            f"Score de verificação: {self._verification_score * 100:.1f}%"
        )
        
        return ProposalResult(
            request_id=request.request_id,
            summary=proposal["summary"],
            full_proposal=proposal["full_text"],
            confidence_score=self._verification_score,
            verification_steps=proposal.get("verification_steps", []),
            sources=proposal.get("sources", []),
            total_amount=self._proposal_value,
        )
    
    # === SIGNALS ===
    
    @workflow.signal
    async def approve(self, signal: ApprovalSignal) -> None:
        """Sinal enviado pelo manager para aprovar a proposta."""
        logger.info(f"✅ Aprovação recebida de {signal.approver_id}")
        self._human_approved = signal.approved
    
    @workflow.signal
    async def reject(self, reason: str) -> None:
        """Sinal para rejeitar a proposta."""
        logger.warning(f"❌ Proposta rejeitada: {reason}")
        self._human_approved = False
        raise ApplicationError(f"Proposta rejeitada: {reason}")
    
    # === QUERIES ===
    
    @workflow.query
    def get_verification_score(self) -> float:
        """Consulta nota de verificação."""
        return self._verification_score
    
    @workflow.query
    def get_proposal_value(self) -> float:
        """Consulta valor da proposta."""
        return self._proposal_value
    
    @workflow.query
    def is_approved(self) -> bool:
        """Consulta status de aprovação."""
        return self._human_approved
