from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request as FastAPIRequest, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from openai import OpenAI
import uuid as uuid_lib
from .utils.prompt import ClientMessage, convert_to_openai_messages
from .utils.stream import fake_data_streamer, patch_response_with_headers, stream_text, stream_resume_required_message
from .utils.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from .utils.gemini import gemini_response, stream_gemini_response, upload_file_to_gemini
from vercel import oidc
from vercel.headers import set_headers
from .utils.supabase import Message, create_message, get_messages, save_resume, get_resume_identifier
from .utils.logging import log_info
load_dotenv(".env.local")

app = FastAPI()


@app.middleware("http")
async def _vercel_set_headers(request: FastAPIRequest, call_next):
    set_headers(dict(request.headers))
    return await call_next(request)

class Request(BaseModel):
    messages: List[ClientMessage]
    id: Optional[str] = None

class PromptRequest(BaseModel):
    prompt: str

@app.get("/api/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)

# @app.post("/api/chat")
# async def handle_chat_data(request: Request, protocol: str = Query('data')):
#     messages = request.messages
#     openai_messages = convert_to_openai_messages(messages)

#     client = OpenAI(api_key=oidc.get_vercel_oidc_token(), base_url="https://ai-gateway.vercel.sh/v1")
#     response = StreamingResponse(
#         stream_text(client, openai_messages, TOOL_DEFINITIONS, AVAILABLE_TOOLS, protocol),
#         media_type="text/event-stream",
#     )
#     return patch_response_with_headers(response, protocol)

@app.post("/api/chat")
async def handle_chat_data(request: Request, protocol: str = Query('data')):
    # Extract the message content from the last message in the conversation
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    last_message = request.messages[-1]
    prompt = last_message.content or ""
    
    if not prompt and last_message.parts:
        # Extract text from parts if content is not directly available
        text_parts = [part.text for part in last_message.parts if part.text]
        prompt = " ".join(text_parts)
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No message content found")

    # Use UUID from request if provided, otherwise generate a random UUID
    thread_id = request.id if request.id else str(uuid_lib.uuid4())

    # Create user message
    await create_message(message=Message(thread_id=thread_id, sender="user", content=prompt))

    resume_identifier = await get_resume_identifier(thread_id)
    if not resume_identifier:
        # Stream AI system message asking to upload resume
        response = StreamingResponse(stream_resume_required_message(thread_id), media_type='text/event-stream')
        return patch_response_with_headers(response, protocol)

    response = StreamingResponse(stream_gemini_response(prompt, thread_id, resume_identifier), media_type='text/event-stream')
    return patch_response_with_headers(response, protocol)

@app.post("/api/generate")
async def generate_response(request: PromptRequest):
    try:
        response = gemini_response(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")
        
@app.get("/api/messages/{thread_id}")
async def get_messages_by_thread_id(thread_id: str):
    data = await get_messages(thread_id)
    return JSONResponse(content=data, status_code=200)

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), uuid: str = Form(None)):
    try:
        gemini_file = await upload_file_to_gemini(file)
        
        # Use uuid from request if provided, otherwise generate a random UUID
        thread_id = uuid if uuid else str(uuid_lib.uuid4())
        
        # Save the resume file to Supabase
        file_name = file.filename or "resume.pdf"
        await save_resume(thread_id=thread_id, file_name=file_name, resume_file=gemini_file)
        
        return JSONResponse(content={"message": "Resume uploaded successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")