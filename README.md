# Python Agent Challenge

API REST construída com FastAPI que responde perguntas em linguagem natural com base em uma knowledge base Markdown, utilizando um LLM com fallback automático entre provedores.

---

## Visão geral

O agente recebe uma pergunta via POST, extrai palavras-chave, recupera contexto relevante da KB e envia tudo ao LLM, que retorna uma resposta estruturada com rastreabilidade da fonte consultada.

```
POST /messages
    │
    ├── Extração de palavras-chave da mensagem
    ├── Busca de contexto na Knowledge Base
    └── LLM (OpenRouter → Groq como fallback)
            │
            └── { "answer": "...", "sources": [...] }
```

---

## Stack

- **Python 3.12**
- **FastAPI** — framework HTTP
- **OpenAI SDK** — cliente compatível com OpenRouter e Groq
- **Redis** — preparado para armazenamento de sessão
- **Docker + Docker Compose** — ambiente reproduzível
- **pytest + pytest-asyncio** — testes unitários e de integração

---

## Estrutura do projeto

```
.
├── app/
│   ├── main.py               # Endpoint /messages
│   ├── llm/
│   │   ├── llm_client.py     # Cliente LLM com fallback OpenRouter → Groq
│   │   └── llm_tools.py      # Montagem do prompt e parse da resposta
│   ├── tools/
│   │   ├── parse_kb.py       # Parse da Knowledge Base Markdown
│   │   ├── get_context.py    # Recuperação de contexto relevante
│   │   ├── get_keywords_message.py  # Extração de palavras-chave
│   │   └── get_kb_text.py    # Fetch do conteúdo da KB
│   └── tests/
│       ├── conftest.py
│       └── test.py
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

---

## Decisões técnicas

### Independência de módulos
Cada responsabilidade tem seu próprio arquivo: parse da KB, extração de contexto, extração de palavras-chave, cliente LLM e tools LLM são todos separados. Isso reduz acoplamento e facilita testes unitários independentes.

### Tratamento da mensagem
Em vez de buscar a mensagem inteira na KB, o agente extrai palavras-chave antes da busca de contexto. Isso reduz falsos positivos e torna a recuperação mais precisa. As instruções de sistema do LLM reforçam o escopo do assistente, evitando respostas inventadas quando o contexto é insuficiente.

### Fallback de LLM
O `LLMClient` tenta o OpenRouter primeiro. Se receber `RateLimitError` (limite diário de modelos gratuitos) ou `AuthenticationError`, faz fallback automático para o Groq — sem intervenção manual.

```python
try:
    return self._openrouter.chat.completions.create(...)
except (RateLimitError, AuthenticationError):
    return self._groq.chat.completions.create(...)
```

### Resposta estruturada
O LLM sempre retorna JSON com contrato fixo:

```json
{
  "answer": "Resposta baseada no contexto.",
  "sources": [{ "section": "Nome da seção consultada" }]
}
```

Quando não há contexto suficiente:

```json
{
  "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
  "sources": []
}
```

### Session ID
O campo `session_id` já está no contrato da requisição, preparado para uma evolução futura com memória de conversa via Redis.

---

## Como executar

### Pré-requisitos
- Docker e Docker Compose instalados
- Arquivo `.env` na raiz do projeto (veja `.env.example` abaixo)

### Variáveis de ambiente

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.3-8b-instruct:free

GROQ_API_KEY=gsk_...
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

KB_URL=https://raw.githubusercontent.com/.../knowledge_base.md

HOST=0.0.0.0
PORT=8000
```

### Subindo a aplicação

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

---

## Como testar

### Swagger UI
Acesse `http://localhost:8000/docs` e use o botão **Try it out** no endpoint `POST /messages`.

### curl

```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é composição em Python?"}'
```

### Testes automatizados

```bash
# Na raiz do projeto
pip install -r requirements.txt
pytest
```

Os testes cobrem: fluxo completo do endpoint, fallback OpenRouter → Groq, parse de JSON com e sem markdown, e casos de erro.

---

## Evoluções possíveis

- Implementar memória de sessão via Redis usando o `session_id`
- Melhorar `get_context` com scoring de relevância para reduzir falsos positivos
- Adicionar streaming de resposta no endpoint
- Expandir a KB com novos domínios de conhecimento
# python-agent-challange
Repositorio para o desafio tecnico para a vaga de desenvolvedor chatbot ai

## Decisões tecnicas
### Independência de funções
Optei por ter um arquivo em separado para cada tool, como por exemplo extração de contexto, palavras chaves, parse da KB, também optei por separa o llm client do llm tools, ainda que tenha definido eles como classes.

### Tratamento da mensagem
Optei por filtrar palavras chaves dentro da mensagem e a partir delas extrair contexto, para não procurar toda a mensagem dentro da KB, ainda que isso gerasse erro na resposta do LLM, para contornar passei regras bem definidas do tipo de assistente que o modelo deve ser, consegui evitar falsos positivos de contexto dessa forma.

### LLM MODEL
Utilizei um modelo gratuito dentro da openrouter, por questões de liberdade de uso em testes da aplicação.

## Evoluções possiveis
Não implementei session id, mas deixei o projeto pronto para uma eventual evolução neste sentido, também pode fazer sentido melhorar o método get_context para evitar falsos positivos ao retornar contexto.

## Como Testar
1. Para testar a aplicação necessário iniciar o container docker e acessar localhost:8000/docs 
Sendo este endereço a página de documentação da FastAPI onde ao selecionar a opção try it out é possível enviar a requisição para a api e visualizar o response.
2. Também é possível realizar testes via postman ou ainda um script python que realize a requisição.



