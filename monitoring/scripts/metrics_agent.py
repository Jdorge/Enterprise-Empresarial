#!/usr/bin/env python3
"""
Metrics Agent - Agente para coleta e processamento de métricas
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import psutil
import platform

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsAgent:
    """Agente para coleta de métricas do sistema"""
    
    def __init__(self, interval: int = 60):
        """
        Inicializa o agente de métricas
        
        Args:
            interval: Intervalo em segundos entre coletas
        """
        self.interval = interval
        self.metrics_history: List[Dict[str, Any]] = []
        self.is_running = False
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            
            # Métricas de rede
            network = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'platform': platform.system(),
                    'platform_version': platform.version(),
                    'hostname': platform.node(),
                },
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {e}")
            return {}
    
    def save_metrics(self, metrics: Dict[str, Any], filename: str = "metrics.json"):
        """Salva métricas em arquivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            logger.info(f"Métricas salvas em {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
    
    def print_metrics(self, metrics: Dict[str, Any]):
        """Exibe métricas no console"""
        if not metrics:
            return
            
        print("\n" + "="*50)
        print(f"MÉTRICAS DO SISTEMA - {metrics.get('timestamp', 'N/A')}")
        print("="*50)
        
        # CPU
        cpu = metrics.get('cpu', {})
        print(f"\nCPU:")
        print(f"  Uso: {cpu.get('percent', 0):.1f}%")
        print(f"  Núcleos: {cpu.get('count', 0)}")
        
        # Memória
        memory = metrics.get('memory', {})
        print(f"\nMemória:")
        print(f"  Total: {self._format_bytes(memory.get('total', 0))}")
        print(f"  Usado: {self._format_bytes(memory.get('used', 0))}")
        print(f"  Disponível: {self._format_bytes(memory.get('available', 0))}")
        print(f"  Uso: {memory.get('percent', 0):.1f}%")
        
        # Disco
        disk = metrics.get('disk', {})
        print(f"\nDisco:")
        print(f"  Total: {self._format_bytes(disk.get('total', 0))}")
        print(f"  Usado: {self._format_bytes(disk.get('used', 0))}")
        print(f"  Livre: {self._format_bytes(disk.get('free', 0))}")
        print(f"  Uso: {disk.get('percent', 0):.1f}%")
        
        # Rede
        network = metrics.get('network', {})
        print(f"\nRede:")
        print(f"  Bytes enviados: {self._format_bytes(network.get('bytes_sent', 0))}")
        print(f"  Bytes recebidos: {self._format_bytes(network.get('bytes_recv', 0))}")
        print(f"  Pacotes enviados: {network.get('packets_sent', 0):,}")
        print(f"  Pacotes recebidos: {network.get('packets_recv', 0):,}")
    
    def _format_bytes(self, bytes: int) -> str:
        """Formata bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"
    
    def run_once(self) -> Dict[str, Any]:
        """Executa uma única coleta de métricas"""
        logger.info("Coletando métricas...")
        metrics = self.collect_system_metrics()
        self.metrics_history.append(metrics)
        return metrics
    
    def start(self):
        """Inicia o agente de métricas"""
        self.is_running = True
        logger.info(f"Agente de métricas iniciado (intervalo: {self.interval}s)")
        
        try:
            while self.is_running:
                metrics = self.run_once()
                self.print_metrics(metrics)
                
                # Salva métricas a cada coleta
                self.save_metrics(metrics)
                
                # Aguarda próximo intervalo
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Agente interrompido pelo usuário")
            self.stop()
        except Exception as e:
            logger.error(f"Erro no agente: {e}")
            self.stop()
    
    def stop(self):
        """Para o agente de métricas"""
        self.is_running = False
        logger.info("Agente de métricas parado")
        
        # Salva histórico completo
        if self.metrics_history:
            self.save_metrics(
                {'history': self.metrics_history},
                'metrics_history.json'
            )


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agente de Métricas do Sistema')
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Intervalo entre coletas em segundos (padrão: 60)'
    )
    parser.add_argument(
        '--once', '-o',
        action='store_true',
        help='Executa apenas uma coleta e sai'
    )
    
    args = parser.parse_args()
    
    # Cria e configura o agente
    agent = MetricsAgent(interval=args.interval)
    
    if args.once:
        # Executa apenas uma vez
        metrics = agent.run_once()
        agent.print_metrics(metrics)
        agent.save_metrics(metrics)
    else:
        # Executa continuamente
        print(f"Iniciando agente de métricas...")
        print(f"Intervalo de coleta: {args.interval} segundos")
        print("Pressione Ctrl+C para parar\n")
        agent.start()


if __name__ == '__main__':
    main()
