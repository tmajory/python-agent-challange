#Procura o contexto dentro da Kb a partir da mensagem do usuário
from .parse_kb import parse_kb
from .get_keywords_message import get_keywords
import asyncio

async def get_context(message:str, parsed_kb:list):
    keywords = get_keywords(message)
    print(f"Keywords extraídas da mensagem: {keywords}")
    context = []
    for keyword in keywords:
        for section in parsed_kb:
            if keyword in section['title'].lower() or keyword in section['content'].lower():
                context.append(section['content'])#Adicona o conteúdo da seção correspondente ao contexto encontrado      
            else:
                context.append("Desculpe, não consegui encontrar uma resposta relevante na base de conhecimento.")
            break
    return context

if __name__ == "__main__":
    message = "Qual a composição de um átomo?"
    parsed_kb = asyncio.run(parse_kb())
    context = get_context(message, parsed_kb)
    print(context)