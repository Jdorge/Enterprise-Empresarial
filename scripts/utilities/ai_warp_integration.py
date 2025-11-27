#!/usr/bin/env python3
"""
🤖 SISTEMA DE INTEGRAÇÃO AI PARA WARP DRIVE
Baseado nas documentações encontradas no Warp Drive do Jorge Freitas
Integração completa: OpenAI + Agentes + APIs + Monitoramento
"""

import os
import json
import yaml
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import openai
from dataclasses import dataclass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/warp_ai_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuração base para agentes AI"""
    name: str
    type: str  # vendas, suporte, operacional, educacao
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    active: bool = True

class WarpAIIntegration:
    """
    Sistema principal de integração AI para Warp Drive
    Baseado nos templates e documentações encontradas
    """
    
    def __init__(self, config_path: str = "config/warp_ai_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.openai_client = None
        self.active_agents = {}
        self.session_logs = []
        
        # Inicialização
        self.setup_directories()
        self.setup_openai()
        self.load_agents()
    
    def setup_directories(self):
        """Cria estrutura de diretórios necessária"""
        dirs = ['logs', 'config', 'templates', 'data', 'reports']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
        logger.info("📁 Estrutura de diretórios criada")
    
    def load_config(self) -> Dict:
        """Carrega configurações do sistema"""
        default_config = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),  # Load from environment variable
                'model': 'gpt-4o-mini'
            },
            'agents': {
                'vendas': {'active': True},
                'suporte': {'active': True},
                'operacional': {'active': True}
            },
            'monitoring': {
                'enabled': True,
                'log_level': 'INFO'
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                return {**default_config, **config}
            else:
                # Cria arquivo de config padrão
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                return default_config
        except Exception as e:
            logger.warning(f"Erro ao carregar config: {e}. Usando configuração padrão.")
            return default_config
    
    def setup_openai(self):
        """Configura cliente OpenAI"""
        try:
            api_key = self.config['openai']['api_key']
            self.openai_client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Teste de conectividade
            models = self.openai_client.models.list()
            logger.info("✅ OpenAI configurado com sucesso")
            logger.info(f"📊 Modelos disponíveis: {len(models.data)}")
        except Exception as e:
            logger.error(f"❌ Erro ao configurar OpenAI: {e}")
            self.openai_client = None
    
    def load_agents(self):
        """Carrega templates de agentes baseados na documentação"""
        agents_templates = {
            'vendas_sdr': AgentConfig(
                name="Agente SDR",
                type="vendas",
                model="gpt-4o-mini"
            ),
            'suporte_24h': AgentConfig(
                name="Suporte 24/7",
                type="suporte", 
                model="gpt-4o-mini"
            ),
            'operacional_rh': AgentConfig(
                name="Automação RH",
                type="operacional",
                model="gpt-4o-mini"
            ),
            'vendedor_consultivo': AgentConfig(
                name="Vendedor Consultivo",
                type="vendas",
                model="gpt-4o-mini"
            )
        }
        
        for agent_id, config in agents_templates.items():
            if config.active:
                self.active_agents[agent_id] = config
        
        logger.info(f"🤖 {len(self.active_agents)} agentes carregados")
    
    def create_chat_completion(self, 
                             prompt: str, 
                             agent_type: str = "geral",
                             temperature: float = 0.7) -> Dict:
        """
        Cria completion baseado no tipo de agente
        Baseado nos templates encontrados na documentação
        """
        if not self.openai_client:
            return {"error": "OpenAI não configurado"}
        
        # Prompts específicos por tipo de agente
        system_prompts = {
            "vendas": """Você é um agente especialista em vendas B2B. 
            Sua função é qualificar leads, superar objeções e fechar vendas.
            Seja consultivo, entenda as necessidades do cliente e proponha soluções.""",
            
            "suporte": """Você é um agente de suporte técnico 24/7.
            Sua função é resolver problemas, orientar usuários e escalacionar quando necessário.
            Seja claro, objetivo e sempre busque resolver o problema do cliente.""",
            
            "operacional": """Você é um agente de automação operacional.
            Sua função é otimizar processos, automatizar tarefas e gerar relatórios.
            Seja analítico, eficiente e focado em resultados mensuráveis.""",
            
            "geral": """Você é um assistente AI especializado em produtividade.
            Ajude o usuário com suas tarefas de forma clara e eficiente."""
        }
        
        system_prompt = system_prompts.get(agent_type, system_prompts["geral"])
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            
            result = {
                "response": response.choices[0].message.content,
                "model": response.model,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Log da sessão
            self.session_logs.append(result)
            logger.info(f"💬 Chat completion criado - Agente: {agent_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na completion: {e}")
            return {"error": str(e)}
    
    def execute_agent_workflow(self, 
                              agent_type: str, 
                              task: str, 
                              context: Dict = None) -> Dict:
        """
        Executa workflow completo de um agente
        Baseado nos casos de uso da documentação
        """
        context = context or {}
        
        # Workflows específicos por tipo
        workflows = {
            "vendas": self._vendas_workflow,
            "suporte": self._suporte_workflow,
            "operacional": self._operacional_workflow
        }
        
        workflow_func = workflows.get(agent_type)
        if not workflow_func:
            return {"error": f"Workflow não encontrado para: {agent_type}"}
        
        try:
            result = workflow_func(task, context)
            logger.info(f"🔄 Workflow executado - {agent_type}")
            return result
        except Exception as e:
            logger.error(f"❌ Erro no workflow {agent_type}: {e}")
            return {"error": str(e)}
    
    def _vendas_workflow(self, task: str, context: Dict) -> Dict:
        """Workflow específico para agentes de vendas"""
        # Simula processo de qualificação de leads
        prompt = f"""
        TAREFA DE VENDAS: {task}
        CONTEXTO: {json.dumps(context, ensure_ascii=False)}
        
        Execute as seguintes etapas:
        1. Qualifique o lead (BANT - Budget, Authority, Need, Timeline)
        2. Identifique objeções potenciais
        3. Proponha próximos passos
        4. Calcule score de conversão (0-100)
        
        Responda em formato JSON estruturado.
        """
        
        return self.create_chat_completion(prompt, "vendas", 0.3)
    
    def _suporte_workflow(self, task: str, context: Dict) -> Dict:
        """Workflow específico para agentes de suporte"""
        prompt = f"""
        TICKET DE SUPORTE: {task}
        CONTEXTO: {json.dumps(context, ensure_ascii=False)}
        
        Execute o protocolo de suporte:
        1. Classifique a urgência (Baixa/Média/Alta/Crítica)
        2. Identifique a categoria do problema
        3. Proponha solução ou escalação
        4. Defina tempo estimado de resolução
        
        Responda em formato JSON estruturado.
        """
        
        return self.create_chat_completion(prompt, "suporte", 0.2)
    
    def _operacional_workflow(self, task: str, context: Dict) -> Dict:
        """Workflow específico para agentes operacionais"""
        prompt = f"""
        PROCESSO OPERACIONAL: {task}
        DADOS: {json.dumps(context, ensure_ascii=False)}
        
        Análise operacional:
        1. Identifique ineficiências no processo
        2. Calcule potencial de automação (%)
        3. Estime ROI da otimização
        4. Sugira KPIs de monitoramento
        
        Responda em formato JSON estruturado.
        """
        
        return self.create_chat_completion(prompt, "operacional", 0.1)
    
    def get_analytics(self) -> Dict:
        """Retorna analytics consolidado do sistema"""
        total_interactions = len(self.session_logs)
        
        if total_interactions == 0:
            return {"message": "Nenhuma interação registrada ainda"}
        
        # Análise por tipo de agente
        agent_stats = {}
        total_tokens = 0
        
        for log in self.session_logs:
            agent_type = log.get('agent_type', 'unknown')
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {'count': 0, 'tokens': 0}
            
            agent_stats[agent_type]['count'] += 1
            if 'usage' in log:
                tokens = log['usage']['total_tokens']
                agent_stats[agent_type]['tokens'] += tokens
                total_tokens += tokens
        
        return {
            'total_interactions': total_interactions,
            'active_agents': len(self.active_agents),
            'total_tokens_used': total_tokens,
            'agent_statistics': agent_stats,
            'last_interaction': self.session_logs[-1]['timestamp'] if self.session_logs else None,
            'system_status': 'operational' if self.openai_client else 'degraded'
        }
    
    def export_report(self, filename: str = None) -> str:
        """Exporta relatório completo do sistema"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/warp_ai_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_info': {
                'warp_drive': 'Jorge Freitas Integration',
                'version': '1.0.0',
                'openai_status': 'connected' if self.openai_client else 'disconnected'
            },
            'analytics': self.get_analytics(),
            'active_agents': {k: v.name for k, v in self.active_agents.items()},
            'session_logs': self.session_logs[-10:],  # Últimas 10 interações
            'configuration': {
                'agents_count': len(self.active_agents),
                'monitoring_enabled': self.config.get('monitoring', {}).get('enabled', False)
            }
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Relatório exportado: {filename}")
        return filename

