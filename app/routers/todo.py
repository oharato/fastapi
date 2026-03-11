from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.deps import get_current_user
from app.database import get_session
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
import app.services.todo as service

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=list[TodoRead])
def list_todos(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return service.get_todos(session, current_user.id)


@router.post("", response_model=TodoRead, status_code=201)
def create_todo(data: TodoCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return service.create_todo(session, data, current_user.id)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, data: TodoUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    todo = service.update_todo(session, todo_id, data, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not service.delete_todo(session, todo_id, current_user.id):
        raise HTTPException(status_code=404, detail="Todo not found")
