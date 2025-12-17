from fastapi import FastAPI, HTTPException
from db import db
from datetime import datetime
from pydantic import BaseModel
from app.gemini_client import chat_with_gemini

app = FastAPI(title="LLM POC Backend")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    
@app.get("/indexes")
async def list_indexes(limit: int = 10):
    docs = list(db.indexes.find({}, {"_id": 0}).limit(limit))
    return docs

@app.get("/index/latest")
async def get_latest_index(id: str):
    doc = db.indexes.find_one(
        {"ID": id},
        sort=[("Date", -1)],  # latest date
        projection={"_id": 0}  # hide Mongo _id
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Index not found")
    return doc

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = chat_with_gemini(req.message)
    return ChatResponse(reply=reply)
