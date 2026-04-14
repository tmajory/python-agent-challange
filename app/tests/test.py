#Realiza teste geral, recebendo mensagem buscando contexto e gerando resposta através do llm
import sys
import pytest
from app.llm.llm_tools import LLMTools
from app.llm.llm_client import LLMClient
from app.tools.get_context import get_context
from app.tools.parse_kb import parse_kb

@pytest.mark.asyncio
async def test_integration():
    #Teste com mensagem que retorna resposta relevante
    message = "O que é composição?"
    llm_tools = LLMTools()
    parsed_kb = await parse_kb()
    context = await get_context(message, parsed_kb)
    response = llm_tools.send_message(message, context)
    print(response)
    assert "answer" in response.choices[0].message.content


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "-s"]))