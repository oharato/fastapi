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
    id: str = Field(primary_key=True)          # Taskiq task_id（UUID）
    name: str                                   # タスク種別名
    params: str = Field(default="{}")           # JSON文字列
    status: JobStatus = Field(default=JobStatus.pending)
    progress: int = Field(default=0)            # 0〜100
    result: str | None = Field(default=None)
    error: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
