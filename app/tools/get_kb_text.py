#Faz request ao caminho da KB e retorna CONTEXT PARA O LLM
from os import getenv
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv(".env")
kb_url = getenv("KB_URL")

async def get_kb():
    async with httpx.AsyncClient() as client:
        response = await client.get(kb_url)
        response.raise_for_status()
        return response.text