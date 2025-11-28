"""Configurações seguras do sistema usando OpenRouter como backend principal."""
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações com gestão segura de secrets.
    Usa OpenRouter como gateway unificado para todos os LLMs.
    """
    
    # ============ OpenRouter (Backend Principal) ============
    openrouter_api_key: SecretStr = Field(
        ...,
        description="Chave da OpenRouter para acesso a 300+ modelos"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="URL base da OpenRouter API"
    )
    
    # ============ APIs Complementares (Opcional) ============
    perplexity_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Chave Perplexity para search especializado"
    )
    
    # ============ Temporal ============
    temporal_host: str = Field(
        default="temporal:7233",
        description="Host do Temporal Server"
    )
    temporal_namespace: str = Field(
        default="default",
        description="Namespace do Temporal"
    )
    
    # ============ Qdrant Vector DB ============
    qdrant_host: str = Field(
        default="qdrant",
        description="Host do Qdrant"
    )
    qdrant_port: int = Field(
        default=6333,
        description="Porta do Qdrant"
    )
    qdrant_api_key: Optional[SecretStr] = Field(
        default=None,
        description="API key do Qdrant (se configurado)"
    )
    
    # ============ Database ============
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="nexus")
    postgres_password: SecretStr = Field(...)
    postgres_db: str = Field(default="nexus")
    
    # ============ n8n ============
    n8n_webhook_url: str = Field(
        default="http://n8n:5678/webhook",
        description="URL base dos webhooks n8n"
    )
    n8n_api_key: Optional[SecretStr] = Field(default=None)
   
    # ============ Security ============
    jwt_secret: SecretStr = Field(
        ...,
        description="Secret para tokens JWT"
    )
    encryption_key: SecretStr = Field(
        ...,
        description="Chave para criptografia de dados sensíveis"
    )
    
    # ============ Application ============
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")
    max_workers: int = Field(default=4)
    
    # ============ Rate Limiting ============
    rate_limit_per_minute: int = Field(
        default=100,
        description="Limite de requisições por minuto"
    )
    rate_limit_burst: int = Field(
        default=20,
        description="Burst máximo permitido"
    )
    
    # ============ Cost Control ============
    max_daily_cost_usd: float = Field(
        default=100.0,
        description="Custo máximo diário em USD"
    )
    alert_threshold_usd: float = Field(
        default=50.0,
        description="Threshold para alertas de custo"
    )
    
    model_config = {
        "env_file": ".env.local",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    def get_openrouter_key(self) -> str:
        """Retorna chave OpenRouter de forma segura."""
        return self.openrouter_api_key.get_secret_value()
    
    def get_postgres_dsn(self) -> str:
        """Retorna DSN do PostgreSQL."""
        password = self.postgres_password.get_secret_value()
        return (
            f"postgresql://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    def get_qdrant_url(self) -> str:
        """Retorna URL do Qdrant."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
