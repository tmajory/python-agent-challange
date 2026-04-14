#Conexão ao LLM, utilizando a biblioteca OpenAI, para enviar mensagens e receber respostas do modelo.
import os 
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
llm_model = os.getenv("LLM_MODEL")

class LLMClient:
    def __init__(self, model:str = llm_model):
        self.model = model

    def start_client(self):
        client = openai.OpenAI(
            api_key = openai.api_key,
            base_url = base_url
        )
        return client