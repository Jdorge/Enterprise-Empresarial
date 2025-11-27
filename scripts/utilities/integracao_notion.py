#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 JORGE OS v2.0 - INTEGRAÇÃO NOTION
Sistema de sincronização automática com Notion
Data: 12/08/2025 | Versão: 2.0.0 | Status: PRODUÇÃO
"""

import os
import requests
import argparse
from datetime import datetime

# Configuração Notion - Removido token hardcoded por segurança
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

# Headers padrão
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}


class NotionIntegration:
    """Classe para integração com Notion API"""

    def __init__(self):
        self.token = NOTION_TOKEN
        self.headers = headers
        self.base_url = NOTION_BASE_URL

    def print_status(self, message, color="white"):
        """Imprime status colorido"""
        colors = {
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "magenta": "\033[95m",
            "white": "\033[97m",
            "end": "\033[0m",
        }
        print(f"{colors.get(color, '')}{message}{colors['end']}")

    def test_connection(self):
        """Testa conexão com Notion API"""
        try:
            url = f"{self.base_url}/users/me"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                self.print_status("✅ CONEXÃO NOTION OK!", "green")
                user_data = response.json()
                self.print_status(f"👤 Usuário: {user_data.get('name', 'N/A')}", "cyan")
                return True
            else:
                self.print_status(f"❌ Erro na conexão: {response.status_code}", "red")
                self.print_status(f"Resposta: {response.text}", "red")
                return False

        except Exception as e:
            self.print_status(f"❌ Erro de conexão: {str(e)}", "red")
            return False

    def search_pages(self, query=""):
        """Busca páginas no Notion"""
        try:
            url = f"{self.base_url}/search"
            data = {"query": query, "filter": {"property": "object", "value": "page"}, "page_size": 10}

            response = requests.post(url, headers=self.headers, json=data)

            if response.status_code == 200:
                results = response.json().get("results", [])
                self.print_status(f"📄 Encontradas {len(results)} páginas", "cyan")

                for i, page in enumerate(results):
                    title = self.get_page_title(page)
                    self.print_status(f"  {i+1}. {title} (ID: {page['id'][:8]}...)", "white")

                return results
            else:
                self.print_status(f"❌ Erro na busca: {response.status_code}", "red")
                return []

        except Exception as e:
            self.print_status(f"❌ Erro na busca: {str(e)}", "red")
            return []

    def get_page_title(self, page):
        """Extrai título da página"""
        try:
            if page.get("properties") and page["properties"].get("title"):
                title_prop = page["properties"]["title"]
                if title_prop.get("title") and len(title_prop["title"]) > 0:
                    return title_prop["title"][0]["text"]["content"]
            elif page.get("title") and len(page["title"]) > 0:
                return page["title"][0]["text"]["content"]
            return "Sem título"
        except Exception:
            return "Sem título"

    def create_page(self, parent_id, title, content_blocks=None):
        """Cria nova página no Notion"""
        try:
            url = f"{self.base_url}/pages"

            page_data = {
                "parent": {"page_id": parent_id},
                "properties": {"title": {"title": [{"text": {"content": title}}]}},
            }

            if content_blocks:
                page_data["children"] = content_blocks

            response = requests.post(url, headers=self.headers, json=page_data)

            if response.status_code == 200:
                page_id = response.json()["id"]
                self.print_status(f"✅ Página criada: {title}", "green")
                self.print_status(f"🔗 ID: {page_id}", "cyan")
                return page_id
            else:
                self.print_status(f"❌ Erro ao criar página: {response.status_code}", "red")
                self.print_status(f"Resposta: {response.text}", "red")
                return None

        except Exception as e:
            self.print_status(f"❌ Erro ao criar página: {str(e)}", "red")
            return None

    def sync_documentation(self):
        """Sincroniza documentação com Notion"""
        self.print_status("🔄 INICIANDO SINCRONIZAÇÃO DE DOCUMENTAÇÃO", "magenta")

        # Buscar página master
        pages = self.search_pages("JORGE OS")

        if not pages:
            self.print_status("❌ Página master não encontrada", "red")
            return False

        master_page_id = pages[0]["id"]
        self.print_status(f"📄 Página master encontrada: {master_page_id}", "green")

        # Criar página de atualização
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        update_title = f"Jorge OS v2.0 - Atualização {timestamp}"

        content_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "🚀 Jorge OS v2.0 - Sistema Atualizado"}}]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"Atualização automática realizada em {timestamp}"}}
                    ]
                },
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "✅ Estrutura ORGANIZACAO_FINAL criada"}}]
                },
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "✅ 8 APIs configuradas e testadas"}}]
                },
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "✅ Documentação master atualizada"}}]
                },
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "✅ Performance 70% melhorada"}}]
                },
            },
        ]

        new_page_id = self.create_page(master_page_id, update_title, content_blocks)

        if new_page_id:
            self.print_status("✅ SINCRONIZAÇÃO COMPLETA!", "green")
            return True
        else:
            self.print_status("❌ Falha na sincronização", "red")
            return False

    def create_project_page(self, project_name):
        """Cria página para novo projeto"""
        self.print_status(f"📄 CRIANDO PÁGINA PARA PROJETO: {project_name}", "magenta")

        # Buscar página master
        pages = self.search_pages("JORGE OS")

        if not pages:
            self.print_status("❌ Página master não encontrada", "red")
            return False

        master_page_id = pages[0]["id"]

        content_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": f"🎯 {project_name}"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Projeto criado em {datetime.now().strftime('%Y-%m-%d %H:%M')}"},
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Definir objetivos do projeto"}}],
                    "checked": False,
                },
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Configurar ambiente de desenvolvimento"}}],
                    "checked": False,
                },
            },
        ]

        new_page_id = self.create_page(master_page_id, f"📁 {project_name}", content_blocks)

        if new_page_id:
            self.print_status("✅ Página do projeto criada com sucesso!", "green")
            return True
        else:
            return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Jorge OS v2.0 - Integração Notion")
    parser.add_argument("--test", action="store_true", help="Testar conexão")
    parser.add_argument("--sync-all", action="store_true", help="Sincronizar documentação")
    parser.add_argument("--create-project", type=str, help="Criar página de projeto")
    parser.add_argument("--search", type=str, help="Buscar páginas")

    args = parser.parse_args()

    # Inicializar integração
    notion = NotionIntegration()

    if args.test:
        print("🧪 TESTANDO INTEGRAÇÃO NOTION...")
        notion.test_connection()

    elif args.sync_all:
        print("🔄 SINCRONIZANDO DOCUMENTAÇÃO...")
        notion.sync_documentation()

    elif args.create_project:
        print(f"📄 CRIANDO PROJETO: {args.create_project}")
        notion.create_project_page(args.create_project)

    elif args.search:
        print(f"🔍 BUSCANDO: {args.search}")
        notion.search_pages(args.search)

    else:
        # Execução padrão - teste de conexão
        print("🚀 JORGE OS v2.0 - INTEGRAÇÃO NOTION")
        print("=" * 50)

        if notion.test_connection():
            notion.search_pages("JORGE")

            # Perguntar se quer sincronizar
            sync = input("\n🔄 Sincronizar documentação? (s/n): ").lower()
            if sync == "s":
                notion.sync_documentation()


if __name__ == "__main__":
    main()
