import os
import json
import traceback
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .prompt import interviewer_system_prompt

load_dotenv(".env.local")
api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
client = genai.Client(api_key=api_key)

def gemini_response(prompt):  
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert on Artificial Intelligence",
            max_output_tokens=500,
            temperature=0.5,
        )
    )
    return response.text

async def stream_gemini_response(prompt: str):
    """Emit a streaming SSE response from Gemini API."""
    
    def format_sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
    
    message_id = f"msg-{uuid.uuid4().hex}"
    text_stream_id = "text-1"
    text_started = False
    
    yield format_sse({"type": "start", "messageId": message_id})
    
    try:
        # Use streaming API from Gemini
        stream = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=interviewer_system_prompt(),
                max_output_tokens=1000,
                temperature=0.5,
            )
        )
        
        for chunk in stream:
            if chunk.text:
                if not text_started:
                    yield format_sse({"type": "text-start", "id": text_stream_id})
                    text_started = True
                yield format_sse({"type": "text-delta", "id": text_stream_id, "delta": chunk.text})
        
        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
    except Exception as e:
        traceback.print_exc()
        if text_started:
            yield format_sse({"type": "text-end", "id": text_stream_id})
        yield format_sse({"type": "finish"})
        yield "data: [DONE]\n\n"
        raise