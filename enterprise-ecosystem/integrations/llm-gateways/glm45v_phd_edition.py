#!/usr/bin/env python3
"""
GLM-4.5V PHD Edition - Sistema Avançado com Cache, Monitoring e Segurança
Autor: WARP Executor | Data: 2025-08-20
"""

import os
import sys
import time
import json
import logging
import hashlib
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Optional, Dict, Any, List
from pathlib import Path

# Instalação automática de dependências
def install_requirements():
    """Instala automaticamente todas as dependências necessárias"""
    required = ['openai', 'python-dotenv', 'diskcache', 'psutil', 'colorama', 'rich']
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Instalando {package}...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])

install_requirements()

# Imports após instalação
from dotenv import load_dotenv
import openai
from diskcache import Cache
import psutil
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import threading
import queue

# Inicialização
init(autoreset=True)
console = Console()
load_dotenv()

# Configuração de Logging Avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'C:/Users/usuario/Warp/Outputs/2025/08/Logs/glm45v_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GLM45V-PHD')

# Cache Persistente
cache_dir = Path('C:/Users/usuario/.cache/glm45v')
cache_dir.mkdir(parents=True, exist_ok=True)
cache = Cache(str(cache_dir), size_limit=int(1e9))  # 1GB cache

class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    def __init__(self):
        self.metrics = {
            'requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'total_latency': 0,
            'avg_latency': 0
        }
        self.start_time = time.time()
    
    def log_request(self, latency: float, cache_hit: bool = False):
        self.metrics['requests'] += 1
        self.metrics['total_latency'] += latency
        self.metrics['avg_latency'] = self.metrics['total_latency'] / self.metrics['requests']
        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
    
    def log_error(self):
        self.metrics['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        return {
            **self.metrics,
            'uptime_seconds': uptime,
            'cache_hit_rate': (self.metrics['cache_hits'] / max(1, self.metrics['requests'])) * 100,
            'error_rate': (self.metrics['errors'] / max(1, self.metrics['requests'])) * 100,
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent
        }

class GLM45VClient:
    """Cliente GLM-4.5V otimizado com todas as melhorias"""
    
    def __init__(self):
        self.token = os.getenv('HF_TOKEN', '')
        self.client = openai.OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.token
        )
        self.monitor = PerformanceMonitor()
        self.request_queue = queue.Queue()
        self.response_cache = {}
        
    def _get_cache_key(self, prompt: str) -> str:
        """Gera chave única para cache"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def _cached_completion(self, prompt_hash: str, prompt: str) -> str:
        """Chamada com cache em memória"""
        return self._make_request(prompt)
    
    def _make_request(self, prompt: str, retry_count: int = 0) -> str:
        """Faz requisição com retry exponencial inteligente"""
        max_retries = int(os.getenv('RETRY_ATTEMPTS', 5))
        
        try:
            start_time = time.time()
            completion = self.client.chat.completions.create(
                model="zai-org/GLM-4.5V:novita",
                messages=[{"role": "user", "content": prompt}],
                timeout=int(os.getenv('REQUEST_TIMEOUT', 30))
            )
            latency = time.time() - start_time
            self.monitor.log_request(latency)
            logger.info(f"Request successful - Latency: {latency:.2f}s")
            return completion.choices[0].message.content
            
        except Exception as e:
            self.monitor.log_error()
            if retry_count < max_retries:
                if "429" in str(e) or "overload" in str(e).lower():
                    wait_time = (2 ** retry_count) * int(os.getenv('RETRY_DELAY', 10))
                    console.print(f"[yellow]Rate limit detectado. Aguardando {wait_time}s... (Tentativa {retry_count+1}/{max_retries})[/yellow]")
                    time.sleep(wait_time)
                    return self._make_request(prompt, retry_count + 1)
            logger.error(f"Request failed after {retry_count} retries: {e}")
            raise
    
    def complete(self, prompt: str, use_cache: bool = True) -> str:
        """Interface principal com cache opcional"""
        cache_key = self._get_cache_key(prompt)
        
        # Verifica cache persistente
        if use_cache and cache_key in cache:
            self.monitor.log_request(0, cache_hit=True)
            console.print("[green]✓ Resposta do cache[/green]")
            return cache[cache_key]
        
        # Faz nova requisição
        response = self._cached_completion(cache_key, prompt)
        
        # Salva no cache persistente
        if use_cache:
            cache.set(cache_key, response, expire=int(os.getenv('CACHE_TTL', 3600)))
        
        return response
    
    def batch_complete(self, prompts: List[str]) -> List[str]:
        """Processa múltiplos prompts em paralelo"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        responses = {}
        with ThreadPoolExecutor(max_workers=int(os.getenv('MAX_WORKERS', 4))) as executor:
            future_to_prompt = {executor.submit(self.complete, prompt): prompt for prompt in prompts}
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Processando prompts...", total=len(prompts))
                
                for future in as_completed(future_to_prompt):
                    prompt = future_to_prompt[future]
                    try:
                        response = future.result()
                        responses[prompt] = response
                        progress.update(task, advance=1)
                    except Exception as e:
                        responses[prompt] = f"Erro: {str(e)}"
                        logger.error(f"Batch processing error for prompt: {e}")
        
        return [responses[p] for p in prompts]
    
    def show_stats(self):
        """Exibe estatísticas de performance"""
        stats = self.monitor.get_stats()
        
        table = Table(title="📊 Estatísticas GLM-4.5V PHD Edition")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Total de Requisições", str(stats['requests']))
        table.add_row("Taxa de Cache Hit", f"{stats['cache_hit_rate']:.1f}%")
        table.add_row("Latência Média", f"{stats['avg_latency']:.2f}s")
        table.add_row("Taxa de Erro", f"{stats['error_rate']:.1f}%")
        table.add_row("CPU", f"{stats['cpu_percent']:.1f}%")
        table.add_row("Memória", f"{stats['memory_percent']:.1f}%")
        table.add_row("Uptime", f"{stats['uptime_seconds']:.0f}s")
        
        console.print(table)

