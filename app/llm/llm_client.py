import os
from openai import OpenAI, AuthenticationError, RateLimitError


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL")
GROQ_MODEL = os.getenv("GROQ_MODEL")
class LLMClient:
    def __init__(self):
        self._openrouter = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )
        self._groq = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
        )

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Tenta OpenRouter primeiro. Se cair em limite de créditos (RateLimitError
        com free tier esgotado) ou AuthenticationError, faz fallback pro Groq.
        """
        try:
            response = self._openrouter.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content

        except (RateLimitError, AuthenticationError) as e:
            print(f"[LLMClient] OpenRouter falhou ({type(e).__name__}), usando Groq como fallback...")
            response = self._groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content