#!/usr/bin/env python3
"""
🚀 Teste Simples de Integração E2B com Prometheus
Baseado no script que funcionou anteriormente
"""
import os
from e2b import Sandbox

def test_prometheus_analysis():
    """Testa análise básica de dados do Prometheus no E2B"""
    
    # Verificar se a chave da API está configurada
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY não está configurada!")
        return
    
    print("🚀 TESTE DE INTEGRAÇÃO PROMETHEUS + E2B")
    print("=" * 50)
    print(f"✅ E2B API Key: {api_key[:10]}...")
    
    try:
        # Criar sandbox
        print("🔄 Criando sandbox E2B...")
        sandbox = Sandbox()
        print("✅ Sandbox criado com sucesso!")
        
        # Dados mock do Prometheus
        mock_prometheus_data = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "up", "instance": "localhost:9090", "job": "prometheus"},
                        "value": [1672531200, "1"]
                    },
                    {
                        "metric": {"__name__": "up", "instance": "localhost:3000", "job": "grafana"},
                        "value": [1672531200, "1"]
                    }
                ]
            }
        }
        
        # Script de análise para executar no sandbox
        analysis_code = f"""
import json

# Dados mock do Prometheus
data = {mock_prometheus_data}

print("🔍 ANÁLISE DE MÉTRICAS DO PROMETHEUS")
print("=" * 50)

if data['status'] == 'success':
    results = data['data']['result']
    print(f"📊 Total de métricas encontradas: {{len(results)}}")
    
    for i, result in enumerate(results):
        metric = result['metric']
        value = result['value']
        
        print(f"\\n📋 Métrica {{i+1}}:")
        print(f"  - Nome: {{metric.get('__name__', 'N/A')}}")
        print(f"  - Instance: {{metric.get('instance', 'N/A')}}")
        print(f"  - Job: {{metric.get('job', 'N/A')}}")
        print(f"  - Valor: {{value[1]}}")
        print(f"  - Timestamp: {{value[0]}}")

print("\\n🎯 ANÁLISE CONCLUÍDA!")
"""
        
        print("🔄 Executando análise no sandbox...")
        result = sandbox.run(analysis_code)
        
        print("\n📊 RESULTADO DA ANÁLISE:")
        print("=" * 50)
        print(result.output)
        
        if result.error:
            print("⚠️ Erros encontrados:")
            print(result.error)
            
        # Teste de instalação de pacotes
        print("\n🔄 Testando instalação de pandas...")
        install_result = sandbox.run("pip list | grep pandas || pip install pandas")
        print(f"Instalação pandas: {install_result.output[:100]}...")
        
        # Teste com pandas
        pandas_test = """
try:
    import pandas as pd
    print("✅ Pandas importado com sucesso!")
    
    # Criar DataFrame simples
    df = pd.DataFrame({'metric': ['up', 'cpu_usage'], 'value': [1, 0.75]})
    print("📊 DataFrame criado:")
    print(df.to_string())
    
except ImportError:
    print("❌ Pandas não está disponível")
except Exception as e:
    print(f"❌ Erro: {e}")
"""
        
        print("\n🔄 Testando pandas...")
        pandas_result = sandbox.run(pandas_test)
        print(pandas_result.output)
        
        print("\n✅ Teste completo!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prometheus_analysis()
