#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jorge OS v2.0 - Verificador de APIs
Data: 12/08/2025
Verifica status de todas as APIs configuradas no sistema
"""

import os
import sys
import json
import yaml
import requests
from datetime import datetime
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "04_CONFIGURACOES"
LOGS_DIR = BASE_DIR / "05_LOGS_RELATORIOS"

def load_config():
    """Carrega configuração do sistema"""
    config_file = CONFIG_DIR / "config.yaml"
    if not config_file.exists():
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def check_env_vars():
    """Verifica variáveis de ambiente"""
    required_vars = [
        'OPENAI_API_KEY',
        'NOTION_TOKEN', 
        'XAI_API_KEY',
        'GEMINI_API_KEY',
        'E2B_API_KEY',
        'OPENROUTER_API_KEY',
        'PERPLEXITY_API_KEY',
        'SCRAPELESS_KEY'
    ]
    
    status = {}
    for var in required_vars:
        value = os.getenv(var)
        if value:
            status[var] = {
                'configured': True,
                'preview': f"{value[:10]}..." if len(value) > 10 else "***"
            }
        else:
            status[var] = {
                'configured': False,
                'preview': None
            }
    
    return status

def check_connectivity():
    """Verifica conectividade básica"""
    try:
        response = requests.get('https://httpbin.org/get', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_openai():
    """Verifica API OpenAI"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'status': 'NOT_CONFIGURED', 'error': 'API key não encontrada'}
    
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=5)
        if response.status_code == 200:
            return {'status': 'OK', 'models': len(response.json().get('data', []))}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def check_notion():
    """Verifica API Notion"""
    token = os.getenv('NOTION_TOKEN')
    if not token:
        return {'status': 'NOT_CONFIGURED', 'error': 'Token não encontrado'}
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Notion-Version': '2022-06-28'
        }
        response = requests.get('https://api.notion.com/v1/users/me', headers=headers, timeout=5)
        if response.status_code == 200:
            return {'status': 'OK', 'user': response.json().get('name', 'Unknown')}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🔍 JORGE OS v2.0 - Verificador de APIs")
    print("="*60)
    
    # Criar diretório de logs se não existir
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Carregar configuração
    config = load_config()
    if not config:
        sys.exit(1)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'system': 'Jorge OS v2.0',
        'checks': {}
    }
    
    # 1. Verificar conectividade
    print("\n📡 Verificando conectividade...")
    connectivity = check_connectivity()
    results['checks']['connectivity'] = connectivity
    print(f"   {'✅' if connectivity else '❌'} Internet: {'OK' if connectivity else 'FALHOU'}")
    
    # 2. Verificar variáveis de ambiente
    print("\n🔐 Verificando variáveis de ambiente...")
    env_status = check_env_vars()
    results['checks']['environment'] = env_status
    
    configured = sum(1 for v in env_status.values() if v['configured'])
    total = len(env_status)
    print(f"   📊 {configured}/{total} APIs configuradas")
    
    for key, status in env_status.items():
        icon = "✅" if status['configured'] else "❌"
        print(f"   {icon} {key}: {'Configurada' if status['configured'] else 'Não configurada'}")
    
    # 3. Verificar APIs específicas
    print("\n🚀 Testando APIs principais...")
    
    # OpenAI
    print("   🤖 OpenAI...")
    openai_status = check_openai()
    results['checks']['openai'] = openai_status
    if openai_status['status'] == 'OK':
        print(f"      ✅ OK - {openai_status['models']} modelos disponíveis")
    else:
        print(f"      ❌ {openai_status['status']}")
    
    # Notion
    print("   📝 Notion...")
    notion_status = check_notion()
    results['checks']['notion'] = notion_status
    if notion_status['status'] == 'OK':
        print(f"      ✅ OK - Usuário: {notion_status.get('user', 'Unknown')}")
    else:
        print(f"      ❌ {notion_status['status']}")
    
    # 4. Salvar resultados
    status_file = LOGS_DIR / "apis_status.json"
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Status salvo em: {status_file}")
    
    # 5. Resumo final
    print("\n" + "="*60)
    if connectivity and configured >= 6:
        print("✅ SISTEMA PRONTO PARA USO!")
    elif connectivity and configured >= 4:
        print("⚠️ SISTEMA PARCIALMENTE CONFIGURADO")
    else:
        print("❌ SISTEMA PRECISA DE CONFIGURAÇÃO")
    print("="*60 + "\n")
    
    return 0 if connectivity else 1

if __name__ == "__main__":
    sys.exit(main())
