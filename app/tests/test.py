import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from openai import RateLimitError, AuthenticationError

from main import app
# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_PARSED_KB = [
    {"section": "Composição", "content": "Composição é quando uma função/classe utiliza outra instância."},
    {"section": "Herança", "content": "Herança permite compartilhar atributos e comportamentos."},
]

MOCK_CONTEXT = [{"section": "Composição", "content": "Composição é quando uma função/classe utiliza outra instância."}]

VALID_LLM_RESPONSE = json.dumps({
    "answer": "Composição é quando uma função usa outra instância para executar parte do trabalho.",
    "sources": [{"section": "Composição"}]
})

FALLBACK_LLM_RESPONSE = json.dumps({
    "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
    "sources": []
})


@pytest.fixture
def client_transport():
    return ASGITransport(app=app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_rate_limit_error():
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}
    mock_response.json.return_value = {"error": {"message": "daily free limit reached"}}
    return RateLimitError("daily free limit reached", response=mock_response, body=None)


def make_auth_error():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.headers = {}
    mock_response.json.return_value = {"error": {"message": "invalid api key"}}
    return AuthenticationError("invalid api key", response=mock_response, body=None)


# ---------------------------------------------------------------------------
# Testes do endpoint /messages
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_messages_retorna_resposta_valida(client_transport):
    """Fluxo feliz: OpenRouter responde corretamente."""
    with (
        patch("main.parse_kb", new_callable=AsyncMock, return_value=MOCK_PARSED_KB),
        patch("main.get_context", new_callable=AsyncMock, return_value=MOCK_CONTEXT),
        patch("llm.llm_tools.LLMClient") as MockLLMClient,
    ):
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = VALID_LLM_RESPONSE

        async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
            response = await ac.post("/messages", json={"message": "O que é composição?"})

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "sources" in body
    assert isinstance(body["sources"], list)


@pytest.mark.asyncio
async def test_messages_sem_contexto_retorna_fallback(client_transport):
    """Quando get_context retorna vazio, LLM deve retornar fallback."""
    with (
        patch("main.parse_kb", new_callable=AsyncMock, return_value=MOCK_PARSED_KB),
        patch("main.get_context", new_callable=AsyncMock, return_value=[]),
        patch("llm.llm_tools.LLMClient") as MockLLMClient,
    ):
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = FALLBACK_LLM_RESPONSE

        async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
            response = await ac.post("/messages", json={"message": "Qual a temperatura do sol?"})

    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == []
    assert "Não encontrei" in body["answer"]


@pytest.mark.asyncio
async def test_messages_com_session_id(client_transport):
    """Endpoint aceita session_id opcional sem quebrar."""
    with (
        patch("main.parse_kb", new_callable=AsyncMock, return_value=MOCK_PARSED_KB),
        patch("main.get_context", new_callable=AsyncMock, return_value=MOCK_CONTEXT),
        patch("llm.llm_tools.LLMClient") as MockLLMClient,
    ):
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = VALID_LLM_RESPONSE

        async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
            response = await ac.post(
                "/messages",
                json={"message": "O que é herança?", "session_id": "abc-123"}
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_messages_payload_invalido(client_transport):
    """Payload sem o campo obrigatório 'message' deve retornar 422."""
    async with AsyncClient(transport=client_transport, base_url="http://test") as ac:
        response = await ac.post("/messages", json={"session_id": "abc-123"})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Testes do fallback LLMClient (OpenRouter → Groq)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_llmclient_fallback_rate_limit():
    """RateLimitError no OpenRouter deve acionar o Groq."""
    with (
        patch("llm.llm_client.OpenAI") as MockOpenAI,
    ):
        mock_openrouter = MagicMock()
        mock_groq = MagicMock()

        mock_openrouter.chat.completions.create.side_effect = make_rate_limit_error()
        mock_groq.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=VALID_LLM_RESPONSE))]
        )

        MockOpenAI.side_effect = [mock_openrouter, mock_groq]

        from llm.llm_client import LLMClient
        llm = LLMClient()
        result = llm.chat(messages=[{"role": "user", "content": "teste"}])

    assert "answer" in result


@pytest.mark.asyncio
async def test_llmclient_fallback_auth_error():
    """AuthenticationError no OpenRouter deve acionar o Groq."""
    with (
        patch("llm.llm_client.OpenAI") as MockOpenAI,
    ):
        mock_openrouter = MagicMock()
        mock_groq = MagicMock()

        mock_openrouter.chat.completions.create.side_effect = make_auth_error()
        mock_groq.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=VALID_LLM_RESPONSE))]
        )

        MockOpenAI.side_effect = [mock_openrouter, mock_groq]

        from llm.llm_client import LLMClient
        llm = LLMClient()
        result = llm.chat(messages=[{"role": "user", "content": "teste"}])

    assert "answer" in result


@pytest.mark.asyncio
async def test_llmclient_sem_fallback_quando_openrouter_ok():
    """Se OpenRouter responder com sucesso, Groq não deve ser chamado."""
    with (
        patch("llm.llm_client.OpenAI") as MockOpenAI,
    ):
        mock_openrouter = MagicMock()
        mock_groq = MagicMock()

        mock_openrouter.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=VALID_LLM_RESPONSE))]
        )

        MockOpenAI.side_effect = [mock_openrouter, mock_groq]

        from llm.llm_client import LLMClient
        llm = LLMClient()
        llm.chat(messages=[{"role": "user", "content": "teste"}])

    mock_groq.chat.completions.create.assert_not_called()


# ---------------------------------------------------------------------------
# Testes do LLMTools (parse do JSON)
# ---------------------------------------------------------------------------

def test_llmtools_parse_resposta_valida():
    """LLMTools deve parsear corretamente um JSON válido retornado pelo LLMClient."""
    with patch("llm.llm_tools.LLMClient") as MockLLMClient:
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = VALID_LLM_RESPONSE

        from llm.llm_tools import LLMTools
        tools = LLMTools()
        result = tools.send_message("O que é composição?", MOCK_CONTEXT)

    assert result["answer"] != ""
    assert isinstance(result["sources"], list)


def test_llmtools_parse_resposta_com_markdown():
    """LLMTools deve limpar markdown code blocks antes de parsear."""
    wrapped = f"```json\n{VALID_LLM_RESPONSE}\n```"

    with patch("llm.llm_tools.LLMClient") as MockLLMClient:
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = wrapped

        from llm.llm_tools import LLMTools
        tools = LLMTools()
        result = tools.send_message("O que é composição?", MOCK_CONTEXT)

    assert "answer" in result
    assert "sources" in result


def test_llmtools_parse_json_invalido_retorna_erro():
    """JSON malformado deve retornar dict com chave 'error'."""
    with patch("llm.llm_tools.LLMClient") as MockLLMClient:
        mock_instance = MockLLMClient.return_value
        mock_instance.chat.return_value = "isso não é json válido"

        from llm.llm_tools import LLMTools
        tools = LLMTools()
        result = tools.send_message("O que é composição?", MOCK_CONTEXT)

    assert "error" in result