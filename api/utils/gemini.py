import os
import json
import traceback
import uuid
import tempfile
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .prompt import system_prompt
from .supabase import create_message, save_resume, Message
from fastapi import UploadFile, File, HTTPException

load_dotenv(".env.local")
api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
client = genai.Client(api_key=api_key)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB size limit
GEMINI_MODEL = "gemini-2.5-flash-lite"

def gemini_response(prompt):  
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert on Artificial Intelligence",
            max_output_tokens=500,
            temperature=0.5,
        )
    )
    return response.text

async def stream_gemini_response(prompt: str, thread_id: str):
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
                system_instruction=system_prompt(),
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
                # Save the AI message to the database
                await create_message(message=Message(thread_id=thread_id, sender="ai", content=chunk.text))

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

async def upload_file_to_gemini(thread_id: str, file: UploadFile = File(...)):
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the allowed limit")
    
    # Create a temporary file with the same extension
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        # Write the uploaded file content to the temp file
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Upload the resume using the Files API
        gemini_file = client.files.upload(file=temp_path)

        # Wait for the file to finish processing
        while gemini_file.state.name == 'PROCESSING':
            time.sleep(1)
            gemini_file = client.files.get(name=gemini_file.name)

        # Generate content using the uploaded resume
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                gemini_file,
                "Briefly thank the user for uploading the resume. Do not output anything else.",
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt(),
                max_output_tokens=1024,
                temperature=0.5,
            )
        )
        return result.text, gemini_file
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)