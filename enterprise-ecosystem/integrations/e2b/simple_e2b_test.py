#!/usr/bin/env python3
"""
🔧 Script básico para integração E2B usando download_url e upload_url
"""
import os
from e2b import Sandbox

def simple_e2b_test():
    """Testa API do E2B com operações básicas"""
    
    # Verificar se a chave da API está configurada
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY não está configurada!")
        return
    
    print("🔧 TESTE BÁSICO DE INTEGRAÇÃO E2B")
    print("=" * 50)
    print(f"✅ E2B API Key: {api_key[:10]}...")
    
    try:
        # Criar sandbox
        sandbox = Sandbox()
        print("✅ Sandbox criado com sucesso!")
        
        # Exemplo de uso de upload_url e download_url
        print("🔄 Testando upload_url e download_url...")
        
        file_content = "print('Hello from E2B sandbox')"
        upload_response = sandbox.upload_url(content=file_content, filename='hello.py')
        if upload_response:
            print("✅ Função upload_url testada!")
            url = upload_response.get('url')
            print(f"🔄 Baixando via download_url de {url}...")
            code = sandbox.download_url(url=url)
            print(f"📋 Código baixado: {code}")
        else:
            print("❌ Erro no upload_url")

    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    simple_e2b_test()
