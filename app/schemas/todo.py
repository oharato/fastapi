from datetime import datetime
from sqlmodel import SQLModel


class TodoCreate(SQLModel):
    title: str


class TodoUpdate(SQLModel):
    title: str | None = None
    completed: bool | None = None


class TodoRead(SQLModel):
    id: int
    title: str
    completed: bool
    created_at: datetime
