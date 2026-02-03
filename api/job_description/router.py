"""
Job description router for handling job description upload, retrieval, and deletion.
"""

import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from api.auth.stack_auth import verify_stack_token
from api.core.dependencies import SupabaseClient, GeminiClient
from api.core.schemas import FileUploadResponse, FileInfoResponse
from api.db.service import (
    save_job_description,
    get_job_description as fetch_job_description,
    delete_job_description as remove_job_description,
)
from api.services.gemini import upload_file

router = APIRouter(
    prefix="/api/job-description",
    tags=["job-description"],
    dependencies=[Depends(verify_stack_token)],
)


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_200_OK
)
async def upload_job_description(
    supabase: SupabaseClient,
    gemini: GeminiClient,
    file: UploadFile = File(...),
    uuid: str = Form(None),
) -> FileUploadResponse:
    """
    Upload a job description file.

    Args:
        supabase: Supabase client dependency
        gemini: Gemini client dependency
        file: Job description file to upload
        uuid: Optional thread UUID

    Returns:
        FileUploadResponse: Success message

    Raises:
        HTTPException: If upload fails
    """
    try:
        gemini_file = await upload_file(gemini, file)

        thread_id = uuid if uuid else str(uuid_lib.uuid4())

        file_name = file.filename or "job_description.pdf"
        await save_job_description(
            supabase=supabase,
            thread_id=thread_id,
            file_name=file_name,
            job_description_file=gemini_file,
        )

        return FileUploadResponse(message="Job description uploaded successfully!")
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
async def get_job_description(
    thread_id: str, supabase: SupabaseClient
) -> FileInfoResponse:
    """
    Get job description information for a thread.

    Args:
        thread_id: Thread identifier
        supabase: Supabase client dependency

    Returns:
        FileInfoResponse: Job description file information

    Raises:
        HTTPException: If job description not found
    """
    job_description = await fetch_job_description(supabase, thread_id)
    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found"
        )

    return FileInfoResponse(
        name=job_description[0]["file_name"],
        contentType=job_description[0]["mime_type"],
    )


@router.delete(
    "/{thread_id}", response_model=FileUploadResponse, status_code=status.HTTP_200_OK
)
async def delete_job_description(
    thread_id: str, supabase: SupabaseClient
) -> FileUploadResponse:
    """
    Delete a job description for a thread.

    Args:
        thread_id: Thread identifier
        supabase: Supabase client dependency

    Returns:
        FileUploadResponse: Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        await remove_job_description(supabase, thread_id)
        return FileUploadResponse(message="Job description deleted successfully!")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job description: {e}",
        )
