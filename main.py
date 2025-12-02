from fastapi import FastAPI
from pydantic import BaseModel
from gemini_client import chat_with_gemini

app = FastAPI(title="Gemini Chat Backend")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    print("Received message:", request.message)
    try:
        reply = chat_with_gemini(request.message)
        print("Model reply:", reply)
        return ChatResponse(reply=reply)
    except Exception as e:
        import traceback
        print("ERROR in /chat:", e)
        traceback.print_exc()
        # Return something simple so you can see it in PowerShell
        return {"reply": f"Error: {e}"}
