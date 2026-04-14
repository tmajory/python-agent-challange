#Testa o fluxo de busca de informações na KB, a partir da mensagem do usuário, utilizando o método de parseamento da KB e o método de busca na mensagem.
import pytest
import sys
from app.tools.parse_kb import parse_kb
from app.tools.search_message_kb import parse_message

@pytest.mark.asyncio
async def test_search_message_kb():
    parsed_kb = await parse_kb()
    message = "O que é composição?"
    result = parse_message(message, parsed_kb)
    print(result)
    assert result != "Desculpe, não consegui encontrar uma resposta relevante na base de conhecimento."
    assert "Composição" in result


@pytest.mark.asyncio
async def test_search_message_kb_no_result():
    parsed_kb = await parse_kb()
    message = "qual é a composição do ar?"
    result = parse_message(message, parsed_kb)
    print(result)
    assert result == "Desculpe, não consegui encontrar uma resposta relevante na base de conhecimento."

if __name__ == "__main__":
    sys.exit(pytest.main(["-s"],plugins=["app.tests.search_test"]))