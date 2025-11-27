#!/usr/bin/env python3
"""
🔍 Explorar detalhadamente os atributos da API E2B
"""
import os
from e2b import Sandbox

def explore_e2b_api():
    """Explora detalhadamente a API E2B"""
    
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY não está configurada!")
        return
    
    print("🔍 EXPLORANDO API E2B EM DETALHES")
    print("=" * 50)
    
    try:
        sandbox = Sandbox()
        print("✅ Sandbox criado com sucesso!")
        
        # Explorar atributo 'files'
        print("\n📁 Explorando atributo 'files':")
        if hasattr(sandbox, 'files'):
            files_obj = sandbox.files
            print(f"  - Tipo: {type(files_obj)}")
            files_methods = [m for m in dir(files_obj) if not m.startswith('_')]
            print(f"  - Métodos: {files_methods}")
            
        # Explorar atributo 'commands'
        print("\n⚡ Explorando atributo 'commands':")
        if hasattr(sandbox, 'commands'):
            commands_obj = sandbox.commands
            print(f"  - Tipo: {type(commands_obj)}")
            commands_methods = [m for m in dir(commands_obj) if not m.startswith('_')]
            print(f"  - Métodos: {commands_methods}")
            
        # Explorar atributo 'pty'
        print("\n💻 Explorando atributo 'pty':")
        if hasattr(sandbox, 'pty'):
            pty_obj = sandbox.pty
            print(f"  - Tipo: {type(pty_obj)}")
            pty_methods = [m for m in dir(pty_obj) if not m.startswith('_')]
            print(f"  - Métodos: {pty_methods}")
            
        # Informações do sandbox
        print("\n📋 Informações do sandbox:")
        try:
            info = sandbox.get_info()
            print(f"  - Info: {info}")
        except Exception as e:
            print(f"  - Erro ao obter info: {e}")
            
        try:
            is_running = sandbox.is_running()
            print(f"  - Está rodando: {is_running}")
        except Exception as e:
            print(f"  - Erro ao verificar status: {e}")
            
        # Testar diferentes formas de execução
        print("\n🔄 Testando execução de comandos...")
        
        # Tentar com commands
        if hasattr(sandbox, 'commands'):
            try:
                print("  - Testando sandbox.commands...")
                cmd_methods = [m for m in dir(sandbox.commands) if not m.startswith('_') and callable(getattr(sandbox.commands, m))]
                print(f"    Métodos executáveis: {cmd_methods}")
                
                # Tentar executar um comando simples
                if hasattr(sandbox.commands, 'run'):
                    result = sandbox.commands.run("echo 'Hello E2B'")
                    print(f"    Resultado run: {result}")
                elif hasattr(sandbox.commands, 'execute'):
                    result = sandbox.commands.execute("echo 'Hello E2B'")
                    print(f"    Resultado execute: {result}")
                    
            except Exception as e:
                print(f"    Erro com commands: {e}")
                
        # Tentar com pty
        if hasattr(sandbox, 'pty'):
            try:
                print("  - Testando sandbox.pty...")
                pty_methods = [m for m in dir(sandbox.pty) if not m.startswith('_') and callable(getattr(sandbox.pty, m))]
                print(f"    Métodos executáveis: {pty_methods}")
                
            except Exception as e:
                print(f"    Erro com pty: {e}")
                
        print("\n✅ Exploração concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante exploração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_e2b_api()
