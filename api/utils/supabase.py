from google.genai.types import File
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import traceback

load_dotenv(".env.local")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_DEFAULT_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pydantic model for message
class Message(BaseModel):
    thread_id: str
    sender: str
    content: str

# Create a message
async def create_message(message: Message):
    try:
        data = supabase.table("message").insert({
            "thread_id": message.thread_id,
            "sender": message.sender,
            "content": message.content
        }).execute()
        return data.data
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error creating message: {e}")

# Get all messages for a thread
async def get_messages(thread_id: str, limit: int = 20):
    try:
        query = supabase.table("message")\
            .select("*")\
            .eq("thread_id", thread_id)\
            .order("sent_at", desc=True)\
            .limit(limit)
        data = query.execute()
        return data.data
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error getting messages: {e}")

async def save_resume(thread_id: str, file_name: str, resume_file: File):
    # Extract file attributes from the File object
    # Access attributes that match the JSON representation
    file_data = {
        # Supabase table attributes
        "thread_id": thread_id,
        "file_name": file_name,
        # Google GenAI File object attributes
        "name": getattr(resume_file, "name", None),
        "display_name": getattr(resume_file, "display_name", None),
        "mime_type": getattr(resume_file, "mime_type", None),
        "size_bytes": getattr(resume_file, "size_bytes", None),
        "create_time": str(getattr(resume_file, "create_time", None)) if getattr(resume_file, "create_time", None) else None,
        "expiration_time": str(getattr(resume_file, "expiration_time", None)) if getattr(resume_file, "expiration_time", None) else None,
        "update_time": str(getattr(resume_file, "update_time", None)) if getattr(resume_file, "update_time", None) else None,
        "sha256_hash": getattr(resume_file, "sha256_hash", None),
        "uri": getattr(resume_file, "uri", None),
        "state": getattr(resume_file, "state", None),
        "source": getattr(resume_file, "source", None),
        "video_metadata": getattr(resume_file, "video_metadata", None),
        "error": getattr(resume_file, "error", None),
    }
    
    # Check if a resume already exists for this thread_id
    try:
        existing_resume = supabase.table("resume").select("*").eq("thread_id", thread_id).execute()
        
        if existing_resume.data:
            # Update existing resume
            data = supabase.table("resume").update(file_data).eq("thread_id", thread_id).execute()
        else:
            # Insert new resume
            data = supabase.table("resume").insert(file_data).execute()
        
        return data.data
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error saving resume: {e}")

# Get resume identifier for a thread, ie `files/q4otskusf4j2`
async def get_resume(thread_id: str):
    try:
        data = supabase.table("resume").select("*").eq("thread_id", thread_id).execute()
        if not data.data:
            return None
        return data.data
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error getting resume identifier: {e}")