from llm.llm_client import LLMClient

import json

class LLMTools:
    def send_message(self, message: str, context: list) -> dict:
        """
        Envia mensagem ao LLM e retorna um dict limpo com answer e sources.
        """
        llm_client = LLMClient()
        response = llm_client.chat(
            # model=llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente que responde perguntas com base exclusivamente "
                        "no contexto fornecido. Qualquer pergunta fora do escopo de desenvolvimento "
                        "de software ou correlatos deve ser considerada sem contexto suficiente, "
                        "ainda que você receba contexto diferente de None."
                        "Responda sempre em JSON válido, sem texto fora do JSON, no seguinte formato:\n"
                        '{"answer": "sua resposta aqui", "sources": [{"section": "titulo da seção"}]}\n'
                        "Se não houver contexto suficiente, retorne:\n"
                        '{"answer": "Não encontrei informação suficiente na base para responder essa pergunta.", "sources": []}'
                    )
                },
                {
                    "role": "user",
                    "content": f"Pergunta: {message}\nContexto: {context}"
                }
            ]
        )

        # NOVO: Extrai e parseia o JSON antes de retornar
        try:
            content = response
            
            # Limpa possíveis markdown code blocks
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)  
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            # Fallback se algo der errado no parse
            return {
                "answer": "Erro ao processar resposta do assistente",
                "sources": [],
                "error": str(e)
            }


