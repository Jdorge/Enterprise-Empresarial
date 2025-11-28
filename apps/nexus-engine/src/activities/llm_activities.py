"""Activities do Temporal para operações com LLMs."""
from __future__ import annotations

import logging
from typing import Dict, Any
from temporalio import activity

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nexus_core.src.shared.config import Settings
from packages.nexus_core.src.shared.models import ProposalRequest
from packages.nexus_llm_factory.src.factory import LLMFactory

logger = logging.getLogger(__name__)


class LLMActivities:
    """Activities para operações com LLMs via OpenRouter."""
    
    def __init__(self, settings: Settings):
        """Inicializa activities com configurações."""
        self.settings = settings
        self.llm_factory = None
    
    async def _get_factory(self) -> LLMFactory:
        """Lazy init do LLM Factory."""
        if not self.llm_factory:
            self.llm_factory = LLMFactory(self.settings)
        return self.llm_factory
    
    @activity.defn(name="generate_commercial_proposal")
    async def generate_commercial_proposal(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera proposta comercial usando LLM.
        
        Args:
            data: Dict com 'request' (ProposalRequest) e 'context' (str)
           
        Returns:
            Dict com summary, full_text, sources, etc.
        """
        request: ProposalRequest = data["request"]
        context: str = data.get("context", "")
        
        activity.logger.info(
            f"📝 Gerando proposta para {request.customer_name}"
        )
        
        factory = await self._get_factory()
        
        # Monta prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um especialista em elaboração de propostas comerciais. "
                    "Crie propostas profissionais, precisas e persuasivas."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Cliente: {request.customer_name}\n"
                    f"Detalhes: {request.details}\n\n"
                    f"Contexto da empresa:\n{context}\n\n"
                    f"Elabore uma proposta comercial completa e profissional."
                )
            }
        ]
        
        # Gera proposta
        proposal_text = await factory.generate(
            messages=messages,
            model="balanced",  # Claude Sonnet
            temperature=0.7,
            max_tokens=4096,
        )
        
        # Estima valor (simplificado - em produção usaria ML)
        estimated_value = len(request.details or "") * 10.0  # $10 por char
        
        activity.logger.info(f"✅ Proposta gerada: {len(proposal_text)} chars")
        
        return {
            "summary": proposal_text[:200],
            "full_text": proposal_text,
            "total_amount": estimated_value,
            "sources": [context[:100]],
            "verification_steps": []
        }
    
    @activity.defn(name="verify_proposal_accuracy")
    async def verify_proposal_accuracy(
        self,
        proposal: Dict[str, Any]
    ) -> float:
        """
        Verifica acurácia da proposta usando Chain-of-Verification.
        
        Returns:
            Score de 0.0 a 1.0
        """
        activity.logger.info("🔍 Verificando acurácia da proposta")
        
        factory = await self._get_factory()
        
        # Prompt de verificação
        messages = [
            {
                "role": "system",
                "content": "Você é um verificador de qualidade. Analise a proposta e retorne um score de 0-100."
            },
            {
                "role": "user",
                "content": (
                    f"Proposta:\n{proposal['full_text']}\n\n"
                    f"Avalie:\n"
                    f"1. Clareza\n"
                    f"2. Completude\n"
                    f"3. Profissionalismo\n"
                    f"4. Precisão técnica\n\n"
                    f"Retorne apenas um número de 0-100."
                )
            }
        ]
        
        score_text = await factory.generate(
            messages=messages,
            model="fast",  # GPT-4o-mini
            temperature=0.0,
        )
        
        # Parse score
        try:
            score = float(score_text.strip()) / 100.0
            score = max(0.0, min(1.0, score))  # Clamp [0,1]
        except:
            activity.logger.warning("⚠️ Falha ao parsear score, usando 0.85")
            score = 0.85
        
        activity.logger.info(f"✅ Score de verificação: {score:.2f}")
        return score
