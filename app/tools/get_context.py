#Procura o contexto dentro da Kb a partir da mensagem do usuário
from tools.parse_kb import parse_kb
from tools.get_keywords_message import get_keywords
import asyncio

async def get_context(message:str, parsed_kb:list):
    keywords = get_keywords(message)
    print(f"Keywords extraídas da mensagem: {keywords}")
    context = []
    for section in parsed_kb:
        if any(keyword in section['title'].lower() or keyword in section['content'].lower() for keyword in keywords):
            print(section['title'].lower())
            context.append({'title':section['title'], 'content': section['content']})#Adiciona o conteúdo da seção correspondente ao contexto encontrado
    return context
