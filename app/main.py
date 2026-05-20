from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from tools.get_context import get_context
from tools.parse_kb import parse_kb
from llm.llm_tools import LLMTools



app = FastAPI()

class Message(BaseModel):
    message: str
    session_id: str | None = None

class LLMResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.post("/messages")
async def receive_message(request: Message):
    message = request.message
    parsed_kb = await parse_kb()
    context = await get_context(message, parsed_kb)
    llm_tools = LLMTools()
    response = llm_tools.send_message(message, context)
    return JSONResponse(content=response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)