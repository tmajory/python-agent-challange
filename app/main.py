from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/message")
async def receive_message(request: Message):
    message = request.message
    return {"received_message": message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)