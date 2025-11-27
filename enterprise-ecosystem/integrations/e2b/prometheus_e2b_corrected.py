#!/usr/bin/env python3
"""
🚀 Integração E2B com Prometheus Analytics - Versão Corrigida
Análise avançada de métricas do Prometheus usando E2B sandboxes com API correta
"""
import json
import os
from datetime import datetime
from e2b import Sandbox

class PrometheusE2BAnalytics:
    def __init__(self):
        self.sandbox = None
        self.prometheus_url = "http://localhost:9090"
        
    def initialize_sandbox(self):
        """Inicializa o sandbox E2B com as dependências necessárias"""
        print("🔄 Inicializando sandbox E2B...")
        self.sandbox = Sandbox()
        
        # Instalar dependências no sandbox
        print("📦 Instalando dependências...")
        result = self.sandbox.commands.run("pip install pandas matplotlib seaborn requests plotly")
        print(f"✅ Instalação concluída: {result.exit_code == 0}")
        
        if result.stderr:
            print(f"⚠️ Avisos: {result.stderr[:200]}...")
        
        print("✅ Sandbox inicializado com sucesso!")
        
    def create_analysis_script(self, metrics_data):
        """Cria script de análise personalizado para as métricas"""
        analysis_script = f'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime

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
                metric = result.get('metric', {{}})
                value = result.get('value', [0, "0"])
                
                print(f"\\n📋 Métrica {{i+1}}:")
                print(f"  - Nome: {{metric.get('__name__', 'N/A')}}")
                print(f"  - Instance: {{metric.get('instance', 'N/A')}}")
                print(f"  - Job: {{metric.get('job', 'N/A')}}")
                print(f"  - Valor atual: {{value[1]}}")
                print(f"  - Timestamp: {{value[0]}}")
                
                # Se houver dados de série temporal (values)
                if 'values' in result:
                    timestamps = [float(val[0]) for val in result['values']]
                    values = [float(val[1]) for val in result['values']]
                    
                    df = pd.DataFrame({{
                        'timestamp': pd.to_datetime(timestamps, unit='s'),
                        'value': values
                    }})
                    
                    print(f"  - Pontos de dados: {{len(df)}}")
                    if len(df) > 0:
                        print(f"  - Valor médio: {{df['value'].mean():.2f}}")
                        print(f"  - Valor máximo: {{df['value'].max():.2f}}")
                        print(f"  - Valor mínimo: {{df['value'].min():.2f}}")
                        
                        # Criar gráfico
                        try:
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
                        except Exception as e:
                            print(f"  ⚠️ Erro ao criar gráfico: {{e}}")

print("\\n🎯 RELATÓRIO CONCLUÍDO!")
print(f"⏰ Análise realizada em: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
'''
        
        # Salvar o script no sandbox
        self.sandbox.files.write("/tmp/analysis.py", analysis_script)
        return "/tmp/analysis.py"
        
    def execute_prometheus_query(self, query="up"):
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
                    "metric": {{"__name__": "up", "instance": "localhost:9090", "job": "prometheus"}},
                    "value": [1672531200, "1"]
                }},
                {{
                    "metric": {{"__name__": "up", "instance": "localhost:3000", "job": "grafana"}},
                    "value": [1672531200, "1"]
                }}
            ]
        }}
    }}
    
    with open('/tmp/prometheus_data.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    print("📝 Usando dados mock para demonstração")
'''
        
        self.sandbox.files.write("/tmp/query.py", query_script)
        result = self.sandbox.commands.run("python /tmp/query.py")
        
        print(f"🔍 Resultado da query: {result.stdout}")
        if result.stderr:
            print(f"⚠️ Avisos: {result.stderr}")
        
        # Ler dados salvos
        try:
            data_content = self.sandbox.files.read("/tmp/prometheus_data.json")
            return json.loads(data_content)
        except Exception as e:
            print(f"❌ Erro ao ler dados: {e}")
            return None
            
    def run_analysis(self, query="up"):
        """Executa análise completa"""
        print(f"\n🚀 INICIANDO ANÁLISE PARA QUERY: {query}")
        print("=" * 60)
        
        # Executar query no Prometheus
        metrics_data = self.execute_prometheus_query(query)
        
        if metrics_data:
            # Criar e executar script de análise
            script_path = self.create_analysis_script(metrics_data)
            
            print("\n🔄 Executando análise...")
            result = self.sandbox.commands.run(f"python {script_path}")
            
            print("\n📊 RESULTADO DA ANÁLISE:")
            print("=" * 50)
            print(result.stdout)
            
            if result.stderr:
                print(f"⚠️ Avisos: {result.stderr}")
            
            # Verificar se há gráficos gerados
            try:
                files_result = self.sandbox.commands.run("ls -la /tmp/*.png 2>/dev/null || echo 'Nenhum gráfico encontrado'")
                if "metric_" in files_result.stdout:
                    print(f"\n📈 Gráficos gerados:")
                    print(files_result.stdout)
                else:
                    print(f"\n📋 Status dos arquivos: {files_result.stdout}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao listar arquivos: {e}")
                
        else:
            print("❌ Não foi possível obter dados do Prometheus")
            
    def cleanup(self):
        """Limpa recursos"""
        if self.sandbox:
            try:
                self.sandbox.kill()
                print("🧹 Sandbox finalizado")
            except:
                print("🧹 Sandbox já estava finalizado")

def main():
    """Função principal"""
    print("🚀 PROMETHEUS + E2B INTEGRATION - VERSÃO CORRIGIDA")
    print("=" * 60)
    
    # Verificar se a chave da API está configurada
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY não está configurada!")
        return
    
    analytics = PrometheusE2BAnalytics()
    
    try:
        analytics.initialize_sandbox()
        
        # Executar análises para diferentes métricas
        queries = [
            "up",  # Status dos targets
            "prometheus_notifications_total",  # Total de notificações
            "go_goroutines"  # Goroutines do Go
        ]
        
        for query in queries:
            analytics.run_analysis(query)
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        analytics.cleanup()

if __name__ == "__main__":
    main()
