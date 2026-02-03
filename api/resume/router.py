"""
Resume router for handling resume upload, retrieval, and deletion.
"""

import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from api.auth.stack_auth import verify_stack_token
from api.core.dependencies import SupabaseClient, GeminiClient
from api.core.schemas import FileUploadResponse, FileInfoResponse
from api.db.service import (
    save_resume,
    get_resume as fetch_resume,
    delete_resume as remove_resume,
)
from api.services.gemini import upload_file

router = APIRouter(
    prefix="/api/resume", tags=["resume"], dependencies=[Depends(verify_stack_token)]
)


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_200_OK
)
async def upload_resume(
    supabase: SupabaseClient,
    gemini: GeminiClient,
    file: UploadFile = File(...),
    uuid: str = Form(None),
) -> FileUploadResponse:
    """
    Upload a resume file.

    Args:
        supabase: Supabase client dependency
        gemini: Gemini client dependency
        file: Resume file to upload
        uuid: Optional thread UUID

    Returns:
        FileUploadResponse: Success message

    Raises:
        HTTPException: If upload fails
    """
    try:
        gemini_file = await upload_file(gemini, file)

        thread_id = uuid if uuid else str(uuid_lib.uuid4())

        file_name = file.filename or "resume.pdf"
        await save_resume(
            supabase=supabase,
            thread_id=thread_id,
            file_name=file_name,
            resume_file=gemini_file,
        )

        return FileUploadResponse(message="Resume uploaded successfully!")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {e}",
        )


@router.get(
    "/{thread_id}", response_model=FileInfoResponse, status_code=status.HTTP_200_OK
)
async def get_resume(thread_id: str, supabase: SupabaseClient) -> FileInfoResponse:
    """
    Get resume information for a thread.

    Args:
        thread_id: Thread identifier
        supabase: Supabase client dependency

    Returns:
        FileInfoResponse: Resume file information

    Raises:
        HTTPException: If resume not found
    """
    resume = await fetch_resume(supabase, thread_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    return FileInfoResponse(
        name=resume[0]["file_name"], contentType=resume[0]["mime_type"]
    )


@router.delete(
    "/{thread_id}", response_model=FileUploadResponse, status_code=status.HTTP_200_OK
)
async def delete_resume(thread_id: str, supabase: SupabaseClient) -> FileUploadResponse:
    """
    Delete a resume for a thread.

    Args:
        thread_id: Thread identifier
        supabase: Supabase client dependency

    Returns:
        FileUploadResponse: Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        await remove_resume(supabase, thread_id)
        return FileUploadResponse(message="Resume deleted successfully!")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting resume: {e}",
        )
