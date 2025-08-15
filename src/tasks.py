from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.database import get_session
from src.models import (
    TASK_CREATE_OPENAPI_EXAMPLES,
    TASK_UPDATE_OPENAPI_EXAMPLES,
    PriorityLevel,
    Task,
    TaskCreate,
    TaskPublic,
    TaskUpdate,
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/", response_model=TaskPublic)
def create_task(
    *,
    session: Session = Depends(get_session),
    task: Annotated[TaskCreate, Body(openapi_examples=TASK_CREATE_OPENAPI_EXAMPLES)],
) -> Task:
    """Create a new task.

    Args:\n
        task (TaskCreate): Task data to create.

    Returns:\n
        Task: The created task.
    """
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/", response_model=list[TaskPublic])
def read_tasks(
    *,
    session: Session = Depends(get_session),
    completed: bool | None = None,
    priority: PriorityLevel | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Sequence[Task]:
    """Read tasks with optional filters and pagination.

    Args:\n
        completed (bool | None, optional): Filter by completion status. Defaults to None.\n
        priority (PriorityLevel | None, optional): Filter by priority. Defaults to None.\n
        limit (int, optional): Maximum number of tasks to return. Defaults to Query(10, ge=1, le=100).\n
        offset (int, optional): Offset for pagination. Defaults to Query(0, ge=0).\n
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:\n
        list[Task]: List of tasks.
    """

    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)
    if priority is not None:
        query = query.where(Task.priority == priority)

    tasks = session.exec(query.offset(offset).limit(limit)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskPublic)
def read_task(*, session: Session = Depends(get_session), task_id: int) -> Task:
    """Read a specific task by ID.

    Args:\n
        task_id (int): ID of the task to read.\n
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:\n
        HTTPException: If the task is not found.

    Returns:\n
        Task: The requested task.
    """

    task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskPublic)
def update_task(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    task: Annotated[TaskUpdate, Body(openapi_examples=TASK_UPDATE_OPENAPI_EXAMPLES)],
) -> Task:
    """Update a specific task by ID.

    Args:\n
        task_id (int): ID of the task to update.\n
        task (TaskCreate): Task data to update.\n
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:\n
        HTTPException: If the task is not found.

    Returns:\n
        Task: The updated task.
    """

    db_task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/{task_id}", response_model=dict)
def delete_task(*, session: Session = Depends(get_session), task_id: int) -> dict[str, str]:
    """Delete a specific task by ID.

    Args:\n
        task_id (int): ID of the task to delete.\n
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:\n
        HTTPException: If the task is not found.

    Returns:
        dict[str, str]: Confirmation message.
    """

    task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
