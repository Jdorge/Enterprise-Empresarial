"""
Agente 4 – Agência/Serviços Profissionais
========================================

Este módulo implementa o **agente de agência**, voltado para
atividades de marketing, contabilidade e consultoria. Ele combina
análises quantitativas (custos, ROI) com insights qualitativos
(sentimento de feedbacks) para produzir propostas e relatórios em
formato CSV que maximizam a eficácia das campanhas e serviços.

Características principais:

* **Análise de Sentimento**: utiliza modelos de PLN (ex.: BERT com
  PyTorch) para inferir o sentimento predominante em feedbacks de
  clientes armazenados no Notion. Isso ajuda a calibrar propostas
  para atender preocupações ou destacar oportunidades.
* **Geração de Propostas**: cria propostas detalhadas em CSV,
  estimando custos e retorno sobre investimento (ROI) e
  incorporando insights qualitativos. Pode também gerar páginas
  automaticamente no Notion via API.
* **Validação Contábil**: aplica rotinas de validação dupla para
  garantir consistência nos números, evitando erros comuns em
  orçamentos e relatórios financeiros.

Este exemplo não integra PyTorch ou Notion de fato, mas mostra como
estruturar a lógica básica do agente.
"""

from __future__ import annotations
from typing import Any, Dict, List
import pandas as pd

from agents.base_agent import BaseAgent, AgentResult, AgentMetrics


class AgenciaAgent(BaseAgent):
    """Agente para automação de marketing, contabilidade e consultoria."""

    name = "agencia"

    def handle(
        self,
        query: str,
        context: Dict[str, Any],
        execution_id: str,
    ) -> AgentResult:
        # 1) Extrai o tipo de serviço solicitado da consulta; aqui
        # simplificamos com palavras-chave
        q = query.lower()
        if "marketing" in q:
            servicos = ["Campanha Google Ads", "Rebranding"]
            custos = [10000.0, 5000.0]
            roi = [1.5, 2.0]  # retorno estimado (multiplicador)
        elif "contab" in q or "finance" in q:
            servicos = ["Balanço Mensal", "Auditoria Fiscal"]
            custos = [7000.0, 9000.0]
            roi = [1.2, 1.1]
        else:
            servicos = ["Consultoria Estratégica", "Treinamento"]
            custos = [8000.0, 4000.0]
            roi = [1.8, 1.3]

        # 2) Análise de sentimento (stub):
        # Em um cenário real, você buscaria feedbacks em Notion
        # e aplicaria um modelo de linguagem. Aqui, simulamos que
        # todos os feedbacks são positivos.
        sentiment = "positivo"

        # 3) Monta DataFrame com custos e ROI estimado
        df = pd.DataFrame({
            "Serviço": servicos,
            "Custo Estimado (R$)": custos,
            "ROI Estimado (x)": roi,
            "Sentimento Feedback": [sentiment] * len(servicos),
        })
        csv_bytes = df.to_csv(index=False).encode("utf-8")

        data_payload = {
            "proposta": df.to_dict(orient="records"),
            "csv_bytes": csv_bytes,
            "sentimento": sentiment,
            "output_format": "proposta_servicos_csv",
            "upload_to_drive": True,
            "send_gmail": True,
            "gmail_subject": "Proposta de Serviços Profissionais",
            "gmail_body": (
                "Segue a proposta de serviços com previsão de ROI e análise "
                "de sentimento."
            ),
            # Sugestão: criar página Notion automaticamente (chave separada)
            "create_notion_page": True,
        }

        metrics = AgentMetrics(
            agent_name=self.name,
            status="success",
            latency_ms=0,
            tokens_prompt=0,
            tokens_completion=0,
            cost_usd_estimated=0.0,
            business_success=None,
            human_override=False,
        )

        message = (
            f"Proposta para {len(servicos)} serviços gerada com sucesso "
            f"(sentimento predominante: {sentiment})."
        )

        return AgentResult(
            status="success",
            message=message,
            data=data_payload,
            metrics=metrics,
            execution_id=execution_id,
        )
