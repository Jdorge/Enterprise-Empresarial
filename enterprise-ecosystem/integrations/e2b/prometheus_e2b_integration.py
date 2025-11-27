#!/usr/bin/env python3
"""
🚀 Integração E2B com Projetos Notion - Prometheus Analytics
Análise avançada de métricas do Prometheus usando E2B sandboxes
"""
import asyncio
import json
import os
from datetime import datetime
from e2b import Sandbox

class PrometheusE2BAnalytics:
    def __init__(self):
        self.sandbox = None
        self.prometheus_url = "http://localhost:9090"
        
    async def initialize_sandbox(self):
        """Inicializa o sandbox E2B com as dependências necessárias"""
        print("🔄 Inicializando sandbox E2B...")
        self.sandbox = Sandbox()
        
        # Instalar dependências no sandbox
        result = self.sandbox.run("bash -c 'pip install pandas matplotlib seaborn requests plotly'")
        print(f"Instalação: {result.output if result.output else 'Concluída'}")
        
        print("✅ Sandbox inicializado com sucesso!")
        
    async def create_analysis_script(self, metrics_data):
        """Cria script de análise personalizado para as métricas"""
        analysis_script = f'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Dados das métricas
metrics = {json.dumps(metrics_data)}

print("🔍 ANÁLISE DE MÉTRICAS DO PROMETHEUS")
print("=" * 50)

# Análise básica
if metrics:
    print(f"📊 Total de métricas coletadas: {{len(metrics)}}")
    
    # Criar DataFrame se houver dados de série temporal
    if 'data' in metrics and 'result' in metrics['data']:
        results = metrics['data']['result']
        if results:
            print(f"📈 Resultados encontrados: {{len(results)}}")
            
            # Análise detalhada para cada resultado
            for i, result in enumerate(results):
                if 'values' in result:
                    timestamps = [float(val[0]) for val in result['values']]
                    values = [float(val[1]) for val in result['values']]
                    
                    df = pd.DataFrame({{
                        'timestamp': pd.to_datetime(timestamps, unit='s'),
                        'value': values
                    }})
                    
                    print(f"\\n📋 Métrica {{i+1}}:")
                    print(f"  - Pontos de dados: {{len(df)}}")
                    print(f"  - Valor médio: {{df['value'].mean():.2f}}")
                    print(f"  - Valor máximo: {{df['value'].max():.2f}}")
                    print(f"  - Valor mínimo: {{df['value'].min():.2f}}")
                    
                    # Criar gráfico
                    plt.figure(figsize=(12, 6))
                    plt.plot(df['timestamp'], df['value'], marker='o', linewidth=2)
                    plt.title(f'Métrica {{i+1}} - Evolução Temporal')
                    plt.xlabel('Tempo')
                    plt.ylabel('Valor')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig(f'/tmp/metric_{{i+1}}.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"  ✅ Gráfico salvo: /tmp/metric_{{i+1}}.png")

print("\\n🎯 RELATÓRIO CONCLUÍDO!")
print(f"⏰ Análise realizada em: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
'''
        
        # Salvar o script no sandbox
        self.sandbox.write_file("/tmp/analysis.py", analysis_script)
        return "/tmp/analysis.py"
        
    async def execute_prometheus_query(self, query="up"):
        """Executa query no Prometheus e retorna dados"""
        query_script = f'''
import requests
import json

try:
    # Query no Prometheus
    response = requests.get('{self.prometheus_url}/api/v1/query?query={query}')
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Query executada com sucesso!")
        print(json.dumps(data, indent=2))
        
        # Salvar dados
        with open('/tmp/prometheus_data.json', 'w') as f:
            json.dump(data, f, indent=2)
            
    else:
        print(f"❌ Erro na query: {{response.status_code}}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erro de conexão: {{e}}")
    # Dados mock para teste
    mock_data = {{
        "status": "success",
        "data": {{
            "resultType": "vector",
            "result": [
                {{
                    "metric": {{"__name__": "up", "instance": "localhost:9090"}},
                    "value": [1638360000, "1"]
                }}
            ]
        }}
    }}
    
    with open('/tmp/prometheus_data.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    print("📝 Usando dados mock para demonstração")
'''
        
        self.sandbox.write_file("/tmp/query.py", query_script)
        result = self.sandbox.run_code("python", open("/tmp/query.py").read())
        
        # Ler dados salvos
        try:
            data_content = self.sandbox.read_file("/tmp/prometheus_data.json")
            return json.loads(data_content)
        except:
            return None
            
    async def run_analysis(self, query="up"):
        """Executa análise completa"""
        print(f"🚀 Iniciando análise para query: {query}")
        
        # Executar query no Prometheus
        metrics_data = await self.execute_prometheus_query(query)
        
        if metrics_data:
            # Criar e executar script de análise
            script_path = await self.create_analysis_script(metrics_data)
            
            print("🔄 Executando análise...")
            result = await self.sandbox.process.start({"cmd": f"python {script_path}"})
            
            print("\n📊 RESULTADO DA ANÁLISE:")
            print("=" * 50)
            print(result.stdout if result.stdout else "Análise concluída!")
            
            # Verificar se há gráficos gerados
            try:
                files = await self.sandbox.filesystem.list("/tmp")
                chart_files = [f for f in files if f.endswith('.png')]
                
                if chart_files:
                    print(f"\n📈 Gráficos gerados: {len(chart_files)}")
                    for chart in chart_files:
                        print(f"  - {chart}")
                        
            except Exception as e:
                print(f"⚠️  Erro ao listar arquivos: {e}")
                
        else:
            print("❌ Não foi possível obter dados do Prometheus")
            
    async def cleanup(self):
        """Limpa recursos"""
        if self.sandbox:
            await self.sandbox.close()
            print("🧹 Sandbox fechado")

async def main():
    """Função principal"""
    print("🚀 PROMETHEUS + E2B INTEGRATION")
    print("=" * 50)
    
    analytics = PrometheusE2BAnalytics()
    
    try:
        await analytics.initialize_sandbox()
        
        # Executar análises para diferentes métricas
        queries = [
            "up",  # Status dos targets
            "prometheus_notifications_total",  # Total de notificações
            "go_goroutines"  # Goroutines do Go
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            await analytics.run_analysis(query)
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        
    finally:
        await analytics.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
