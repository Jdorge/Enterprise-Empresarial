"""Modelos de dados compartilhados para workflows e activities."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class ProposalRequest(BaseModel):
    """Entrada para geração de propostas comerciais."""
    
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="ID do usuário solicitante")
    customer_name: str = Field(..., description="Nome do cliente")
    customer_email: Optional[str] = Field(None, description="Email do cliente")
    details: Optional[str] = Field(None, description="Detalhes do pedido")
    max_value: Optional[float] = Field(None, description="Valor máximo da proposta")


class ProposalResult(BaseModel):
    """Resultado do workflow de proposta comercial."""
    
    request_id: str
    summary: str
    full_proposal: str
    confidence_score: float
    verification_steps: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    total_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResearchRequest(BaseModel):
    """Request para workflow de pesquisa."""
    
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    topic: str
    constraints: Optional[List[str]] = None
    max_results: int = Field(default=10)


class ResearchResult(BaseModel):
    """Resultado de pesquisa."""
    
    request_id: str
    summary: str
    key_findings: List[str]
    confidence_score: float
    sources: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalSignal(BaseModel):
    """Sinal de aprovação humana."""
    
    approved: bool
    feedback: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: datetime = Field(default_factory=datetime.utcnow)
