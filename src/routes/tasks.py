"""任务 CRUD 路由。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db import get_db
from src.models.schemas import TaskCreate, TaskListResponse, TaskRead, TaskUpdate
from src.models.task import Task, TaskPriority, TaskStatus
from src.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """FastAPI 依赖：为每个请求构造一个 TaskService。"""
    return TaskService(db)


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    return service.create(payload)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: TaskStatus | None = Query(default=None),
    priority: TaskPriority | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    tasks, total = service.list(
        status=status,
        priority=priority,
        tag=tag,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return TaskListResponse(items=tasks, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> Task:
    task = service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    task = service.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> None:
    if not service.delete(task_id):
        raise HTTPException(status_code=404, detail="任务不存在")
