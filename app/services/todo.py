from sqlmodel import Session, select
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


def get_todos(session: Session) -> list[Todo]:
    return list(session.exec(select(Todo).order_by(Todo.created_at)).all())


def create_todo(session: Session, data: TodoCreate) -> Todo:
    todo = Todo(title=data.title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def update_todo(session: Session, todo_id: int, data: TodoUpdate) -> Todo | None:
    todo = session.get(Todo, todo_id)
    if not todo:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo_id: int) -> bool:
    todo = session.get(Todo, todo_id)
    if not todo:
        return False
    session.delete(todo)
    session.commit()
    return True