class InteractiveREPL:
    """REPL interativo avançado com comandos especiais"""
    
    def __init__(self):
        self.client = GLM45VClient()
        self.history = []
        self.commands = {
            '/help': self.show_help,
            '/stats': self.client.show_stats,
            '/clear': self.clear_cache,
            '/history': self.show_history,
            '/save': self.save_session,
            '/batch': self.batch_mode,
            '/exit': self.exit_repl
        }
    
    def show_help(self):
        """Mostra ajuda dos comandos"""
        console.print("\n[bold cyan]Comandos Disponíveis:[/bold cyan]")
        console.print("  /help     - Mostra esta ajuda")
        console.print("  /stats    - Exibe estatísticas de performance")
        console.print("  /clear    - Limpa o cache")
        console.print("  /history  - Mostra histórico de conversas")
        console.print("  /save     - Salva sessão atual")
        console.print("  /batch    - Modo batch (múltiplos prompts)")
        console.print("  /exit     - Sair\n")
    
    def clear_cache(self):
        """Limpa cache"""
        cache.clear()
        console.print("[green]✓ Cache limpo com sucesso[/green]")
    
    def show_history(self):
        """Mostra histórico"""
        for i, (prompt, response) in enumerate(self.history[-10:], 1):
            console.print(f"[cyan]{i}. P:[/cyan] {prompt[:50]}...")
            console.print(f"[green]   R:[/green] {response[:50]}...\n")
    
    def save_session(self):
        """Salva sessão em arquivo"""
        filename = f"C:/Users/usuario/Warp/Outputs/2025/08/Sessions/session_{datetime.now():%Y%m%d_%H%M%S}.json"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        console.print(f"[green]✓ Sessão salva em: {filename}[/green]")
    
    def batch_mode(self):
        """Modo batch para múltiplos prompts"""
        console.print("[cyan]Modo Batch - Digite os prompts (linha vazia para processar):[/cyan]")
        prompts = []
        while True:
            prompt = input("  > ")
            if not prompt:
                break
            prompts.append(prompt)
        
        if prompts:
            responses = self.client.batch_complete(prompts)
            for prompt, response in zip(prompts, responses):
                console.print(f"\n[cyan]P:[/cyan] {prompt}")
                console.print(f"[green]R:[/green] {response}")
    
    def exit_repl(self):
        """Sair do REPL"""
        self.save_session()
        self.client.show_stats()
        console.print("[bold green]Até logo! Sessão salva.[/bold green]")
        sys.exit(0)
    
    def run(self):
        """Loop principal do REPL"""
        console.print("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║  GLM-4.5V PHD Edition - REPL v2.0   ║[/bold cyan]")
        console.print("[bold cyan]║  Digite /help para ver comandos     ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")
        
        while True:
            try:
                prompt = console.input("[bold yellow]GLM>[/bold yellow] ").strip()
                
                if not prompt:
                    continue
                
                # Verifica comandos especiais
                if prompt.startswith('/'):
                    if prompt in self.commands:
                        self.commands[prompt]()
                    else:
                        console.print("[red]Comando desconhecido. Use /help[/red]")
                    continue
                
                # Processa prompt normal
                with console.status("[cyan]Processando...[/cyan]", spinner="dots"):
                    response = self.client.complete(prompt)
                
                console.print(f"\n[green]{response}[/green]\n")
                self.history.append((prompt, response))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit para sair[/yellow]")
            except Exception as e:
                logger.error(f"REPL error: {e}")
                console.print(f"[red]Erro: {e}[/red]")

# Sistema de Health Check
def health_check():
    """Verifica saúde do sistema"""
    checks = {
        'Python': sys.version.split()[0],
        'OpenAI lib': openai.__version__,
        'Cache': 'OK' if cache_dir.exists() else 'FAIL',
        'CPU': f"{psutil.cpu_percent()}%",
        'RAM': f"{psutil.virtual_memory().percent}%",
        'Disk': f"{psutil.disk_usage('/').percent}%"
    }
    
    table = Table(title="🏥 Health Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    for component, status in checks.items():
        table.add_row(component, status)
    
    console.print(table)
    return all('FAIL' not in str(v) for v in checks.values())

if __name__ == "__main__":
    # Health check inicial
    if not health_check():
        console.print("[red]⚠ Sistema com problemas. Verifique os logs.[/red]")
        sys.exit(1)
    
    # Inicia REPL
    repl = InteractiveREPL()
    repl.run()
