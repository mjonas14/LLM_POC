import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You are a helpful assistant for an internal finance analytics platform. "
    "Answer concisely and clearly."
)

def chat_with_gemini(message: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=types.Part.from_text(text='Why is the sky blue?'),
        config=types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            top_k=20,
        ),
    )
    return response.text