from fastapi import FastAPI, Depends, HTTPException, status
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
import os

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
    data = supabase.table("message").insert({
        "thread_id": message.thread_id,
        "sender": message.sender,
        "content": message.content
    }).execute()
    return data.data

# Get all messages for a thread
async def get_messages(thread_id: str):
    data = supabase.table("message").select("*").eq("thread_id", thread_id).execute()
    return data.data