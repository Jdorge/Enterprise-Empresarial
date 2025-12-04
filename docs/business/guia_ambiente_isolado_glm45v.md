# Setup Rápido – Ambiente Isolado para GLM-4.5V (HuggingFace)

## 1. Ambiente Virtual Dedicado (opcional, mas recomendado)
Para evitar conflitos e garantir que só scripts GLM rodem nesta janela.

### Passo 1: Criar Ambiente
```powershell
python -m venv glm_env
```

### Passo 2: Ativar Ambiente
```powershell
.\glm_env\Scripts\Activate.ps1
```

### Passo 3: Instalar Dependências
```powershell
pip install openai
```

### Passo 4: Definir Token HuggingFace
```powershell
$env:HF_TOKEN="SEU_TOKEN_HF"
```

---

## 2. Mini-REPL Python para GLM-4.5V Somente
Salve como `repl_glm45v.py` e execute com `python repl_glm45v.py`.

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

while True:
    prompt = input("[GLM] Prompt (vazio = sair): ")
    if not prompt.strip():
        break
    completion = client.chat.completions.create(
        model="zai-org/GLM-4.5V:novita",
        messages=[{"role": "user", "content": prompt}],
    )
    print("\n[RESPOSTA] ", completion.choices[0].message.content, "\n")
```

- Basta rodar em terminal isolado. Só utilizará o GLM: todo input vira prompt.
- Pode adaptar para inputs multimodais.

---

## 3. Dicas de Fluxo
- Feche Warp ou outros agentes enquanto estiver nesse terminal, se quiser isolamento completo.
- Anote/registre outputs como desejar.
- Se for usar imagens, adapte o prompt para incluir o bloco type "image_url".

---

Pronto! Você tem ambiente dedicado, seguro e “GLM-ONLY” para pesquisas ou automações.
