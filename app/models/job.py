import enum
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class Job(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    params: str = Field(default="{}")
    status: JobStatus = Field(default=JobStatus.pending)
    progress: int = Field(default=0)
    result: str | None = Field(default=None)
    error: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
