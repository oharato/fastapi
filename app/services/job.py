import json
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate


def create_job(session: Session, job_id: str, data: JobCreate, user_id: int) -> Job:
    job = Job(id=job_id, name=data.name, params=json.dumps(data.params), user_id=user_id)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_jobs(session: Session, user_id: int) -> list[Job]:
    return list(session.exec(select(Job).where(Job.user_id == user_id).order_by(Job.created_at.desc())).all())


def get_job(session: Session, job_id: str) -> Job | None:
    return session.get(Job, job_id)


def update_job_status(
    session: Session,
    job_id: str,
    status: JobStatus,
    *,
    progress: int | None = None,
    result: str | None = None,
    error: str | None = None,
) -> Job | None:
    job = session.get(Job, job_id)
    if not job:
        return None
    job.status = status
    if progress is not None:
        job.progress = progress
    if result is not None:
        job.result = result
    if error is not None:
        job.error = error
    if status == JobStatus.running and not job.started_at:
        job.started_at = datetime.now(timezone.utc)
    if status in (JobStatus.success, JobStatus.failed, JobStatus.cancelled):
        job.finished_at = datetime.now(timezone.utc)
        job.progress = 100 if status == JobStatus.success else job.progress
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def cancel_job(session: Session, job_id: str) -> bool:
    job = session.get(Job, job_id)
    if not job or job.status not in (JobStatus.pending, JobStatus.running):
        return False
    job.status = JobStatus.cancelled
    job.finished_at = datetime.now(timezone.utc)
    session.add(job)
    session.commit()
    return True
