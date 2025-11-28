"""LLM Factory usando OpenRouter como backend unificado."""
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory para LLMs usando OpenRouter como gateway unificado.
    Suporta 300+ modelos com fallback e rastreamento de custo.
    """
    
    # Modelos recomendados por custo/performance
    MODELS = {
        "fast": "openai/gpt-4o-mini",              # Rápido e barato
        "balanced": "anthropic/claude-3-5-sonnet", # Balanceado
        "powerful": "openai/gpt-4o",               # Mais poderoso
        "cheap": "google/gemini-2.0-flash-exp",    # Mais barato
    }
    
    def __init__(self, settings):
        """Inicializa factory com configurações."""
        self.api_key = settings.get_openrouter_key()
        self.base_url = settings.openrouter_base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Métricas
        self.total_cost = 0.0
        self.call_counts: Dict[str, int] = {}
        self.last_request_time = None
        
        logger.info("✅ LLMFactory inicializado com OpenRouter")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: str = "fast",
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Any:
        """
        Gera resposta usando OpenRouter.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            model: Nome do modelo ou preset (fast/balanced/powerful/cheap)
            response_model: Modelo Pydantic para parsing estruturado
            temperature: Criatividade (0-1)
            max_tokens: Máximo de tokens na resposta
        """
        # Resolve preset do modelo
        model_name = self.MODELS.get(model, model)
        
        # Rate limiting básico (evitar saturar API)
        await self._rate_limit()
        
        try:
            # Prepara request
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/nexus-enterprise",
                "X-Title": "Nexus Enterprise v2"
            }
            
            # Faz chamada
            logger.info(f"🚀 Chamando OpenRouter: {model_name}")
            start_time = time.time()
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            
            latency = time.time() - start_time
            data = response.json()
            
            # Extrai conteúdo
            content = data["choices"][0]["message"]["content"]
            
            # Calcula custo (se disponível)
            usage = data.get("usage", {})
            cost = self._estimate_cost(usage)
            
            # Atualiza métricas
            self.total_cost += cost
            self.call_counts[model_name] = self.call_counts.get(model_name, 0) + 1
            
            logger.info(
                f"✅ Resposta recebida: {latency:.2f}s | "
                f"Tokens: {usage.get('total_tokens', 0)} | "
                f"Custo: ${cost:.4f}"
            )
            
            # Parse estruturado se solicitado
            if response_model:
                try:
                    return response_model.model_validate_json(content)
                except Exception as e:
                    logger.warning(f"⚠️ Falha no parse estruturado: {e}")
                    # Tenta parse manual
                    import json
                    return response_model(**json.loads(content))
            
            return content
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("🚨 Rate limit atingido!")
                raise
            elif e.response.status_code == 401:
                logger.error("🚨 API key inválida!")
                raise ValueError("OpenRouter API key inválida")
            else:
                logger.error(f"🚨 Erro HTTP {e.response.status_code}: {e.response.text}")
                raise
        
        except Exception as e:
            logger.error(f"🚨 Erro na chamada LLM: {e}")
            raise
    
    async def _rate_limit(self):
        """Rate limiting básico entre requests."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            min_interval = 0.1  # 100ms entre requests mínimo
            
            if elapsed < min_interval:
                import asyncio
                await asyncio.sleep(min_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def _estimate_cost(self, usage: dict) -> float:
        """Estima custo baseado em tokens (aproximação)."""
        # OpenRouter cobra por modelo, mas fazemos estimativa conservadora
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        # Custo médio aproximado: $0.002/1k tokens input, $0.006/1k output
        input_cost = (prompt_tokens / 1000) * 0.002
        output_cost = (completion_tokens / 1000) * 0.006
        
        return input_cost + output_cost
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de uso."""
        total_calls = sum(self.call_counts.values())
        avg_cost = self.total_cost / total_calls if total_calls > 0 else 0.0
        
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_calls": total_calls,
            "calls_by_model": self.call_counts,
            "average_cost_per_call": round(avg_cost, 4),
        }
    
    async def close(self):
        """Fecha cliente HTTP."""
        await self.client.aclose()
