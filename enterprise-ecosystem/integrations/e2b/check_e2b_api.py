#!/usr/bin/env python3
"""
🔍 Verificar métodos disponíveis na API E2B
"""
import os
from e2b import Sandbox

def check_e2b_api():
    """Verificar quais métodos estão disponíveis no objeto Sandbox"""
    
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY não está configurada!")
        return
    
    print("🔍 VERIFICANDO API E2B")
    print("=" * 50)
    
    try:
        # Criar sandbox
        sandbox = Sandbox()
        print("✅ Sandbox criado com sucesso!")
        
        # Listar todos os métodos e atributos disponíveis
        print("\n📋 Métodos e atributos disponíveis:")
        methods = [method for method in dir(sandbox) if not method.startswith('_')]
        
        for method in sorted(methods):
            attr = getattr(sandbox, method)
            if callable(attr):
                print(f"  🔧 {method}() - método")
            else:
                print(f"  📋 {method} - atributo")
        
        # Verificar se existem propriedades específicas
        print("\n🔍 Verificando propriedades específicas:")
        
        # Verificar se tem propriedades process, filesystem, etc.
        if hasattr(sandbox, 'process'):
            print(f"  ✅ sandbox.process: {type(sandbox.process)}")
            process_methods = [m for m in dir(sandbox.process) if not m.startswith('_')]
            print(f"    - Métodos: {process_methods}")
            
        if hasattr(sandbox, 'filesystem'):
            print(f"  ✅ sandbox.filesystem: {type(sandbox.filesystem)}")
            fs_methods = [m for m in dir(sandbox.filesystem) if not m.startswith('_')]
            print(f"    - Métodos: {fs_methods}")
            
        # Verificar versão da biblioteca
        import e2b
        if hasattr(e2b, '__version__'):
            print(f"\n📦 Versão E2B: {e2b.__version__}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_e2b_api()