# Função principal para testes
def main():
    """Função principal para demonstração"""
    print("🚀 INICIANDO SISTEMA WARP AI INTEGRATION")
    print("=" * 60)
    
    # Inicializa o sistema
    warp_ai = WarpAIIntegration()
    
    if not warp_ai.openai_client:
        print("❌ OpenAI não configurado. Verifique sua API key.")
        return
    
    # Testes dos agentes
    test_cases = [
        {
            "type": "vendas",
            "task": "Qualificar lead interessado em automação de processos para empresa de 50 funcionários",
            "context": {"empresa": "TechCorp", "funcionarios": 50, "setor": "tecnologia"}
        },
        {
            "type": "suporte", 
            "task": "Cliente relatou que o sistema está lento há 3 dias",
            "context": {"cliente": "Premium", "sistema": "CRM", "dias_problema": 3}
        },
        {
            "type": "operacional",
            "task": "Analisar processo de aprovação de compras que demora 7 dias",
            "context": {"processo": "aprovacao_compras", "tempo_atual": "7 dias", "etapas": 5}
        }
    ]
    
    print("\n🤖 EXECUTANDO TESTES DOS AGENTES:")
    print("-" * 40)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🔄 Teste {i}: Agente {test['type'].upper()}")
        result = warp_ai.execute_agent_workflow(
            test['type'], 
            test['task'], 
            test['context']
        )
        
        if 'error' in result:
            print(f"❌ Erro: {result['error']}")
        else:
            print(f"✅ Sucesso - Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            # Mostra primeiras linhas da resposta
            response = result.get('response', '')[:200]
            print(f"📝 Resposta: {response}...")
    
    # Analytics
    print("\n📊 ANALYTICS DO SISTEMA:")
    print("-" * 30)
    analytics = warp_ai.get_analytics()
    for key, value in analytics.items():
        print(f"{key}: {value}")
    
    # Exporta relatório
    print("\n📋 EXPORTANDO RELATÓRIO...")
    report_file = warp_ai.export_report()
    print(f"✅ Relatório salvo: {report_file}")
    
    print("\n" + "=" * 60)
    print("🎉 SISTEMA WARP AI INTEGRATION FUNCIONANDO!")
    print("📖 Baseado nas documentações encontradas no Warp Drive")
    print("🔗 Integração: OpenAI + Agentes + Analytics + Relatórios")

if __name__ == "__main__":
    main()
