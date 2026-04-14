from .llm_client import LLMClient, llm_model

class LLMTools:
    def send_message(self, message:str, context:list):
        with LLMClient.start_client(self) as llm_client:
            response = llm_client.chat.completions.create(
                model = llm_model,
                messages = [
                {"role":"system",
                "content": ("Você é um assistente que responde perguntas com base exclusivamente no contexto fornecido."
                    "Responda sempre em JSON válido, sem texto fora do JSON, no seguinte formato:\n"
                    '{"answer": "sua resposta aqui", "sources": [{"section": "titulo da seção"}]}\n'
                    "Se não houver contexto suficiente, retorne:\n"
                    '{"answer": "Não encontrei informação suficiente na base para responder essa pergunta.", "sources": []}')
                },
                {
                "role":"user",
                "content":f"Pergunta: {message} Contexto: {context}"}
                ]
                )
            return response


