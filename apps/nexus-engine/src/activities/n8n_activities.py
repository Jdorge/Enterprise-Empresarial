"""Activities para integração com n8n (webhooks e notificações)."""
from __future__ import annotations

import logging
from typing import Dict, Any
from temporalio import activity
import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.nexus_core.src.shared.config import Settings

logger = logging.getLogger(__name__)


class N8NActivities:
    """Activities para integração com n8n workflows."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.webhook_base = settings.n8n_webhook_url
    
    @activity.defn(name="send_approval_notification")
    async def send_approval_notification(self, data: Dict[str, Any]) -> str:
        """
        Envia notificação de aprovação via n8n webhook.
        
        Args:
            data: Dict com proposal_id, customer_name, amount, manager_email
            
        Returns:
            ID da notificação enviada
        """
        activity.logger.info(
            f"📧 Enviando notificação de aprovação para {data.get('manager_email')}"
        )
        
        # Payload para n8n
        payload = {
            "event": "proposal_approval_required",
            "proposal_id": data["proposal_id"],
            "customer_name": data["customer_name"],
            "amount": data["amount"],
            "manager_email": data.get("manager_email", "manager@company.com"),
            "approval_url": f"https://app.company.com/approvals/{data['proposal_id']}",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.webhook_base}/proposal-approval",
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                result = response.json()
                notification_id = result.get("notification_id", "unknown")
                
                activity.logger.info(
                    f"✅ Notificação enviada: {notification_id}"
                )
                return notification_id
                
        except Exception as e:
            activity.logger.error(f"❌ Erro ao enviar notificação: {e}")
            # Fallback: log apenas (não bloqueia workflow)
            return f"failed:{str(e)}"
