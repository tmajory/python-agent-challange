#Método de parseamento da KB, para extrair informações relevantes e formatá-las para o LLM
import re
import asyncio
from unidecode import unidecode
from .get_kb_text import get_kb

async def parse_kb():
    #Executa get_kb para obter o texto bruto da KB e gera o parse do documento.
    kb_text = await get_kb()
    sections = []
    parts = re.split(r'^##\s+', kb_text, flags=re.MULTILINE)
    for part in parts[1:]:  # Ignora a primeira parte, que é o título principal
        if not part.strip():
            continue
        lines = part.splitlines()
        title = unidecode(lines[0].strip())
        content = unidecode("\n".join(lines[1:]).strip())
        sections.append({'title': title, 'content': content})
    return sections
        
    



if __name__ == "__main__":
    parse = asyncio.run(parse_kb())
    print(parse)