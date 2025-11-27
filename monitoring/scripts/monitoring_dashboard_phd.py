#!/usr/bin/env python3
"""
Sistema de Monitoramento e Dashboard - PHD Edition
Autor: WARP Executor | Data: 2025-08-20
Dashboard em tempo real para métricas do sistema e APIs
"""

import os
import sys
import time
import json
import psutil
import threading
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, Any, List

# Auto-instalação de dependências
def auto_install():
    packages = ['psutil', 'plotly', 'dash', 'pandas', 'prometheus-client']
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            print(f"Instalando {pkg}...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

auto_install()

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary

# Métricas Prometheus
cpu_usage_gauge = Gauge('system_cpu_usage_percent', 'CPU usage in percent')
memory_usage_gauge = Gauge('system_memory_usage_percent', 'Memory usage in percent')
disk_usage_gauge = Gauge('system_disk_usage_percent', 'Disk usage in percent')
api_requests_counter = Counter('api_requests_total', 'Total API requests', ['endpoint', 'status'])
api_latency_histogram = Histogram('api_request_duration_seconds', 'API request latency')
cache_hits_counter = Counter('cache_hits_total', 'Total cache hits')
cache_misses_counter = Counter('cache_misses_total', 'Total cache misses')

class SystemMonitor:
    """Monitor de sistema avançado com histórico"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.ram_history = deque(maxlen=history_size)
        self.disk_history = deque(maxlen=history_size)
        self.network_history = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)
        self.api_metrics = {
            'total_requests': 0,
            'success_requests': 0,
            'failed_requests': 0,
            'avg_latency': 0,
            'cache_hit_rate': 0
        }
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Loop de monitoramento contínuo"""
        while self.running:
            try:
                # Coleta métricas
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                net = psutil.net_io_counters()
                
                # Armazena no histórico
                self.cpu_history.append(cpu)
                self.ram_history.append(ram)
                self.disk_history.append(disk)
                self.network_history.append({
                    'bytes_sent': net.bytes_sent,
                    'bytes_recv': net.bytes_recv
                })
                self.timestamps.append(datetime.now())
                
                # Atualiza métricas Prometheus
                cpu_usage_gauge.set(cpu)
                memory_usage_gauge.set(ram)
                disk_usage_gauge.set(disk)
                
                # Salva snapshot
                self._save_snapshot()
                
                time.sleep(5)  # Atualiza a cada 5 segundos
                
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
    
    def _save_snapshot(self):
        """Salva snapshot das métricas"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'cpu': list(self.cpu_history)[-1] if self.cpu_history else 0,
            'ram': list(self.ram_history)[-1] if self.ram_history else 0,
            'disk': list(self.disk_history)[-1] if self.disk_history else 0,
            'api_metrics': self.api_metrics
        }
        
        snapshot_file = Path('C:/Users/usuario/Warp/Outputs/2025/08/Monitoring')
        snapshot_file.mkdir(parents=True, exist_ok=True)
        
        with open(snapshot_file / f'snapshot_{datetime.now():%Y%m%d_%H%M%S}.json', 'w') as f:
            json.dump(snapshot, f, indent=2)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        return {
            'cpu': list(self.cpu_history)[-1] if self.cpu_history else 0,
            'ram': list(self.ram_history)[-1] if self.ram_history else 0,
            'disk': list(self.disk_history)[-1] if self.disk_history else 0,
            'processes': len(psutil.pids()),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'api_metrics': self.api_metrics
        }
    
    def get_history_dataframe(self) -> pd.DataFrame:
        """Retorna histórico como DataFrame"""
        return pd.DataFrame({
            'timestamp': list(self.timestamps),
            'cpu': list(self.cpu_history),
            'ram': list(self.ram_history),
            'disk': list(self.disk_history)
        })

class DashboardApp:
    """Dashboard interativo com Dash/Plotly"""
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Configura layout do dashboard"""
        self.app.layout = html.Div([
            html.H1('🚀 Sistema de Monitoramento PHD Edition', 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            html.Div([
                html.Div([
                    html.H3('CPU'),
                    dcc.Graph(id='cpu-gauge'),
                ], className='four columns'),
                
                html.Div([
                    html.H3('RAM'),
                    dcc.Graph(id='ram-gauge'),
                ], className='four columns'),
                
                html.Div([
                    html.H3('Disco'),
                    dcc.Graph(id='disk-gauge'),
                ], className='four columns'),
            ], className='row'),
            
            html.Div([
                dcc.Graph(id='history-graph'),
            ]),
            
            html.Div([
                html.H3('Métricas de API'),
                html.Div(id='api-metrics'),
            ]),
            
            html.Div([
                html.H3('Processos Top 10'),
                html.Div(id='process-table'),
            ]),
            
            dcc.Interval(
                id='interval-component',
                interval=5000,  # Atualiza a cada 5 segundos
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):
        """Configura callbacks para atualização automática"""
        
        @self.app.callback(
            [Output('cpu-gauge', 'figure'),
             Output('ram-gauge', 'figure'),
             Output('disk-gauge', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_gauges(n):
            metrics = self.monitor.get_current_metrics()
            
            # CPU Gauge
            cpu_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['cpu'],
                title={'text': "CPU %"},
                delta={'reference': 50},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75, 'value': 90}}
            ))
            
            # RAM Gauge
            ram_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['ram'],
                title={'text': "RAM %"},
                delta={'reference': 60},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkgreen"},
                       'steps': [
                           {'range': [0, 60], 'color': "lightgray"},
                           {'range': [60, 85], 'color': "yellow"},
                           {'range': [85, 100], 'color': "red"}]}
            ))
            
            # Disk Gauge
            disk_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['disk'],
                title={'text': "Disco %"},
                delta={'reference': 70},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "purple"},
                       'steps': [
                           {'range': [0, 70], 'color': "lightgray"},
                           {'range': [70, 90], 'color': "yellow"},
                           {'range': [90, 100], 'color': "red"}]}
            ))
            
            return cpu_fig, ram_fig, disk_fig
        
        @self.app.callback(
            Output('history-graph', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_history_graph(n):
            df = self.monitor.get_history_dataframe()
            
            fig = make_subplots(rows=3, cols=1, 
                               subplot_titles=('CPU %', 'RAM %', 'Disco %'))
            
            if not df.empty:
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu'],
                                        mode='lines', name='CPU'),
                            row=1, col=1)
                
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ram'],
                                        mode='lines', name='RAM'),
                            row=2, col=1)
                
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['disk'],
                                        mode='lines', name='Disco'),
                            row=3, col=1)
            
            fig.update_layout(height=600, showlegend=False)
            return fig
        
        @self.app.callback(
            Output('process-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_process_table(n):
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'PID': proc.info['pid'],
                        'Nome': proc.info['name'],
                        'CPU %': proc.info['cpu_percent'],
                        'RAM %': round(proc.info['memory_percent'], 2)
                    })
                except:
                    pass
            
            # Top 10 por CPU
            processes = sorted(processes, key=lambda x: x['CPU %'], reverse=True)[:10]
            
            table = html.Table([
                html.Thead([
                    html.Tr([html.Th(col) for col in ['PID', 'Nome', 'CPU %', 'RAM %']])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(proc['PID']),
                        html.Td(proc['Nome'][:30]),
                        html.Td(f"{proc['CPU %']:.1f}"),
                        html.Td(f"{proc['RAM %']:.1f}")
                    ]) for proc in processes
                ])
            ])
            
            return table
    
    def run(self, host: str = '127.0.0.1', port: int = 8050, debug: bool = False):
        """Inicia o dashboard"""
        print(f"🚀 Dashboard iniciado em http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)

def main():
    """Função principal"""
    print("╔══════════════════════════════════════════════╗")
    print("║   SISTEMA DE MONITORAMENTO PHD EDITION      ║")
    print("╚══════════════════════════════════════════════╝")
    
    # Inicia servidor Prometheus
    start_http_server(9090)
    print("✓ Servidor Prometheus iniciado na porta 9090")
    
    # Inicia monitor
    monitor = SystemMonitor()
    print("✓ Monitor de sistema iniciado")
    
    # Inicia dashboard
    dashboard = DashboardApp(monitor)
    print("✓ Iniciando dashboard...")
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n✓ Sistema encerrado")
        monitor.running = False

if __name__ == "__main__":
    main()
