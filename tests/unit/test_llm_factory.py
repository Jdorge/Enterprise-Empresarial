"""Teste básico do LLMFactory com OpenRouter."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from packages.nexus_llm_factory.src.factory import LLMFactory
from pydantic import SecretStr


class MockSettings:
    """Settings mockadas para testes."""
    openrouter_api_key = SecretStr("sk-or-test-key")
    openrouter_base_url = "https://openrouter.ai/api/v1"
    
    def get_openrouter_key(self):
        return self.openrouter_api_key.get_secret_value()


@pytest.mark.asyncio
async def test_llm_factory_initialization():
    """Testa inicialização do LLMFactory."""
    settings = MockSettings()
    factory = LLMFactory(settings)
    
    assert factory.api_key == "sk-or-test-key"
    assert factory.base_url == "https://openrouter.ai/api/v1"
    assert factory.total_cost == 0.0


@pytest.mark.asyncio
async def test_generate_fast_model():
    """Testa geração com modelo fast (gpt-4o-mini)."""
    settings = MockSettings()
    
    with patch("httpx.AsyncClient") as mock_client_class:
        # Mock do client HTTP
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response from GPT-4o-mini"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        
        # Testa geração
        factory = LLMFactory(settings)
        messages = [{"role": "user", "content": "Hello"}]
        
        result = await factory.generate(messages=messages, model="fast")
        
        assert result == "Test response from GPT-4o-mini"
        assert factory.total_cost > 0  # Custo foi calculado
        assert "openai/gpt-4o-mini" in factory.call_counts


@pytest.mark.asyncio
async def test_metrics_tracking():
    """Testa rastreamento de métricas."""
    settings = MockSettings()
    factory = LLMFactory(settings)
    
    # Simula 2 chamadas
    factory.call_counts = {"openai/gpt-4o-mini": 2, "anthropic/claude-3-5-sonnet": 1}
    factory.total_cost = 0.05
    
    metrics = factory.get_metrics()
    
    assert metrics["total_calls"] == 3
    assert metrics["total_cost_usd"] == 0.05
    assert metrics["average_cost_per_call"] > 0
    assert "openai/gpt-4o-mini" in metrics["calls_by_model"]
