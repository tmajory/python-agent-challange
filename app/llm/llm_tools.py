from .llm_client import LLMClient, llm_model

class LLMTools:
    def send_message(self, message:str, context:list):
        llm_client = LLMClient.start_client(self)
        response = llm_client.chat.completions.create(
            model = llm_model,
            messages = [
            {"role":"system",
            "content": ("Você é um assistente que responde perguntas com base exclusivamente no contexto fornecido qualquer pergunta fora do\
                escopo de desenvolvimento de software ou correlatos deve ser considerada sem contexto suficiente ainda que você receba contexto diferente de None."
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


