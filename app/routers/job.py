import asyncio
import json
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.core.deps import get_current_user, get_current_user_from_query
from app.database import engine, get_session
from app.models.user import User
from app.schemas.job import JobCreate, JobRead
from app.tasks.sample import run_sample_job
import app.services.job as job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

TASK_REGISTRY = {
    "sample": run_sample_job,
}


@router.get("", response_model=list[JobRead])
def list_jobs(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return job_service.get_jobs(session, current_user.id)


@router.get("/stream")
async def stream_jobs(
    current_user: User = Depends(get_current_user_from_query),
):
    """SSEでジョブ一覧の変化を1秒ごとに配信する。認証はBearerまたは?token=で行う。"""
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            with Session(engine) as session:
                jobs = job_service.get_jobs(session, current_user.id)
                data = [JobRead.model_validate(j).model_dump(mode="json") for j in jobs]
            yield f"data: {json.dumps(data, default=str)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    job = job_service.get_job(session, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobRead, status_code=201)
async def create_job(data: JobCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    task_fn = TASK_REGISTRY.get(data.name)
    if not task_fn:
        raise HTTPException(status_code=400, detail=f"不明なジョブ種別: {data.name}。有効: {list(TASK_REGISTRY)}")
    job_id = str(uuid.uuid4())
    job = job_service.create_job(session, job_id, data, current_user.id)
    seconds = int(data.params.get("seconds", 10))
    await task_fn.kiq(job_id, seconds)
    return job


@router.delete("/{job_id}", status_code=204)
def cancel_job(job_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    job = job_service.get_job(session, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job_service.cancel_job(session, job_id):
        raise HTTPException(status_code=400, detail="キャンセルできない状態です")

