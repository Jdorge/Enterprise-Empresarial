"""Activities para operações com Qdrant (vector database)."""
from __future__ import annotations

import logging
from typing import Dict, Any, List
from uuid import uuid4
from temporalio import activity
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nexus_core.src.shared.config import Settings
from packages.nexus_core.src.shared.models import ProposalRequest

logger = logging.getLogger(__name__)


class VectorActivities:
    """Activities para operações vetoriais com Qdrant."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.qdrant = QdrantClient(
            url=settings.get_qdrant_url(),
            api_key=settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None,
        )
        self.openrouter_key = settings.get_openrouter_key()
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Garante que coleção existe."""
        try:
            self.qdrant.get_collection("agent_memory")
        except:
            # Cria coleção se não existe
            self.qdrant.create_collection(
                collection_name="agent_memory",
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            activity.logger.info("✅ Coleção 'agent_memory' criada")
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenRouter (modelo de embedding via text-embedding-3-small)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "openai/text-embedding-3-small",
                    "input": text,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    
    @activity.defn(name="retrieve_company_context")
    async def retrieve_company_context(self, request: ProposalRequest) -> str:
        """
        Recupera contexto relevante do Qdrant via RAG.
        
        Args:
            request: Solicitação de proposta
            
        Returns:
            Contexto textual relevante
        """
        activity.logger.info(f"🔍 Buscando contexto para {request.customer_name}")
        
        # Cria query
        query_text = f"{request.customer_name} {request.details or ''}"
        
        # Gera embedding
        query_vector = await self._get_embedding(query_text)
        
        # Busca similares
        results = self.qdrant.search(
            collection_name="agent_memory",
            query_vector=query_vector,
            limit=5,
        )
        
        if results:
            # Concatena contexto dos resultados
            context = "\n\n".join([
                result.payload.get("summary", "")
                for result in results
            ])
            activity.logger.info(f"✅ Encontrados {len(results)} contextos relevantes")
            return context
        else:
            activity.logger.warning("⚠️ Nenhum contexto encontrado, usando genérico")
            return "Empresa referência no mercado com soluções inovadoras."
    
    @activity.defn(name="store_proposal_in_qdrant")
    async def store_proposal_in_qdrant(self, proposal: Dict[str, Any]) -> str:
        """
        Armazena proposta no Qdrant para memória futura.
        
        Args:
            proposal: Dados da proposta
            
        Returns:
            ID do ponto armazenado
        """
        activity.logger.info("💾 Armazenando proposta no Qdrant")
        
        # Prepara texto para embedding
        text = f"{proposal['summary']}\n{proposal['full_text'][:500]}"
        
        # Gera embedding REAL
        vector = await self._get_embedding(text)
        
        # ID único
        point_id = str(uuid4())
        
        # Armazena
        self.qdrant.upsert(
            collection_name="agent_memory",
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "summary": proposal["summary"],
                    "full_text": proposal["full_text"],
                    "total_amount": proposal.get("total_amount", 0.0),
                    "sources": proposal.get("sources", []),
                }
            )]
        )
        
        activity.logger.info(f"✅ Proposta armazenada com ID: {point_id}")
        return point_id
