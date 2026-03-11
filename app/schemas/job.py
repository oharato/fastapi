from datetime import datetime
from sqlmodel import SQLModel
from app.models.job import JobStatus


class JobCreate(SQLModel):
    name: str
    params: dict = {}


class JobRead(SQLModel):
    id: str
    name: str
    params: str
    status: JobStatus
    progress: int
    result: str | None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
