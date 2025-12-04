# Prompt para Criação de Plataforma Frontend

**Instrução:** Copie e cole o texto abaixo em uma ferramenta de IA (como ChatGPT, Claude ou o próprio Antigravity em uma nova sessão) para gerar o código do frontend.

---

## 🤖 PROMPT DE DESENVOLVIMENTO: PLATAFORMA ENTERPRISE

**Role:** Você é um Engenheiro de Frontend Sênior e Especialista em UX/UI.

**Objetivo:** Criar uma aplicação web moderna (Frontend) para o sistema "Enterprise Empresarial". Esta plataforma servirá como o painel de controle para gerenciar agentes de IA, workflows e visualizar métricas.

**Stack Tecnológica:**
- **Framework:** Next.js 14 (App Router)
- **Linguagem:** TypeScript
- **Estilização:** Tailwind CSS + Shadcn/UI (para componentes premium)
- **Ícones:** Lucide React
- **Gerenciamento de Estado:** Zustand ou React Query
- **Gráficos:** Recharts (para métricas)

**Design & Tema:**
- **Referência Visual:** [INSIRA AQUI O LINK OU NOME DO SITE QUE VOCÊ QUER COPIAR O TEMA]
- **Estética:** Minimalista, "Dark Mode" profundo, com acentos em gradiente (Roxo/Azul Neon ou Dourado/Preto, conforme referência).
- **Layout:** Sidebar lateral de navegação, Header com perfil e notificações, Área central de conteúdo dinâmico.

**Funcionalidades Necessárias:**

1.  **Dashboard Executivo (Home):**
    - Cards com KPIs principais (Total Requisições, Custo IA, Workflows Ativos).
    - Gráfico de linha (Recharts) mostrando atividade nas últimas 24h.
    - Lista de atividades recentes ("Agente Comercial gerou proposta X").

2.  **Central de Agentes (AI Hub):**
    - Interface de Chat (estilo ChatGPT) para conversar com o "Router Agent".
    - Seletor de Agente (Comercial, Varejo, Suporte).
    - Visualização de logs de pensamento da IA (Chain of Thought).

3.  **Monitor de Workflows:**
    - Tabela listando execuções do n8n.
    - Status visual (Sucesso/Falha/Em andamento).
    - Botão para "Disparar Manualmente" um workflow.

4.  **Configurações:**
    - Formulário para editar chaves de API (OpenAI, Anthropic) - *apenas visual, não salvar real*.
    - Toggle para ativar/desativar agentes específicos.

**Integração (Mock):**
- Como o backend (n8n/Python) roda localmente, crie serviços de API mockados ou prepare para conectar em `http://localhost:8000` e `http://localhost:5678`.

**Entregável:**
- Estrutura de pastas do projeto Next.js.
- Código dos componentes principais (Sidebar, Dashboard, ChatInterface).
- Arquivo `globals.css` com as variáveis de cor do tema solicitado.

**Instrução Adicional:**
Por favor, foque na **beleza visual** e na **fluidez das animações**. O sistema deve parecer uma ferramenta "Enterprise Grade" de alto nível.

---
