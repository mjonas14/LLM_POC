import os
import time
from dotenv import load_dotenv
from google import genai
from google.api_core.exceptions import ServiceUnavailable
from google.genai import types as genai_types

from .tools import get_latest_index_snapshot

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful assistant for an internal finance analytics platform. "
    "When asked about index performance, call tools to retrieve data and "
    "never make up numeric values."
)

latest_index_fn = genai_types.FunctionDeclaration(
    name="get_latest_index_snapshot",
    description="Get the latest performance snapshot for an index by ID.",
    parameters={
        "type": "object",
        "properties": {
            "index_id": {
                "type": "string",
                "description": "The index ID, e.g. '2003RealEstate'.",
            }
        },
        "required": ["index_id"],
    },
)

latest_index_tool = genai_types.Tool(
    function_declarations=[latest_index_fn]
)

def chat_with_gemini(message: str) -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {message}"

    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            print(">>> First call to Gemini")
            response = client.models.generate_content(
                model=MODEL,
                contents=full_prompt,
                config=genai_types.GenerateContentConfig(
                    tools=[latest_index_tool],
                    temperature=0.1,
                ),
            )
            print("First response:", response)
            
            # Get the first candidate and first part
            candidate = response.candidates[0]
            part = candidate.content.parts[0]
            
            print("Candidate: ", candidate)

            # Some SDK versions expose function calls differently; guard both ways.
            fn_calls = getattr(response, "function_calls", None) or getattr(response, "tool_calls", None)

            if not fn_calls:
                # No tool requested; just return text
                return response.text

            fn_call = fn_calls[0]
            print("Function call received:", fn_call)

            # Depending on SDK, args may be a dict or an object with .args
            args = dict(fn_call.args)
            name = fn_call.name
            
            # After you compute name and args
            print("Function call name from model:", name)
            print("Function call args from model:", args)

            if name != "get_latest_index_snapshot":
                return f"The model requested an unknown tool: {name}"

            index_id = args.get("index_id")
            print("Calling Python tool with index_id:", index_id)

            result = get_latest_index_snapshot(index_id)
            print("Tool result from Mongo:", result)

            # If nothing found, short-circuit with a friendly message
            if result is None:
                return f"No data found for index '{index_id}'."

            fn_response_part = genai_types.Part.from_function_response(
                name=name,
                response=result,
            )

            followup = client.models.generate_content(
                model=MODEL,
                contents=[
                    # original user/system prompt as text is fine
                    full_prompt,
                    # the model’s original function call content
                    candidate.content,
                    # and the function response part
                    fn_response_part,
                ],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                ),
            )
            print("Second response:", followup)
            return followup.text

        except ServiceUnavailable:
            if attempt == max_retries - 1:
                return "Gemini is temporarily overloaded. Please try again in a moment."
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            # This prevents internal server error and lets you see the issue
            import traceback
            print("ERROR in chat_with_gemini:", e)
            traceback.print_exc()
            return f"Internal error in tool handling: {e}"
