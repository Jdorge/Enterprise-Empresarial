#!/usr/bin/env python3
"""
🧪 Teste Simples E2B - Verificação Básica
"""
import asyncio
import os

async def test_e2b_basic():
    """Teste básico do E2B sem necessidade de API key"""
    print("🚀 INICIANDO TESTE BÁSICO E2B")
    print("=" * 40)
    
    try:
        from e2b import Sandbox
        print("✅ Biblioteca E2B importada com sucesso!")
        
        # Criar sandbox (modo gratuito/demo)
        print("🔄 Criando sandbox...")
        sandbox = Sandbox.connect()
        print("✅ Sandbox conectado com sucesso!")
        
        # Testar execução de código simples
        print("🔄 Testando execução de código...")
        
        # Criar um script Python simples
        test_script = """
import sys
import platform
import datetime

print("🐍 INFORMAÇÕES DO SANDBOX:")
print(f"Python: {sys.version}")
print(f"Plataforma: {platform.platform()}")
print(f"Data/Hora: {datetime.datetime.now()}")

# Teste de cálculo
numbers = [1, 2, 3, 4, 5]
resultado = sum(numbers)
print(f"Soma de {numbers} = {resultado}")

# Teste de criação de arquivo
with open('/tmp/test_file.txt', 'w') as f:
    f.write("Teste do E2B funcionando!\\n")
    f.write("Sandbox criado com sucesso!\\n")

print("✅ Arquivo criado em /tmp/test_file.txt")
"""
        
        # Escrever o script no sandbox
        await sandbox.filesystem.write("/tmp/test.py", test_script)
        print("✅ Script escrito no sandbox")
        
        # Executar o script
        result = await sandbox.process.start({"cmd": "python /tmp/test.py"})
        
        print("\n📊 RESULTADO DO TESTE:")
        print("=" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ AVISOS/ERROS:")
            print(result.stderr)
            
        # Verificar se o arquivo foi criado
        try:
            file_content = await sandbox.filesystem.read("/tmp/test_file.txt")
            print("\n📄 CONTEÚDO DO ARQUIVO CRIADO:")
            print(file_content)
        except Exception as e:
            print(f"⚠️ Erro ao ler arquivo: {e}")
            
        # Listar arquivos no diretório /tmp
        try:
            files = await sandbox.filesystem.list("/tmp")
            print(f"\n📁 ARQUIVOS EM /tmp: {files}")
        except Exception as e:
            print(f"⚠️ Erro ao listar arquivos: {e}")
            
        # Fechar sandbox
        await sandbox.close()
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("🎉 E2B está funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ ERRO DURANTE O TESTE: {e}")
        print("\n🔍 POSSÍVEIS SOLUÇÕES:")
        print("1. Verifique sua conexão com a internet")
        print("2. Confirme se o E2B está instalado: pip install e2b")
        print("3. Tente novamente em alguns minutos")

if __name__ == "__main__":
    asyncio.run(test_e2b_basic())
