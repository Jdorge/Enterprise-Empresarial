"""Temporal Worker - Ponto de entrada para execução de workflows e activities."""
from __future__ import annotations

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.nexus_core.src.shared.config import Settings
from workflows.commercial_agent import CommercialProposalWorkflow
from activities.llm_activities import LLMActivities
from activities.vector_activities import VectorActivities
from activities.n8n_activities import N8NActivities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Inicializa e executa o Temporal Worker."""
    
    # Carrega configurações
    logger.info("📦 Carregando configurações...")
    settings = Settings()
    
    # Conecta ao Temporal
    logger.info(f"🔌 Conectando ao Temporal em {settings.temporal_host}...")
    client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )
    
    # Inicializa activities
    logger.info("🛠️ Inicializando activities...")
    llm_activities = LLMActivities(settings)
    vector_activities = VectorActivities(settings)
    n8n_activities = N8NActivities(settings)
    
    # Cria worker
    worker = Worker(
        client,
        task_queue="commercial-agents",
        workflows=[CommercialProposalWorkflow],
        activities=[
            llm_activities.generate_commercial_proposal,
            llm_activities.verify_proposal_accuracy,
            vector_activities.retrieve_company_context,
            vector_activities.store_proposal_in_qdrant,
            n8n_activities.send_approval_notification,
        ],
        max_concurrent_activities=settings.max_workers,
    )
    
    logger.info("✅ Nexus Engine inicializado com sucesso!")
    logger.info(f"📊 Workers: {settings.max_workers}")
    logger.info(f"🎯 Task Queue: commercial-agents")
    logger.info("")
    logger.info("🚀 Worker rodando... (Ctrl+C para parar)")
    
    # Executa até interrupção
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Worker encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)
