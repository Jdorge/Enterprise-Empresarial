# 🤝 Guia de Contribuição - Enterprise Empresarial

Obrigado por considerar contribuir com o Enterprise Empresarial! Este documento fornece diretrizes e melhores práticas para contribuições.

---

## 📋 Índice

- [Código de Conduta](#-código-de-conduta)
- [Como Contribuir](#-como-contribuir)
- [Processo de Desenvolvimento](#-processo-de-desenvolvimento)
- [Padrões de Código](#-padrões-de-código)
- [Commits e Branches](#-commits-e-branches)
- [Pull Requests](#-pull-requests)
- [Relatando Issues](#-relatando-issues)

---

## 📜 Código de Conduta

### Nosso Compromisso

Estamos comprometidos em fornecer um ambiente amigável, seguro e acolhedor para todos, independentemente de experiência, identidade de gênero, orientação sexual, deficiência, etnia, religião ou características semelhantes.

### Comportamentos Esperados

- ✅ Ser respeitoso e inclusivo
- ✅ Aceitar feedback construtivo
- ✅ Focar no que é melhor para a comunidade
- ✅ Demonstrar empatia com outros membros

### Comportamentos Inaceitáveis

- ❌ Linguagem ou imagens sexualizadas
- ❌ Comentários insultuosos ou depreciativos
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas de terceiros

---

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub

# Clone seu fork
git clone https://github.com/seu-usuario/enterprise-empresarial.git
cd enterprise-empresarial

# Adicione o repositório original como upstream
git remote add upstream https://github.com/Jdorge/enterprise-empresarial.git
```

### 2. Configure o Ambiente

```bash
# Copie o arquivo de ambiente
cp .env.example .env.local

# Instale as dependências
cd n8n-workflows
npm install

# Inicie os serviços
docker-compose up -d
```

### 3. Crie uma Branch

```bash
# Atualize seu main
git checkout main
git pull upstream main

# Crie uma branch para sua feature
git checkout -b feature/minha-nova-feature
```

---

## 🔄 Processo de Desenvolvimento

### Workflow de Desenvolvimento

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   1. Fork ──► 2. Branch ──► 3. Develop ──► 4. Test ──► 5. PR       │
│       │           │             │            │           │          │
│       ▼           ▼             ▼            ▼           ▼          │
│    Clone      feature/     Implement     npm test    Submit PR     │
│    Repo       branch       Changes       validate    for Review    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Tipos de Contribuição

| Tipo | Descrição | Branch Prefix |
|------|-----------|---------------|
| **Feature** | Nova funcionalidade | `feature/` |
| **Bugfix** | Correção de bug | `fix/` |
| **Docs** | Documentação | `docs/` |
| **Refactor** | Refatoração de código | `refactor/` |
| **Test** | Adicionar testes | `test/` |
| **Chore** | Tarefas de manutenção | `chore/` |

---

## 📝 Padrões de Código

### JavaScript/Node.js

```javascript
// ✅ BOM: Funções com nomes descritivos
const calculateLeadScore = (lead) => {
  // Implementação
};

// ❌ RUIM: Nomes genéricos
const calc = (x) => {
  // Implementação
};

// ✅ BOM: Constantes em SCREAMING_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;
const API_TIMEOUT_MS = 5000;

// ✅ BOM: Tratamento de erros
try {
  const result = await apiCall();
  return result;
} catch (error) {
  logger.error('API call failed', { error: error.message });
  throw new AppError('SERVICE_UNAVAILABLE', 'Could not connect to service');
}
```

### Workflows n8n

```json
// ✅ BOM: IDs descritivos
{
  "id": "validate-lead-input",
  "name": "Validate Lead Input"
}

// ❌ RUIM: IDs genéricos
{
  "id": "node1",
  "name": "Code"
}
```

### Documentação

```markdown
# ✅ BOM: Documentação clara
/**
 * Calcula o score de um lead baseado em múltiplos fatores.
 * 
 * @param {Object} lead - Dados do lead
 * @param {string} lead.email - Email do lead
 * @param {string} lead.company - Empresa do lead
 * @returns {number} Score calculado (0-100)
 * @throws {ValidationError} Se dados obrigatórios estiverem faltando
 * 
 * @example
 * const score = calculateLeadScore({
 *   email: 'ceo@company.com',
 *   company: 'Big Corp'
 * });
 * // Returns: 85
 */
```

---

## 📦 Commits e Branches

### Formato de Commit (Conventional Commits)

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit

| Tipo | Emoji | Descrição |
|------|-------|-----------|
| `feat` | ✨ | Nova feature |
| `fix` | 🐛 | Correção de bug |
| `docs` | 📚 | Documentação |
| `style` | 💄 | Formatação |
| `refactor` | ♻️ | Refatoração |
| `test` | 🧪 | Testes |
| `chore` | 🔧 | Manutenção |
| `perf` | ⚡ | Performance |
| `ci` | 👷 | CI/CD |
| `security` | 🔒 | Segurança |

### Exemplos

```bash
# ✅ BOM
git commit -m "feat(workflows): add SW1_LEADS lead scoring algorithm"
git commit -m "fix(router): handle invalid domain parameter"
git commit -m "docs(readme): update installation instructions"

# ❌ RUIM
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### Branches

```bash
# Formato
<tipo>/<ticket-ou-descricao>

# Exemplos
feature/ENT-123-lead-scoring
fix/ENT-456-null-pointer-validation
docs/update-api-reference
```

---

## 🔀 Pull Requests

### Template de PR

```markdown
## 📝 Descrição
[Descreva as mudanças realizadas]

## 🔗 Issue Relacionada
Fixes #123

## 📋 Tipo de Mudança
- [ ] 🐛 Bug fix
- [ ] ✨ Nova feature
- [ ] 📚 Documentação
- [ ] ♻️ Refatoração
- [ ] 🧪 Testes

## ✅ Checklist
- [ ] Meu código segue os padrões do projeto
- [ ] Eu executei os testes localmente
- [ ] Eu atualizei a documentação (se necessário)
- [ ] Eu adicionei testes para cobrir minhas mudanças

## 📸 Screenshots (se aplicável)
[Adicione screenshots aqui]

## 📝 Notas Adicionais
[Qualquer informação adicional]
```

### Processo de Review

1. **Submeta o PR** com descrição clara
2. **Aguarde CI/CD** - Todos os checks devem passar
3. **Review por Pares** - Mínimo 1 aprovação
4. **Resolva Comentários** - Responda e ajuste
5. **Merge** - Pelo maintainer ou autor após aprovação

---

## 🐛 Relatando Issues

### Template de Bug Report

```markdown
## 🐛 Descrição do Bug
[Descrição clara do problema]

## 📝 Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

## ✅ Comportamento Esperado
[O que deveria acontecer]

## ❌ Comportamento Atual
[O que está acontecendo]

## 📱 Ambiente
- OS: [ex: Windows 11]
- Node.js: [ex: 18.17.0]
- Docker: [ex: 24.0.5]
- n8n: [ex: 1.15.0]

## 📸 Screenshots/Logs
[Adicione evidências]

## 📝 Contexto Adicional
[Qualquer informação extra]
```

### Template de Feature Request

```markdown
## ✨ Descrição da Feature
[Descrição clara da feature desejada]

## 🎯 Problema que Resolve
[Qual problema esta feature resolve?]

## 💡 Solução Proposta
[Como você visualiza a solução?]

## 🔄 Alternativas Consideradas
[Outras abordagens que você considerou]

## 📝 Contexto Adicional
[Screenshots, mockups, exemplos]
```

---

## 📚 Recursos Adicionais

- [Documentação do n8n](https://docs.n8n.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

## ❓ Dúvidas?

- Abra uma [Discussion](https://github.com/Jdorge/enterprise-empresarial/discussions)
- Entre em contato: contribuicao@enterprise-empresarial.com

---

**Obrigado por contribuir! 🎉**
